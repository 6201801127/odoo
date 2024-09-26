# -*- coding: utf-8 -*-
from datetime import date
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WEEKOFF,DAY_STATUS_RHOLIDAY, DAY_STATUS_HOLIDAY, DAY_STATUS_WORKING, LEAVE_STS_SHALF, LEAVE_STS_FHALF, LEAVE_STS_ALL_DAY, ATD_STATUS_SHALF_ABSENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_ABSENT, ATD_STATUS_PRESENT, OUT_STATUS_EE_HALF_DAY, OUT_STATUS_EXTRA_LE, OUT_STATUS_LE, OUT_STATUS_ON_TIME, OUT_STATUS_EARLY_EXIT, IN_STATUS_LE_FULL_DAY, IN_STATUS_LE_HALF_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, IN_STATUS_EXTRA_EARLY_ENTRY, IN_STATUS_EARLY_ENTRY, IN_STATUS_ON_TIME, IN_STATUS_LE, IN_STATUS_EXTRA_LE, IN_STATUS_EXTRA_LE


class AttendancePaycutReport(models.Model):
    _name = "kw_attendance_paycut_report"
    _description = "Employee Attendance Paycut Report"
    _rec_name = 'emp_name'
    _order = "attendance_recorded_date desc"
    _auto = False

    attendance_recorded_date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    emp_name = fields.Char(string='Name')
    # branch              = fields.Char(string="Branch")
    # department          = fields.Char(string='Department')
    designation = fields.Many2one('hr.job', string="Designation")
    check_in = fields.Datetime(string="Check In", )
    check_out = fields.Datetime(string="Check Out", )
    check_in_status = fields.Selection(string='In Status',
                                       selection=[(IN_STATUS_EXTRA_EARLY_ENTRY, 'Extra Early Entry'),
                                                  (IN_STATUS_EARLY_ENTRY, 'Early Entry'),
                                                  (IN_STATUS_ON_TIME, 'On Time'),
                                                  (IN_STATUS_LE, 'Late Entry'),
                                                  (IN_STATUS_EXTRA_LE, 'Extra Late Entry'),
                                                  (IN_STATUS_LE_HALF_DAY, 'Late Entry Half Day Absent'),
                                                  (IN_STATUS_LE_FULL_DAY, 'Late Entry Full Day Absent')])
    check_out_status = fields.Selection(string='Out Status',
                                        selection=[(OUT_STATUS_EARLY_EXIT, 'Early Exit'),
                                                   (OUT_STATUS_ON_TIME, 'On Time'),
                                                   (OUT_STATUS_LE, 'Late Exit'),
                                                   (OUT_STATUS_EXTRA_LE, 'Extra Late Exit'),
                                                   (OUT_STATUS_EE_HALF_DAY, 'Early Exit Half Day Absent')], )
    state = fields.Selection(string="Attendance Status",
                             selection=[(ATD_STATUS_PRESENT, 'Present'),
                                        (ATD_STATUS_ABSENT, 'Absent'),
                                        (ATD_STATUS_FHALF_ABSENT, 'First Half Absent'),
                                        (ATD_STATUS_SHALF_ABSENT, 'Second Half Absent')])
    leave_status = fields.Selection(string="Leave Status", selection=[(LEAVE_STS_ALL_DAY, 'On Leave'),
                                                                      (LEAVE_STS_FHALF, 'First Half Leave'),
                                                                      (LEAVE_STS_SHALF, 'Second Half Leave')], )
    is_on_tour = fields.Boolean(string="Is On Tour")
    payroll_day_value = fields.Float(string="Payroll Day")

    attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Attendance")
    shift_name = fields.Char(string='Work Shift')

    shift_in = fields.Char(string="Shift In Time", related="attendance_id.shift_in")
    shift_out = fields.Char(string="Shift Out Time", related="attendance_id.shift_out")
    check_in_time = fields.Char(string="In Time", related="attendance_id.check_in_time")
    check_out_time = fields.Char(string="Out Time", related="attendance_id.check_out_time")
    status = fields.Char(string="Status", related="attendance_id.status")

    day_status = fields.Selection(string="Day Status",
                                  selection=[
                                      (DAY_STATUS_WORKING, 'Working Day'),
                                      (DAY_STATUS_HOLIDAY, 'Holiday'),
                                      (DAY_STATUS_RWORKING, 'Roster Working Day'),
                                      (DAY_STATUS_RHOLIDAY, 'Roster Week Off'),
                                      (DAY_STATUS_WEEKOFF, 'Week Off')])
    paycut = fields.Char(string="Paycut")
    paycut_value = fields.Float(string="Absent Day")
    description = fields.Text("Description", compute="_compute_description")
    department_id = fields.Many2one('hr.department', string="Department")
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")

    employement_type = fields.Many2one('kwemp_employment_type', string="Employment Type")

    def get_message(self):
        message = ""
        if self.check_in_status and  self.check_in_status in [IN_STATUS_LE_HALF_DAY,IN_STATUS_LE_FULL_DAY]:
            message += dict(self._fields['check_in_status'].selection).get(self.check_in_status)

        if self.check_out_status and self.check_out_status in [OUT_STATUS_EE_HALF_DAY]:
            temp_message = dict(self._fields['check_out_status'].selection).get(self.check_out_status)
            message += '\n'+temp_message if len(message) else temp_message

        if not self.check_in_status or not self.check_out:
            temp_message = "No office-out time available."
            message += '\n'+temp_message if len(message) else temp_message
        return message

    @api.multi
    def _compute_description(self):
        for paycut in self:
            common = ""  # Paycut Info: \n
            if paycut.state == ATD_STATUS_ABSENT:
                if not paycut.check_in_status and not paycut.check_out_status:
                    paycut.description = common + "Office-in and Office-out info(s) are not available."
                else:
                    paycut.description = common + paycut.get_message()

            elif paycut.state in [ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT]:
                paycut.description = common + dict(self._fields['state'].selection).get(paycut.state) + " : " + paycut.get_message()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select a.id as id,a.attendance_recorded_date,a.employee_id,a.department_id,a.branch_id,concat(emp.name,'(',emp.emp_code,') ,',job.name,'(',dept.name,')') as emp_name,job.id as designation,
            a.check_in,a.check_out,a.check_in_status,a.check_out_status,a.state,a.leave_status,a.is_on_tour,a.payroll_day_value,
            a.id as attendance_id,a.shift_name,a.day_status,CASE    WHEN a.payroll_day_value=0 THEN 'Full Day'
                                                                    WHEN a.payroll_day_value=0.5 THEN 'Half Day'
                                                                    END as paycut
            ,CASE  WHEN a.payroll_day_value=0 THEN 1 WHEN a.payroll_day_value=0.5 THEN 0.5 END as paycut_value
            ,emp.employement_type
            from kw_daily_employee_attendance a
            join hr_employee emp on a.employee_id = emp.id
            left join hr_department dept on emp.department_id = dept.id
            left join hr_job job on emp.job_id = job.id
            
            where a.payroll_day_value <1 and a.is_on_tour = False 
        )"""
        self.env.cr.execute(query)
