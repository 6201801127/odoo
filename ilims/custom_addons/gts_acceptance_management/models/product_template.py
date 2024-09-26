from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    acceptance_triggers = fields.One2many(comodel_name="acceptance.trigger.product_template_line",
                                          inverse_name="product_template", string="Acceptance triggers")
