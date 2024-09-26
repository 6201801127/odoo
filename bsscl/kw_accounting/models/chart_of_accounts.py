from odoo import models, fields, api

class AccountInherit(models.Model):
    _name = 'account.account'
    _inherit = 'account.account'

    # branch_id = fields.Many2one('accounting.branch.unit', 'Branch')
    is_budget_mandatory = fields.Boolean('Is Budget Mandatory', default=False)
    # group2 = fields.Many2one('group_type', string='Group Type', required=True)
    # group3 = fields.Many2one('group_head', string='Group Head', required=True) 
    # kw_code = fields.Char(string="Kwantify Code")
    # group_name = fields.Char(string="Group Name") 
    # account_subhead = fields.Char(string="Account Subhead")
    reconcile = fields.Boolean(string='Allow Reconciliation', default=True,
        help="Check this box if this account allows invoices & payments matching of journal items.")

    group_type = fields.Many2one('kw.group.type',string="Group Type")
    group_name = fields.Many2one('account.group.name',string="Group Name")
    account_head_id = fields.Many2one('account.head',string="Account Head")
    account_sub_head_id = fields.Many2one('account.sub.head',string="Account Sub Head")
    partner_type = fields.Selection([('customer','Customer'),('vendor','Vendor'),('employee','Employee')],string="Partner Type")
    sequence = fields.Integer(string="Sequence.")
    active = fields.Boolean(string='Archive',default=True)
    ledger_type = fields.Selection([('bank','Bank'),('cash','Cash'),('others','Others')],string="Ledger Type")
    effective_from =fields.Date("Effective From")

    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id,name)', 'The code of the account must be unique per company !')
    ]

    @api.onchange('internal_type')
    def onchange_internal_type(self):
        self.reconcile = True
        if self.internal_type == 'liquidity':
            self.reconcile = True
            
    @api.onchange('group_type')
    def _onchange_group_type(self):
        self.user_type_id = False
        group_type = self.env['account.account.type'].sudo().search([('group_type','=',self.group_type.id)])
        result = {}
        if group_type:
            result = {'domain': {'user_type_id': [('id', 'in', group_type.ids)]}}
        else:
            result = {'domain': {'user_type_id': [('id', 'in', [])]}}
        return result
    
    @api.onchange('user_type_id')
    def _onchange_user_type_id(self):
        self.group_name = False
        group_name = self.env['account.group.name'].sudo().search([('group_head','=',self.user_type_id.id)])
        result = {}
        if group_name:
            result = {'domain': {'group_name': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'group_name': [('id', 'in', [])]}}
        return result

    @api.onchange('group_name')
    def _onchange_group_name(self):
        self.account_head_id = False
        group_name = self.env['account.head'].sudo().search([('group_name','=',self.group_name.id)])
        result = {}
        if group_name:
            result = {'domain': {'account_head_id': [('id', 'in', group_name.ids)]}}
        else:
            result = {'domain': {'account_head_id': [('id', 'in', [])]}}
        return result

    @api.onchange('account_head_id')
    def _onchange_account_head_id(self):
        self.account_sub_head_id = False
        account_sub_head_ids = self.env['account.sub.head'].sudo().search([('account_head','=',self.account_head_id.id)])
        result = {}
        if account_sub_head_ids:
            result = {'domain': {'account_sub_head_id': [('id', 'in', account_sub_head_ids.ids)]}}
        else:
            result = {'domain': {'account_sub_head_id': [('id', 'in', [])]}}
        return result
    
    
    def write(self,vals):
        # print("inside if=============",self.account_head_id,vals)
        if vals.get('account_sub_head_id'):
            subcat = self.env['account.sub.head'].search([('active','=',True),('id','=',int(vals.get('account_sub_head_id')))])
            group_type = vals.get('group_type') if 'group_type' in vals else self.group_type.id 
            user_type_id = vals.get('user_type_id') if 'user_type_id' in vals else self.user_type_id.id 
            account_head_id = vals.get('account_head_id') if 'account_head_id' in vals else self.account_head_id.id
            group_name = vals.get('group_name') if 'group_name' in vals else self.group_name.id
            account_sub_head_id = vals.get('account_sub_head_id') if 'account_sub_head_id' in vals else self.account_sub_head_id.id

            seq,dyseq = self.get_account_sequence(group_type,user_type_id,account_head_id,group_name,account_sub_head_id)
            # vals['code'] = subcat.group_head.group_type.code + subcat.group_head.code + subcat.code + seq 
            vals['code'] = (subcat.group_type.code or self.group_type.code or ' ') + "-" + (subcat.group_head.code or self.user_type_id.code or ' ') + "-" + (subcat.group_name.code or self.group_name.code or ' ') + "-" + (subcat.account_head.code or self.account_head_id.code or ' ') + "-" + (subcat.code or self.account_sub_head_id.code or ' ') + "-" + seq
            if dyseq:
                vals['sequence']=dyseq
        return super(AccountInherit, self).write(vals)

    @api.model
    def create(self, vals):
        if 'account_head_id' in vals:
            subcat = self.env['account.sub.head'].search([('active','=',True),('id','=',int(vals.get('account_sub_head_id')))])
            seq,dyseq = self.get_account_sequence(vals.get('group_type'),vals.get('user_type_id'),vals.get('account_head_id'),vals.get('group_name'),vals.get('account_sub_head_id'))
            # print("code ----",subcat.group_head.group_type.code + subcat.group_head.code + subcat.code + seq)
            vals['code'] = (subcat.group_head.group_type.code or ' ') + "-" + (subcat.group_head.code or ' ') + "-" + (subcat.group_name.code or ' ') + "-" + (subcat.account_head.code or ' ') + "-" + (subcat.code or ' ') + "-" + seq
            if dyseq:
                vals['sequence']=dyseq
        return super(AccountInherit, self).create(vals)


    def get_account_sequence(self,group_type,user_type_id,account_head_id,group_name,account_sub_head_id):
        records = self.env['account.account'].search([('group_type','=',group_type),('user_type_id','=',user_type_id),('group_name','=',group_name),('account_head_id','=',account_head_id),('account_sub_head_id','=',account_sub_head_id),('sequence','!=',False)], order='sequence desc',limit=1)
        # print("============",records, self)
        codes = (records.code)[-3:] if records else False
        seq = '001'
        # print("codes=====",codes)
        if codes:
            # len_rec = len((records.code)[-3:])
            sum = str(int(codes) + 1)
            if len(sum) == 3:
                seq = str(int(codes) + 1)
            elif len(sum) == 2:
                seq = '0' + str(int(codes) + 1) 
            elif len(sum) == 1:
                seq = '00' + str(int(codes) + 1)
            else:
                pass
        sequence=int(codes if records else 0) + 1
        # print("sequence=====",seq)
        return seq,sequence