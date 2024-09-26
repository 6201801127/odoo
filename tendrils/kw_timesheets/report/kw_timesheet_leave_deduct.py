# from datetime import date, datetime, timezone, timedelta
# from dateutil.relativedelta import relativedelta
# from odoo import tools
from odoo import models, fields, api
from odoo.exceptions import ValidationError

month_list = [
        ('01', "January"), ('02', "February"), ('03', "March"), ('04', "April"),
        ('05', "May"), ('06', "June"), ('07', "July"), ('08', "August"),
        ('09', "September"), ('10', "October"), ('11', "November"), ('12', "December")]


class TimesheetLeaveDeduct(models.Model):
    _name = "kw_timesheet_leave_deduct"
    _description = "EL Deduction due to Deficit in Timesheet Efforts"

    emp_code = fields.Char(string="Employee Code")
    employee_id = fields.Many2one('hr.employee', string="Employee Name")
    designation = fields.Char(string="Designation")
    department_id = fields.Char(string="Department")
    division = fields.Char(string="Division")
    parent_id = fields.Char('Reporting Authority')
    timesheet_month = fields.Selection(string="Timesheet Month", selection=month_list)
    timesheet_year = fields.Integer("Timesheet Year")
    # timesheet_month_year = fields.Date(string="Timesheet Year/Month/Day")
    timesheet_el_deduct_in_days = fields.Float(string='Timesheet EL deduct in days')

    timesheet_payroll_report_id = fields.Many2one('kw_timesheet_payroll_report', string="Timesheet Payroll Report Id")
    el_deducted = fields.Boolean(string='EL Deducted')
    attendance_month_year = fields.Date(string="Timesheet Year/Month/Day")

    @api.multi
    def unlink(self):
        month_dict = dict(month_list)
        deducted_els = self.filtered('el_deducted')
        if deducted_els:
            raise ValidationError(f'EL is already deducted for {deducted_els[0].employee_id.name} for the year {deducted_els[0].timesheet_year} and for the month {month_dict[deducted_els[0].timesheet_month]}.\nHence it can\'t be deleted')
        return super(TimesheetLeaveDeduct, self).unlink()


