from odoo import models, fields, api

class EmployeeReligion(models.Model):
    _name = 'employee.religion'
    _description = 'Employee Religion'
    # _rec_name ='name'

    name = fields.Char('Religion')