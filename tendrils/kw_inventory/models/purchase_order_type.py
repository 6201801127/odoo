from odoo import api, fields, models


class PurchaseType(models.Model):
    _name = 'purchase_order_type'
    _description = 'purchase_order_type'
    _rec_name = 'po_type'

    po_type = fields.Char('Type Of PO', )
