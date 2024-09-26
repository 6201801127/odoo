from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class AccountTypemaster(models.Model):
    _name = "kw.group.type"
    _rec_name = 'name'
    

    name = fields.Char(string="Group Type")
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Active',default=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            duplicate_data = self.env['kw.group.type'].sudo().search([('name','=',self.name),('active','=',True)]) - self
            if duplicate_data:
                raise ValidationError("Group Type already exist")

    
    # @api.model
    # def create(self, vals):
    #     subcat = self.env['group.type'].search([], order='id desc', limit=1)
    #     seq = '1'
    #     if subcat:
    #         seq = str(int(subcat.code) + 1)
    #     vals['code'] = seq
    #     return super(AccountTypemaster, self).create(vals)

class AccountGroupName(models.Model):
    _name = "account.group.name"
    _rec_name = 'name'    

    name = fields.Char(string="Group Name")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    active = fields.Boolean(string='Active',default=True)
    sequence = fields.Integer(default=1)


    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            duplicate_data = self.env['account.group.name'].sudo().search([('name','=',self.name),('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id)]) - self
            if duplicate_data:
                raise ValidationError("Group name already exist")


class AccountHead(models.Model):
    _name = "account.head"
    _rec_name = 'name'

    name = fields.Char(string="Account Head")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    group_name = fields.Many2one("account.group.name")
    active = fields.Boolean(string='Active',default=True)
    sequence = fields.Integer(default=1)


    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            duplicate_data = self.env['account.head'].sudo().search([('name','=',self.name),('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id)]) - self
            if duplicate_data:
                raise ValidationError("Account head already exist")
    
    # @api.model
    # def create(self, vals):
    #     group_head = self.env['account.account.type'].browse(vals['group_head'])
    #     subcat = self.env['account.head'].search([('group_head','=',group_head.id)], order='id desc', limit=1)
    #     seq = '1'
    #     if subcat:
    #         seq = str(int(subcat.code) + 1)
    #     vals['code'] = seq
    #     return super(AccountHead, self).create(vals)

class AccountSubHead(models.Model):
    _name = "account.sub.head"
    _rec_name = 'name'

    active = fields.Boolean(string='Active',default=True)
    name = fields.Char(string="Account Sub Head")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    group_name = fields.Many2one("account.group.name")
    account_head = fields.Many2one("account.head")
    sequence = fields.Integer(default=1)


    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            duplicate_data = self.env['account.sub.head'].sudo().search([('name','=',self.name),('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id),('account_head','=',self.account_head.id)]) - self
            if duplicate_data:
                raise ValidationError("Account Sub head already exist")
    
    # @api.model
    # def create(self, vals):
    #     account_head = self.env['account.account.type'].browse(vals['account_head'])
    #     subcat = self.env['account.sub.head'].search([('account_head','=',account_head.id)], order='id desc', limit=1)
    #     seq = '1'
    #     if subcat:
    #         seq = str(int(subcat.code) + 1)
    #     vals['code'] = seq
    #     return super(AccountSubHead, self).create(vals)

class AccountTypeInherited(models.Model):
    _inherit = "account.account.type"
    _order = 'sequence asc'

    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    sequence = fields.Integer(default=1)

    internal_group = fields.Selection([
        ('equity', 'Equity'),
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('off_balance', 'Off Balance'),
    ], string="Internal Group",
        required=False,
        help="The 'Internal Group' is used to filter accounts based on the internal group set on the account type.")
    active = fields.Boolean(string='Active',default=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            duplicate_data = self.env['account.account.type'].sudo().search([('name','=',self.name),('active','=',True),('group_type','=',self.group_type.id)]) - self
            if duplicate_data:
                raise ValidationError("Group head already exist")

    # @api.model
    # def create(self, vals):
    #     group_type = self.env['kw.group.type'].browse(vals['group_type'])
    #     catagory = self.env['account.account.type'].search([('group_type','=',group_type.id)], order='id desc', limit=1)
    #     seq = '1'
    #     if catagory:
    #         seq = str(int(catagory.code) + 1)
    #     vals['code'] = seq
    #     return super(AccountTypeInherited, self).create(vals)