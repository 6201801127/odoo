from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')
    state = fields.Selection([('draft', 'Unposted'), ('to_approve', 'To Approve'), ('posted', 'Posted')],
                             string='Status',
                             required=True, readonly=True, copy=False, default='draft',
                             help='All manually created new journal entries are usually in the status \'Unposted\', '
                                  'but you can set the option to skip that status on the related journal. '
                                  'In that case, they will behave as journal entries automatically created by the '
                                  'system on document validation (invoices, bank statements...) and will be created '
                                  'in \'Posted\' status.')
    exchange_rate = fields.Float('Exchange Rate')
    company_currency_id = fields.Many2one('res.currency', 'Company Currency',
                                          default=lambda self: self.env.user.company_id.currency_id)
    is_foreign_currency = fields.Boolean('Is Foreign Currency', default=False)
    # csm_acc_conf = fields.Boolean('csm account conf', compute="compute_csm_config")
    # is_payment_receipt = fields.Boolean(compute='compute_csm_config', default=False)
    ref = fields.Char(string='Description', copy=False)
    mode_of_payment = fields.Many2one('account.payment.method',string="Mode of Payment")
    
    
    #
    # def action_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'
    #
    #
    # def action_post(self):
    #     for rec in self:
    #         if rec.is_payment_receipt:
    #             for r in rec.line_ids:
    #                 if r.invoice_id:
    #                     r.invoice_id.assign_outstanding_credit(r.id)
    #     res = super().action_post()
    #     return res
	#
    # @api.depends('date')
    # def compute_csm_config(self):
    #     for rec in self:
    #         enable_csm_account_conf_status = self.env['ir.config_parameter'].sudo().get_param(
    #             'kw_accounting.enable_csm_account_conf_status')
    #         rec.csm_acc_conf = enable_csm_account_conf_status
    #         if self._context.get('search_default_receipt_filter') or self._context.get('search_default_payment_filter'):
    #             rec.is_payment_receipt = True
	#
    # @api.onchange('exchange_rate')
    # def _onchange_exchange_rate(self):
    #     currency_rate_obj = self.env['res.currency.rate'].sudo()
    #     for invoice in self:
    #         if (invoice.currency_id.id != invoice.company_currency_id.id) and invoice.exchange_rate > 0:
    #             currency_obj = currency_rate_obj.search(
    #                 [('name', '=', date.today()), ('currency_id', '=', invoice.currency_id.id)])
    #             delete_query = f'delete from res_currency_rate where currency_id = {invoice.currency_id.id}'
    #             self.env.cr.execute(delete_query)
    #             currency_rate_obj.create({
    #                 'name': date.today(), 'rate': 1 / invoice.exchange_rate, 'currency_id': invoice.currency_id.id})
	#
    # # @api.model
    # # def default_get(self, default_fields):
    # #     res = super().default_get(default_fields)
    # #     journal_obj = self.env['account.journal'].sudo()
    # #     if self._context.get('search_default_receipt_filter'):
    # #         res['journal_id'] = journal_obj.search([('code', 'in', ['BNK','CSH'])]).id
    # #     if self._context.get('search_default_payment_filter'):
    # #         res['journal_id'] = journal_obj.search([('code', 'in', ['BNK','CSH'])]).id
    # #     if self._context.get('search_default_general_journal_filter'):
    # #         res['journal_id'] = journal_obj.search([('code', '=', 'GJ')]).id
    # #     if self._context.get('search_default_contra_filter'):
    # #         res['journal_id'] = journal_obj.search([('code', '=', 'CV')]).id
    # #     return res
    # @api.onchange('move_type')
    # def get_journals(self):
    #     for move in self:
    #         if move.move_type == 'contra':
    #             return {'domain': {'journal_id': [('code', '=','CV')]}}
    #         if move.move_type == 'payment' or move.move_type == 'receipt' :
    #             return {'domain': {'journal_id': [('code', 'in',['BNK','CSH'])]}}
    #
    #
    # @api.onchange('currency_id')
    # def onchange_currency(self):
    #     for rec in self:
    #         if rec.currency_id.id != rec.company_currency_id.id:
    #             rec.is_foreign_currency = True
	#
    # def apply_journal(self):
    #     for rec in self:
    #         rec.write({'state': 'to_approve'})
    #     return True
    #


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    _order = "date desc, id asc"

    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    group_id = fields.Many2one('account.group', 'Group',)
	# domain="[('account_type_id.code','=', 'gn')]")
    account_head_id = fields.Many2one('account.group', 'Account Head',)
		# domain="[('account_type_id.code','=', 'ah')]")
    account_subhead_id = fields.Many2one('account.group', 'Account Sub-Head')
                                         # domain="[('account_type_id.code','=', 'ash')]")
    is_payment_receipt = fields.Boolean()
    is_budget_mandatory = fields.Boolean(related='account_id.is_budget_mandatory')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    product_category = fields.Selection([('product','Goods'),('service','Service')],string="Category")
    clear_date = fields.Date(string="Clear Date")

    
    @api.constrains('clear_date')
    def _check_future_clear_date(self):
        for record in self:
            if record.clear_date and record.clear_date < record.date:
                raise ValidationError("Clear date should not be less than transaction date.")
            
    
    @api.onchange('group_id')
    def onchange_group_id(self):
        self.account_head_id, self.account_subhead_id, self.account_id = False, False, False
        return {'domain': {'account_head_id': [('parent_id', '=', self.group_id.id)]}}

    @api.onchange('account_head_id')
    def onchange_account_head_id(self):
        self.account_subhead_id, self.account_id = False, False
        return {'domain': {'account_subhead_id': [('parent_id', '=', self.account_head_id.id)]}}

    @api.onchange('account_subhead_id')
    def onchange_account_subhead_id(self):
        self.account_id = False
        return {'domain': {'account_id': [('group_id', '=', self.account_subhead_id.id)]}}

