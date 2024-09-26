from odoo import models, fields, api,_

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = "Salary Rule"

    pf_eve_type = fields.Selection(
        [('employee', 'employee'), ('voluntary', 'To voluntary'), ('employer', 'employer')
         ],string="PF Withdrawal Type")