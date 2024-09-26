from odoo import api,models,fields
from odoo import tools


class TimesheetELDeductReport(models.Model):
    _name = "timesheet_el_deduct_report"
    _description = "Timesheet El Deduct Report"

    # created_by = fields.Many2one('hr.employee', string='Created By', compute="get_created_by_name")
    emp_code = fields.Char(string="Employee Code")
    employee = fields.Char(string="Employee Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    designation = fields.Char(string="Designation")
    department_id = fields.Char(string="Department")
    division = fields.Char(string="Division")
    parent_id = fields.Char('Reporting Authority')

    working_days = fields.Integer('Working Days')
    absent_days = fields.Float('Absent Days')
    on_tour_days = fields.Float('On Tour Days')
    on_leave_days = fields.Float('On Leave Days')

    per_day_effort = fields.Float(string='Per Day Effort')
    required_effort_hour = fields.Float('Required Effort Hour')
    num_actual_effort = fields.Float('Actual Effort Hour')
    total_effort = fields.Float(string='Extra/Deficit Effort Hour')
    required_effort_day = fields.Float(string='Required Effort in Days')
    num_actual_effort_day = fields.Float(string='Actual Effort in Days')
    total_effort_day = fields.Float(string='Extra/Deficit Effort in Days')

    attendance_month = fields.Selection(string="Timesheet Month", selection=[
        ('01', "January"), ('02', "February"), ('03', "March"), ('04', "April"),
        ('05', "May"), ('06', "June"), ('07', "July"), ('08', "August"),
        ('09', "September"), ('10', "October"), ('11', "November"), ('12', "December")])
    attendance_year = fields.Integer("Timesheet Year")
    attendance_month_year = fields.Date(string="Timesheet Year/Month/Day")

    required_effort_char = fields.Char(string='Required Effort In HH:MM')
    actual_effort_char = fields.Char(string="Actual Effort In HH:MM")
    total_effort_char = fields.Char(string="Extra/Deficit Effort In HH:MM")
    total_effort_percent = fields.Float(string="Extra/Deficit Effort In (%)")

    timesheet_el_days = fields.Float(string="Timesheet EL Deduction in Days")
    timesheet_paycut_days = fields.Float(string="Timesheet Paycut in Days")



    # def get_created_by_name(self):
    #     for rec in self:
    #         pass
