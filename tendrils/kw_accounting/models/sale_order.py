from odoo import models, fields, api, _
from datetime import date


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')
    unit_id = fields.Many2one('accounting.branch.unit', 'Unit')
    attach_wo_eq = fields.Binary('Attach WO/EQ', attachment=True)
    exchange_rate = fields.Float('Exchange Rate')
    currency_id = fields.Many2one('res.currency', 'Currency')
    company_currency_id = fields.Many2one('res.currency', 'Company Currency',
                                          default=lambda self: self.env.user.company_id.currency_id)
    is_foreign_currency = fields.Boolean('Is Foreign Currency', default=False)
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    billed_amount = fields.Monetary('Billed amount', compute='_get_billed_amount')
    to_be_billed = fields.Monetary('To be billed amount', compute='calc_to_billed_amount')

    @api.onchange('partner_id')
    def onchange_customer(self):
        self.analytic_account_id = False
        return {'domain': {
            'analytic_account_id': [('partner_id', '=', self.partner_id.id), ('budget_type', '=', 'project')]}}

    @api.multi
    def _get_billed_amount(self):
        invoiceObj = self.env['account.invoice'].sudo()
        for rec in self:
            invoice_total = 0
            for r in rec.invoice_ids.ids:
                invoice_total += invoiceObj.browse(r).amount_total
            rec.billed_amount = invoice_total

    @api.multi
    def calc_to_billed_amount(self):
        for rec in self:
            rec.to_be_billed = rec.amount_total - rec.billed_amount

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        currency_rate_obj = self.env['res.currency.rate'].sudo()
        for invoice in self:
            if (invoice.currency_id.id != invoice.company_currency_id.id) and invoice.exchange_rate > 0:
                currency_obj = currency_rate_obj.search([('name', '=', date.today()), ('currency_id', '=', invoice.currency_id.id)])
                delete_query = f'delete from res_currency_rate where currency_id = {invoice.currency_id.id}'
                self.env.cr.execute(delete_query)
                currency_rate_obj.create({'name': date.today(), 'rate': 1 / invoice.exchange_rate, 'currency_id': invoice.currency_id.id})

    @api.onchange('currency_id')
    def check_currency(self):
        for rec in self:
            rec.is_foreign_currency, rec.exchange_rate = False, False
            if rec.company_currency_id.id != rec.currency_id.id:
                rec.is_foreign_currency = True

    @api.multi
    def createInvoice(self):
        invoiceObj = self.env['account.invoice'].sudo()
        journalObj = self.env['account.journal'].sudo()

        for rec in self:
            vals = {
                'partner_id': rec.partner_id.id,
                'branch_id': rec.branch_id.id,
                'unit_id': rec.unit_id.id,
                'department_id': rec.department_id.id,
                'user_id': rec.user_id.id,
                'payment_term_id': rec.payment_term_id.id,
                'team_id': rec.team_id.id,
                'origin': rec.name,
                'currency_id': rec.currency_id.id,
                'exchange_rate': rec.exchange_rate if rec.currency_id.id != self.env.user.company_id.currency_id.id else False,
                'is_foreign_currency': True if rec.currency_id.id != self.env.user.company_id.currency_id.id else False,
                'invoice_line_ids': [[0, 0, {
                    'product_id': r.product_id.id,
                    'hsn_code': r.product_id.l10n_in_hsn_code,
                    'name': r.name,
                    'account_id': journalObj.browse(1).default_credit_account_id.id,  # Static Value
                    'quantity': r.product_uom_qty,
                    'price_unit': r.price_unit,
                    'lcy': r.lcy,
                    'invoice_line_tax_ids': [(6, 0, r.tax_id.ids)]
                }] for r in rec.order_line]
            }
            invoiceObj.create(vals)

        return True


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    lcy = fields.Float('Amount in LCY')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.order_id.company_currency_id.id != rec.order_id.currency_id.id:
                if rec.order_id.exchange_rate == 0:
                    return {'warning': {
                        'title': _('Warning'),
                        'message': _('Please set exchange rate.')
                    }}

    @api.onchange('price_subtotal')
    def _onchange_subtotal(self):
        for rec in self:
            if (rec.order_id.company_currency_id.id != rec.order_id.currency_id.id) and rec.order_id.exchange_rate != 0:
                rec.lcy = rec.price_subtotal * rec.order_id.exchange_rate
                rec.order_id.amount_tax *= round(1 / rec.order_id.exchange_rate, 3) if rec.tax_id else False