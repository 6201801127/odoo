from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class kw_negotiation_log(models.Model):
    _name = 'kw_negotiation_log'
    _description = "Negotiation Log model"

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    reject_dt = fields.Date(string='Date', required=True, default=date.today(), )
    partner_id = fields.Many2one('res.partner', string='Vendor')
    product_qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    price_unit = fields.Float(string='Unit Price', required=True,digits=dp.get_precision('Product Price'))
    reject_remark = fields.Text(string='Remark')
    consolidation_id = fields.Many2one('kw_quotation_consolidation', string='Consolidation id')
