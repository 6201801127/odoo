from odoo import models, fields


class MiscAllowanceDeduct(models.Model):
    _name = 'misc.allowance.deduct'
    _description = 'Misc. Allowance/Deduction'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    centre_id = fields.Many2one('res.branch', 'Centre', related='employee_id.branch_id')
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule')
    active = fields.Boolean('Active', default=True)
    date = fields.Date('Date')
    amount = fields.Float('Amount')