from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta


class PhysicalEmployeeBonusReport(models.Model):
    _name = 'employee_bonus_report_physical'
    _description =  "Payroll Employee Bonus Physical Model"
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee')
    fy_id = fields.Many2one('account.fiscalyear')
    april = fields.Float(string="April")
    may = fields.Float(string="May")
    june = fields.Float(string="June")
    july = fields.Float(string="July")
    august = fields.Float(string="August")
    september = fields.Float(string="September")
    october = fields.Float(string="October")
    november = fields.Float(string="November")
    december = fields.Float(string="December")
    january = fields.Float(string="January")
    february = fields.Float(string="February")
    march = fields.Float(string="March")
    name = fields.Char(related='employee_id.name', string="Name of the Employee")
    emp_code = fields.Char(related='employee_id.emp_code')
    department = fields.Many2one('hr.department',string='Department',related='employee_id.department_id')
    job = fields.Many2one('hr.job', string='Designation',related='employee_id.job_id')
    exit_date = fields.Date(related='employee_id.last_working_day')
    joining_date = fields.Date(string='Date Of Joining',related='employee_id.date_of_joining')