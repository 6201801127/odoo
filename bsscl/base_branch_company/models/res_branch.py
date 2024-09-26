# -*- coding: utf-8 -*-
import os
import base64
from odoo import SUPERUSER_ID
from odoo import api, fields, models,tools

def migrate_company_branch(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env.ref('base.main_company')
    company.write({'branch_id': env.ref('base_branch_company.data_branch_1').id})
    cr.commit()
    user_ids = env['res.users'].search([])
    for user_id in user_ids:
       if not user_id.user_has_groups('base_branch_company.group_multi_branch'):
           user_id.sudo().write({'default_branch_id': user_id.company_id.branch_id.id,
                                 'branch_ids': [(6, 0, [user_id.company_id.branch_id.id])]})
           cr.commit()


class Company(models.Model):
    _name = "res.company"
    _inherit = ["res.company"]

    branch_id = fields.Many2one('res.branch', 'Branch', ondelete="cascade")

    @api.model
    def create(self, vals):
        branch = self.env['res.branch'].create({
            'name': vals['name'],
            'code': vals['name'],
        })
        vals['branch_id'] = branch.id
        self.clear_caches()
        company = super(Company, self).create(vals)
        branch.write({'partner_id': company.partner_id.id,
                      'company_id': company.id})
        return company


class ResBranch(models.Model):
    _name = "res.branch"
    _description = "Res Branch"

    def _get_logo(self):
        return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'), 'rb') .read())

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 ondelete='restrict')
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.user.company_id, required=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    logo = fields.Binary(related='partner_id.image_1920', default=_get_logo, string="Branch Logo", readonly=False)

    #open parent branch id (priyanka)
    parent_branch_id = fields.Many2one(
        'res.branch', 'Parent Branch', index=True, ondelete='cascade',
        help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")

    child_ids = fields.One2many('res.branch', 'parent_branch_id', 'Contains')
    complete_name = fields.Char("Full Branch Name", compute='_compute_complete_name', store=True)
    website = fields.Char(related='partner_id.website', readonly=False)
    vat = fields.Char(related='partner_id.vat', string="GSTIN", readonly=False)
    # added on 10 june 2021 (Gouranga)
    location_type_id = fields.Many2one('location.type','Location Type')

    # @api.one
    @api.depends('name', 'parent_branch_id.complete_name')
    def _compute_complete_name(self):
        for line in self:
            if line.parent_branch_id.complete_name:
                line.complete_name = '%s/%s' % (line.parent_branch_id.complete_name, line.name)
            else:
                line.complete_name = line.name

    _sql_constraints = [('branch_code_company_uniq',
                         'unique (code,company_id)',
                         'The branch code must be unique per company!')]

#     @api.model
#     def create(self, vals):
#         res = super(ResBranch, self).create(vals)
#         vals.pop("name", None)
#         vals.pop("code", None)
#         vals.pop("partner_id", None)
#         vals.update({'branch_id': res.id})
#         res.partner_id.write(vals)
#         return res
    
    @api.model
    def create(self, vals):
        if not vals.get('partner_id', False):
            partner_id = self.env['res.partner'].create({'name': vals['name']})
            vals.update({'partner_id': partner_id.id})
        res = super(ResBranch, self).create(vals)
        vals.pop("name", None)
        vals.pop("code", None)
        vals.pop("partner_id", None)
        vals.update({'branch_id': res.id})
        res.partner_id.write(vals)
        return res

    # @api.multi
    def write(self, vals):
        res = super(ResBranch, self).write(vals)
        vals.pop("name", None)
        vals.pop("code", None)
        vals.pop("company_id", None)
        vals.pop("partner_id", None)
        ctx = self.env.context.copy()
        if 'branch' not in ctx:
            for record in self:
                record.partner_id.write(vals)
        return res


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def branch_default_get(self, user):
        if not user:
            user = self._uid
        branch_id = self.env['res.users'].browse(user).default_branch_id
        if not branch_id:
            branch_id = \
                self.env['res.users'].browse(user).company_id.branch_id
        return branch_id

    @api.model
    def _get_branch(self):
        return self.env.user.default_branch_id

    @api.model
    def _get_default_branch(self):
        ctx = self._context
        uid = ctx.get('uid',1)
        return self.branch_default_get(uid)

    def _branches_count(self):
        return self.env['res.branch'].sudo().search_count([])

    branch_ids = fields.Many2many('res.branch',
                                  'res_branch_users_rel',
                                  'user_id',
                                  'branch_id',
                                  'Branches', default=_get_branch,
                                  domain="[('company_id','=',company_id)]")
    default_branch_id = fields.Many2one('res.branch', 'Default branch',
                                        default=_get_branch,
                                        domain="[('company_id','=',company_id)"
                                               "]")
    branches_count = fields.Integer(
        compute='_compute_branches_count',
         default=_branches_count)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id.branch_id:
            self.default_branch_id = self.company_id.branch_id.id
            self.branch_ids = [(4, self.company_id.branch_id.id)]

    # To do : Check with all base module test cases
    # @api.multi
    # @api.constrains('default_branch_id', 'branch_ids')
    # def _check_branches(self):
    #     for user in self:
    #         if user.branch_ids \
    #                 and user.default_branch_id not in user.branch_ids:
    #             raise ValidationError(_('The selected Default Branch (%s) '
    #                                     'is not in the Branches!') % (
    #                 user.default_branch_id.name))

    # @api.multi
    def _compute_branches_count(self):
        branches_count = self._branches_count()
        for user in self:
            user.branches_count = branches_count

    @api.model
    def create(self, vals):
        res = super(Users, self).create(vals)
        if 'company_id' in vals:
            vals.update({
                'default_branch_id': self.company_id.branch_id.id,
            })
        return res

    # @api.multi
    def write(self, vals):
        res = super(Users, self).write(vals)
        if 'company_id' in vals:
            self.default_branch_id = self.company_id.branch_id.id
        return res
