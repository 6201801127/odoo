from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    # branch_id = fields.Many2one('kw_res_branch', 'Branch')
    reference_number = fields.Char(string="Reference Number")
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    invoice_number = fields.Char('Invoice Number')
    kw_id = fields.Integer('KW ID')
    has_outstanding = fields.Boolean(compute='_get_outstanding_info_JSON')
    exchange_rate = fields.Float('Exchange Rate')
    is_foreign_currency = fields.Boolean('Is Foreign Currency', default=False)
    # unit_id = fields.Many2one('accounting.branch.unit', 'Unit')
    # csm_acc_conf = fields.Boolean('csm account conf', compute="compute_csm_config")
    client_certificate = fields.Binary('Client Certificate', attachment=True)
    is_budget_treasury = fields.Boolean(compute="compute_line_budget")
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export'),
            ('deductor','Registered Business - Deductor'),
            ('regular_deductor','Regular & Deductor')], string="GST Treatment",compute="_compute_l10n_in_gst_treatment", store=True, readonly=False)
    comment = fields.Text('Narration', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Accounting Date',
        copy=False,
        help="Keep empty to use the invoice date.",
        readonly=True, default=date.today())
    #
    #
    # def action_invoice_draft(self):
    #     # if self.filtered(lambda inv: inv.state != 'cancel'):
    #     #     raise UserError(_("Invoice must be cancelled in order to reset it to draft."))
    #     # go from canceled state to draft state
    #     self.action_cancel()
    #     self.write({'state': 'draft', 'date': False})
    #     # Delete former printed invoice
    #     try:
    #         report_invoice = self.env['ir.actions.report']._get_report_from_name('account.report_invoice')
    #     except IndexError:
    #         report_invoice = False
    #     if report_invoice and report_invoice.attachment:
    #         for invoice in self:
    #             with invoice.env.do_in_draft():
    #                 invoice.number, invoice.state = invoice.move_name, 'open'
    #                 attachment = self.env.ref('account.account_invoices').retrieve_attachment(invoice)
    #             if attachment:
    #                 attachment.unlink()
    #     return True
    #
    # @api.depends('partner_id')
    # def _compute_l10n_in_gst_treatment(self):
    #     for record in self:
    #         record.l10n_in_gst_treatment = record.partner_id.l10n_in_gst_treatment
	#
    # @api.depends('invoice_line_ids')
    # def compute_line_budget(self):
    #     for rec in self:
    #         for r in rec.invoice_line_ids:
    #             if r.budget_type == 'treasury':
    #                 rec.is_budget_treasury = True
	#
    # @api.depends('name')
    # def compute_csm_config(self):
    #     for rec in self:
    #         enable_csm_account_conf_status = self.env['ir.config_parameter'].sudo().get_param(
    #             'kw_accounting.enable_csm_account_conf_status')
    #         rec.csm_acc_conf = enable_csm_account_conf_status
	#
    # @api.onchange('currency_id')
    # def check_currency(self):
    #     for rec in self:
    #         rec.is_foreign_currency, rec.exchange_rate = False, False
    #         if rec.company_currency_id.id != rec.currency_id.id:
    #             rec.is_foreign_currency = True
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
    # @api.onchange('cash_rounding_id', 'invoice_line_ids', 'tax_line_ids', 'amount_total')
    # def _onchange_cash_rounding(self):
    #     # Drop previous cash rounding lines
    #     lines_to_remove = self.invoice_line_ids.filtered(lambda l: l.is_rounding_line)
    #     if lines_to_remove:
    #         self.invoice_line_ids -= lines_to_remove
	#
    #     # Clear previous rounded amounts
    #     for tax_line in self.tax_line_ids:
    #         if tax_line.amount_rounding != 0.0:
    #             tax_line.amount_rounding = 0.0
	#
    #     if self.cash_rounding_id:
    #         rounding_amount = self.cash_rounding_id.compute_difference(self.currency_id, self.amount_total)
    #         if not self.currency_id.is_zero(rounding_amount):
    #             if self.cash_rounding_id.strategy == 'biggest_tax':
    #                 # Search for the biggest tax line and add the rounding amount to it.
    #                 # If no tax found, an error will be raised by the _check_cash_rounding method.
    #                 if not self.tax_line_ids:
    #                     return
    #                 biggest_tax_line = None
    #                 for tax_line in self.tax_line_ids:
    #                     if not biggest_tax_line or tax_line.amount > biggest_tax_line.amount:
    #                         biggest_tax_line = tax_line
    #                 biggest_tax_line.amount_rounding += rounding_amount
    #             elif self.cash_rounding_id.strategy == 'add_invoice_line':
    #                 if rounding_amount > 0.0:
    #                     account_id = self.cash_rounding_id._get_loss_account_id().id
    #                 else:
    #                     account_id = self.cash_rounding_id._get_profit_account_id().id
    #                 # Create a new invoice line to perform the rounding
    #                 rounding_line = self.env['account.move.line'].new({
    #                     'name': self.cash_rounding_id.name,
    #                     'invoice_id': self.id,
    #                     'account_id': self.cash_rounding_id.account_id.id,
    #                     'price_unit': rounding_amount,
    #                     'quantity': 1,
    #                     'is_rounding_line': True,
    #                     'sequence': 9999  # always last line
    #                 })
	#
    #                 # To be able to call this onchange manually from the tests,
    #                 # ensure the inverse field is updated on account.move.
    #                 if not rounding_line in self.invoice_line_ids:
    #                     self.invoice_line_ids += rounding_line
	#
    #
    # def action_move_create(self):
    #     """ Creates invoice related analytics and financial move lines """
    #     account_move = self.env['account.move']
	#
    #     for inv in self:
    #         if not inv.journal_id.sequence_id:
    #             raise UserError(_('Please define sequence on the journal related to this invoice.'))
    #         if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
    #             raise UserError(_('Please add at least one invoice line.'))
    #         if inv.move_id:
    #             continue
	#
	#
    #         if not inv.date_invoice:
    #             inv.write({'date_invoice': fields.Date.context_today(self)})
    #         if not inv.date_due:
    #             inv.write({'date_due': inv.date_invoice})
    #         company_currency = inv.company_id.currency_id
    #         # create move lines (one per invoice line + eventual taxes and analytic lines)
    #         iml = inv.invoice_line_move_line_get()
    #         iml += inv.tax_line_move_line_get()
	#
    #         diff_currency = inv.currency_id != company_currency
    #         # create one move line for the total and possibly adjust the other lines amount
    #         total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)
	#
    #         name = inv.name or ''
    #         if inv.payment_term_id:
    #             totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
    #             res_amount_currency = total_currency
    #             for i, t in enumerate(totlines):
    #                 if inv.currency_id != company_currency:
    #                     amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
    #                 else:
    #                     amount_currency = False
	#
    #                 # last line: add the diff
    #                 res_amount_currency -= amount_currency or 0
    #                 if i + 1 == len(totlines):
    #                     amount_currency += res_amount_currency
	#
    #                 iml.append({
    #                     'type': 'dest',
    #                     'name': name,
    #                     'price': t[1],
    #                     'account_id': inv.account_id.id,
    #                     'date_maturity': t[0],
    #                     'amount_currency': diff_currency and amount_currency,
    #                     'currency_id': diff_currency and inv.currency_id.id,
    #                     'invoice_id': inv.id
    #                 })
    #         else:
    #             iml.append({
    #                 'type': 'dest',
    #                 'name': name,
    #                 'price': total,
    #                 'account_id': inv.account_id.id,
    #                 'date_maturity': inv.date_due,
    #                 'amount_currency': diff_currency and total_currency,
    #                 'currency_id': diff_currency and inv.currency_id.id,
    #                 'invoice_id': inv.id
    #             })
	#
    #         part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
    #         line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
    #         line = inv.group_lines(iml, line)
	#
    #         line = inv.finalize_invoice_move_lines(line)
	#
    #         date = inv.date_invoice
    #         move_vals = {
    #             'ref': inv.reference,
    #             'line_ids': line,
    #             'journal_id': inv.journal_id.id,
    #             'date': date,
    #             'narration': inv.comment,
    #         }
    #         move = account_move.create(move_vals)
    #         # Pass invoice in method post: used if you want to get the same
    #         # account move reference when creating the same invoice after a cancelled one:
    #         move.post(invoice = inv)
    #         # make the invoice point to that move
    #         vals = {
    #             'move_id': move.id,
    #             'date': date,
    #             'move_name': move.name,
    #         }
    #         inv.write(vals)
    #     return True
	#

class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.move.line'
    
    name = fields.Text(string='Description', required=False)
    hsn_code = fields.Char('HSN/SAC Code')
    group_id = fields.Many2one('account.group', 'Group', domain="[('account_type_id.code','=', 'gn')]")
    account_head_id = fields.Many2one('account.group', 'Account Head', domain="[('account_type_id.code','=', 'ah')]")
    account_subhead_id = fields.Many2one('account.group', 'Account Sub-Head',
                                         domain="[('account_type_id.code','=', 'ash')]")
    lcy = fields.Float('Amount in LCY')
    budget_type = fields.Selection([('project', 'Project'), ('treasury', 'Treasury')], 'Budget Type')
    product_category = fields.Selection([('product','Goods'),('service','Service')],string="Category")
    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")

    @api.onchange('product_id')
    def onchange_product(self):
        self.hsn_code = self.product_id.l10n_in_hsn_code

    @api.onchange('product_category')
    def _onchange_product_category(self):
        self.product_id = False
        self.name = False
        if self.product_category == 'product':
            return {'domain': {'product_id': [('type', 'in', ['consu','product'])]}}
        elif self.product_category == 'service':
            return {'domain': {'product_id': [('type','=','service')]}}
        
    @api.onchange('group_id')
    def onchange_group_id(self):
        self.account_head_id, self.account_subhead_id, self.account_id = False, False, False
        return {'domain': {
            'account_head_id': [('parent_id', '=', self.group_id.id), ('budget_type', '=', self.budget_type)]}}

    @api.onchange('account_head_id')
    def onchange_account_head_id(self):
        self.account_subhead_id, self.account_id = False, False
        return {'domain': {'account_subhead_id': [('parent_id', '=', self.account_head_id.id),
                                                  ('budget_type', '=', self.budget_type)]}}

    @api.onchange('account_subhead_id')
    def onchange_account_subhead_id(self):
        self.account_id = False
        return {'domain': {'account_id': [('group_id', '=', self.account_subhead_id.id)]}}

    @api.onchange('budget_type')
    def onchange_budget_type(self):
        self.account_analytic_id = False
        if self.budget_type == 'project':
            return {'domain': {'account_analytic_id': [('budget_type', '=', 'project')]}}
        else:
            return {'domain': {'account_analytic_id': [('budget_type', '=', 'treasury'),
                                                       ('department_id', '=',
                                                        self._context.get('department_id', False))]}}

    @api.onchange('price_subtotal')
    def _onchange_price_unit(self):
        for rec in self:
            if rec.price_unit > 0:
                if rec.account_analytic_id:
                    analytic_rec = self.env['account.analytic.account'].sudo().browse(rec.account_analytic_id.id)
                    budget_lines = analytic_rec.crossovered_budget_line
                    for budget_line in budget_lines:
                        line_account_ids = budget_line.general_budget_id.account_ids.ids
                        for line_account_id in line_account_ids:
                            if self.env['account.account'].sudo().browse(line_account_id).code == rec.account_id.code:
                                if (budget_line.planned_amount - budget_line.practical_amount) < rec.price_subtotal:
                                    return {'warning': {
                                        'title': _('Validation Error'),
                                        'message': _('Transaction amount is more than Available amount.')
                                    }}

    @api.onchange('account_id', 'account_analytic_id')
    def _check_budget_head(self):
        account_ids_lst = []
        for rec in self:
            if rec.account_id and rec.account_analytic_id:
                analytic_rec = self.env['account.analytic.account'].sudo().browse(rec.account_analytic_id.id)
                budget_lines = analytic_rec.crossovered_budget_line
                for budget_line in budget_lines:
                    line_account_ids = budget_line.general_budget_id.account_ids.ids
                    for line_account_id in line_account_ids:
                        account_ids_lst.append(line_account_id)
                if rec.account_id.id not in account_ids_lst:
                    return {'warning': {
                        'title': _('Validation Error'),
                        'message': _(f'{rec.account_id.code} {rec.account_id.name} is not available in {rec.account_analytic_id.name}.')
                    }}

    @api.onchange('price_subtotal')
    def onchange_price_subtotal(self):
        for rec in self:
            if rec.invoice_id.company_currency_id.id != rec.invoice_id.currency_id.id:
                if rec.invoice_id.exchange_rate == 0:
                    return {'warning': {
                        'title': _('Warning'),
                        'message': _('Please set exchange rate.')
                    }}
                rec.lcy = rec.price_subtotal * rec.invoice_id.exchange_rate
                rec.invoice_id.amount_tax *= round(1 / rec.invoice_id.exchange_rate, 3)
            # if self._context.get('type') == 'out_invoice':
            # 	rec.price_unit *= round(1/rec.invoice_id.exchange_rate, 3)
