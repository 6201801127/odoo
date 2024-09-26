from odoo import api, fields, models


class KwProductCategoryMaster(models.Model):
    _name = "kw_product_category"
    _description = "kw_product_category"
    _rec_name = 'name'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    base_code = fields.Char(string="Base Code")
    active = fields.Boolean(string="Active")
