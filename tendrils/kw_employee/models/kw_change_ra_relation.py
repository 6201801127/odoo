# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class kw_change_ra_relation(models.TransientModel):
    _name = 'kw_change_ra_relation'
    _description = 'Change RA'
    _rec_name = "display_name"

    display_name = fields.Char(string="Name", default="Change RA", compute='_ra_display_name')
    search_by = fields.Selection(string="Search By",
                                 selection=[('ra', 'RA'), ('user', 'User')], default="user")
    reporting_auth_id = fields.Many2one('hr.employee', string="Enter Name")
    ra_details_id = fields.One2many('kw_change_ra_log', 'ra_rel_id', string="RA Details")

    """ Change the New Ra by clicking A button"""

    def change_ra(self):
        for rec in self.ra_details_id:
            if rec.new_ra_id.id != False:
                inform_template = self.env.ref('kw_employee.new_change_ra_email_template')
                email_cc = str(rec.new_ra_id.work_email + ',' + rec.emp_name.parent_id.work_email)
                hr_email = self.env['res.groups'].sudo().search([('name', '=', 'HRD')])
                if hr_email:
                    if hr_email.users:
                        hrd_email = hr_email.users.mapped('email')
                        hrd_email_str = email_cc + ',' + ','.join(hrd_email)
                    else:
                        hrd_email_str = email_cc
                else:
                    hrd_email_str = email_cc

                inform_template.with_context(email=rec.emp_name.work_email, email_cc1=hrd_email_str).send_mail(rec.id,
                                                                                                               notif_layout="kwantify_theme.csm_mail_notification_light")
                new_rec = self.env['hr.employee'].sudo().search([('id', '=', rec.emp_name.id)])

                new_rec.write({'parent_id': rec.new_ra_id.id})
                record = self.env['kw_emp_sync_log'].sudo().search(
                    [('model_id', '=', 'hr.employee'), ('rec_id', '=', new_rec.id), ('code', '=', 1),
                     ('status', '=', 0)])
                # print(record,"=======record===========")
                # print(j)
                if not record.exists():
                    record.create({'model_id': 'hr.employee', 'rec_id': new_rec.id, 'code': 1, 'status': 0})
                else:
                    pass

        """ reload the page when one functionality is over"""
        if self._context.get('eos_ra_change_action'):
            tree_view_id = self.env.ref('kw_eos_integrations.kw_eos_checklist_view_tree').id
            form_view_id = self.env.ref('kw_eos_kw_eos_checklist_view_form').id  # change the id name for eos
            action = {
                'name': 'EOS Apply',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_eos_checklist',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'target': 'current',
                'view_id': tree_view_id,
            }
            return action
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    """ Validation for New RA"""

    @api.model
    @api.onchange('ra_details_id')
    def _check_new_ra(self):
        for record in self:
            for rec in record.ra_details_id:
                if rec.new_ra_id.name == rec.emp_parent and rec.emp_parent != False:
                    raise ValidationError('New RA Must Not Be Same With Current RA')
                if rec.new_ra_id.id == rec.emp_name.id:
                    raise ValidationError('New RA Must Not Be Same With Employee Name.')
                if rec.new_ra_id.parent_id.id == rec.emp_name.id:
                    raise ValidationError('Recursive RA can not be Created')

    @api.model
    def _ra_display_name(self):
        for record in self:
            record.display_name = 'Change RA'

    """Showing the RA Name and Users by searching as an RA or user respectively"""

    @api.onchange('search_by')
    def _get_ra(self):
        lst = []
        lst1 = []
        emp = self.env['hr.employee'].sudo().search([])
        for rec in emp:
            if rec.parent_id:
                lst1.append(rec.id)
            if rec.parent_id:
                if rec.parent_id.id not in lst:
                    lst.append(rec.parent_id.id)

        if self.search_by == "user":
            self.reporting_auth_id = False
            return {'domain': {
                'reporting_auth_id': (['&', ('id', 'in', lst1), '|', ('active', '=', False), ('active', '=', True)])}}
        else:
            check_eos = self._context.get('eos_ra_change_action')
            if not check_eos:
                self.reporting_auth_id = False
            return {'domain': {
                'reporting_auth_id': (['&', ('id', 'in', lst), '|', ('active', '=', False), ('active', '=', True)])}}

    """Showing the RA details by searching as an RA or user"""

    @api.onchange('reporting_auth_id')
    def get_employee(self):
        self.ra_details_id = False
        vals = []
        if self.reporting_auth_id:
            if self.search_by == 'user':
                emp_rec = self.env['hr.employee'].sudo().search([('id', '=', self.reporting_auth_id.id)])
                vals.append([0, 0, {
                    'emp_name': emp_rec.id,
                    'new_ra_id': emp_rec.new_ra_id.id if emp_rec.new_ra_id else False,
                }])
                self.ra_details_id = vals
            else:
                vals = []
                child_id = self.env['hr.employee'].sudo().search([('parent_id', '=', self.reporting_auth_id.id)])
                for rec in child_id:
                    vals.append([0, 0, {
                        'emp_name': rec.id if rec.id else False,
                        'new_ra_id': rec.new_ra_id.id if rec.new_ra_id.id else False,
                    }])
                self.ra_details_id = vals

    """ Open the form view when click the menu item"""

    @api.multi
    def view_form(self):
        check_active_id = self.env['kw_change_ra_relation'].browse(self.id)
        form_view_id = self.env.ref("kw_employee.kw_change_ra_relation_view_form")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_change_ra_relation',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': check_active_id.id,
            'view_id': form_view_id.id,
            'target': 'self',
            'flags': {'mode': 'edit', "toolbar": False}
        }
