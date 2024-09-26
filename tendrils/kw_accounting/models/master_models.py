from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class AccountTypemaster(models.Model):
    _name = "kw.group.type"
    _description = "kw.group.type"
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
    _description = "account.group.name"
    _rec_name = 'name'


    name = fields.Char(string="Group Name")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    active = fields.Boolean(string='Active',default=True)
    sequence = fields.Integer(default=1)
    
    @api.onchange('group_type','group_head')
    def get_code(self):
        last_sequence =self.env['account.group.name'].search([('group_type','=',self.group_type.id),('group_head','=',self.group_head.id)]).mapped('code')
        res = sorted([eval(i) for i in last_sequence])[-1] if len(last_sequence) > 0 else 1
        if self.group_type and self.group_head:
            if last_sequence:
                self.code = str(res + 1)
            else:
                self.code = str(res)
                
    @api.onchange('group_type')
    def _onchange_group_type(self):
        self.group_head = False
        group_type = self.env['account.account.type'].sudo().search([('group_type','=',self.group_type.id)])
        result = {}
        if group_type:
            result = {'domain': {'group_head': [('id', 'in', group_type.ids)]}}
        else:
            result = {'domain': {'group_head': [('id', 'in', [])]}}
        return result
    
    @api.constrains('code')
    def _check_duplicate(self):
        if self.code:
            duplicate_data = self.env['account.group.name'].sudo().search([('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('code','=',self.code)]) - self
            if duplicate_data:
                raise ValidationError("Code is already exist")


class AccountHead(models.Model):
    _name = "account.head"
    _description = "account.head"
    _rec_name = 'name'

    name = fields.Char(string="Account Head")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    group_name = fields.Many2one("account.group.name")
    active = fields.Boolean(string='Active',default=True)
    sequence = fields.Integer(default=1)

    @api.onchange('group_type','group_head','group_name')
    def get_code(self):
        last_sequence =self.env['account.head'].search([('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id)]).mapped('code')
        res = sorted([eval(i) for i in last_sequence])[-1] if len(last_sequence) > 0 else 1
        if self.group_type and self.group_head and self.group_name:
            if last_sequence:
                self.code = str(res + 1)
            else:
                self.code = str(res)
                
    @api.onchange('group_type')
    def _onchange_group_type(self):
        self.group_head = False
        group_type = self.env['account.account.type'].sudo().search([('group_type','=',self.group_type.id)])
        result = {}
        if group_type:
            result = {'domain': {'group_head': [('id', 'in', group_type.ids)]}}
        else:
            result = {'domain': {'group_head': [('id', 'in', [])]}}
        return result
    
    @api.onchange('group_head')
    def _onchange_group_head(self):
        self.group_name = False
        group_name = self.env['account.group.name'].sudo().search([('group_head','=',self.group_head.id)])
        result = {}
        if group_name:
            result = {'domain': {'group_name': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'group_name': [('id', 'in', [])]}}
        return result
    
    
    @api.constrains('code')
    def _check_duplicate(self):
        if self.code:
            duplicate_data = self.env['account.head'].sudo().search([('code','=',self.code),('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id)]) - self
            if duplicate_data:
                raise ValidationError("Code is already exist")
    
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
    _description = "account.sub.head"
    _rec_name = 'name'

    active = fields.Boolean(string='Active',default=True)
    name = fields.Char(string="Account Sub Head")
    code = fields.Char(string="Code")
    group_type = fields.Many2one("kw.group.type")
    group_head = fields.Many2one("account.account.type")
    group_name = fields.Many2one("account.group.name")
    account_head = fields.Many2one("account.head")
    sequence = fields.Integer(default=1)

    @api.onchange('group_type')
    def _onchange_group_type(self):
        self.group_head = False
        group_type = self.env['account.account.type'].sudo().search([('group_type','=',self.group_type.id)])
        result = {}
        if group_type:
            result = {'domain': {'group_head': [('id', 'in', group_type.ids)]}}
        else:
            result = {'domain': {'group_head': [('id', 'in', [])]}}
        return result
    
    @api.onchange('group_head')
    def _onchange_group_head(self):
        self.group_name = False
        group_name = self.env['account.group.name'].sudo().search([('group_head','=',self.group_head.id)])
        result = {}
        if group_name:
            result = {'domain': {'group_name': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'group_name': [('id', 'in', [])]}}
        return result
    
    @api.onchange('group_name')
    def _onchange_group_name(self):
        self.account_head = False
        group_name = self.env['account.head'].sudo().search([('group_name','=',self.group_name.id)])
        result = {}
        if group_name:
            result = {'domain': {'account_head': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'account_head': [('id', 'in', [])]}}
        return result
    
    @api.onchange('group_type','group_head','group_name','account_head')
    def get_code(self):
        last_sequence =self.env['account.sub.head'].search([('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id),('account_head','=',self.account_head.id)]).mapped('code')
        res = sorted([eval(i) for i in last_sequence])[-1] if len(last_sequence) > 0 else 1
        if self.group_type and self.group_head and self.group_name and self.account_head:
            if last_sequence:
                self.code = str(res + 1)
            else:
                self.code = str(res)
    
    @api.constrains('code')
    def _check_duplicate(self):
        if self.code:
            duplicate_data = self.env['account.sub.head'].sudo().search([('code','=',self.code),('active','=',True),('group_type','=',self.group_type.id),('group_head','=',self.group_head.id),('group_name','=',self.group_name.id),('account_head','=',self.account_head.id)]) - self
            if duplicate_data:
                raise ValidationError("Code is already exist")
    
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

    code = fields.Char(string="Code",readonly=True)
    group_type = fields.Many2one("kw.group.type")
    sequence = fields.Integer(default=1)
    budget_update = fields.Boolean(string="Capital Budget Update")

    @api.onchange('group_type')
    def get_code(self):
        last_sequence =self.env['account.account.type'].search([('group_type','=',self.group_type.id)]).mapped('code')
        res = sorted([eval(i) for i in last_sequence])[-1] if len(last_sequence) > 0 else 1
        if self.group_type:
            if last_sequence:
                self.code = str(res + 1)
            else:
                self.code = str(res)

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

    @api.constrains('code')
    def _check_duplicate(self):
        if self.code:
            duplicate_data = self.env['account.account.type'].sudo().search([('code','=',self.code),('active','=',True),('group_type','=',self.group_type.id)]) - self
            if duplicate_data:
                raise ValidationError("Code is already exist")

    # @api.model
    # def create(self, vals):
    #     group_type = self.env['kw.group.type'].browse(vals['group_type'])
    #     catagory = self.env['account.account.type'].search([('group_type','=',group_type.id)], order='id desc', limit=1)
    #     seq = '1'
    #     if catagory:
    #         seq = str(int(catagory.code) + 1)
    #     vals['code'] = seq
    #     return super(AccountTypeInherited, self).create(vals)