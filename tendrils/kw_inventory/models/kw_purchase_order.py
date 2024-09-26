# from datetime import datetime
# from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
# from odoo.osv import expression
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from odoo.tools.float_utils import float_compare
# from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo.tools.misc import formatLang
# from odoo.addons import decimal_precision as dp


class kw_purchase_order(models.Model):
    _name = "kw_purchase_order"
    _description = "A master model to create Purchase Order"
    _rec_name = "po_no"

    po_no = fields.Char('Quotation Reference', required=True, default="New", readonly="1")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    partner_ref = fields.Char('Vendor Reference')
    quotation_no = fields.Many2many('kw_consolidation', string="Indent")
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now, )
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    order_line = fields.One2many('kw_quotation_items', 'order_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Purchase Order'),
        ('sent', 'PO Sent'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    user_id = fields.Many2one('res.users', string='Quotation Representative', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    dest_address_id = fields.Many2one('res.partner', string='Drop Ship Address')
