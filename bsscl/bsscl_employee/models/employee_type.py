from odoo import models, fields

class EmployeeType(models.Model):
    _name = 'employee.type'
    _description = 'Employee type'
    # _rec_name = 'name'

    name = fields.Char('Employee Type / रोजगार के प्रकार')