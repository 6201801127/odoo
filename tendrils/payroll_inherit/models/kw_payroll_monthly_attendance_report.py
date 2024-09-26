# -*- coding: utf-8 -*-
#########################
#
# Created On : 21-Oct-2020 , By : T Ketaki Debadarshini

#########################
import math
from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions
import calendar

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, \
    IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, LATE_WPC, LATE_WOPC, \
    ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT, DAY_STATUS_WEEKOFF, DAY_STATUS_RHOLIDAY, \
    DAY_STATUS_HOLIDAY, EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP


class AttendanceMonthlyPayroll(models.Model):
    _name = "kw_payroll_monthly_attendance_report"
    _description = "Attendance Monthly Payroll Info"
    _rec_name = 'employee_id'

    # @api.depends('num_leave_lwop','num_total_late_days_pc','num_absent_days')
    # def _compute_pay_cut(self):
    #     for rec in self:
    #         print("compute pay cut")
    #         rec.total_pay_cut = rec.num_leave_lwop + rec.num_total_late_days_pc + rec.num_absent_days

    # @api.depends('total_pay_cut')
    # def _compute_total_days_payable(self):
    #     for rec in self:
    #         print("total payable days")
    #         rec.total_days_payable = rec.num_present_days - rec.total_pay_cut

    attendance_year = fields.Integer(string="Attendance Year", index=True)
    attendance_month = fields.Integer(string="Attendance Month", index=True)
    attendance_month_name = fields.Char(string="Attendance Month", compute="_compute_month_name")
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', index=True)
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", index=True)
    department_id = fields.Many2one('hr.department', string="Department", index=True)

    num_leave_days = fields.Float(string="No Of Days in Leave (A)")
    num_tour_days = fields.Float(string="No Of Days in Business Tour (B)")
    num_absent_days = fields.Float(string="No Of Days in Absent (C)")
    absent_days = fields.Float(string="Absent Days")
    num_present_days = fields.Float(string="Present Days (Calendar)")
    num_shift_working_days = fields.Float(string="Shift Working Days (F)")  # # no of working days

    num_late_wopc = fields.Float(string="Late WOPC Days")
    num_fixed_late_days_pc = fields.Float(string="Fixed Late WPC Days")
    num_late_days_pc_after_fixed = fields.Float(string="Late WPC Days after Fixed")
    num_late_wpc = fields.Float(string="Late WPC Days")
    num_ex_late_wopc = fields.Float(string="Extra Late WOPC Days")
    num_ex_late_wpc = fields.Float(string="Fixed Extra Late WPC Days")
    num_total_late_days_pc = fields.Float(string="No of Paycut(Late attendance) (D)")

    num_wh_leave_days = fields.Float(string="Leave+Week Holiday")
    num_fh_leave_days = fields.Float(string="Leave+Fixed Holiday")
    num_wh_tour_days = fields.Float(string="Tour+Week Holiday")
    num_fh_tour_days = fields.Float(string="Tour+Fixed Holiday")

    num_present_days_count_log = fields.Float(string='Attendance Present Days', )
    emp_status = fields.Integer(string="Employee Status", )

    num_actual_working_days = fields.Float(string='Actual Working Days', )
    num_leave_lwop = fields.Float(string="No of Days in LWOP (E)")
    sync_status = fields.Selection(string="Sync Status",
                                   selection=[('0', 'Not Synced'), ('1', 'Inserted'), ('2', 'Updated'),
                                              ('5', 'Error Occurred')], default='0')

    num_mt_leave_days = fields.Float(string="Maternity Leave Days")
    total_pay_cut = fields.Float(string="Total Paycut (I) (C+D+E)", store=True, readonly=False)
    total_days_payable = fields.Float(string="Total Days Payable (F-I)", store=True, readonly=False)
    employee_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id')

    emp_status_value = fields.Char(string='Employee Status', compute='compute_emp_status', store=True)
    actual_working = fields.Float(string="Actual Working Day")
    boolean_readonly = fields.Boolean()
    kw_payable_days =  fields.Float(string="Tendrils Payable Days")
    month_days =  fields.Float(string="Month Days")
    calculation_days =  fields.Float(string="Calculation Days")

    ckeck_calendar_days = fields.Boolean()
    zero_payslip_boolean = fields.Boolean()
    company_id = fields.Many2one('res.company', string="Company", index=True)

    
    @api.onchange('attendance_year','attendance_month','emp_status')
    def onchange_attendance_monthdays(self):
        for rec in self:
            calculation_days = 0
            month_days = calendar.monthrange(rec.attendance_year, rec.attendance_month)[1]
            if rec.emp_status == 1:
                calculation_days = month_days
            elif rec.emp_status == 2:
                calculation_days = month_days - rec.employee_id.date_of_joining.day + 1
            elif rec.employee_id.last_working_day:
                if rec.employee_id.last_working_day.month == rec.employee_id.date_of_joining.month and rec.employee_id.last_working_day.year == rec.employee_id.date_of_joining.year:
                    calculation_days = rec.employee_id.last_working_day.day - rec.employee_id.date_of_joining.day + 1
                else:
                    calculation_days = rec.employee_id.last_working_day.day
            rec.write({
                'month_days': month_days,
                'calculation_days': calculation_days

            })
        
    @api.depends('emp_status')
    def compute_emp_status(self):
        value = '--'
        for rec in self:
            rec.onchange_attendance_monthdays()
            if rec.emp_status == 1:
                rec.emp_status_value = '--'
            elif rec.emp_status == 2:
                joining_day = rec.employee_id.date_of_joining.day
                joining_month = rec.employee_id.date_of_joining.month
                joining_year = rec.employee_id.date_of_joining.year
                month_dictionary = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                                    5: 'May', 6: 'June', 7: 'July', 8: 'Aug',
                                    9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
                month_name = month_dictionary.get(joining_month)
                joining_date = f"{joining_day}-{month_name}-{joining_year}"
                rec.emp_status_value = f"Joining date is {joining_date}"
            else:
                if rec.employee_id.last_working_day:
                    day = rec.employee_id.last_working_day.day
                    last_month = rec.employee_id.last_working_day.month
                    year = rec.employee_id.last_working_day.year
                    month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                                  5: 'May', 6: 'June', 7: 'July', 8: 'Aug',
                                  9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
                    month = month_dict.get(last_month)
                    last_day = f"{day}-{month}-{year}"
                    rec.emp_status_value = f"Last working date is {last_day}" if rec.employee_id.last_working_day else '--'
                else:
                    rec.emp_status_value = '--'

    @api.multi
    def _compute_month_name(self):
        for rec in self:
            rec.attendance_month_name = datetime.strptime(
                str(rec.attendance_year) + "-" + str(rec.attendance_month) + "-01", "%Y-%m-%d").strftime('%B')

    @api.onchange('num_leave_lwop', 'num_total_late_days_pc', 'num_absent_days')
    def onchange_for_total_pay_cut(self):
        for rec in self:
            rec.total_pay_cut = rec.num_leave_lwop + rec.num_total_late_days_pc + rec.num_absent_days

    @api.onchange('total_pay_cut')
    def onchange_total_pay_cut(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
        for rec in self:
            if enable_month_days != False:
                result = rec.calculation_days - rec.total_pay_cut
                rec.total_days_payable = result if result > 0 else 0
            else:
                result = rec.actual_working - rec.total_pay_cut
                rec.total_days_payable = result if result > 0 else 0