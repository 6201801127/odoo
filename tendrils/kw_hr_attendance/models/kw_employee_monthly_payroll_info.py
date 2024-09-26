# -*- coding: utf-8 -*-
#########################
    #
    # Created On : 21-Oct-2020 , By : T Ketaki Debadarshini

#########################
import math
from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, \
    IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, LATE_WPC, LATE_WOPC, \
    ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT, DAY_STATUS_WEEKOFF, DAY_STATUS_RHOLIDAY, \
    DAY_STATUS_HOLIDAY, EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP


class HrAttendanceMonthlyPayroll(models.Model):
    _name = "kw_employee_monthly_payroll_info"
    _description = "Attendance Monthly Payroll Info"
    _rec_name = 'employee_id'

    attendance_year = fields.Integer(string="Attendance Year", index=True)
    attendance_month = fields.Integer(string="Attendance Month", index=True)
    attendance_month_name = fields.Char(string="Attendance Month", compute="_compute_month_name")
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', index=True)
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", index=True)
    department_id = fields.Many2one('hr.department', string="Department", index=True)
    company_id = fields.Many2one('res.company', string="Company", index=True)
    

    num_leave_days = fields.Float(string="Leave Days")
    num_tour_days = fields.Float(string="Tour Days")
    num_absent_days = fields.Float(string="Absent Days")
    num_present_days = fields.Float(string="Present Days")
    num_shift_working_days = fields.Float(string="Shift Working Days")  # # no of working days

    num_late_wopc = fields.Float(string="Late WOPC Days", help="Late Without Pay Cut Days")
    num_fixed_late_days_pc = fields.Float(string="Fixed Late WPC Days")
    num_late_days_pc_after_fixed = fields.Float(string="Late WPC Days after Fixed")
    num_late_wpc = fields.Float(string="Late WPC Days", help="Late With Pay Cut Days")
    num_ex_late_wopc = fields.Float(string="Extra Late WOPC Days", help="Extra Late Without Pay Cut Days")
    num_ex_late_wpc = fields.Float(string="Fixed Extra Late WPC Days", help="Fixed Extra Late With Pay Cut Days")
    num_total_late_days_pc = fields.Float(string="Total WPC Days", help="Total With Pay Cut Days")

    num_wh_leave_days = fields.Float(string="Leave+Week Holiday")
    num_fh_leave_days = fields.Float(string="Leave+Fixed Holiday")
    num_wh_tour_days = fields.Float(string="Tour+Week Holiday")
    num_fh_tour_days = fields.Float(string="Tour+Fixed Holiday")

    num_present_days_count_log = fields.Float(string='Attendance Present Days', )
    emp_status = fields.Integer(string="Employee Status", )

    num_actual_working_days = fields.Float(string='Actual Working Days(Old)')
    actual_working_days = fields.Float(string='Actual Working Days')
    
    num_leave_lwop = fields.Float(string="Leave + LWOP")
    sync_status = fields.Selection(string="Sync Status",
                                   selection=[('0', 'Not Synced'), ('1', 'Inserted'), ('2', 'Updated'),
                                              ('5', 'Error Occurred')], default='0')

    num_mt_leave_days = fields.Float(string="Maternity Leave Days")

    @api.multi
    def _compute_month_name(self):
        for rec in self:
            rec.attendance_month_name = datetime.strptime(str(rec.attendance_year)+"-"+str(rec.attendance_month)+"-01", "%Y-%m-%d").strftime('%B')

    # method to share payroll info with kwantify
    def share_payroll_info_with_kwantify(self, atd_year=False, atd_month=False):
        """Share the payroll info with the kwantify         
        """

        daily_attendance = self.env['kw_daily_employee_attendance']
        for payroll_info in self:

            actual_present_days = int(math.ceil(payroll_info.num_actual_working_days))
            num_present_days = int(math.ceil(payroll_info.num_present_days))

            json_params = {"Absent": payroll_info.num_absent_days,
                           "Count_ExLate_Days_pc": payroll_info.num_ex_late_wpc,
                           "Count_ExLate_Days_wpc": payroll_info.num_ex_late_wopc,
                           "Count_FH_Leave": payroll_info.num_fh_leave_days,
                           "Count_FH_Tour": payroll_info.num_fh_tour_days,
                           "Count_Late_Days_pc": payroll_info.num_late_days_pc_after_fixed,
                           "Count_Present": payroll_info.num_present_days_count_log,
                           "Count_Total_Late_Days_pc": payroll_info.num_total_late_days_pc,
                           "Count_WH_Leave": payroll_info.num_wh_leave_days,
                           "Count_WH_Tour": payroll_info.num_wh_tour_days,
                           "Fixed_Late_Days": payroll_info.num_fixed_late_days_pc,
                           "Fixed_Late_Days_pc": payroll_info.num_fixed_late_days_pc,
                           "LWOP": payroll_info.num_leave_lwop,
                           "Late_WPC": payroll_info.num_late_wpc,
                           "Leave": payroll_info.num_leave_days,
                           "Month": atd_month if atd_month else payroll_info.attendance_month,
                           "Present": num_present_days,
                           "Tour": payroll_info.num_tour_days,
                           "UserID": payroll_info.employee_id.kw_id,
                           "Working_Days": payroll_info.num_shift_working_days,
                           "Year": atd_year if atd_year else payroll_info.attendance_year,
                           "int_Act_Workingdays": actual_present_days,
                           "int_CreatedBy": payroll_info.employee_id.kw_id,
                           "int_Status": payroll_info.emp_status}
            # print(json_params)            
            try:
                # print(payroll_info.employee_id.kw_id)
                if payroll_info.employee_id.kw_id != '' and payroll_info.employee_id.kw_id > 0:
                    # print('------------------')
                    resp_result = daily_attendance._call_attendance_web_service('UserPayrollAttendance', json_params)
                    # print(resp_result)
                    if resp_result and (resp_result[0]['OutputStatus'] == '1' or resp_result[0]['OutputStatus'] == '2'):
                        payroll_info.sync_status = resp_result[0]['OutputStatus']
                    else:
                        payroll_info.sync_status = '5'

            except Exception as e:
                # self.env.user.notify_danger(message='Some error occured while sharing info with Kwantify.')
                payroll_info.sync_status = '5'
                continue
