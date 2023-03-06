from odoo import fields, models, api

class EmployeeLanguage(models.Model):

    _name = 'employee.language'
    _rec_name = 'name'
    _description = 'employee language'


    name = fields.Char("Employee Language")


