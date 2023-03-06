from odoo import fields, models, api

class EmployeeState(models.Model):
    _name ="employee.state"
    _description ="state info"
   

    name = fields.Char("Staete name")
    code = fields.Char("Code")
    country_id = fields.Many2one(comodel_name="employee.country",string="Country")

  