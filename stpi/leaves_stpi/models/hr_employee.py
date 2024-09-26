from odoo import models, fields, api,_

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    
    leave_balance_id = fields.One2many('hr.employee.leave.info','hr_employee_id','Leave Info')
    mid_year_factor = fields.Boolean(string="Mid Year Factor")
    work_shifts = fields.Many2one('resource.calendar',string="Working Shifts")
    
    
class HREmployeeLeaveInfo(models.Model):
    
    _name = 'hr.employee.leave.info'
    _description = 'HR Employee Leave Info'
    
    hr_employee_id = fields.Many2one('hr.employee',string="Employee")
    holiday_status_id = fields.Many2one('hr.leave.type')
    date = fields.Date(string="Date")
    leave_info = fields.Selection([('debit','Debit'),
                                   ('credit','Credit')
                                ],string="Leave Info")
    no_of_days = fields.Float(string="No Of Days")
