        # -*- coding: utf-8 -*-
#########################
#
# Created On : 21-Oct-2020 , By : T Ketaki Debadarshini
# Future day added to tour , leave , maternity and lwop 19 March 2021 (Gouranga)

#########################

from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta


from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import  LEAVE_TYPE_MATERNITY,DAY_STATUS_WORKING,DAY_STATUS_RWORKING
class HrAttendancePayrollProcessInherit(models.TransientModel):
    _inherit = "kw_payroll_process_wizard"
    _description = "Attendance Monthly Payroll Process"

    def share_selected_payroll_info_with_payroll_module(self):
        if self.monthly_payroll_ids:
            for monthly_payroll_id in self.monthly_payroll_ids:
                monthly_payroll_id.share_payroll_info_with_payroll_module()

    def share_with_payroll(self):
        atd_year, atd_month, company_id, department_id  = int(self.attendance_year), int(self.attendance_month), self.company_id.id, self.department_id.id
        daily_attendance = self.env['kw_daily_employee_attendance']
        start_date, _, payroll_end_date = daily_attendance._get_recompute_date_range_configs(
            end_date=datetime.today().date().replace(day=1, month=atd_month, year=atd_year))

        employee_monthly_payroll = self.env['kw_employee_monthly_payroll_info']

        payroll_end_date = payroll_end_date.replace(day=payroll_end_date.day - 1)
        # print(start_date,payroll_end_date)

        if payroll_end_date > start_date:
            latest_payroll_info = employee_monthly_payroll.search(
                [('attendance_year', '=', atd_year), ('attendance_month', '=', atd_month),('company_id','=',company_id),('department_id','=',department_id)])

            for payroll_info in latest_payroll_info:
                # #call the sharing method of payroll
                payroll_info.share_payroll_info_with_payroll_module(atd_year, atd_month)

        self.env.user.notify_success(message='Payroll details shared with Payroll module successfully.')
        return {"type": "set_scrollTop", }


class HrAttendanceMonthlyPayrollInherit(models.Model):
    _inherit = "kw_employee_monthly_payroll_info"
    _description = "Attendance Monthly Payroll Info"

    def share_payroll_info_with_payroll_module(self, atd_year=False, atd_month=False):
        daily_attendance = self.env['kw_daily_employee_attendance']
        for payroll_info in self:
            if payroll_info.employee_id.enable_payroll == 'yes':
                # if payroll_info.employee_id.kw_id != '' and payroll_info.employee_id.kw_id > 0:
                    
                    # result = 0
                    # if payroll_info.emp_status == 1:
                    #     result = payroll_info.actual_working_days - (payroll_info.num_leave_lwop + payroll_info.num_total_late_days_pc + payroll_info.num_absent_days)
                    # else:
                    #     result = payroll_info.actual_working_days - (payroll_info.num_leave_lwop + payroll_info.num_total_late_days_pc + payroll_info.num_absent_days)
                    
                result = payroll_info.actual_working_days - (payroll_info.num_leave_lwop + payroll_info.num_total_late_days_pc + payroll_info.num_absent_days)
                compare_payroll_record = self.env['kw_payroll_monthly_attendance_report'].sudo().search([
                    ('attendance_year', '=', payroll_info.attendance_year),
                    ('attendance_month', '=', payroll_info.attendance_month),
                    ('employee_id', '=', payroll_info.employee_id.id),('company_id','=',payroll_info.company_id.id),('department_id','=',payroll_info.employee_id.department_id.id)])
                ir_config_params = self.env['ir.config_parameter'].sudo()
                enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
                ckeck_calendar_days = True if enable_month_days else False
                start_date = date(int(payroll_info.attendance_year), int(payroll_info.attendance_month)-1, 26) if int(payroll_info.attendance_month) != 1 else date(int(payroll_info.attendance_year)-1,12, 26)
                payroll_end_date =date(int(payroll_info.attendance_year), int(payroll_info.attendance_month),25)
                ids =[]
                query = f" SELECT sum(case when  leave_day_value >0 and leave_code ='{LEAVE_TYPE_MATERNITY}' then leave_day_value else 0 end) as num_mt_leave_days  from kw_daily_employee_attendance where attendance_recorded_date >= '{start_date}' and attendance_recorded_date <= '{payroll_end_date}' and employee_id = {payroll_info.employee_id.id}"
                self._cr.execute(query)
                ids = self._cr.dictfetchall()
                maternity_leave_days = ids[0]['num_mt_leave_days'] if ids else 0
                employee_status = 0
                if payroll_info.emp_status == 2:
                    if payroll_info.employee_id.date_of_joining:
                        if payroll_info.employee_id.date_of_joining.month != payroll_info.attendance_month:
                            employee_status = 1
                zero_payslip_boolean = False
                enable_zero_payslip = ir_config_params.get_param('payroll_inherit.enable_zero_payslip') or False
                if enable_zero_payslip != False:
                    zero_payslip_rec = self.env['kw_payroll_zero_payslip'].sudo().search([('year', '=', str(payroll_info.attendance_year)), ('month', '=', str(payroll_info.attendance_month)),('employee', '=', payroll_info.employee_id.id)])
                    if zero_payslip_rec:
                        zero_payslip_boolean = True
                if not compare_payroll_record:
                    self.env['kw_payroll_monthly_attendance_report'].sudo().create({
                        'attendance_year': payroll_info.attendance_year,
                        'attendance_month': payroll_info.attendance_month,
                        'employee_id': payroll_info.employee_id.id,
                        'branch_id': payroll_info.branch_id,
                        'department_id': payroll_info.employee_id.department_id.id,
                        'num_leave_days': payroll_info.num_leave_days,
                        'num_tour_days': payroll_info.num_tour_days,
                        'num_absent_days': payroll_info.num_absent_days,
                        'num_present_days': payroll_info.num_present_days,
                        'num_shift_working_days': payroll_info.num_shift_working_days,
                        'num_late_wopc': payroll_info.num_late_wopc,
                        'num_fixed_late_days_pc': payroll_info.num_fixed_late_days_pc,
                        'num_late_days_pc_after_fixed': payroll_info.num_late_days_pc_after_fixed,
                        'num_late_wpc': payroll_info.num_late_wpc,
                        'num_ex_late_wopc': payroll_info.num_ex_late_wopc,
                        'num_ex_late_wpc': payroll_info.num_ex_late_wpc,
                        'num_total_late_days_pc': payroll_info.num_total_late_days_pc,
                        'num_wh_leave_days': payroll_info.num_wh_leave_days,
                        'num_fh_leave_days': payroll_info.num_fh_leave_days,
                        'num_wh_tour_days': payroll_info.num_wh_tour_days,
                        'num_fh_tour_days': payroll_info.num_fh_tour_days,
                        'num_present_days_count_log': payroll_info.num_present_days_count_log,
                        'emp_status': employee_status if employee_status != 0 else payroll_info.emp_status,
                        'num_actual_working_days': payroll_info.num_actual_working_days,
                        'num_leave_lwop': payroll_info.num_leave_lwop,
                        'num_mt_leave_days': maternity_leave_days,
                        'total_pay_cut': payroll_info.num_leave_lwop + payroll_info.num_total_late_days_pc + payroll_info.num_absent_days,
                        'total_days_payable': result if result > 0 else 0,
                        'absent_days': payroll_info.num_absent_days,
                        'actual_working': payroll_info.actual_working_days,
                        'ckeck_calendar_days': ckeck_calendar_days,
                        'zero_payslip_boolean': zero_payslip_boolean,
                        'company_id': payroll_info.company_id.id
                        
                    })
                else:
                    compare_payroll_record.sudo().write({
                        'department_id': payroll_info.employee_id.department_id.id,
                        'num_leave_days': payroll_info.num_leave_days,
                        'num_tour_days': payroll_info.num_tour_days,
                        'num_absent_days': payroll_info.num_absent_days,
                        'num_present_days': payroll_info.num_present_days,
                        'num_shift_working_days': payroll_info.num_shift_working_days,
                        'num_late_wopc': payroll_info.num_late_wopc,
                        'num_fixed_late_days_pc': payroll_info.num_fixed_late_days_pc,
                        'num_late_days_pc_after_fixed': payroll_info.num_late_days_pc_after_fixed,
                        'num_late_wpc': payroll_info.num_late_wpc,
                        'num_ex_late_wopc': payroll_info.num_ex_late_wopc,
                        'num_ex_late_wpc': payroll_info.num_ex_late_wpc,
                        'num_total_late_days_pc': payroll_info.num_total_late_days_pc,
                        'num_wh_leave_days': payroll_info.num_wh_leave_days,
                        'num_fh_leave_days': payroll_info.num_fh_leave_days,
                        'num_wh_tour_days': payroll_info.num_wh_tour_days,
                        'num_fh_tour_days': payroll_info.num_fh_tour_days,
                        'num_present_days_count_log': payroll_info.num_present_days_count_log,
                        'emp_status': employee_status if employee_status != 0 else payroll_info.emp_status,
                        'num_actual_working_days': payroll_info.num_actual_working_days,
                        'num_leave_lwop': payroll_info.num_leave_lwop,
                        'num_mt_leave_days': maternity_leave_days,
                        'total_pay_cut': payroll_info.num_leave_lwop + payroll_info.num_total_late_days_pc + payroll_info.num_absent_days,
                        'total_days_payable': result if result > 0 else 0,
                        'absent_days': payroll_info.num_absent_days,
                        'actual_working': payroll_info.actual_working_days,
                        'ckeck_calendar_days': ckeck_calendar_days,
                        'zero_payslip_boolean': zero_payslip_boolean,
                        'company_id': payroll_info.company_id.id
                        
                    })
                    
                    
