from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    acceptance_triggers = fields.One2many(comodel_name="acceptance.trigger.product_line", inverse_name="product",
                                          string="Acceptance Triggers")
