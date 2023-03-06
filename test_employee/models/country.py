from odoo import fields, models, api

class EmployeeCountry(models.Model):
    _name ="employee.country"
    _description="country"
    
    name = fields.Char("country name")
    code = fields.Char("Code")
