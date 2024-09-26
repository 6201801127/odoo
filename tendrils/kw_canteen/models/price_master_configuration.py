import string
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PriceMasterConfiguration(models.Model):
    _name = 'price_master_configuration'
    _description = 'Price Master Configuration'
    _rec_name = 'meal_type'

    meal_type = fields.Char(required=True, string="Meals")
    price = fields.Float(string="Price", required=True)
    meal_code=fields.Char(string="Code")

    @api.constrains('meal_type')
    def validate_weekdays(self):
        template_rec = self.env['price_master_configuration'].search([]) - self
        filtered_rec = template_rec.filtered(lambda r: r.meal_type == self.meal_type)
        if len(filtered_rec) > 0:
            raise ValidationError("The code\"" + self.meal_type + "\" already exists.")

    @api.constrains('price')
    def price_validation(self):
        if self.price <= 0:
            raise ValidationError("Price Should Be Greater Than Than 0.")

