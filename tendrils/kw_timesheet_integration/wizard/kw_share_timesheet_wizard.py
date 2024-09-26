from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api

from dateutil.relativedelta import relativedelta



class kw_share_timesheet_wizard(models.TransientModel):
    _name           = "kw_share_timesheet_wizard"
    _description    = "Timesheet Monthly Data Share"


    timesheet_year    = fields.Selection(selection='_get_year_list', string='Year',default=str(datetime.today().year))
    timesheet_month   = fields.Selection(selection=[
                                            ('01',"January"),
                                            ('02', "February"),
                                            ('03', "March"),
                                            ('04', "April"),
                                            ('05', "May"),
                                            ('06', "June"),
                                            ('07', "July"),
                                            ('08', "August"),
                                            ('09', "September"),
                                            ('10', "October"),
                                            ('11', "November"),
                                            ('12',"December")], string='Month')


    @api.model
    def _get_month_name_list(self):
        cur_date = datetime.today().date()
        months_choices = [(str(cur_date.month), cur_date.strftime('%B'))]
        first = cur_date.replace(day=1)
        last_month_date = first - timedelta(days=1)

        months_choices.append((str(last_month_date.month), last_month_date.strftime('%B')))
        return months_choices

    @api.model
    def _get_year_list(self):
        cur_date = datetime.today().date()
        first = cur_date.replace(day=1)
        last_month_date = first - timedelta(days=1)

        YEARS = [(str(cur_date.year), cur_date.year)]
        if last_month_date.year != cur_date.year:
            YEARS.append((str(last_month_date.year), last_month_date.year))

        return YEARS

    def share_timesheet_data_with_payroll(self):
        timesheet_payroll_id = self.env['kw_timesheet_payroll_report'].sudo().search([('attendance_month','=',self.timesheet_month),('attendance_year','=',self.timesheet_year)])
        
        for monthly_timesheet_id in timesheet_payroll_id:
                tot_lwop = 0
                compare_payroll_record = self.env['kw_payroll_monthly_attendance_report'].sudo().search([
                    ('attendance_year', '=', monthly_timesheet_id.attendance_year),
                    ('attendance_month', '=', monthly_timesheet_id.attendance_month),
                    ('employee_id', '=', monthly_timesheet_id.employee_id.id)])
                if compare_payroll_record:
                    tot_lwop = compare_payroll_record.num_absent_days + compare_payroll_record.num_total_late_days_pc + compare_payroll_record.num_leave_lwop + monthly_timesheet_id.timesheet_paycut_days
                    compare_payroll_record.write({'timesheet_el_deduct_in_day':monthly_timesheet_id.timesheet_el_days, 'timesheet_paycut_in_day': monthly_timesheet_id.timesheet_paycut_days,'total_pay_cut':tot_lwop, 'timesheet_payroll_report_id':monthly_timesheet_id.id})

                self.env['timesheet_el_deduct_report'].create({
                            'attendance_year': monthly_timesheet_id.attendance_year,
                            'attendance_month': monthly_timesheet_id.attendance_month,
                            'emp_code': monthly_timesheet_id.emp_code,
                            'employee': monthly_timesheet_id.employee,
                            'employee_id': monthly_timesheet_id.employee_id.id,
                            'designation': monthly_timesheet_id.designation,
                            'department_id': monthly_timesheet_id.department_id,
                            'division': monthly_timesheet_id.division,
                            'parent_id': monthly_timesheet_id.parent_id,
                            'working_days': monthly_timesheet_id.working_days,
                            'absent_days': monthly_timesheet_id.absent_days,
                            'on_tour_days': monthly_timesheet_id.on_tour_days,
                            'on_leave_days': monthly_timesheet_id.on_leave_days,
                            'per_day_effort': monthly_timesheet_id.per_day_effort,
                            'required_effort_hour': monthly_timesheet_id.required_effort_hour,
                            'num_actual_effort': monthly_timesheet_id.num_actual_effort,
                            'total_effort': monthly_timesheet_id.total_effort,
                            'required_effort_day': monthly_timesheet_id.required_effort_day,
                            'num_actual_effort_day': monthly_timesheet_id.num_actual_effort_day,
                            'total_effort_day': monthly_timesheet_id.total_effort_day,
                            'required_effort_char': monthly_timesheet_id.required_effort_char,
                            'actual_effort_char': monthly_timesheet_id.actual_effort_char,
                            'total_effort_char': monthly_timesheet_id.total_effort_char,
                            'total_effort_percent': monthly_timesheet_id.total_effort_percent,
                            'timesheet_el_days': monthly_timesheet_id.timesheet_el_days,
                            'timesheet_paycut_days': monthly_timesheet_id.timesheet_paycut_days,
                            })
        self.env.user.notify_success(message='Timesheet data shared to payroll successfully')