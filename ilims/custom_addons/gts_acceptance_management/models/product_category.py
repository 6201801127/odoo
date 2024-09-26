from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    acceptance_triggers = fields.One2many(comodel_name="acceptance.trigger.product_category_line",
                                          inverse_name="product_category", string="Acceptance Triggers")
