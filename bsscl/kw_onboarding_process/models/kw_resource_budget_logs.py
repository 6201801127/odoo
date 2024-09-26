from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployeeResourceBudgetMappingLog(models.Model):
    _name = 'hr.employee.budget.mapping.log'
    _description = 'Hr Employee Resource Budget Mapping Log'

    employee_id = fields.Many2one('hr.employee',string="Employee Name")
    emp_role = fields.Many2one('kwmaster_role_name',string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name',string="Employee Category")
    budget_effective_from = fields.Date(string='Effective From')
    effective_to = fields.Date(string='Effective To')
