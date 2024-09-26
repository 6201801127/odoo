from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.addons import decimal_precision as dp
from odoo.addons.kw_accounting.models.chart_of_accounts import state_list
from odoo.http import request

TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}
MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal','product_line_ids.amount','tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'date')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.invoice_amount = sum(line.amount for line in self.product_line_ids)
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            rate_date = self._get_currency_rate_date() or fields.Date.today()
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, rate_date)
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, rate_date)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        self.invoice_line_ids._onchange_unit_id()

    # branch_id = fields.Many2one('kw_res_branch', 'Branch')
    reference_number = fields.Char(string="Reference Number",default="NA",states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')],states={'draft': [('readonly', False)]})
    invoice_number = fields.Char('Invoice Number')
    kw_id = fields.Integer('KW ID')
    has_outstanding = fields.Boolean(compute='_get_outstanding_info_JSON')
    exchange_rate = fields.Float('Exchange Rate')
    is_foreign_currency = fields.Boolean('Is Foreign Currency', default=False)
    unit_id = fields.Many2one('accounting.branch.unit', 'Unit',states={'draft': [('readonly', False)]},required=True)
    csm_acc_conf = fields.Boolean('csm account conf', compute="compute_csm_config")
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
            ('regular_deductor','Regular & Deductor')], string="GST Treatment",compute="_compute_l10n_in_gst_treatment", store=True, readonly=False,states={'draft': [('readonly', False)]})
    comment = fields.Text('Narration', readonly=True,)
    date = fields.Date(string='Accounting Date',
        copy=False,  states={'draft': [('readonly', False)]},
        help="Keep empty to use the invoice date.",
        readonly=True, default=fields.Date.context_today)
    tds_applicable = fields.Selection([('payable','payable'),('receivable','Receivable')],string="TDS",states={'draft': [('readonly', False)]})
    product_line_ids = fields.One2many('account.product.line', 'invoice_id', string='Product Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    tds_line_ids = fields.One2many('account.tds.line', 'invoice_id', string='TDS Lines', store=True,
        readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    invoice_amount = fields.Monetary(string="Invoice Amount",compute="_compute_amount",store=True)
    state_gstin_id = fields.Many2one('state_gstin',string="State")
    state_bill_id = fields.Selection(state_list,string="State")
    sync_status = fields.Integer("Sync Status")
    invoice_kw_id = fields.Integer("KW Invoice ID")
    kw_voucher_no = fields.Char("Tendrils Voucher No.")
    particulars = fields.Char(string="Particulars",compute="_get_particulars")
    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_register_search_current_financial_year")
    purchase_order_id = fields.Many2one('purchase.order',string="Purchase No.", domain=[('state','=','purchase')]) 
    last_updated_user_id = fields.Many2one('res.users',string="Last Updated By",track_visibility='always')
    last_update_date = fields.Datetime(string="Last Updated Date",track_visibility='always',)
    posted_user_id = fields.Many2one('res.users',string="Posted By",track_visibility='always',)
    posted_date = fields.Datetime(string="Posted Date",track_visibility='always',)
    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Posted'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    
    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Credit Note'),
            'in_refund': _('Vendor Credit note'),
        }
        result = []
        for inv in self:
            result.append((inv.id, "%s %s (%s)" % (inv.number or TYPES[inv.type], inv.name or '',inv.reference_number or '')))
        return result

    @api.multi
    def print_voucher(self):
        return self.env.ref('kw_accounting.account_print_invoice').report_action(self)
    
    @api.multi
    def preview_invoice(self):
        self.ensure_one()
        request.session['invoice_id'] = self.id
        view_id = self.env.ref('kw_accounting.preview_voucher_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Voucher'),
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'target': 'new',
            'res_id': self.id,
            'views': [[view_id, 'form']],
        }

    @api.model
    def preview_invoices(self,**args):
        invoice_id = args.get('voucher_id',False)
        request.session['invoice_id'] = int(invoice_id)
        view_id = self.env.ref('kw_accounting.preview_voucher_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Voucher'),
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'target': 'new',
            'res_id': int(invoice_id),
            'views': [[view_id, 'form']],
        }

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.partner_id not in invoice.message_partner_ids:
                invoice.message_subscribe([invoice.partner_id.id])

            # Auto-compute reference, if not already existing and if configured on company
            if not invoice.reference and invoice.type == 'out_invoice':
                invoice.reference = invoice._get_computed_reference()

            # DO NOT FORWARD-PORT.
            # The reference is copied after the move creation because we need the move to get the invoice number but
            # we need the invoice number to get the reference.
            invoice.move_id.ref = invoice.reference
        self._check_duplicate_supplier_reference()
        if not self.posted_user_id:
            return self.write({'state': 'open','posted_user_id':self.env.user.id,'posted_date':datetime.today()})
        else:
            return self.write({'state': 'open'})

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass
        
    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """            
            Method Overwrite from account.invoice
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)
        values['product_line_ids'] = self._refund_cleanup_lines(invoice.product_line_ids)
        tax_lines = invoice.tax_line_ids
        taxes_to_change = {
            line.tax_id.id: line.tax_id.refund_account_id.id
            for line in tax_lines.filtered(lambda l: l.tax_id.refund_account_id != l.tax_id.account_id)
        }
        cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
        values['tax_line_ids'] = self._refund_tax_lines_account_change(cleaned_tax_lines, taxes_to_change)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(invoice)
        values['date_due'] = values['date_invoice']
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['refund_invoice_id'] = invoice.id
        values['reference'] = False

        if values['type'] == 'in_refund':
            values['payment_term_id'] = invoice.partner_id.property_supplier_payment_term_id.id
            partner_bank_result = self._get_partner_bank_id(values['company_id'])
            if partner_bank_result:
                values['partner_bank_id'] = partner_bank_result.id
        else:
            values['payment_term_id'] = invoice.partner_id.property_payment_term_id.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values    
    
    def _get_refund_common_fields(self):
        return ['partner_id', 'payment_term_id', 'account_id', 'currency_id', 'journal_id','unit_id','state_gstin_id']
    
    
    @api.model
    def _refund_cleanup_lines(self, lines):
        """            
            Method Overwrite from account.invoice
        """
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                if name in MAGIC_COLUMNS:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name == 'analytic_tag_ids':
                    values[name] = [(6, 0, line[name].ids)]
                    
            result.append((0, 0, values))
        
        for i, line in enumerate(lines):
            if line._name == 'account.invoice.line':
                if line.mode == 'credit':
                    result[i][2]['mode'] = 'debit'
                elif line.mode == 'debit':
                    result[i][2]['mode'] = 'credit'
        return result
    
    # @api.multi
    # def _get_aml_for_register_payment(self):
    #     """ Get the aml to consider to reconcile in register payment """
    #     self.ensure_one()
    #     x = self.move_id.line_ids.filtered(lambda r: not r.reconciled)
    #     return self.move_id.line_ids.filtered(lambda r: not r.reconciled)
      
    @api.multi
    def _register_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        domain = [('date', '>=', start_date),('date', '<=', end_date)]
        return domain

    @api.constrains('date','date_invoice')
    def validate_invoice_date(self):
        for inv in self:
            string = "Bill" if self.type in ['in_invoice','in_refund'] else "Invoice" 
            if inv.date_invoice and inv.date_invoice > inv.date:
                raise ValidationError(f'{string} date should not be greater than Accounting Date.')

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
        elif self.date_due and (date_invoice > self.date_due):
            self.date_due = date_invoice

    @api.onchange('invoice_line_ids.account_id')
    @api.multi
    def _get_particulars(self):
        for rec in self:
            account_ids = rec.invoice_line_ids.mapped('account_id')
            account_name = account_ids.mapped('name') + [rec.account_id.name or '']
            rec.particulars = (', '.join(account_name)) if len(account_name) > 0 else ''

    @api.model
    def create(self, vals):
        inv = super(AccountInvoiceInherit, self).create(vals)
        fy_obj = self.env['account.fiscalyear']
        period_obj = self.env['account.period']
        if inv.date and inv.company_id:
            fy = fy_obj.finds(dt=inv.date, company_id=inv.company_id.id)
            fy_date_stop = fy.date_stop.strftime('%d-%b-%Y')
            period = period_obj.find(dt=inv.date, company_id=inv.company_id.id)
            pr_date_stop = period.date_stop.strftime('%d-%b-%Y')
            if period.lock_in:
                raise ValidationError(_('Period has been Locked, You can\'t add new entry.'))
            if inv.date != period.date_stop and not period.lock_in and period.lock_in_flag == 1:
                raise ValidationError(_(f'You can create entry only on the date {pr_date_stop}.'))
            if fy.lock_in:
                raise ValidationError(_('Fiscal Year has been Locked, You can\'t add new entry.'))
            if inv.date != fy.date_stop and not fy.lock_in and fy.lock_in_flag == 1:
                raise ValidationError(_(f'You can create entry only on the date {fy_date_stop}.'))
        return inv

    @api.multi
    def write(self, vals):
        if self.posted_user_id and ('invoice_line_ids' in vals or 'product_line_ids' in vals or 'tax_line_ids' in vals) :
            vals['last_updated_user_id'] = self.env.user.id,
            vals['last_update_date'] = datetime.today()

        res = super(AccountInvoiceInherit, self).write(vals)        
        return res
    #     period_obj = self.env['account.period']
    #     inv = super(AccountInvoiceInherit, self).write(vals)
    #     if 'date' in vals and vals['date']:
    #         for inv in self:
    #             fy = fy_obj.finds(dt=inv.date, company_id=inv.company_id.id)
    #             fy_date_stop = fy.date_stop.strftime('%d-%b-%Y')
    #             period = period_obj.find(dt=inv.date, company_id=inv.company_id.id)
    #             pr_date_stop = period.date_stop.strftime('%d-%b-%Y')
    #             if period.lock_in:
    #                 raise ValidationError(_('Period has been Locked, You can\'t add new entry.'))
    #             if inv.date != period.date_stop and not period.lock_in and period.lock_in_flag == 1:
    #                 raise ValidationError(_(f'You can create entry only on the date {pr_date_stop}.'))
    #             if fy.lock_in:
    #                 raise ValidationError(_('Fiscal Year has been Locked, You can\'t add new entry.'))
    #             if inv.date != fy.date_stop and not fy.lock_in and fy.lock_in_flag == 1:
    #                 raise ValidationError(_(f'You can create entry only on the date {fy_date_stop}.'))
    #     return inv

      
    @api.constrains('invoice_line_ids','tds_line_ids')
    def tds_value_match(self):
        for rec in self:
            tds_invoice_line_amount = sum(line.transaction_amount for line in rec.invoice_line_ids if line.account_id.tds == True)
            tds_line_amount = sum(line.ds_amount for line in rec.tds_line_ids)
            if tds_invoice_line_amount != tds_line_amount and rec.tds_applicable != False:
                raise ValidationError("TDS Amount is mismatched")

    @api.multi
    def action_invoice_draft(self):
        # if self.filtered(lambda inv: inv.state != 'cancel'):
        #     raise UserError(_("Invoice must be cancelled in order to reset it to draft."))
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        self.move_id.write({'state':'draft'})
        if self.move_name != False:
            self.move_id.line_ids.unlink()
        # Delete former printed invoice
        return True
        
    @api.depends('partner_id')
    def _compute_l10n_in_gst_treatment(self):
        for record in self:
            record.l10n_in_gst_treatment = record.partner_id.l10n_in_gst_treatment

    @api.depends('invoice_line_ids')
    def compute_line_budget(self):
        for rec in self:
            for r in rec.invoice_line_ids:
                if r.budget_type == 'treasury':
                    rec.is_budget_treasury = True

    @api.depends('name')
    def compute_csm_config(self):
        for rec in self:
            enable_csm_account_conf_status = self.env['ir.config_parameter'].sudo().get_param(
                'kw_accounting.enable_csm_account_conf_status')
            rec.csm_acc_conf = enable_csm_account_conf_status

    @api.onchange('currency_id')
    def check_currency(self):
        for rec in self:
            rec.is_foreign_currency, rec.exchange_rate = False, False
            if rec.company_currency_id.id != rec.currency_id.id:
                rec.is_foreign_currency = True

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        currency_rate_obj = self.env['res.currency.rate'].sudo()
        for invoice in self:
            if (invoice.currency_id.id != invoice.company_currency_id.id) and invoice.exchange_rate > 0:
                currency_obj = currency_rate_obj.search(
                    [('name', '=', date.today()), ('currency_id', '=', invoice.currency_id.id)])
                delete_query = f'delete from res_currency_rate where currency_id = {invoice.currency_id.id}'
                self.env.cr.execute(delete_query)
                currency_rate_obj.create({
                    'name': date.today(), 'rate': 1 / invoice.exchange_rate, 'currency_id': invoice.currency_id.id})
                
    @api.onchange('cash_rounding_id', 'invoice_line_ids', 'tax_line_ids', 'amount_total')
    def _onchange_cash_rounding(self):
        # Drop previous cash rounding lines
        lines_to_remove = self.invoice_line_ids.filtered(lambda l: l.is_rounding_line)
        if lines_to_remove:
            self.invoice_line_ids -= lines_to_remove

        # Clear previous rounded amounts
        for tax_line in self.tax_line_ids:
            if tax_line.amount_rounding != 0.0:
                tax_line.amount_rounding = 0.0

        if self.cash_rounding_id:
            rounding_amount = self.cash_rounding_id.compute_difference(self.currency_id, self.amount_total)
            if not self.currency_id.is_zero(rounding_amount):
                if self.cash_rounding_id.strategy == 'biggest_tax':
                    # Search for the biggest tax line and add the rounding amount to it.
                    # If no tax found, an error will be raised by the _check_cash_rounding method.
                    if not self.tax_line_ids:
                        return
                    biggest_tax_line = None
                    for tax_line in self.tax_line_ids:
                        if not biggest_tax_line or tax_line.amount > biggest_tax_line.amount:
                            biggest_tax_line = tax_line
                    biggest_tax_line.amount_rounding += rounding_amount
                elif self.cash_rounding_id.strategy == 'add_invoice_line':
                    if rounding_amount > 0.0:
                        account_id = self.cash_rounding_id._get_loss_account_id().id
                    else:
                        account_id = self.cash_rounding_id._get_profit_account_id().id
                    # Create a new invoice line to perform the rounding
                    rounding_line = self.env['account.invoice.line'].new({
                        'name': self.cash_rounding_id.name,
                        'invoice_id': self.id,
                        'account_id': self.cash_rounding_id.account_id.id,
                        'transaction_amount': rounding_amount,
                        'quantity': 1,
                        'is_rounding_line': True,
                        'sequence': 9999  # always last line
                    })

                    # To be able to call this onchange manually from the tests,
                    # ensure the inverse field is updated on account.invoice.
                    if not rounding_line in self.invoice_line_ids:
                        self.invoice_line_ids += rounding_line
    @api.model
    def invoice_line_move_line_get(self):
        res = []
        for line in self.invoice_line_ids:
            if not line.account_id:
                continue
            if line.quantity==0:
                continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.price_subtotal,
                'account_id': line.account_id.id,
                'budget_type': line.budget_type,
                'budget_update': line.budget_update,
                'employee_id': line.employee_id.id,
                'department_id': line.department_id.id,
                'division_id': line.division_id.id,
                'section_id': line.section_id.id,
                'project_id': line.project_id.id,
                'product_id': line.product_id.id,
                'project_wo_id': line.project_wo_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'analytic_tag_ids': analytic_tag_ids,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
                'budget_line': line.budget_line.id,
                'capital_line': line.capital_line.id,
                'project_line': line.project_line.id,
            }
            res.append(move_line_dict)
        return res
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            # if inv.move_id:
            #     continue


            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id
            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
                'branch_id': inv.unit_id.id,
            }

            if inv.move_name !=  False:
                inv.move_id.write(move_vals)
                inv.move_id.write({'state':'posted','posted_user_id':self.env.user.id,'posted_date':datetime.today()})
            else:
                move = account_move.create(move_vals)
                # Pass invoice in method post: used if you want to get the same
                # account move reference when creating the same invoice after a cancelled one:
                move.post(invoice = inv)
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': move.name,
                }
                inv.write(vals)
        return True
    
    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        message = 'dedit' if self.type == 'in_invoice' else 'credit'
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should a %s note instead.") % message)
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    def get_session_details(self):
        company_id = request.session.get('accounting_company_id', False)
        branch_id = request.session.get('accounting_branch_id', False)
        financial_year = request.session.get('accounting_financial_year',False)
        fy_id = self.env['account.fiscalyear'].browse(financial_year) if financial_year else None
        return company_id,branch_id,fy_id

    def sale_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Sales Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','not in',['draft']),('type','=','out_invoice'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'type':'out_invoice', 'journal_type': 'sale','default_company_id': int(company_id),'default_unit_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def credit_note_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Credit Note Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','not in',['draft']),('type','=','out_refund'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'out_refund', 'type': 'out_refund', 'journal_type': 'sale','default_company_id': int(company_id),'default_unit_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def purchase_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_supplier_tree').id
        form_view_id = self.env.ref('account.invoice_supplier_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Purchase Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','not in',['draft']),('type','=','in_invoice'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'in_invoice', 'type': 'in_invoice', 'journal_type': 'purchase','default_company_id': int(company_id),'default_unit_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def debit_note_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_supplier_tree').id
        form_view_id = self.env.ref('account.invoice_supplier_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Debit Note Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','not in',['draft']),('type','=','in_refund'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'in_refund', 'type': 'in_refund', 'journal_type': 'purchase','default_company_id': int(company_id),'default_unit_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def draft_sale_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Sales Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','=','draft'),('type','=','out_invoice'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'type':'out_invoice', 'journal_type': 'sale','default_company_id': int(company_id),'unit_id':int(branch_id),'default_unit_id':int(branch_id)},
                }
        return action
    
    def draft_credit_note_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Credit Note Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','=','draft'),('type','=','out_refund'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'out_refund', 'type': 'out_refund', 'journal_type': 'sale','default_company_id': int(company_id),'unit_id':int(branch_id),'default_unit_id':int(branch_id)},
                }
        return action

    def draft_purchase_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_supplier_tree').id
        form_view_id = self.env.ref('account.invoice_supplier_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Purchase Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','=','draft'),('type','=','in_invoice'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'in_invoice', 'type': 'in_invoice', 'journal_type': 'purchase','default_company_id': int(company_id),'unit_id':int(branch_id),'default_unit_id':int(branch_id)},
                }
        return action

    def draft_debit_note_voucher_action(self):
        company_id,branch_id,fy_id = self.get_session_details()
        tree_view_id = self.env.ref('account.invoice_supplier_tree').id
        form_view_id = self.env.ref('account.invoice_supplier_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Debit Note Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.invoice',
                'domain': [('state','=','draft'),('type','=','in_refund'),('company_id','=',int(company_id)),('unit_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'default_type': 'in_refund', 'type': 'in_refund', 'journal_type': 'purchase','default_company_id': int(company_id),'unit_id':int(branch_id),'default_unit_id':int(branch_id)},
                }
        return action

class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date','transaction_amount','mode')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        
        if (self.mode == 'debit' and self.invoice_id.type in ['in_invoice','out_refund']) or (self.mode == 'credit' and self.invoice_id.type in ['out_invoice','in_refund']):
            self.price_subtotal = (self.transaction_amount * 1)
        elif (self.mode == 'credit' and self.invoice_id.type in ['in_invoice','out_refund']) or (self.mode == 'debit' and self.invoice_id.type in ['out_invoice','in_refund']):
            self.price_subtotal = (self.transaction_amount * -1)

        self.price_total = self.price_subtotal
        # if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
        #     currency = self.invoice_id.currency_id
        #     date = self.invoice_id._get_currency_rate_date()
        #     price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        # sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        # self.price_subtotal_signed = price_subtotal_signed
    # @api.model
    # def get_account_ids(self):
    #     company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
    #     account_ids = self.env['account.account'].sudo().search([('branch_id', '=', int(branch_id)),('company_id', '=', int(company_id)),('deprecated', '=', False)])
    #     return [('id', 'in', account_ids.ids)]
    
    name = fields.Text(string='Description', required=False)
    hsn_code = fields.Char('HSN/SAC Code')
    group_id = fields.Many2one('account.group', 'Group', domain="[('account_type_id.code','=', 'gn')]")
    account_head_id = fields.Many2one('account.group', 'Account Head', domain="[('account_type_id.code','=', 'ah')]")
    account_subhead_id = fields.Many2one('account.group', 'Account Sub-Head',
                                         domain="[('account_type_id.code','=', 'ash')]")
    price_unit = fields.Float(string='Unit Price', required=False, digits=dp.get_precision('Product Price'))
    lcy = fields.Float('Amount in LCY')
    product_category = fields.Selection([('product','Goods'),('service','Service')],string="Category")
    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")
    budget_type = fields.Selection([('treasury','Treasury'),('project','Project'),('capital','Capital'),('other','Other')],string="Budget Type",default="other")
    mode = fields.Selection([('debit','Dr'),('credit','Cr')])
    transaction_amount = fields.Monetary(string="Amount",store=True,readonly=False)
    tds_applicable = fields.Boolean(string="TDS",related="account_id.tds")
    department_id = fields.Many2one('hr.department', 'Department',domain=[('dept_type.code', '=', 'department')])
    division_id = fields.Many2one('hr.department', 'Division',domain=[('dept_type.code', '=', 'division')])
    section_id = fields.Many2one('hr.department', 'Section',domain=[('dept_type.code', '=', 'section')])
    employee_id = fields.Many2one('hr.employee', 'Employee',domain=['|', ('active', '=', False), ('active', '=', True)])
    project_id = fields.Many2one('kw_sales_workorder_master',string="Project")
    invoice_line_kw_id = fields.Integer(string="Kw ID")
    update_capital_budget = fields.Boolean(related="account_id.user_type_id.budget_update")
    budget_update = fields.Boolean(string="Capital Budget Update")
    unit_id = fields.Many2one('accounting.branch.unit', related='invoice_id.unit_id', string='Branch', readonly=True)

    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        return {'domain':{'account_id':[('branch_id','=',self.invoice_id.unit_id.id)]}}
        
    
        
            
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
        
    

    # @api.onchange('account_head_id')
    # def onchange_account_head_id(self):
    #     self.account_subhead_id, self.account_id = False, False
    #     return {'domain': {'account_subhead_id': [('parent_id', '=', self.account_head_id.id),
    #                                               ('budget_type', '=', self.budget_type)]}}

    # @api.onchange('account_subhead_id')
    # def onchange_account_subhead_id(self):
    #     self.account_id = False
    #     return {'domain': {'account_id': [('group_id', '=', self.account_subhead_id.id)]}}


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

    @api.multi
    def write(self, vals):
        result = super(AccountInvoiceLineInherit, self).write(vals)
        if set(vals) & set(self._get_tracked_fields(list(vals))):
            self._track_changes(vals)
        return result
    
    @api.model
    def _get_tracked_fields(self, updated_fields):
        """ Return a structure of tracked fields for the current model.
            :param list updated_fields: modified field names
            :return dict: a dict mapping field name to description, containing on_change fields
        """
        tracked_fields = []
        for name, field in self._fields.items():
            # if getattr(field, 'track_visibility', False):
            tracked_fields.append(name)

        if tracked_fields:
            return self.fields_get(tracked_fields)
        return {}

    def _track_changes(self,vals):
        # self.write({
        #     'last_updated_user_id' : self.env.user.id,
        #     'last_update_date' : datetime.today()
        # })
        if 'budget_type' in vals:
            msg = _('Budget Type: ') + vals['budget_type']
            self.invoice_id.message_post(body=msg)
        if 'account_id' in vals and vals['account_id'] != False:
            account_id = self.env['account.account'].browse(int(vals['account_id']))
            msg = _('Account: ') + account_id.code + " " + account_id.name
            self.invoice_id.message_post(body=msg)
        if 'department_id' in vals and vals['department_id'] != False:
            department_id = self.env['hr.department'].browse(int(vals['department_id']))
            msg = _('Department: ') + department_id.name
            self.invoice_id.message_post(body=msg)
        if 'division_id' in vals and vals['division_id'] != False:
            division_id = self.env['hr.department'].browse(int(vals['division_id']))
            msg = _('Division: ') + division_id.name
            self.invoice_id.message_post(body=msg)
        if 'section_id' in vals and vals['section_id'] != False:
            section_id = self.env['hr.department'].browse(int(vals['section_id']))
            msg = _('Section: ') + section_id.name
            self.invoice_id.message_post(body=msg)
        if 'employee_id' in vals and vals['employee_id'] != False:
            employee_id = self.env['hr.employee'].browse(int(vals['employee_id']))
            msg = _('Employee: ') + employee_id.name + " (" + employee_id.emp_code + ")"
            self.invoice_id.message_post(body=msg)
        if 'debit' in vals and vals['debit'] != False:
            msg = _('Debit: ') + str(self.debit)
            self.invoice_id.message_post(body=msg)
        if 'credit' in vals and vals['credit'] != False:
            msg = _('Credit: ') + str(self.credit)
            self.invoice_id.message_post(body=msg)
        if 'project_wo_id' in vals and vals['project_wo_id'] != False:
            project_id = self.env['kw_project_budget_master_data'].browse(int(vals['project_wo_id']))
            msg = _('Project: ') + project_id.workorder_name
            self.invoice_id.message_post(body=msg)  \

class AccountProductLine(models.Model):
    _name = 'account.product.line'
    _description = 'Account Product Line'
    _order = "invoice_id,sequence,id"

    @api.one
    @api.depends('price_unit','cgst_per','cgst_amount','sgst_per','sgst_amount','igst_per','igst_amount', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date','rate')
    def _compute_price(self):
        self.amount = (self.price_unit + self.cgst_amount + self.sgst_amount + self.igst_amount)
        
        # if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
        #     currency = self.invoice_id.currency_id
        #     date = self.invoice_id._get_currency_rate_date()
        #     price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        # sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        # self.price_subtotal_signed = price_subtotal_signed

    name = fields.Text(string='Description',)
    origin = fields.Char(string='Source Document',help="Reference of the document that produced this invoice.")
    sequence = fields.Integer(default=10,help="Gives the sequence of this line when displaying the invoice.")
    company_id = fields.Many2one('res.company', string='Company',related='invoice_id.company_id', store=True, readonly=True, related_sudo=False)
    partner_id = fields.Many2one('res.partner', string='Partner',related='invoice_id.partner_id', store=True, readonly=True, related_sudo=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference',ondelete='cascade', index=True)
    invoice_type = fields.Selection(related='invoice_id.type', readonly=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True, related_sudo=False, readonly=False)
    company_currency_id = fields.Many2one('res.currency', related='invoice_id.company_currency_id', readonly=True, related_sudo=False)
    is_rounding_line = fields.Boolean(string='Rounding Line', help='Is a rounding line in case of cash rounding.')

    product_category = fields.Selection([('product','Goods'),('service','Service')],string="Category")
    product_id = fields.Many2one('product.product', string='Product',ondelete='restrict', index=True)
    product_image = fields.Binary('Product Image', related="product_id.image", store=False, readonly=True)
    hsn_code = fields.Char('HSN/SAC Code')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),required=True, default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',ondelete='set null', index=True, oldname='uos_id')
    price_unit = fields.Float(string='Base Amount', digits=dp.get_precision('Product Price'))
    rate = fields.Float(string='Rate', required=True, digits=dp.get_precision('Product Price'))
    cgst_per = fields.Selection([('0','0'),('2.5','2.5'),('5.0','5.0'),('6.0','6.0'),('9.0','9.0'),('12.0','12.0'),('14.0','14.0'),('18.0','18.0'),('28.0','28.0')],default="0",string="CGST %")
    cgst_amount = fields.Monetary(string="CGST Amount")
    sgst_per = fields.Selection([('0','0'),('2.5','2.5'),('5.0','5.0'),('6.0','6.0'),('9.0','9.0'),('12.0','12.0'),('14.0','14.0'),('18.0','18.0'),('28.0','28.0')],default="0",string="SGST %")
    sgst_amount = fields.Monetary(string="SGST Amount")
    igst_per = fields.Selection([('0','0'),('2.5','2.5'),('5.0','5.0'),('6.0','6.0'),('9.0','9.0'),('12.0','12.0'),('14.0','14.0'),('18.0','18.0'),('28.0','28.0')],default="0",string="IGST %")    
    igst_amount = fields.Monetary(string="IGST Amount")
    rcm_applicable = fields.Boolean(string="RCM Applicable")
    itc_applicable = fields.Boolean(string="ITC Applicable")
    amount = fields.Monetary(string="Amount",compute="_compute_price" ,store=True)
    product_line_kw_id = fields.Integer(string="Kw ID")

    @api.onchange('product_category')
    def get_itc_applicable(self):
        for rec in self:
            if rec.partner_id.supplier == True:
                rec.itc_applicable = True
            else:
                rec.itc_applicable = False
                
    @api.onchange('product_id')
    def onchange_product(self):
        self.hsn_code = self.product_id.l10n_in_hsn_code
        self.rate = self.product_id.standard_price

    @api.onchange('rate','cgst_per','sgst_per','igst_per','quantity')
    def get_tax_value_onchange(self):
        self.price_unit = self.rate * self.quantity
        self.cgst_amount = (self.price_unit * float(self.cgst_per))/100 if self.cgst_per else 0.0
        self.sgst_amount = (self.price_unit * float(self.sgst_per))/100 if self.sgst_per else 0.0
        self.igst_amount = (self.price_unit * float(self.igst_per))/100 if self.igst_per else 0.0


    @api.onchange('product_category')
    def _onchange_product_category(self):
        self.product_id = False
        self.name = False
        if self.product_category == 'product':
            return {'domain': {'product_id': [('type', 'in', ['consu','product'])]}}
        elif self.product_category == 'service':
            return {'domain': {'product_id': [('type','=','service')]}}
    
    def _get_invoice_line_name_from_product(self):
        """ Returns the automatic name to give to the invoice line depending on
        the product it is linked to.
        """
        self.ensure_one()
        if not self.product_id:
            return ''
        invoice_type = self.invoice_id.type
        rslt = self.product_id.partner_ref
        if invoice_type in ('in_invoice', 'in_refund'):
            if self.product_id.description_purchase:
                rslt += '\n' + self.product_id.description_purchase
        else:
            if self.product_id.description_sale:
                rslt += '\n' + self.product_id.description_sale

        return rslt
    

class AccountProductLine(models.Model):
    _name = 'account.tds.line'
    _description = 'Account TDS Line'
    _order = "invoice_id,sequence,id"

    origin = fields.Char(string='Source Document',help="Reference of the document that produced this invoice.")
    sequence = fields.Integer(default=10,help="Gives the sequence of this line when displaying the invoice.")
    company_id = fields.Many2one('res.company', string='Company',related='invoice_id.company_id', store=True, readonly=True, related_sudo=False)
    partner_id = fields.Many2one('res.partner', string='Partner', store=True, readonly=False, related_sudo=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference',ondelete='cascade', index=True)
    invoice_type = fields.Selection(related='invoice_id.type', readonly=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True, related_sudo=False, readonly=False)
    company_currency_id = fields.Many2one('res.currency', related='invoice_id.company_currency_id', readonly=True, related_sudo=False)
    move_id = fields.Many2one('account.move',string="Voucher", ondelete='cascade', index=True)
    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False),('tds','=',True)],help="The income or expense account related to the selected product.")
    base_amount = fields.Monetary(string="Base Amount")
    percentage = fields.Float(string="Percentage")
    ds_amount = fields.Monetary(string="TDS Amount")

    @api.onchange('base_amount','percentage')
    def get_ds_amount_value(self):
        if self.base_amount or self.percentage:
            self.ds_amount = (self.base_amount * self.percentage) / 100
