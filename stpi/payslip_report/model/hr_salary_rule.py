from odoo import api, fields, models

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    appear_in_allowance = fields.Boolean(string="Appear in Allowance")