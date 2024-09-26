import calendar,datetime
from datetime import datetime,date
from odoo import fields, models, api


class hr_employee_in(models.Model):
    _inherit = 'hr.employee'

    enable_timesheet = fields.Boolean('Timesheet Enable', default=True)
    allow_backdate = fields.Boolean('Allow Backdate', default=False)
    timesheet_cost = fields.Monetary('Timesheet Cost', currency_field='currency_id', groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
   
   
    def timesheet_per_hour_cost(self):
        emp_data = self.env['hr.employee'].sudo().search([])
        current_month,current_year,current_date,required_effort = date.today().month, date.today().year, date.today(),[]
        no_of_day_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
        # print('number day month',no_of_day_in_month)
        # start_date,end_date = self.env['kw_late_attendance_summary_report']._get_month_range(current_year,current_month)
        for emp in emp_data:
            # present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',emp.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
            # absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',emp.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
            # leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',emp.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('leave_day_value','=',0.5)])
            # for present in present_attendance_ids:
            #     required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
            # for absent in absent_attendance_ids:
            #     required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
            # for leave in leave_attendance_ids:
            #     required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time) * 0.5)
            averge_working_hour_per_day = emp.resource_calendar_id.hours_per_day
            emp_ctc = emp.current_ctc
            cost_per_hour=emp_ctc/(averge_working_hour_per_day*no_of_day_in_month)
            emp.timesheet_cost = cost_per_hour