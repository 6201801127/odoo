from odoo import models, fields, api

class MealType(models.Model):
    _name="kw_canteen_meal_type"
    _description = "Meal Type"

    code = fields.Char()
    name = fields.Char()
