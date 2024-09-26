import string
from odoo import models, fields, api

class BeverageType(models.Model):
    _name="kw_canteen_beverage_type"
    _description = "Beverage Type"
    _rec_name = "beverage_type"

    beverage_type = fields.Char(string="Beverages")
    beverage_code = fields.Char(string="Code")
    beverage_price = fields.Float(string="Price")
    device_ids = fields.Many2many('kw_device_master','canteen_device_rel',string="Device ID" , domain="[('type', '=','baverage')]")