from odoo import api, models, fields


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"
