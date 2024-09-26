from odoo import _, api, fields, models

class HRExpense(models.Model):
    _inherit = 'hr.expense'

    branch_id = fields.Many2one('res.branch', 'Branch')
#                                 default=lambda self: self.env['res.users']._get_default_branch())

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for employee in self:
#             print("///////////////////")
            employee.branch_id = employee.employee_id.branch_id.id

class HRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    branch_id = fields.Many2one('res.branch', 'Branch')
#                                 default=lambda self: self.env['res.users']._get_default_branch())
#   
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for employee in self:
#             print("///////////////////")
            employee.branch_id = employee.employee_id.branch_id.id
