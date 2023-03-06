from odoo import fields, models, api

class EmployeeCity(models.Model):
    _name ="employee.city"
    _rec_name ="city_name"
    _description = "employee city"

    city_name = fields.Char("City name")
    code = fields.Char("Code")


    state_id = fields.Many2one(comodel_name="employee.state", string="State")