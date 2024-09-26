from odoo import api, fields, models


class KW_Employee_Social_Notify(models.Model):
    _name = 'kw_employee_social_sync'
    _description = 'Employee Candid Image Sync'

    name = fields.Char(string='Employee Name')
    status = fields.Char(string='Status')
    payload = fields.Char(string='payload')
