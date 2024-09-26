from odoo import models, fields

class EmployeeCategory(models.Model):
    _name = 'employee.category'
    _description = 'Employee category'
    # _rec_name = 'name'

    name = fields.Char('Category / वर्ग')

# class ResCity(models.Model):
#     _inherit = 'res.city'
#     _description = 'Res City'
    # _rec_name = 'name'

    # name = fields.Char('Category / वर्ग')