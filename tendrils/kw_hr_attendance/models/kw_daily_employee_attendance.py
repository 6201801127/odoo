# -*- coding: utf-8 -*-
# #################################
# # Daily employee attendance consolidated data for payroll :: Created BY : T Ketaki Debadrashini,
# # Half Day Absent if No check-out : 10th Nov 20 , By : T Ketaki Debadarshini
# # Update Work Mode of employee during attendance recomputation 23-Feb-2021 (Gouranga)
# ##################################
from datetime import datetime, timezone, timedelta, time, date
import pytz
import calendar
import random
import logging
import secrets
import requests, json
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from odoo.http import request
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from odoo.addons.resource.models import resource
from odoo.addons.resource.models.resource import Intervals

from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
# import the auth module log-in
from odoo.addons.kw_auth.controllers.web_controller_main_in import Home as login_controller

DAY_STATUS_WORKING, DAY_STATUS_LEAVE, DAY_STATUS_HOLIDAY, DAY_STATUS_RWORKING, DAY_STATUS_RHOLIDAY, DAY_STATUS_WEEKOFF = '0', '1', '2', '3', '4', '5'

IN_STATUS_EXTRA_EARLY_ENTRY, IN_STATUS_EARLY_ENTRY, IN_STATUS_ON_TIME, IN_STATUS_LE, IN_STATUS_EXTRA_LE, IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY = '-1', '0', '1', '2', '3', '4', '5'
OUT_STATUS_EARLY_EXIT, OUT_STATUS_ON_TIME, OUT_STATUS_LE, OUT_STATUS_EXTRA_LE, OUT_STATUS_EE_HALF_DAY = '0', '1', '2', '3', '4'

ATD_STATUS_PRESENT, ATD_STATUS_ABSENT, ATD_STATUS_TOUR, ATD_STATUS_LEAVE, ATD_STATUS_FHALF_LEAVE, ATD_STATUS_SHALF_LEAVE, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT = '1', '2', '3', '4', '5', '6', '7', '8'

ATD_MODE_BIO, ATD_MODE_MANUAL, ATD_MODE_PORTAL, ATD_MODE_ATD_REQUEST = 'bio_metric', 'manual', 'portal', 'attendance_request'

LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF = '1', '2', '3'

LVISIT_STS_ALL_DAY, LVISIT_STS_FHALF, LVISIT_STS_SHALF = '1', '2', '3'

EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP = 1, 2, 3

RECOMPUTE_START_DAY, KWANTIFY_SERVER_TIMEZONE = 1, "Asia/Kolkata"
WFH_STATUS, WFO_STATUS, WFA_STATUS = '0', '1', '2'
LE_STATE_DRAFT, LE_STATE_APPLY, LE_STATE_GRANT, LE_STATE_FORWARD = '0', '1', '2', '3'
LATE_WPC, LATE_WOPC = '1', '2'

LATE_PC_PER_DAY_VALUE, LATE_PC_FIXED_DAY_VALUE, LATE_PC_FIXED_DAY = 0.25, 0.2, 5
LEAVE_TYPE_MATERNITY = 'MT'


def float_time_to_seconds(float_time):
    """ Convert a float time timedelta object. """

    time_obj = resource.float_to_time(float_time)
    ho, mi, se = str(time_obj).split(':')
    time_delta_obj = timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))

    return time_delta_obj.seconds


class DailyHrAttendance(models.Model):
    _name = "kw_daily_employee_attendance"
    _description = "Daily Attendance"
    _order = "attendance_recorded_date desc"
    _rec_name = 'employee_id'

    # _inherit        = ["mail.thread"]

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True, )
    attendance_recorded_date = fields.Date('Attendance Date', required=True, index=True, )

    check_in = fields.Datetime(string="Check In", )  # #optional as the record can be inserted for holiday
    check_out = fields.Datetime(string="Check Out", )
    check_in_mode = fields.Integer(string='Log-in Mode', default=0)  # #0- web, 1- bio, 2-manual ,3- Attendance request
    check_in_through = fields.Selection(selection=[('0', 'Portal'), ('1', 'Biometric'), ('2', 'Manual'), ('3', 'Attendance Request')],
                                        string="Check In Mode", compute="_compute_check_in_through")
    check_out_mode = fields.Integer(string='Log-out Mode', default=0)

    emp_tz_check_in = fields.Char('Check In Emp. Timezone', compute='_compute_display_time')
    emp_tz_check_out = fields.Char('Check Out Emp. Timezone', compute='_compute_display_time')

    tz = fields.Selection(_tz_get, string='Timezone',
                          default=lambda self: self._context.get('tz') or self.env.user.employee_ids.tz or 'UTC',
                          help="This field is used in order to define in which timezone the resources will work.")

    shift_id = fields.Many2one('resource.calendar', string="Shift ", )
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", index=True)
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit',compute="get_infra_of_employee",string="Infra Location")
    # branch_location     = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)
    is_cross_shift = fields.Boolean(string="Is Cross Shift", )
    shift_name = fields.Char(string='Shift Name', )

    shift_in_time = fields.Float(string="Shift In Time", )
    shift_out_time = fields.Float(string="Shift Out Time", )
    shift_rest_time = fields.Float(string='Shift Rest Hour', compute="_compute_shift_details", store=True)

    shift_second_half_time = fields.Float(string="Shift Second Half In Time", )

    check_in_status = fields.Selection(string='Office-in Status',
                                       selection=[(IN_STATUS_EXTRA_EARLY_ENTRY, 'Extra Early Entry'),
                                                  (IN_STATUS_EARLY_ENTRY, 'Early Entry'),
                                                  (IN_STATUS_ON_TIME, 'On Time'), (IN_STATUS_LE, 'Late Entry'),
                                                  (IN_STATUS_EXTRA_LE, 'Extra Late Entry'),
                                                  (IN_STATUS_LE_HALF_DAY, 'Late Entry Half Day Absent'),
                                                  (IN_STATUS_LE_FULL_DAY, 'Late Entry Full Day Absent')], readonly=True,
                                       compute='_compute_checkin_status', store=True)

    late_entry_duration = fields.Float(string="Late Entry Duration", )
    check_out_status = fields.Selection(string='Office-out Status', selection=[(OUT_STATUS_EARLY_EXIT, 'Early Exit'),
                                                                               (OUT_STATUS_ON_TIME, 'On Time'),
                                                                               (OUT_STATUS_LE, 'Late Exit'),
                                                                               (OUT_STATUS_EXTRA_LE, 'Extra Late Exit'),
                                                                               (OUT_STATUS_EE_HALF_DAY,
                                                                                'Early Exit Half Day Absent')],
                                        readonly=True, compute='_compute_attendance_check_out_status', store=True, )

    lunch_in = fields.Datetime(string="Lunch In")
    lunch_out = fields.Datetime(string="Lunch Out")
    worked_hours = fields.Float(string='Working Hours', compute='_compute_worked_hours', store=True, readonly=True)  #

    state = fields.Selection(string="Attendance Status",
                             selection=[(ATD_STATUS_PRESENT, 'Present'), (ATD_STATUS_ABSENT, 'Absent'),
                                        (ATD_STATUS_FHALF_ABSENT, 'First Half Absent'),
                                        (ATD_STATUS_SHALF_ABSENT, 'Second Half Absent')],
                             readonly=True,
                             compute="_compute_attendance_status",
                             store=True)  # # (ATD_STATUS_TOUR, 'On Tour'), (ATD_STATUS_LEAVE, 'On-leave'),

    day_status = fields.Selection(string="Day Status",
                                  selection=[(DAY_STATUS_WORKING, 'Working Day'), (DAY_STATUS_HOLIDAY, 'Holiday'),
                                             (DAY_STATUS_RWORKING, 'Roster Working Day'),
                                             (DAY_STATUS_RHOLIDAY, 'Roster Week Off'),
                                             (DAY_STATUS_WEEKOFF, 'Week Off')],
                                  readonly=True, default='0',
                                  compute="_compute_shift_details",
                                  store=True, )  # #WeekHoliday    (DAY_STATUS_LEAVE, 'On Leave'),

    late_entry_reason = fields.Text(string='Late Entry Reason', )
    le_forward_to = fields.Many2one('hr.employee', string="Late Entry Forwarded To", ondelete='cascade',
                                    compute='_compute_leapproval_status', store=True)
    le_forward_reason = fields.Text(string='Late Entry Forward Reason', )

    le_authority_remark = fields.Text(string='Late Entry Remark', )
    le_action_taken_by = fields.Many2one('hr.employee', string="Late Entry Action Taken By", ondelete='cascade', )
    le_action_taken_on = fields.Datetime(string="Late Entry Action Taken On", )
    le_state = fields.Selection(string="Late Entry Status",
                                selection=[(LE_STATE_DRAFT, 'Draft'), (LE_STATE_APPLY, 'Applied'),
                                           (LE_STATE_GRANT, 'Granted'), (LE_STATE_FORWARD, 'Forwarded')],
                                )
    # le_actions              = fields.Selection(string="Late Entry Action" ,selection=[('1', 'Approve'),('2', 'Reject'),('3', 'Forward')],)
    le_action_status = fields.Selection(string="Late Entry Action Status",
                                        selection=[(LATE_WPC, 'With Pay Cut'), (LATE_WOPC, 'Without Pay Cut')],
                                        compute='_compute_leapproval_status', store=True)  ##LateWOPC  LateWPC

    le_approval_log_ids = fields.One2many(
        string='Approval Logs',
        comodel_name='kw_late_entry_approval_log',
        inverse_name='daily_attendance_id',
    )

    shift_in = fields.Char(string="Shift In Time", compute="_compute_convert_float_time_to_string", store=False)
    shift_out = fields.Char(string="Shift Out Time", compute="_compute_convert_float_time_to_string", store=False)
    check_in_time = fields.Char(string="Check In Time", compute="_compute_convert_float_time_to_string", store=False)
    check_out_time = fields.Char(string="Check Out Time", compute="_compute_convert_float_time_to_string", store=False)
    lunch_in_time = fields.Char(string="Lunch In Time", compute="_compute_convert_float_time_to_string", store=False)
    lunch_out_time = fields.Char(string="Lunch Out Time", compute="_compute_convert_float_time_to_string", store=False)
    status = fields.Char(string="Status", compute="_merge_day_status_attendance_status", store=False)
    this_month_record = fields.Boolean(string="Is Current Month Record", compute="_merge_day_status_attendance_status", store=False)
    is_le_authorized = fields.Boolean(string="Is Authorized to Take Action", compute="_merge_day_status_attendance_status", store=False)

    kw_sync_status = fields.Boolean(string="Tendrils Sync Status", default=False)
    is_on_tour = fields.Boolean(string="Is On Tour", default=False)
    leave_status = fields.Selection(string="Leave Status",
                                    selection=[(LEAVE_STS_ALL_DAY, 'On Leave'), (LEAVE_STS_FHALF, 'First Half Leave'),
                                               (LEAVE_STS_SHALF, 'Second Half Leave')], )
    is_lwop_leave = fields.Boolean(string="Is LWOP Leave", default=False)
    leave_day_value = fields.Float(string="Leave Day", default=0, compute="_compute_leave_day_value", store=True)  # ,groups="base.group_no_one"
    leave_code = fields.Char(string="Leave Code")
    payroll_day_value = fields.Float(string="Payroll Day", default=0, compute="_compute_payroll_day_value", store=True)
    is_valid_working_day = fields.Boolean(string="Is Valid Working Day", default=True, compute="_compute_valid_working_day", store=True)

    department_id = fields.Many2one('hr.department', string="Department", index=True)
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Practice")
    practice_id = fields.Many2one('hr.department', string="Section")
    work_mode = fields.Selection(string="Working From", selection=[(WFH_STATUS, 'WFH'), (WFO_STATUS, 'WFO'), (WFA_STATUS, 'WFA')], default=WFO_STATUS)

    employee_status = fields.Integer(string='Employee Month Status', default=1)  # #1 for normal ,2 for new joinee and 3 for ex-employee this month

    local_visit_status = fields.Selection(string='Local Visit Status',
                                          selection=[(LVISIT_STS_FHALF, 'First Half Absent'),
                                                     (LVISIT_STS_SHALF, 'Second Half Absent'),
                                                     (LVISIT_STS_ALL_DAY, 'Absent')])

    is_fixed_holiday = fields.Boolean(string="Is Fixed Holiday", compute="_merge_day_status_attendance_status", store=False)
    is_weekoff = fields.Boolean(string="Is Fixed Holiday", compute="_merge_day_status_attendance_status", store=False)
    is_roster_weekoff = fields.Boolean(string="Is Fixed Holiday", compute="_merge_day_status_attendance_status", store=False)

    attendance_update_logs = fields.Text("Attendance Update Logs")
    # subordinate_ids     = fields.Many2many('hr.employee','Subordinates',compute="_compute_subordinates")

    _sql_constraints = [
        ('daily_attendance_unique', 'unique (employee_id,attendance_recorded_date)', 'The attendance record exists for the selected date.'),
    ]
               

    @api.depends('employee_id')
    def get_infra_of_employee(self):
        for rec in self:
            rec.infra_unit_location_id = rec.employee_id.branch_unit_id

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print('self._context',self._context)
        if self._context.get('late_entry_report'):
            if self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
                args +=[]
            else:
                args += [('employee_id','child_of',self.env.user.employee_ids.ids)]
        return super(DailyHrAttendance, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)   

    @api.multi
    def _compute_convert_float_time_to_string(self):
        for attendance in self:
            emp_timezone = pytz.timezone(attendance.tz or attendance.employee_id.tz or 'UTC')

            if attendance.shift_in_time:
                shiftIn = '{0:02.0f}:{1:02.0f}'.format(*divmod(attendance.shift_in_time * 60, 60))
                attendance.shift_in = datetime.strptime(shiftIn, "%H:%M").strftime("%I:%M %p") if shiftIn else ''

            if attendance.shift_out_time:
                shiftOut = '{0:02.0f}:{1:02.0f}'.format(*divmod(attendance.shift_out_time * 60, 60))
                attendance.shift_out = datetime.strptime(shiftOut, "%H:%M").strftime("%I:%M %p") if shiftOut else ''

            attendance.check_in_time = datetime.strftime(attendance.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M:%S %p") if attendance.check_in else ''

            attendance.check_out_time = datetime.strftime(attendance.check_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M:%S %p") if attendance.check_out else ''

            attendance.lunch_in_time = datetime.strftime(attendance.lunch_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M:%S %p") if attendance.lunch_in else ''

            attendance.lunch_out_time = datetime.strftime(attendance.lunch_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M:%S %p") if attendance.lunch_out else ''

    @api.multi
    def _merge_day_status_attendance_status(self):
        for attendance in self:
            str_state = ''
            if attendance.payroll_day_value == 0:
                str_state = 'Absent'
            if attendance.day_status in [DAY_STATUS_RHOLIDAY, DAY_STATUS_WEEKOFF]:
                str_state = 'Week Off'
            if attendance.day_status in [DAY_STATUS_HOLIDAY]:
                str_state = 'Holiday'
            if attendance.day_status not in [DAY_STATUS_RHOLIDAY, DAY_STATUS_WEEKOFF, DAY_STATUS_HOLIDAY] and attendance.check_in:
                str_state = 'Present'
            if attendance.is_on_tour:
                str_state = 'On Tour'
            if attendance.leave_status:
                str_state = dict(self._fields['leave_status'].selection).get(attendance.leave_status)

                # added on 5 April 2021 to show the leave type in status (Gouranga)
                if attendance.leave_code:
                    try:
                        leave_type = self.env['hr.leave.type'].sudo().search([('leave_code', '=', attendance.leave_code)])
                        if leave_type:
                            str_state += f'({leave_type.name})'

                    except Exception:
                        pass

            attendance.status = str_state

            attendance.this_month_record = True if attendance.employee_id.user_id and attendance.employee_id.user_id == self.env.user and attendance.attendance_recorded_date.strftime("%m") == datetime.now().strftime("%m") and attendance.attendance_recorded_date.strftime("%Y") == datetime.now().strftime("%Y") else False

            attendance.is_le_authorized = True if attendance.le_forward_to.user_id and attendance.le_forward_to.user_id == self.env.user else False

            attendance.is_fixed_holiday = True if attendance.day_status in [DAY_STATUS_HOLIDAY] else False
            attendance.is_weekoff = True if attendance.day_status in [DAY_STATUS_WEEKOFF] else False
            attendance.is_roster_weekoff = True if attendance.day_status in [DAY_STATUS_RHOLIDAY] else False

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.employee_id.name
            result.append((record.id, record_name))
        return result

    # added to get working mode of an employee for a date 23-Feb-2021 (Gouranga)
    def get_employee_work_mode(self, employee_id, work_date):
        mode = WFO_STATUS
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.location == 'wfa':
            mode = WFA_STATUS
        else:
            try:
                emp_wfh_data = self.env['kw_wfh'].sudo().search(
                    ['&', ('employee_id', '=', employee_id),
                     '|',
                     '&', '&', ('state', '=', 'grant'), ('request_from_date', '<=', work_date), ('request_to_date', '>=', work_date),
                     '&', '&', ('state', '=', 'expired'), ('act_from_date', '<=', work_date), ('act_to_date', '>=', work_date),
                     ])
                if emp_wfh_data:
                    mode = WFH_STATUS
            except Exception as e:
                pass
        return mode

    @api.multi
    def _compute_display_time(self):
        for attendance in self:
            attendance.emp_tz_check_in = self._get_display_time(attendance.tz,attendance.check_in) if attendance.tz and attendance.check_in else False
            attendance.emp_tz_check_out= self._get_display_time(attendance.tz,attendance.check_out) if attendance.tz and attendance.check_out else False

    @api.model
    def _get_display_time(self, emp_tz, display_datetime):
        """ Return date and time (from to from) based on duration with timezone in string. Eg :
            return : August-23-2013 at (04-30 To 06-30) (Europe/Brussels)
                
        """
        # timezone = emp_tz or 'UTC'
        timezone = pycompat.to_native(emp_tz)  # make safe for str{p,f}time()

        # get date/time format according to context
        format_date, format_time = self._get_date_formats()

        # convert date and time into user timezone
        self_tz = self.with_context(tz=timezone)
        date = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(display_datetime))
        to_text = pycompat.to_text
        date_str = to_text(date.strftime(format_date))
        time_str = to_text(date.strftime(format_time))
        display_time = (u"%s %s (%s)") % (date_str, time_str, timezone,)

        return display_time

    @api.depends('shift_rest_time', 'lunch_in', 'lunch_out', 'check_in', 'check_out', 'day_status', 'state')
    def _compute_worked_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                worked_hour_in_sec      = (rec.check_out - rec.check_in).total_seconds()
                # print('working hour calculation --------------')
                # print(worked_hour_in_sec)
                rest_time_in_sec = 0
                if rec.day_status in [DAY_STATUS_WORKING,DAY_STATUS_RWORKING]: #and rec.state in [ATD_STATUS_PRESENT,ATD_STATUS_FHALF_ABSENT,ATD_STATUS_SHALF_ABSENT]
                    emp_timezone = pytz.timezone(rec.tz)
                    emp_cur_time_tz = rec.check_out.astimezone(emp_timezone)
                    half_start_datetime = datetime.combine(rec.attendance_recorded_date,resource.float_to_time(rec.shift_second_half_time))

                    if emp_cur_time_tz.replace(tzinfo=None) >= half_start_datetime:
                        if rec.lunch_in and rec.lunch_out:
                            rest_time_in_sec = (rec.lunch_in - rec.lunch_out).total_seconds()
                        else:
                            rest_time_in_sec = float_time_to_seconds(rec.shift_rest_time)

                rec.worked_hours = float_round((worked_hour_in_sec - rest_time_in_sec) / 3600, precision_digits=2)

    @api.depends('employee_id', 'attendance_recorded_date', 'check_in')
    def _compute_shift_details(self):
        for attendance_rec in self:
            shift_info = self._compute_day_status(attendance_rec.employee_id, attendance_rec.attendance_recorded_date)
            if shift_info:
                attendance_rec.day_status, attendance_rec.shift_rest_time = shift_info[0], shift_info[1]

    @api.depends('check_in', 'day_status', 'shift_in_time', 'leave_status', 'shift_second_half_time', 'is_on_tour')
    def _compute_checkin_status(self):
        for attendance_rec in self:
            # #check for attendance mode, for no attendance mode enabled , late entry status will not be calculated :: and if the day is not holiday/weekoff
            if not attendance_rec.employee_id.no_attendance and attendance_rec.day_status in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING] \
                    and attendance_rec.check_in and not attendance_rec.is_on_tour:

                timezone = pytz.timezone(attendance_rec.tz or attendance_rec.employee_id.tz or 'UTC')
                check_in_status = IN_STATUS_ON_TIME
                # #Start check-in time status updation

                check_in_time_tz = attendance_rec.check_in.astimezone(timezone)
                in_date = attendance_rec.attendance_recorded_date.strftime("%Y-%m-%d")

                # #"""if first half is on-leave then the entry time would be shift second half start time"""
                shift_in_time = attendance_rec.shift_second_half_time if attendance_rec.leave_status == LEAVE_STS_FHALF and attendance_rec.shift_second_half_time else attendance_rec.shift_in_time

                naive_in_datetime = datetime.strptime(in_date + ' ' + str(resource.float_to_time(shift_in_time)), "%Y-%m-%d %H:%M:%S")

                naive_early_entry_time = naive_in_datetime + relativedelta(seconds=-float_time_to_seconds(attendance_rec.shift_id.early_entry_time)) if attendance_rec.shift_id.early_entry_time > 0 else False

                naive_extra_late_entry_time = naive_in_datetime + relativedelta(seconds=+float_time_to_seconds(attendance_rec.shift_id.late_entry_time)) if attendance_rec.shift_id.late_entry_time > 0 else False

                naive_half_day_late_entry_time = naive_in_datetime + relativedelta(seconds=+float_time_to_seconds(attendance_rec.shift_id.late_entry_half_leave_time)) if attendance_rec.shift_id.late_entry_half_leave_time > 0 else False

                naive_full_day_late_entry_time = naive_in_datetime + relativedelta(seconds=+float_time_to_seconds(attendance_rec.shift_id.late_entry_full_leave_time)) if attendance_rec.shift_id.late_entry_full_leave_time > 0 else False

                if naive_early_entry_time and check_in_time_tz.replace(tzinfo=None) <= naive_early_entry_time:
                    check_in_status = IN_STATUS_EARLY_ENTRY

                    naive_extra_early_entry_time = naive_in_datetime + relativedelta(seconds=-float_time_to_seconds(attendance_rec.shift_id.extra_early_entry_time)) if attendance_rec.shift_id.extra_early_entry_time > 0 else False
                    if naive_extra_early_entry_time and check_in_time_tz.replace(tzinfo=None) <= naive_extra_early_entry_time:
                        check_in_status = IN_STATUS_EXTRA_EARLY_ENTRY

                else:
                    # #fetch the grace time
                    grace_time = attendance_rec.shift_id._get_shift_grace_time(attendance_rec.shift_id, in_date)

                    if check_in_time_tz.replace(tzinfo=None) > naive_in_datetime \
                            and check_in_time_tz.replace(tzinfo=None) > naive_in_datetime + relativedelta(seconds=+float_time_to_seconds(grace_time)):
                        check_in_status = IN_STATUS_LE
                        if naive_extra_late_entry_time and check_in_time_tz.replace(tzinfo=None) >= naive_extra_late_entry_time:
                            check_in_status = IN_STATUS_EXTRA_LE
                        if naive_half_day_late_entry_time and check_in_time_tz.replace(tzinfo=None) >= naive_half_day_late_entry_time:
                            check_in_status = IN_STATUS_LE_HALF_DAY
                        if naive_full_day_late_entry_time and check_in_time_tz.replace(tzinfo=None) >= naive_full_day_late_entry_time:
                            check_in_status = IN_STATUS_LE_FULL_DAY
                # print(check_in_status)
                attendance_rec.check_in_status = check_in_status

                # #END: chec-in time status updation ##

    @api.depends('check_in_status','late_entry_reason')
    def _compute_leapproval_status(self):
        for attendance_rec in self:
            query=f"select le_action_status from kw_daily_employee_attendance where id={attendance_rec.id}"
            self._cr.execute(query)
            le_action=self._cr.fetchall()
            if attendance_rec.check_in_status:
                if attendance_rec.check_in_status in [IN_STATUS_LE,IN_STATUS_EXTRA_LE]:
                    if attendance_rec.le_state in [LE_STATE_DRAFT,LE_STATE_APPLY,False]:
                        config_param = self.env['ir.config_parameter'].sudo()
                        late_entry_enabled = config_param.get_param('kw_hr_attendance.late_entry_screen_enable')
                        excluded_grade_ids = literal_eval(config_param.get_param('kw_hr_attendance.attn_exclude_grade_ids','False'))
                        if late_entry_enabled:
                            if attendance_rec.employee_id.grade.id not in excluded_grade_ids:
                                attendance_rec.le_action_status = LATE_WPC
                                if attendance_rec.late_entry_reason:
                                    attendance_rec.le_forward_to = attendance_rec.employee_id.parent_id.id
                            else :
                                attendance_rec.le_action_status = LATE_WOPC
                                attendance_rec.le_forward_to = False
                        else:
                            attendance_rec.le_action_status =  LATE_WOPC
                            attendance_rec.le_forward_to    = False   
                    else:
                        check_status = le_action[0][0]
                        if attendance_rec.le_state in [LE_STATE_GRANT]:
                            attendance_rec.le_action_status = check_status
                        else:
                            attendance_rec.le_action_status = False
                            attendance_rec.le_forward_to    = False

    @api.depends('check_out', 'day_status', 'shift_out_time', 'is_on_tour')
    def _compute_attendance_check_out_status(self):
        for attendance_rec in self:
            # #check for attendance mode, for no attendance mode enabled , late entry status will not be calculated :: and the day is not holiday/weekoff
            if not attendance_rec.employee_id.no_attendance and attendance_rec.day_status in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING] and not attendance_rec.is_on_tour:

                timezone = pytz.timezone(attendance_rec.tz or attendance_rec.employee_id.tz or 'UTC')

                # #Start :: check-out time status updation ##
                if attendance_rec.check_out:
                    check_out_status = OUT_STATUS_ON_TIME
                    check_out_time_tz = attendance_rec.check_out.astimezone(timezone)
                    out_date = (attendance_rec.attendance_recorded_date + timedelta(days=1)).strftime("%Y-%m-%d") if attendance_rec.is_cross_shift else attendance_rec.attendance_recorded_date.strftime("%Y-%m-%d")

                    naive_out_datetime = datetime.strptime(out_date + ' ' + str(resource.float_to_time(attendance_rec.shift_out_time)), "%Y-%m-%d %H:%M:%S")

                    naive_late_exit_time = naive_out_datetime + relativedelta(seconds=+float_time_to_seconds(attendance_rec.shift_id.late_exit_time)) if attendance_rec.shift_id.late_exit_time > 0 else False

                    naive_extra_late_exit_time = naive_out_datetime + relativedelta(seconds=+float_time_to_seconds(attendance_rec.shift_id.extra_late_exit_time)) if attendance_rec.shift_id.extra_late_exit_time > 0 else False

                    naive_half_day_early_exit_time = naive_out_datetime + relativedelta(seconds=-float_time_to_seconds(attendance_rec.shift_id.early_exit_half_leave_time)) if attendance_rec.shift_id.early_exit_half_leave_time > 0 else False

                    if check_out_time_tz.replace(tzinfo=None) < naive_out_datetime:
                        check_out_status = OUT_STATUS_EARLY_EXIT

                        if naive_half_day_early_exit_time and check_out_time_tz.replace(tzinfo=None) <= naive_half_day_early_exit_time:
                            check_out_status = OUT_STATUS_EE_HALF_DAY
                    elif naive_late_exit_time and check_out_time_tz.replace(tzinfo=None) >= naive_late_exit_time:
                        check_out_status = OUT_STATUS_LE
                        if naive_extra_late_exit_time and check_out_time_tz.replace(tzinfo=None) >= naive_extra_late_exit_time:
                            check_out_status = OUT_STATUS_EXTRA_LE

                    attendance_rec.check_out_status = check_out_status
                # #END: check_out  time status updation ##

    @api.depends('check_in_status', 'day_status', 'check_out_status', 'is_on_tour', 'leave_status')
    def _compute_attendance_status(self):
        for attendance_rec in self:

            attendance_status = ATD_STATUS_PRESENT if attendance_rec.check_in else ATD_STATUS_ABSENT
            # #if its a working day
            if attendance_rec.day_status in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]:

                if attendance_rec.check_in_status in [IN_STATUS_LE_HALF_DAY]:
                    attendance_status = ATD_STATUS_FHALF_ABSENT

                if (attendance_rec.check_out_status in [OUT_STATUS_EE_HALF_DAY]) or (attendance_rec.check_in and not attendance_rec.check_out):
                    attendance_status = ATD_STATUS_SHALF_ABSENT

                if attendance_rec.check_in_status in [IN_STATUS_LE_FULL_DAY] \
                        or (attendance_rec.check_in_status in [IN_STATUS_LE_HALF_DAY] \
                            and (attendance_rec.check_out_status in [OUT_STATUS_EE_HALF_DAY] or not attendance_rec.check_out)):
                    attendance_status = ATD_STATUS_ABSENT

            # print('------------inside state change ------------------')
            attendance_rec.state = attendance_status

    @api.depends('leave_status')
    def _compute_leave_day_value(self):
        for attendance_rec in self:
            if attendance_rec.leave_status:
                attendance_rec.leave_day_value = 0.5 if attendance_rec.leave_status in [LEAVE_STS_FHALF, LEAVE_STS_SHALF] else 1
            else:
                attendance_rec.leave_day_value = 0

    @api.depends('leave_status', 'state', 'leave_day_value')
    def _compute_payroll_day_value(self):
        for attendance_rec in self:
            payroll_day_value = 1
            if attendance_rec.day_status in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]:
                if attendance_rec.state in [ATD_STATUS_ABSENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT]:
                    if attendance_rec.state == ATD_STATUS_ABSENT:
                        payroll_day_value = 0
                    elif attendance_rec.state in [ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT]:
                        payroll_day_value = 0.5

                    if attendance_rec.leave_day_value:
                        payroll_day_value += attendance_rec.leave_day_value

            attendance_rec.payroll_day_value = 1 if payroll_day_value >= 1 else payroll_day_value

    @api.depends('employee_id.date_of_joining', 'employee_id.last_working_day')
    def _compute_valid_working_day(self):
        for attendance_rec in self:
            valid_day = True
            if attendance_rec.employee_id.date_of_joining and attendance_rec.attendance_recorded_date < attendance_rec.employee_id.date_of_joining:
                valid_day = False
            if not attendance_rec.employee_id.active and attendance_rec.employee_id.last_working_day \
                    and attendance_rec.attendance_recorded_date > attendance_rec.employee_id.last_working_day:
                valid_day = False

            attendance_rec.is_valid_working_day = valid_day

    @api.multi
    def _compute_check_in_through(self):
        for attd in self:
            if attd.check_in:
                attd.check_in_through = str(attd.check_in_mode)
            else:
                attd.check_in_through = False

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record    
            @return: returns a id of new record
        """
        employee_id = values.get('employee_id', False)
        if employee_id and (not values.get('branch_id') or not values.get('department_id')):
            emp_rec = self.env['hr.employee'].browse(employee_id)
            values.update({'department_id': emp_rec.department_id.id})
            try:
                values.update({'branch_id': emp_rec.job_branch_id.id,
                               'division_id': emp_rec.division.id,
                               'section_id': emp_rec.section.id,
                               'practice_id': emp_rec.practise.id})
            except Exception as e:
                # print(str(e))
                pass

        result = super(DailyHrAttendance, self).create(values)

        return result

    @api.multi
    def write(self, values):
        if values.get('check_in') or values.get('check_out'):
            values.update({'kw_sync_status': False})

        result = super(DailyHrAttendance, self).write(values)

        return result

    # #method to get the employee shift and office hour details as per shift/flexi/Roaster
    def _get_employee_shift(self, employee, check_in_time):
        """
        get the detail shift information (regular/roaster/flexi)
        @param values: provides attendance time / resource working hours

        @return: returns [shift_type,work_hours,roaster_shift_rec,shift record, shift in time, shift out time]
        """
        try:
            roaster_shift = self._get_employee_roaster_shift(employee.id, check_in_time)
            flexi_shift = self._get_employee_flexi_shift(employee.id, check_in_time)

            employee_shift = employee.resource_calendar_id

            timezone = pytz.timezone(employee.tz or employee.resource_calendar_id.tz or 'UTC')
            start_dt = datetime.combine(check_in_time, resource.float_to_time(0.0))
            end_dt = datetime.combine(check_in_time, resource.float_to_time(23.98))
            attendance_intervals = False
            shift_type = 'default'  # #regular shift

            if roaster_shift:
                employee_shift = roaster_shift.shift_id
                shift_type = 'roster'  ##roaster shift
                attendance_intervals = employee_shift.with_context(employee_id=employee.id)._attendance_intervals(start_dt.replace(tzinfo=timezone), end_dt.replace(tzinfo=timezone), resource=None)

            if flexi_shift:
                attendance_intervals = flexi_shift.with_context(employee_id=employee.id)._attendance_intervals(start_dt.replace(tzinfo=timezone), end_dt.replace(tzinfo=timezone), resource=None)

                if attendance_intervals:
                    employee_shift = flexi_shift
                    shift_type = 'flexi'  # #flexi shift

            if not attendance_intervals:
                # #Check employee shift change history and effective date
                employee_shift = self._get_employee_assigned_shift(employee, check_in_time)

                attendance_intervals = employee_shift.with_context(employee_id=employee.id)._attendance_intervals(start_dt.replace(tzinfo=timezone), end_dt.replace(tzinfo=timezone), resource=None)

            all_ofc_hours = self.env['resource.calendar.attendance']
            exceptional_ofc_hours = self.env['resource.calendar.attendance']
            regular_ofc_hours = self.env['resource.calendar.attendance']

            for _, _, rec in attendance_intervals:
                all_ofc_hours |= rec

            # print(all_ofc_hours)

            exceptional_ofc_hours = all_ofc_hours.filtered(lambda rec: rec.date_from and rec.date_to)
            regular_ofc_hours = all_ofc_hours.filtered(lambda rec: not rec.date_from)

            ofc_hours = exceptional_ofc_hours if exceptional_ofc_hours else regular_ofc_hours
            shift_inout_info = self._get_shift_in_out_time(ofc_hours)

            default_shift_name = ''
            if shift_type == 'flexi':
                # #Check employee shift change history and effective date
                employee_shift = self._get_employee_assigned_shift(employee, check_in_time)
                default_shift_name = employee_shift.name + '-Flexi Time' if employee_shift else ''

            # print(employee.name,shift_inout_info)
        # try:
            shift_name = default_shift_name if default_shift_name else shift_inout_info[0].name
        except Exception:
            shift_name = ''
            ofc_hours = ''
            shift_inout_info = []
            pass

        return [shift_type, ofc_hours, roaster_shift if roaster_shift else False] + shift_inout_info + [shift_name]

    # #method to return the flexi shift of employee
    def _get_employee_flexi_shift(self, employee_id, search_date):
        search_date = search_date.strftime("%Y-%m-%d")
        return self.env['resource.calendar'].search(
            [('employee_id', '=', employee_id), ('start_date', '<=', search_date), ('end_date', '>=', search_date),('state','=','approved')],
            limit=1)

    # #method to return the roaster shift of employee
    def _get_employee_roaster_shift(self, employee_id, search_date):
        search_date = search_date.strftime("%Y-%m-%d")
        return self.env['kw_employee_roaster_shift'].search(
            [('employee_id', '=', employee_id), ('date', '=', search_date)], limit=1)

    # #method to return employee current shift as per the given date
    def _get_employee_assigned_shift(self, employee_id, search_ref_date):
        # print(search_date,employee_id)
        search_date = search_ref_date
        if employee_id.effective_from and employee_id.effective_from <= search_date:
            return employee_id.resource_calendar_id
        else:
            emp_history_log = self.env['kw_attendance_shift_log'].search(
                [('employee_id', '=', employee_id.id), ('effective_from', '<=', search_date),
                 ('effective_to', '>=', search_date)], order='effective_from desc', limit=1)

            # print(emp_history_log)
            return emp_history_log.shift_id if emp_history_log else employee_id.resource_calendar_id

    # # method to get the shift information ,as per the shift type
    def _get_shift_in_out_time(self, ofc_hours):
        """
        get the shift in/out time as per the cross shift/normal shift type
        @param values: provides attendance time / resource working hours

        @return: returns [shift record, shift in time, shift out time]
        """
        day_shift, shift_in_time, shift_out_time, shift_second_half_time = None, None, None, None
        if ofc_hours:
            day_shift = ofc_hours.mapped('calendar_id')[0]
            shift_second_half_time     = max(ofc_hours.filtered(lambda rec: rec.day_period == 'afternoon').mapped('hour_from')) if ofc_hours.filtered(lambda rec: rec.day_period == 'afternoon') else None

            if day_shift.cross_shift:
                shift_in_time = max(ofc_hours.mapped('hour_from'))
                shift_out_time = min(ofc_hours.mapped('hour_to'))
            else:
                shift_in_time = min(ofc_hours.mapped('hour_from'))
                shift_out_time = max(ofc_hours.mapped('hour_to'))

        return [day_shift,shift_in_time,shift_out_time,shift_second_half_time]

    @api.model
    def _get_date_formats(self):
        """ get current date and time format, according to the context lang
            :return: a tuple with (format date, format time)
        """
        lang = self._context.get("lang")
        lang_params = {}
        if lang:
            record_lang = self.env['res.lang'].search([("code", "=", lang)], limit=1)
            lang_params = {
                'date_format': record_lang.date_format,
                'time_format': record_lang.time_format
            }

        # formats will be used for str{f,p}time() which do not support unicode in Python 2, coerce to str
        format_date = pycompat.to_native(lang_params.get("date_format", '%B-%d-%Y'))
        format_time = pycompat.to_native(lang_params.get("time_format", '%I-%M %p'))
        return (format_date, format_time)

    @api.model
    def get_current_user_office_time_details(self):
        """a method to get logged in user/employee attendance details of current shift
        
        """
        employee_id = self.env.user.employee_ids
        emp_tz = employee_id.tz or employee_id.resource_calendar_id.tz or 'UTC'
        emp_timezone = pytz.timezone(emp_tz)

        attendance_date, emp_atd_record, _ = self.get_attendance_date_from_time(datetime.now(), employee_id)
        # emp_day_status = emp_atd_record and emp_atd_record.day_status or self._compute_day_status(employee_id,attendance_date)[0]
        portal_mode = employee_id.attendance_mode_ids.filtered(lambda r: r.alias == ATD_MODE_PORTAL)
        portal_mode_atd_enable = 1 if (not employee_id.no_attendance and portal_mode) or employee_id.no_attendance else 0
        working_hours = '--'

        quote_object = self.env['kw_attendance_quotes']
        current_date = datetime.now().date()

        quotes = quote_object.search([('from_date', '<=', current_date), ('to_date', '>=', current_date)])
        if not quotes:
            current_day_name = (calendar.day_name[datetime.now().weekday()]).lower()
            quotes = quote_object.search([(current_day_name, '=', True)])
        if not quotes:
            quotes = self.env['kw_attendance_quotes'].search([])
        # quote = quotes and random.choice(quotes.mapped('name')) or "Always Deliver More Than Expected"
        quote = quotes and secrets.choice(quotes.mapped('name')) or "Always Deliver More Than Expected"

        if emp_atd_record and emp_atd_record.check_in:
            if emp_atd_record.day_status in [DAY_STATUS_WORKING,DAY_STATUS_RWORKING]:

                end_datetime = emp_atd_record.check_out if emp_atd_record.check_out else datetime.now()
                worked_hour_in_sec = (end_datetime - emp_atd_record.check_in).total_seconds()

                if worked_hour_in_sec > 0:
                    rest_time_in_sec = 0
                    if emp_atd_record.lunch_in and emp_atd_record.lunch_out:
                        rest_time_in_sec = (emp_atd_record.lunch_in - emp_atd_record.lunch_out).total_seconds()
                    elif emp_atd_record.shift_second_half_time or emp_atd_record.check_out:
                        emp_cur_time_tz           = end_datetime.astimezone(emp_timezone)    # emp_atd_record.employee_id.get_employee_tz_today()
                        half_start_datetime       = datetime.combine(attendance_date,resource.float_to_time(emp_atd_record.shift_second_half_time))
                        rest_time_in_sec          = float_time_to_seconds(emp_atd_record.shift_rest_time)

                        if emp_cur_time_tz.replace(tzinfo=None) >= half_start_datetime:
                            worked_hour_in_sec    = worked_hour_in_sec-rest_time_in_sec

                    factor = 1 if worked_hour_in_sec > 0 else -1
                    min, sec = divmod(worked_hour_in_sec * factor, 60)
                    hr, mn = divmod(int(min), 60)
                    working_hours = "%02dh %02dm %02ds" % (hr, mn, sec) if factor > 0 else "- %02dh %02dm %02ds" % (hr, mn, sec)

        data = {'employee_id': employee_id.id,
                'employee_name': employee_id.name,
                'designation': employee_id.job_id.name,
                'department': employee_id.department_id.name,
                'date': datetime.strftime(attendance_date, '%d %b %Y'),
                'day': datetime.strftime(attendance_date, '%A'),
                'check_in': datetime.strftime(emp_atd_record.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone),
                                              "%I:%M:%S %p") if emp_atd_record.check_in else '',
                'check_out': datetime.strftime(
                    emp_atd_record.check_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone),
                    "%I:%M:%S %p") if emp_atd_record.check_out else '',
                'portal_mode': portal_mode_atd_enable,
                'lunch_in_time': datetime.strftime(
                    emp_atd_record.lunch_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone),
                    "%I:%M:%S %p") if emp_atd_record.lunch_in else '',
                'lunch_out_time': datetime.strftime(
                    emp_atd_record.lunch_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone),
                    "%I:%M:%S %p") if emp_atd_record.lunch_out else '',
                'attendance_rec': emp_atd_record,
                'attendance_rec_id': emp_atd_record.id,
                'working_hour': working_hours,
                # 'le_url'            :le_url,
                # 'user_redirect_urls':enc_uid_user_activities if enc_uid_user_activities else '',
                'error_msg': '',
                'quote': quote
                }
        return data

    @api.model
    def update_myoffice_time(self, args):
        """method to update check-in, check-out , lunch-in and out options through portal by clicking on the options"""
        update_status = args.get('update_status', False)
        attendance_log = self.env['hr.attendance']

        if update_status == 'check_in':
            portal_mode = self.env.user.employee_ids.attendance_mode_ids.filtered(lambda r: r.alias == ATD_MODE_PORTAL)
            if portal_mode:
                attendance_log.employee_check_in(self.env.user.employee_ids.id, 0)

            else:
                raise ValidationError("Sorry, your office-in time can not be recorded through portal.")
        else:
            office_info = self.get_current_user_office_time_details()
            attendance_rec  = office_info['attendance_rec']
            # print(office_info)
            # print(attendance_rec.attendance_recorded_date)

            if attendance_rec and attendance_rec.check_in:

                if update_status == 'lunch_out':
                    attendance_rec.lunch_out = datetime.now()

                elif update_status == 'lunch_in':
                    if not attendance_rec.lunch_out:
                        raise ValidationError("Lunch-out time should be updated first.")
                    if attendance_rec.lunch_out > datetime.now():
                        raise ValidationError("Lunch-in time should be greater than lunch-out time.")
                    attendance_rec.lunch_in = datetime.now()

                elif update_status == 'check_out':
                    if office_info['portal_mode']:
                        if not attendance_rec.check_in or not attendance_rec.check_in < datetime.now():
                            raise ValidationError("Office-in time should be updated first and it should be less than office-out time.")
                        else:
                            # emp_record.check_out = datetime.now()
                            today = datetime.now().date()
                            yesterday_date = today - timedelta(days=1)
                            latest_log_rec = attendance_log.search(
                                [('employee_id', '=', attendance_rec.employee_id.id), ('check_in_mode', '=', 0)],
                                limit=1)
                            if latest_log_rec and latest_log_rec.check_in and latest_log_rec.check_in.date() in [today,yesterday_date] and latest_log_rec.check_in < datetime.now() and not latest_log_rec.check_out:
                                latest_log_rec.sudo(self.env.user.id).write(
                                    {'check_out': datetime.now(), 'out_ip_address': request.httprequest.remote_addr})
                            else:
                                attendance_log.employee_check_in(attendance_rec.employee_id.id)
                            # attendance_log.employee_check_out(self.env.user.id)

                    else:
                        raise ValidationError("Sorry, your office out time can not be recorded through portal.")
            else:
                raise ValidationError("Attendance details are not available for today.")

    def _compute_day_status(self, employee_id, attendance_recorded_date):
        """
          @params  : employee record set, attendance_date
          @returns : day status,rest_hour
        """
        
        shift_info = self._get_employee_shift(employee_id, attendance_recorded_date)
        if shift_info:
            # print(ofc_hours.mapped('id'))  
            shift_type = shift_info[0]  # #default/flexi/roaster
            roaster_shift = shift_info[2]
            ofc_hours = shift_info[1]

            shift_id = shift_info[3]
            shift_in_time = shift_info[4]
            shift_out_time = shift_info[5]
            shift_second_half_time = shift_info[6]
            shift_rest_time = max(ofc_hours.mapped('rest_time')) if ofc_hours else 0.0
            shift_name = shift_info[7]
            # ##day status
            if shift_type == 'roster' or roaster_shift:
                day_status = DAY_STATUS_RHOLIDAY if roaster_shift.week_off_status else DAY_STATUS_RWORKING  # 3, roster working day, 4: roaster week off
            else:

                day_status = DAY_STATUS_WORKING
                timezone = pytz.timezone(employee_id.tz or 'UTC')
                # #time range should be from 0-23.98 else for cross shift it will not work
                naive_in_datetime = datetime.combine(attendance_recorded_date, resource.float_to_time(0.0))
                naive_out_datetime = datetime.combine(attendance_recorded_date, resource.float_to_time(23.98))

                # #check if the shift is flexi:: if flexi shift then get the work intervals from employee's default shift
                work_shift_employee = shift_id
                if work_shift_employee and work_shift_employee.employee_id:
                    work_shift_employee = employee_id.resource_calendar_id
                    
                leave_intervals = work_shift_employee.with_context(employee_id=employee_id.id)._leave_intervals(
                    naive_in_datetime.replace(tzinfo=timezone), naive_out_datetime.replace(tzinfo=timezone),
                    resource=None, domain=None) if work_shift_employee else Intervals([])
                
                attendance_intervals = work_shift_employee.with_context(employee_id=employee_id.id)._attendance_intervals(
                    naive_in_datetime.replace(tzinfo=timezone), naive_out_datetime.replace(tzinfo=timezone),
                    resource=None) if work_shift_employee else Intervals([])
                
                work_interval = attendance_intervals - leave_intervals
                
                # #if there are no working attendance record found then holiday
                if len(work_interval) == 0:
                    
                    holiday_intervals = leave_intervals & attendance_intervals
                    week_off_status = 0
                    holiday_status = 0
                    for fdt, tdt, holiday_rec in holiday_intervals:
                        # #if it is an instance of global leaves and the holiday type is week off
                        for h_rec in holiday_rec:
                            if isinstance(h_rec.id, int):
                                if h_rec.holiday_type == '1':
                                    week_off_status = 1
                                else:
                                    holiday_status = 1
                            else:
                                holiday_status = 1
                                
                    day_status = DAY_STATUS_HOLIDAY if holiday_status else DAY_STATUS_WEEKOFF
                elif work_shift_employee and work_shift_employee.cross_shift:
                    # check if employee has week off today
                    current_day_week_off = self.env['resource.calendar.leaves'].search([('calendar_id','=',work_shift_employee.id),('start_date','=',attendance_recorded_date),('time_type','=','leave'),('resource_id','=',False)])
                    if current_day_week_off:
                        day_status = DAY_STATUS_WEEKOFF
            return [day_status, shift_rest_time, shift_id, shift_in_time, shift_out_time, shift_second_half_time, shift_name]

        return False

    # # method to recompute the daily attendance fields of the employees
    def recompute_employee_daily_attendance(self):
       
        """
            recompute the daily attendance data of each employee
            -   checks if roaster assigned
            -   checks if flexi assigned
            -   checks if exceptional office hours assigned
            -   checks if holiday exists
             
            -   checks if shift changed
            -   checks if attendance mode changed

            ** Assumptions
            -   Default Working/shift hours does not change
            -   Grace Period & Other Timings (EE,LE,ELE etc) does not change
            ** It will consider the latest info same for all days
        """
        daily_attendance = self.env['kw_daily_employee_attendance']
        # all_employees         = self.env['hr.employee'].search([])

        start_date, end_date, _ = self._get_recompute_date_range_configs(end_date=datetime.today().date())
        error_log, update_record_log = '', ''
        if end_date > start_date:
            # print("start:attendance recomputation ---",start_date,end_date)
            for day in range(int((end_date - start_date).days)+1):

                attendance_date = start_date + timedelta(day)
                employee_attendance_data = daily_attendance.search([('attendance_recorded_date', '=', attendance_date)])

                for emp_attendance_rec in employee_attendance_data:

                    # #check shift details
                    # shift_info    = self._get_employee_shift(emp_attendance_rec.employee_id,emp_attendance_rec.attendance_recorded_date)
                    employee_status = False  # emp_attendance_rec.employee_status
                    try:
                        if emp_attendance_rec.employee_id.date_of_joining and (emp_attendance_rec.attendance_recorded_date == emp_attendance_rec.employee_id.date_of_joining):
                            employee_status = EMP_STS_NEW_JOINEE

                        if not emp_attendance_rec.employee_id.active and emp_attendance_rec.employee_id.last_working_day and emp_attendance_rec.attendance_recorded_date == emp_attendance_rec.employee_id.last_working_day:
                            employee_status = EMP_STS_EXEMP

                        if not employee_status and emp_attendance_rec.attendance_recorded_date > emp_attendance_rec.employee_id.date_of_joining:
                            employee_status = EMP_STS_NORMAL

                        if not emp_attendance_rec.employee_id.active and emp_attendance_rec.employee_id.last_working_day and emp_attendance_rec.attendance_recorded_date > emp_attendance_rec.employee_id.last_working_day:
                            employee_status = False

                    except Exception as e:
                        # print(str(e))
                        continue
                    shift_info = []
                    try:
                        shift_info = self._compute_day_status(emp_attendance_rec.employee_id,emp_attendance_rec.attendance_recorded_date)
                        if shift_info :
                            emp_shift_id = shift_info[2].id if shift_info[2] else False
                            shift_second_half_time = shift_info[5] if shift_info[5] else 0
                            emp_shift_name = shift_info[6] if shift_info[6] else shift_info[2].name
                            attendance_status = emp_attendance_rec.state
                            # get work mode from WFH module 23-Feb-2021 (Gouranga)
                            work_mode = self.get_employee_work_mode(emp_attendance_rec.employee_id.id, emp_attendance_rec.attendance_recorded_date)
                            if (shift_info[0] in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]) and (emp_attendance_rec.check_in and not emp_attendance_rec.check_out):
                                attendance_status = ATD_STATUS_SHALF_ABSENT

                                if emp_attendance_rec.check_in_status in [IN_STATUS_LE_HALF_DAY]:
                                    attendance_status = ATD_STATUS_ABSENT

                            # added work mode from wfh module (23 Feb 2021) (Gouranga)
                            if emp_attendance_rec.work_mode != work_mode or emp_attendance_rec.day_status != shift_info[0] \
                                    or emp_attendance_rec.shift_id.id != emp_shift_id or emp_attendance_rec.shift_name != emp_shift_name \
                                    or emp_attendance_rec.shift_rest_time != shift_info[1] or emp_attendance_rec.shift_in_time != shift_info[3] \
                                    or emp_attendance_rec.shift_out_time != shift_info[4] or emp_attendance_rec.shift_second_half_time != shift_second_half_time \
                                    or emp_attendance_rec.employee_status != employee_status or emp_attendance_rec.state != attendance_status:
                                emp_attendance_rec.write({'day_status': shift_info[0],
                                                          'shift_id': emp_shift_id,
                                                          'shift_name': emp_shift_name,
                                                          'work_mode': work_mode,
                                                          'shift_rest_time': shift_info[1],
                                                          'shift_in_time': shift_info[3],
                                                          'shift_out_time': shift_info[4],
                                                          'shift_second_half_time': shift_second_half_time,
                                                          'employee_status': employee_status})
                                                          
                                # update_query = f"""update kw_daily_employee_attendance set
                                #                 day_status = '{shift_info[0]}',
                                #                 shift_id = {emp_shift_id},
                                #                 shift_name = '{emp_shift_name}',
                                #                 work_mode = '{work_mode}',
                                #                 shift_rest_time = {shift_info[1]},
                                #                 shift_in_time = {shift_info[3]},
                                #                 shift_out_time = {shift_info[4]},
                                #                 shift_second_half_time = {shift_second_half_time},
                                #                 employee_status = {employee_status} where id = {emp_attendance_rec.id}"""
                                # # print("update query is--->",update_query)
                                # self._cr.execute(update_query)
                                update_record_log += "## start_rec## \nRecomputation of date :\t%s\t Employee:\t%s ## end_rec##" % (attendance_date, emp_attendance_rec.employee_id.name)

                    except Exception as e:
                        logging.exception("message")

                        error_log +="\nError while recomputing daily attendance record of date :\t%s\t Employee:\t%s\nday_status:\t%s, shift_id:\t%s, shift_name:\t%s, shift_rest_time:\t%s, shift_in_time:\t%s, shift_out_time:\t%s\nError Msg:\t%s"%( attendance_date, emp_attendance_rec.employee_id.name,shift_info[0] if shift_info else False,shift_info[2].id if shift_info and shift_info[2] else False,shift_info[2].name if shift_info and shift_info[2] else False,shift_info[1] if shift_info else False,shift_info[3] if shift_info else False,shift_info[4] if shift_info else False,str(e))
                        continue
            # print("end:attendance recomputation ---",start_date,end_date)

        # #insert into log table -- and if error log exists send mail to configured email-id
        # if error_log :
        try:
            self.env['kw_kwantify_integration_log'].sudo().create(
                {'name': 'Daily Attendance Employee Data Recomputation',
                 'error_log': error_log,
                 'update_record_log': update_record_log, })
        except Exception as e:
            logging.exception("message")
            pass

    # #create daily attendance record for pay roll as per the log-in & log-out
    def create_daily_attendance(self, attendance_log_records, mode):
        """ ## get the attendance date from record
            ## if no cross shift then normal flow
            ## if cross shift current date or previous date, then conditions applied
            ## modification of log datetime range consideration as per the employee timezone
        """
        attendance_log_records.ensure_one()

        atd_employee_id = attendance_log_records.employee_id
        emp_tz = atd_employee_id.tz or atd_employee_id.resource_calendar_id.tz or 'UTC'
        emp_timezone = pytz.timezone(emp_tz)


        attendance_date_time = attendance_log_records.check_out if mode == 'check_out' and attendance_log_records.check_out else attendance_log_records.check_in

        # #get the attendance date as per the timezone and shift info for which the calculations are to be made
        cur_attendance_date, emp_atd_record, current_day_shift_info = self.get_attendance_date_from_time(attendance_date_time, atd_employee_id)

        # #calculate the rest as per the current attendance date
        if not current_day_shift_info:
            current_day_shift_info = self._get_employee_shift(atd_employee_id, cur_attendance_date)

        current_day_shift, curr_shift_in_time, curr_shift_out_time, curr_shift_second_half_time, curr_shift_name = \
            current_day_shift_info[3], current_day_shift_info[4], current_day_shift_info[5], current_day_shift_info[6], \
            current_day_shift_info[7]

        if current_day_shift and current_day_shift.cross_shift:

            previous_day = cur_attendance_date - timedelta(days=1)
            previous_day_shift_info = self._get_employee_shift(atd_employee_id, previous_day)

            previous_day_shift, previous_shift_out_time = previous_day_shift_info[3], previous_day_shift_info[5]

            prev_naive_out_datetime = datetime.combine(cur_attendance_date, resource.float_to_time(previous_shift_out_time)) if previous_day_shift.cross_shift else datetime.combine(previous_day, resource.float_to_time(previous_shift_out_time))

            prev_naive_extra_late_exit_time = emp_timezone.localize(prev_naive_out_datetime + relativedelta(seconds=+float_time_to_seconds(previous_day_shift.extra_late_exit_time))).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)

            curr_naive_out_datetime = datetime.combine(cur_attendance_date + timedelta(days=1), resource.float_to_time(curr_shift_out_time))

            curr_naive_extra_late_exit_time = emp_timezone.localize(curr_naive_out_datetime + relativedelta(seconds=+float_time_to_seconds(current_day_shift.extra_late_exit_time))).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)
            # print(cur_attendance_date)

            # #create daily attendance record from log
            self.create_attendance_from_log(emp_atd_record, atd_employee_id, current_day_shift, curr_shift_in_time,
                                            curr_shift_out_time, cur_attendance_date, prev_naive_extra_late_exit_time,
                                            curr_naive_extra_late_exit_time, curr_shift_second_half_time,
                                            curr_shift_name)

        else:

            start_attendance_date_emp = emp_timezone.localize(datetime.combine(cur_attendance_date, time(0, 0, 0))).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)
            end_attendance_date_emp = emp_timezone.localize(datetime.combine(cur_attendance_date, time(23, 59, 59))).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)

            # #create daily attendance record from log
            self.create_attendance_from_log(emp_atd_record, atd_employee_id, current_day_shift, curr_shift_in_time,
                                            curr_shift_out_time, cur_attendance_date, start_attendance_date_emp,
                                            end_attendance_date_emp, curr_shift_second_half_time, curr_shift_name)

    def create_attendance_from_log(self, emp_atd_record, atd_employee_id, current_day_shift, curr_shift_in_time,
                                   curr_shift_out_time, attendance_date, start_attendance_datetime,
                                   end_attendance_datetime, curr_shift_second_half_time, curr_shift_name):
        """create daily attendance records from the start and end time duration of employee for the requested date
            modified the existing logic to fix bugs on 17th sep 2020
        """
        attendance_logs = self.env['hr.attendance'].search(
            ['&',
             '&', ('mode_enabled', '=', True), ('employee_id', '=', atd_employee_id.id),
             '|',
             '&', ('check_in', '>=', start_attendance_datetime), ('check_in', '<=', end_attendance_datetime),
             '&', ('check_out', '>=', start_attendance_datetime), ('check_out', '<=', end_attendance_datetime)])

        if attendance_logs:
            emp_tz = atd_employee_id.tz or atd_employee_id.resource_calendar_id.tz or 'UTC'

            all_valid_check_ins = attendance_logs.filtered(lambda rec: rec.check_in >= start_attendance_datetime).mapped('check_in')
            all_valid_check_outs = attendance_logs.filtered(lambda rec: rec.check_out != False and rec.check_out <= end_attendance_datetime).mapped('check_out')

            all_valid_times = all_valid_check_ins + all_valid_check_outs
            first_check_in = min(all_valid_times) if all_valid_times else False
            last_check_out = max(all_valid_times) if all_valid_times and len(all_valid_times) > 1 else False

            # #START:: get check-in and check-out mode details , modified by : Gaurang, Modified on : 19-Feb-2021
            first_check_in_rec = attendance_logs.filtered(lambda r: r.check_in == first_check_in or r.check_out == first_check_in)
            last_check_out_rec = attendance_logs.filtered(lambda r: r.check_in == last_check_out or r.check_out == last_check_out)
            first_check_in_mode = first_check_in_rec and first_check_in_rec[0].check_in_mode or 0
            last_check_out_mode = last_check_out_rec and last_check_out_rec[0].check_in_mode or 0

            # work_mode            =  WFO_STATUS if attendance_logs.filtered(lambda rec:rec.check_in_mode ==1) else WFH_STATUS            
            # #END:: get check-in and check-out mode details

            # #if previous day record exists then update the  check-out
            if emp_atd_record:
                emp_atd_record.write({'check_in': first_check_in,
                                      'check_out': last_check_out,
                                      'check_in_mode': first_check_in_mode,
                                      'check_out_mode': last_check_out_mode,
                                      'kw_sync_status': False})
            # #else insert a new one
            else:
                # #create yesterday's attendance
                if start_attendance_datetime <= first_check_in <= end_attendance_datetime:
                    self.env['kw_daily_employee_attendance'].create(
                        {'employee_id': atd_employee_id.id,
                         'shift_id': current_day_shift.id,
                         'shift_name': current_day_shift.name if not curr_shift_name else curr_shift_name,
                         'is_cross_shift': current_day_shift.cross_shift,
                         'shift_in_time': curr_shift_in_time,
                         'shift_out_time': curr_shift_out_time,
                         'attendance_recorded_date': attendance_date,
                         'check_in': first_check_in,
                         'check_out': last_check_out,
                         'check_in_mode': first_check_in_mode,
                         'check_out_mode': last_check_out_mode,
                         'tz': emp_tz,
                         'le_state': '0',
                         'shift_second_half_time': curr_shift_second_half_time,
                         'kw_sync_status': False})

    def get_attendance_date_from_time(self,attendance_date_time,atd_employee_id):
        """find attendance date as per the employee timezone and shift info
        
        """
        emp_tz = atd_employee_id.tz or atd_employee_id.resource_calendar_id.tz or 'UTC'
        emp_timezone = pytz.timezone(emp_tz)

        # #get attendance date as per the employee timezone
        attendance_date_emp = attendance_date_time.astimezone(emp_timezone).date()
        yesterday_date = attendance_date_emp - timedelta(days=1)

        yesterday_shift_info = self._get_employee_shift(atd_employee_id, yesterday_date)
        yesterday_shift = yesterday_shift_info[3]

        atd_records = self.env['kw_daily_employee_attendance'].search([('employee_id', '=', atd_employee_id.id),
                                                                       ('attendance_recorded_date', 'in', [attendance_date_emp, yesterday_date])])

        emp_atd_record = atd_records.filtered(lambda rec: rec.attendance_recorded_date == attendance_date_emp)
        cur_attendance_date = attendance_date_emp
        current_day_shift_info = []
        if yesterday_shift and yesterday_shift.cross_shift:

            yesterday_shift_out_time = yesterday_shift_info[5]
            # #out date time should be today
            yesterday_naive_out_datetime = datetime.strptime(attendance_date_emp.strftime("%Y-%m-%d")+' '+str(resource.float_to_time(yesterday_shift_out_time)),"%Y-%m-%d %H:%M:%S")
            yesterday_naive_extra_late_exit_time = emp_timezone.localize(yesterday_naive_out_datetime + relativedelta(seconds=+float_time_to_seconds(yesterday_shift.extra_late_exit_time))).replace(tzinfo=None)

            yesterday_attendance = atd_records.filtered(lambda rec: rec.attendance_recorded_date == yesterday_date)

            if attendance_date_time.astimezone(emp_timezone).replace(tzinfo=None) <= yesterday_naive_extra_late_exit_time:
                emp_atd_record = yesterday_attendance
                cur_attendance_date = yesterday_date
                current_day_shift_info = yesterday_shift_info

        return [cur_attendance_date, emp_atd_record, current_day_shift_info]

    # #method to share information with kwantify
    @api.model
    def call_share_attendance_info_with_kwantify(self, args):
        attendance_rec_id = args.get('attendance_rec_id', False)
        if attendance_rec_id:
            attendance_rec = self.env['kw_daily_employee_attendance'].browse(int(attendance_rec_id))
            attendance_rec.share_attendance_info_with_kwantify()

    # #method to check after log-in activities
    @api.model
    def check_after_log_in_activities(self, args):
        # print('called check_after_log_in_activities')
        """method to check after log-in activities"""
        attendance_rec_id = args.get('attendance_rec_id', False)
        # print("attendance id==",attendance_rec_id)
        if attendance_rec_id:
            config_parameter_obj = self.env["ir.config_parameter"].sudo()
            emp_atd_record = self.env['kw_daily_employee_attendance'].browse(int(attendance_rec_id))

            redirect_url, le_url, enc_uid_user_activities, epf_url, social_image_url = '', '', '', '', ''

            emp_attendance_modes = emp_atd_record.employee_id.attendance_mode_ids.mapped('alias') if emp_atd_record else []
            # print(attendance_rec_id, emp_attendance_modes, ATD_MODE_MANUAL)
            # if log-in details exist or manual attendance mode
            if (emp_atd_record and emp_atd_record.check_in) \
                    or (emp_atd_record and not emp_atd_record.check_in and ATD_MODE_MANUAL in emp_attendance_modes):
                late_entry_enabled = config_parameter_obj.get_param('kw_hr_attendance.late_entry_screen_enable')
                excluded_grade_ids = literal_eval(config_parameter_obj.get_param('kw_hr_attendance.attn_exclude_grade_ids','False'))
                enable_epf_status = config_parameter_obj.get_param('kw_epf.epf_status')

                epf_status, leave_status, is_on_tour = 0, False, False

                """STOP API call to V5 if odoo epf form is enabled"""
                if not enable_epf_status:
                    try:
                        # #get employee day status from kwantify
                        emp_day_status = emp_atd_record.employee_day_status_kwantify()
                        if 'EPFPopupOutput' in emp_day_status[0] and emp_day_status[0]['EPFPopupOutput'] == 1:
                            epf_status = 1
                        # if 'on_tour' in emp_day_status[0] and emp_day_status[0]['on_tour'] =='1':
                        #     is_on_tour   = True
                    except Exception as e:
                        pass

                # Start : Fetch tour of employee from tour module 1 April 2021 (Gouranga)
                atd_date = emp_atd_record.attendance_recorded_date
                # print(atd_date)
                try:
                    emp_on_tour = self.env['kw_tour'].sudo().search(
                        [('employee_id', '=', emp_atd_record.employee_id.id), ('state', '=', 'Finance Approved'),
                         ('date_travel', '<=', atd_date), ('date_return', '>=', atd_date)])
                    if emp_on_tour:
                        is_on_tour = True

                    if emp_atd_record.is_on_tour != is_on_tour:
                        emp_atd_record.write({'is_on_tour': is_on_tour})
                except Exception as e:
                    pass
                # End : Fetch tour of employee from tour module 1 April 2021 (Gouranga)

                # Start : Fetch Leave of employee from leave module 1 April 2021 (Nikunja Maharana)
                try:
                    leave_type_id = self.env['hr.leave'].sudo().search([
                        ('date_from', '<=', atd_date),
                        ('date_to', '>=', atd_date),
                        ('employee_id', '=', emp_atd_record.employee_id.id),
                        ('state', '=', 'validate'),
                    ])
                    # print(leave_type_id)
                    if leave_type_id:
                        for leave in leave_type_id:
                            data = self.attendance_leave_approval_update(leave,False)
                            # print(data)
                except Exception as e:
                    pass
                # End : Fetch Leave of employee from leave module 1 April 2021 (Nikunja Maharana)

                # if 'leave_info' in emp_day_status[0] and emp_day_status[0]['leave_info'][0]:

                #     if emp_day_status[0]['leave_info'][0]['all_day_leave']  == '1' or (emp_day_status[0]['leave_info'][0]['first_half_leave']  == '1' and emp_day_status[0]['leave_info'][0]['second_half_leave']  == '1'):
                #         leave_status = LEAVE_STS_ALL_DAY
                #     elif emp_day_status[0]['leave_info'][0]['first_half_leave']  == '1':
                #         leave_status = LEAVE_STS_FHALF
                #     elif emp_day_status[0]['leave_info'][0]['second_half_leave']  == '1':
                #         leave_status = LEAVE_STS_SHALF
                # update the attendance record tour and leave status if not updated
                    # update the attendance record tour and leave status if not updated
                # update the attendance record tour and leave status if not updated

                social_picture_enable_form = config_parameter_obj.get_param("social_picture_enable_form")
                employee_handbook_enable_form = config_parameter_obj.get_param("employee_handbook_enable_form")
                employee_certification_enable_form = config_parameter_obj.get_param("employee_certification_enable_form")
                enable_work_from_home_survey = config_parameter_obj.get_param('kw_surveys.enable_work_from_home_survey')
                interview_feedback_enabled = config_parameter_obj.sudo().get_param('kw_recruitment.interview_feedback_check')
                # if late entry enabled and LE & no LE reason & not in tour

                if late_entry_enabled and emp_atd_record.check_in \
                        and emp_atd_record.check_in_status in [IN_STATUS_LE, IN_STATUS_EXTRA_LE] \
                        and emp_atd_record.le_state in ['0', False] \
                        and emp_atd_record.late_entry_reason == False \
                        and not emp_atd_record.is_on_tour and emp_atd_record.employee_id.grade.id not in excluded_grade_ids:
                            
                    le_url = self.env['hr.attendance'].generate_le_url(emp_atd_record.attendance_recorded_date, emp_atd_record)
                    redirect_url = le_url

                if redirect_url == '' and enable_epf_status and self.env.user.employee_ids:
                    url = self.env['kw_epf'].check_pending_epf(self.env.user)
                    epf_url = url if url else ''
                    redirect_url = epf_url

                if redirect_url == '' and social_picture_enable_form == 'Yes':
                    social_image_url = self.env['kw_employee_social_image'].check_employee_social_image(self.env.user)
                    redirect_url = social_image_url
                # enable handbook form start
                # condition to run only on friday afternoon
                weekday = datetime.now().weekday()
                user_timezone = pytz.timezone(self.env.user.tz or 'UTC')
                current_time = datetime.strftime(datetime.now().replace(tzinfo=pytz.utc).astimezone(user_timezone), "%H")
                if redirect_url == '' and weekday == 4 and int(current_time) >= 12 \
                        and employee_handbook_enable_form == 'Yes':
                    current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                    # handbook which have auth login true and all view access
                    handbook_auth_login = self.env['kw_onboarding_handbook'].sudo().search(
                        [('auth_login', '=', True), ('view_access', '=', 'All')])
                    # handbook which have auth login true and specific view access
                    handbook_auth_login += self.env['kw_onboarding_handbook'].sudo().search(
                        [('auth_login', '=', True), ('view_access', '=', 'Specific'),
                         ('employee_ids', '=', current_employee.id)])
                    # handbook understood by employee
                    handbook_understood = self.env['kw_handbook'].sudo().search(
                        [('employee_id', '=', current_employee.id), ('handbook_id', 'in', handbook_auth_login.ids)])
                    handbook_auth_login -= handbook_understood.mapped('handbook_id')

                    if handbook_auth_login:
                        enable_handbook_url = self.env['kw_handbook']._get_employee_handbook_url(self.env.user)
                        redirect_url = enable_handbook_url
                # enable handbook form end

                day_list = [1, 2, 3, 4]
                current_day = date.today().day
                if current_day in day_list and redirect_url == '' and employee_certification_enable_form == 'Yes':
                    emp_certification_url = self.env['kw_update_employee_certification'].sudo()._get_employee_certfication_url(request.env.user)
                    redirect_url = emp_certification_url

                if redirect_url == '' and interview_feedback_enabled:
                    interview_feedback_url = self.env['survey.user_input'].check_pending_interview_feedback(request.env.user)
                    redirect_url = interview_feedback_url.get('url') if interview_feedback_url != '/web/' else interview_feedback_url

                if redirect_url == '' and enable_work_from_home_survey and self.env.user.employee_ids:
                    work_from_home_survey_url = self.env['kw_surveys_details']._give_feedback(self.env.user)
                    if work_from_home_survey_url:
                        redirect_url = work_from_home_survey_url

                enable_health_insurance_form = config_parameter_obj.get_param("payroll_inherit.enable_health_insurance_form")
                if redirect_url == '' and enable_health_insurance_form and self.env.user.employee_ids:
                    health_insurance_rec = self.env['health_insurance_dependant'].check_employee_health_insurance(self.env.user)
                    if not health_insurance_rec:
                        redirect_url = '/health-insurance-for-dependant'
                if redirect_url == '':
                    user_activities, enc_uid_user_activities = login_controller.after_login_user_actions(login_controller(), user=self.env.user, my_ofc_redirect=1, epf_status=epf_status)
                    # print(request.session)

                    if enc_uid_user_activities != '' \
                            and 'EPFPopupOutput' not in user_activities \
                            and 'work_from_home_survey_url' not in user_activities \
                            and 'skip_activities' in request.session \
                            and request.session['skip_activities'] == 1:
                        enc_uid_user_activities = ''
                    if len(user_activities) == 0:
                        dashboard_action_id = self.env.ref('ks_dashboard_ninja.board_dashboard_action_window').id
                        dashboard_menu_id = self.env.ref('ks_dashboard_ninja.board_menu_root').id
                        if dashboard_action_id and dashboard_menu_id:
                            redirect_url = f"/web?#action={dashboard_action_id}&menu_id={dashboard_menu_id}"

            data = {
                # 'le_url': le_url,
                # 'epf_url': epf_url,
                # 'img_url': social_image_url,
                'redirect_url': redirect_url,
                'user_redirect_urls': enc_uid_user_activities if enc_uid_user_activities else '',
            }
            return data

    @api.multi
    def share_attendance_info_with_kwantify(self):
        """method to call the share the attendance info with kwantify"""

        for attendance_rec in self:
            if not attendance_rec.kw_sync_status and attendance_rec.employee_id.kw_id:

                kw_server_tz = pytz.timezone(KWANTIFY_SERVER_TIMEZONE or 'UTC')
                kw_server_check_in = attendance_rec.check_in.astimezone(kw_server_tz).strftime("%Y-%m-%d %H:%M:%S") if attendance_rec.check_in else ''
                kw_server_check_out = attendance_rec.check_out.astimezone(kw_server_tz).strftime("%Y-%m-%d %H:%M:%S") if attendance_rec.check_out else ''

                json_params = {"employee_id": attendance_rec.employee_id.kw_id,
                               "attendance_date": attendance_rec.attendance_recorded_date.strftime("%Y-%m-%d"),
                               "check_in_date_time": kw_server_check_in,
                               "check_out_date_time": kw_server_check_out}
                # print(json_params)         
                try:
                    if kw_server_check_in != '' or kw_server_check_out != '':
                        resp_result = attendance_rec._call_attendance_web_service('employee_attendance', json_params)
                        # print(resp_result)
                        if resp_result and resp_result[0]['status'] == '200':
                            attendance_rec.kw_sync_status = True

                        return resp_result
                except Exception as e:
                    pass

    @api.multi
    def employee_day_status_kwantify(self):
        """method to call the employee day status with kwantify"""

        for attendance_rec in self:
            if attendance_rec.employee_id.kw_id:
                json_params = {"employee_id": attendance_rec.employee_id.kw_id,
                               "attendance_date": attendance_rec.attendance_recorded_date.strftime("%Y-%m-%d")}

                try:
                    resp_result = attendance_rec._call_attendance_web_service('employee_pending_activity_status', json_params)
                    # print(resp_result)                    
                    return resp_result
                except Exception as e:
                    pass
                    return {'status': 500, 'error_log': str(e)}
            else:
                return {'status': 500, 'error_log': 'employee id does not exists.'}

    def _call_attendance_web_service(self, method_name, json_params):
        """method to call the kwantify web service"""
        kwantify_atd_sync_url = self.env['ir.config_parameter'].sudo().get_param('kw_hr_attendance.kwantify_atd_sync_url') if method_name != 'employee_day_status' else 'https://kwportalservice.csmpl.com/OdooSynSVC.svc'
        if kwantify_atd_sync_url != '':
            kwantify_atd_sync_url = kwantify_atd_sync_url+'/'+method_name if method_name != '' else kwantify_atd_sync_url
            # print(kwantify_atd_sync_url)
            header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
            data = json.dumps(json_params)
            # print(data)

            try:
                resp_result = requests.post(kwantify_atd_sync_url, headers=header, data=data)
                # print(resp_result)
                resp = json.loads(resp_result.text)
                # print(resp)
                return resp
            except Exception as e:
                # print(e)
                return {'status': 500, 'error_log': str(e)}
        else:
            return {'status': 500, 'error_log': 'sync url does not exists.'}

    def _get_recompute_date_range_configs(self,end_date=datetime.today().date()):
        # end_date              = end_date
        curr_month = end_date.month
        # start date should be previous month 25th day
        config_param = self.env['ir.config_parameter'].sudo()
        recompute_previous_month = config_param.get_param('kw_hr_attendance.recompute_previous_month')
        recompute_start_day = config_param.get_param('kw_hr_attendance.recompute_start_day')
        recompute_start_day = int(recompute_start_day) if recompute_start_day else 1
        _, month_end_date = self.env['kw_late_attendance_summary_report']._get_month_range(end_date.year, curr_month)

        if recompute_previous_month and recompute_start_day:
            start_date = end_date.replace(day=int(recompute_start_day),
                                          month=curr_month - 1) if curr_month > 1 else end_date.replace(
                day=recompute_start_day, month=12, year=end_date.year - 1)

            payroll_end_date = month_end_date.replace(day=recompute_start_day)

        else:
            start_date = end_date.replace(day=recompute_start_day if recompute_start_day else 1, month=curr_month)
            payroll_end_date = month_end_date

        return start_date,end_date,payroll_end_date
    # Removed : 2 April 2021 (Gouranga) used for wfh 19 feb 2021

    # # method to update leave and tour status of daily attendance trasctions
    def update_daily_attendance_leave_tour_status(self):
        """
            update leave / tour status the daily attendance data of each employee
            -   checks if on tour
            -   checks if on leave
            -   checks if LWOP                       
        """
        daily_attendance = self.env['kw_daily_employee_attendance']
        start_date, end_date, _ = self._get_recompute_date_range_configs(end_date=datetime.today().date())
        error_log, update_record_log = [], []
        # print(start_date,end_date)
        if end_date > start_date:

            # #""" call the .net web service for leave /tour status update with a date range"""

            try:
                json_params = {"from_date": start_date.strftime("%Y-%m-%d"), "to_date": end_date.strftime("%Y-%m-%d")}
                resp_result = self._call_attendance_web_service('employee_day_status', json_params)
                # print("resp result",resp_result)

                employee_kw_ids, date_list = [], []
                # emp_tour_dict = {} # {emp_id:{date:status}}
                if resp_result:
                    for emp_info in resp_result:
                        emp_kw_id = emp_info['employee_id']
                        employee_kw_ids.append(emp_kw_id)

                        formatted_date = datetime.strptime(emp_info['date'], '%d-%b-%Y').date()
                        date_list.append(formatted_date)

                        # tour_status = True if emp_info['on_tour'] == '1' else False

                        # if emp_kw_id in emp_tour_dict:
                        #     emp_tour_dict[emp_kw_id][formatted_date] = tour_status
                        # else:
                        #     emp_tour_dict[emp_kw_id] = {formatted_date:tour_status}

                    employee_attendance_data = daily_attendance.search([('employee_id.kw_id', 'in', employee_kw_ids), ('attendance_recorded_date', 'in', date_list)])
                    # print(employee_attendance_data)
                    for emp_info in resp_result:
                        emp_date = datetime.strptime(emp_info['date'], '%d-%b-%Y').date()
                        if emp_date < date(2021, 4, 1):
                            emp_record = employee_attendance_data.filtered(lambda rec: rec.employee_id.kw_id == int(emp_info['employee_id']) and rec.attendance_recorded_date == emp_date)

                            if emp_record:
                                # print(emp_record)
                                leave_status, is_lwop_leave = False, False
                                # is_on_tour, leave_status, is_lwop_leave = False, False, False

                                # if 'on_tour' in emp_info and emp_info['on_tour'] =='1':
                                #     is_on_tour   = True

                                if 'LWOP' in emp_info and emp_info['LWOP'] == 1:
                                    is_lwop_leave = True

                                if 'leave_info' in emp_info and emp_info['leave_info'][0]:
                                    if emp_info['leave_info'][0]['all_day_leave'] == '1' \
                                            or (emp_info['leave_info'][0]['first_half_leave'] == '1' and emp_info['leave_info'][0]['second_half_leave'] == '1'):
                                        leave_status = LEAVE_STS_ALL_DAY
                                    elif emp_info['leave_info'][0]['first_half_leave']  == '1':
                                        leave_status = LEAVE_STS_FHALF
                                    elif emp_info['leave_info'][0]['second_half_leave']  == '1':
                                        leave_status = LEAVE_STS_SHALF

                                # #"""update the attendance record tour and leave status if not updated """
                                # if emp_record.is_on_tour != is_on_tour or emp_record.leave_status != leave_status or emp_record.is_lwop_leave != is_lwop_leave:
                                if emp_record.leave_status != leave_status or emp_record.is_lwop_leave != is_lwop_leave:
                                    try:
                                        # print(emp_record.employee_id.name,emp_record.attendance_recorded_date)

                                        # if datetime.today().date() <= datetime.today().date().replace(day=6,month=2,year=2021):
                                        emp_record.write({'is_lwop_leave': is_lwop_leave, 'leave_status': leave_status})
                                        # else:
                                        #     emp_record.write({'is_lwop_leave':is_lwop_leave,'leave_status':leave_status})

                                        update_record_log.append("## start_rec## V5 leave status update of date :\t%s\t Employee:\t%s ## end_rec##" % (emp_record.attendance_recorded_date, emp_record.employee_id.name))
                                    except Exception as e:
                                        # print(str(e))
                                        error_log.append("\n %s, %s:\t%s"%(emp_record.employee_id.name, emp_record.attendance_recorded_date, str(e)))
                                        continue
                # # Nikunja - 31 Mar 2021
                try:
                    leave_data = self.env['hr.leave'].generate_days_with_from_and_to_date(start_date,end_date)
                    # print(leave_data)
                    for data in leave_data:
                        try:
                            self.attendance_leave_approval_update(data,leave_data)
                        except Exception as e:
                            # print(str(e))
                            error_log.append("\n %s, %s:\t%s" % (data.employee_id.name, data.id, str(e)))
                            continue
                except Exception as e:
                    # print(str(e))
                    error_log.append("\nError while updating V6 leave status \nError Msg:\t%s" % (str(e)))
                    pass
                # # Nikunja - 31 Mar 2021

                # #STRAT : code for new odoo Tour module integration
                # if datetime.today().date() > datetime.today().date().replace(day=6,month=2,year=2021):
                try:
                    tour_data = self.env['kw_tour'].get_tour_data(start_date,end_date)
                    tour_str = f"## Tour Request : get_tour_data({start_date},{end_date}) ## Request Date : {datetime.today().date()} ## Response :{tour_data}"
                    update_record_log.append(tour_str)
                    # Request and response from tour module stored in log 02-March-2021 (Gouranga)
                    # employees = self.env['hr.employee']
                    # tour_date_list = date_list.copy()

                    if tour_data:
                        # employees |= self.env['hr.employee'].browse(list(tour_data.keys()))
                        # tour_date_list += tour_data[next(iter(tour_data))]
                        employees = self.env['hr.employee'].browse(list(tour_data.keys()))
                        tour_date_list = list(tour_data[next(iter(tour_data))])

                        # if emp_tour_dict:
                        #     employees |= self.env['hr.employee'].search([('kw_id','in',employee_kw_ids)])

                        tour_attendance_records = daily_attendance.search(
                            [('employee_id', 'in', employees.ids), ('attendance_recorded_date', 'in', tour_date_list)])
                        for emp in employees:
                            # emp_dates = set(tour_data.get(emp.id,{})) |  set(emp_tour_dict.get(emp.kw_id,{}))

                            attendance_records = tour_attendance_records.filtered(lambda r: r.employee_id == emp and r.attendance_recorded_date in tour_date_list)

                            for emp_record in attendance_records:
                                attendance_date = emp_record.attendance_recorded_date

                                # emp_tour_status = False
                                # odoo_tour_status = v5_tour_status = False
                                emp_tour_status = tour_data[emp.id][attendance_date]

                                # if emp.id in tour_data and attendance_date in tour_data[emp.id]:
                                #     odoo_tour_status = tour_data[emp.id][attendance_date]

                                # if emp.kw_id in emp_tour_dict and attendance_date in emp_tour_dict[emp.kw_id]:
                                #     v5_tour_status = emp_tour_dict[emp.kw_id][attendance_date]

                                # if odoo_tour_status or v5_tour_status:
                                #     emp_tour_status = True

                                if emp_record.is_on_tour != emp_tour_status:
                                    try:
                                        # print(emp_record.employee_id.name,emp_record.attendance_recorded_date,emp_tour_status)
                                        emp_record.write({'is_on_tour': emp_tour_status})
                                        update_record_log.append("## start_rec## tour status  update of date : %s \t Employee:%s ## end_rec##" % (emp_record.attendance_recorded_date, emp_record.employee_id.name))
                                    except Exception as e:
                                        # print(str(e))
                                        error_log.append("\n %s, %s:\t%s" % (emp_record.employee_id.name, emp_record.attendance_recorded_date, str(e)))
                                        continue
                except Exception as tour_exception:
                    error_log.append(f"\nError while processing Tour data \nError Msg:{tour_exception}")
                    pass
                # #END : code for new odoo Tour module integration
                # Removed commented code for WFH 2 April 2021 (Gouranga)

            except Exception as e:
                # print(str(e))
                error_log.append("\nError while updating leave/tour/WFH status \nError Msg: %s"%(str(e)))
                pass

            # #insert into log table -- and if error log exists send mail to configured email-id
            # if error_log :
            try:
                self.env['kw_kwantify_integration_log'].sudo().create(
                    {'name': 'Attendance Employee update leave /tour/WFH status',
                     'error_log': str(error_log) if error_log else '',
                     'update_record_log': str(update_record_log) if update_record_log else '',
                     'request_params': str(json_params),
                     'response_result': resp_result if resp_result else []})
            except Exception as e:
                logging.exception("message")
                pass

    # #method to send reminder mail for absentee statements and late entry pending requests
    def attendance_reminder_mail_absentee_late_entry(self):
        """
            update leave /tour status the daily attendance data of each employee
            -   checks if pending late entry
            -   checks if absent     
            -   checks if pending attendance request      
        """
        daily_attendance = self.env['kw_daily_employee_attendance']
        emp_attendance_request = self.env['kw_employee_apply_attendance']

        config_param = self.env['ir.config_parameter'].sudo()
        reminder_mail_start_day = config_param.get_param('kw_hr_attendance.reminder_mail_start_day')
        reminder_mail_start_day = int(reminder_mail_start_day) if reminder_mail_start_day else 21
        notif_layout = "kwantify_theme.csm_mail_notification_light"
        # if reminder_mail_start_day and reminder_mail_start_day>0 :
        start_date, end_date, payroll_end_date = self._get_recompute_date_range_configs(end_date=datetime.today().date())
        curr_date = datetime.today().date()
        mail_start_date = curr_date.replace(day=reminder_mail_start_day)

        # _,end_date               = self.env['kw_late_attendance_summary_report']._get_month_range(curr_date.year,curr_date.month)
        end_date = payroll_end_date.replace(day=payroll_end_date.day - 1)
        # print(mail_start_date,payroll_end_date,end_date)

        if mail_start_date <= curr_date <= payroll_end_date:
            # ##"""send pending late-entry approval requests """
            pending_le_approval_record = daily_attendance.search(
                [('le_state', 'in', [LE_STATE_APPLY, LE_STATE_FORWARD]),
                 ('day_status', 'in', [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]),
                 ('attendance_recorded_date', '>=', start_date),
                 ('attendance_recorded_date', '<=', end_date),
                 ('attendance_recorded_date', '!=', curr_date),
                 ('le_forward_to.employement_type.code', '!=', 'O')], order="attendance_recorded_date asc")
            # print(pending_le_approval_record)
            pending_employee_list = pending_le_approval_record.mapped('le_forward_to')
            # print(pending_employee_list)

            for emp_rec in pending_employee_list:
                try:
                    request_list = []
                    pending_le_requests = pending_le_approval_record.filtered(lambda rec: rec.le_forward_to.id == emp_rec.id).sorted(key=lambda r: r.attendance_recorded_date)
                    # print(pending_le_requests)
                    if pending_le_requests:
                        request_list = pending_le_requests
                        # cc_list             = pending_le_requests.filtered(lambda rec: rec.employee_id.work_email != False).mapped('employee_id').mapped('work_email')

                        extra_params = {'to_mail': emp_rec.work_email,
                                        'emp_name': emp_rec.name,
                                        'emp_request_list': request_list}  # ,'cc_list':",".join(cc_list) if cc_list else False

                        self.env['hr.attendance'].attendance_send_custom_mail(res_id=pending_le_requests[0].id,
                                                                              notif_layout=notif_layout,
                                                                              template_layout="kw_hr_attendance.kw_pending_late_entry_approval_email_template",
                                                                              ctx_params=extra_params,
                                                                              description="Late Entry Approval")

                except Exception as e:
                    # print(str(e))
                    continue

            # ###"""send pending employee attendance approval requests """
            pending_attendance_approval_record = emp_attendance_request.search(
                [('state', 'in', ['2']),
                 ('attendance_date', '>=', start_date),
                 ('attendance_date', '<=', end_date),
                 ('attendance_date', '!=', curr_date),
                 ('action_taken_by.employement_type.code', '!=', 'O')], order="attendance_date asc")
            # print(pending_le_approval_record)
            pending_attendance_employee_list = pending_attendance_approval_record.mapped('action_taken_by')
            # print(pending_attendance_employee_list)

            for emp_rec in pending_attendance_employee_list:
                try:
                    atd_request_list = []
                    pending_atd_requests = pending_attendance_approval_record.filtered(
                        lambda rec: rec.action_taken_by.id == emp_rec.id).sorted(key=lambda r: r.attendance_date)
                    # print(pending_atd_requests)
                    if pending_atd_requests:
                        atd_request_list = pending_atd_requests
                        # cc_list             = pending_atd_requests.filtered(lambda rec: rec.employee_id.work_email != False).mapped('employee_id').mapped('work_email')

                        extra_params = {'atd_request_list': atd_request_list}  # ,'cc_list':",".join(cc_list) if cc_list else False
                        # print(atd_request_list[0])
                        self.env['hr.attendance'].attendance_send_custom_mail(res_id=atd_request_list[0].id,
                                                                              notif_layout=notif_layout,
                                                                              template_layout="kw_hr_attendance.kw_pending_attendance_request_approval_email_template",
                                                                              ctx_params=extra_params,
                                                                              description="Attendance Correction Request Approval")

                except Exception as e:
                    # print(str(e))
                    continue

            # #"""send absentee statements """
            absentee_record = daily_attendance.search([('payroll_day_value', '<', 1), ('is_on_tour', '=', False),
                                                       ('day_status', 'in', [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]),
                                                       ('attendance_recorded_date', '>=', start_date),
                                                       ('attendance_recorded_date', '<=', end_date),
                                                       ('attendance_recorded_date', '!=', curr_date),
                                                       ('employee_id.employement_type.code', '!=', 'O')],
                                                      order="attendance_recorded_date asc")
            absentee_employee_list = absentee_record.mapped('employee_id')
            # print('-----------------------------------------------------------')
            # print(absentee_employee_list)

            for emp_rec in absentee_employee_list:
                try:
                    if not emp_rec.no_attendance and emp_rec.parent_id is not False:
                        request_list = []
                        emp_absentee_records = absentee_record.filtered(lambda rec: rec.employee_id.id == emp_rec.id and emp_rec.date_of_joining and rec.attendance_recorded_date >= emp_rec.date_of_joining).sorted(key=lambda r: r.attendance_recorded_date)
                        if not emp_rec.active and emp_rec.last_working_day:

                            ex_emp_day_records = emp_absentee_records.filtered(lambda rec: rec.attendance_recorded_date <= emp_rec.last_working_day)
                            # print(ex_emp_day_records)
                            emp_absentee_records -= ex_emp_day_records

                        # print(emp_absentee_records)
                        if emp_absentee_records:
                            request_list = emp_absentee_records
                            extra_params = {'emp_request_list': request_list,
                                            'description': 'Monthly Attendance Information'}
                            # print(extra_params)
                            self.env['hr.attendance'].attendance_send_custom_mail(res_id=emp_absentee_records[0].id,
                                                                                  notif_layout=notif_layout,
                                                                                  template_layout="kw_hr_attendance.kw_absentee_statement_email_template",
                                                                                  ctx_params=extra_params,
                                                                                  description="Absentee Statement")

                except Exception as e:
                    # print(str(e))
                    continue
    # Removed commented code 2 April (Gouranga)
