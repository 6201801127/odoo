from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api

from dateutil.relativedelta import relativedelta



class kw_share_timesheet_el_deduct_wizard(models.TransientModel):
    _name           = "kw_share_timesheet_el_deduct_wizard"
    _description    = "Timesheet Monthly EL Data Share"


    timesheet_year    = fields.Selection(selection = lambda self : [(str(date.today().year),date.today().year)], string='Year',default=str(datetime.today().year))
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



    @api.multi
    def share_timesheet_el_data_with_deduct_report(self):
        timesheet_payrolls = self.env['kw_timesheet_payroll_report'].sudo().search([('attendance_month','=',self.timesheet_month),('attendance_year','=',self.timesheet_year)])
        timesheet_payrolls = timesheet_payrolls.filtered(lambda r:r.timesheet_el_days > 0)

        timesheet_leave_deducts = self.env['kw_timesheet_leave_deduct'].search([('timesheet_payroll_report_id', 'in', timesheet_payrolls.ids)])

        for timesheet_payroll in timesheet_payrolls:
            timesheet_leave_deduct = timesheet_leave_deducts.filtered(lambda r:r.timesheet_payroll_report_id == timesheet_payroll)
            # print('leave_deduct_record',timesheet_leave_deduct)
            if timesheet_leave_deduct:
                timesheet_leave_deduct.write({
                    'emp_code': timesheet_payroll.emp_code,
                    'employee_id': timesheet_payroll.employee_id.id,
                    'designation': timesheet_payroll.designation,
                    'department_id': timesheet_payroll.department_id,
                    'division': timesheet_payroll.division,
                    'parent_id': timesheet_payroll.parent_id,
                    'timesheet_month': timesheet_payroll.attendance_month,
                    'timesheet_year': timesheet_payroll.attendance_year,
                    'timesheet_el_deduct_in_days': timesheet_payroll.timesheet_el_days,
                    'attendance_month_year': timesheet_payroll.attendance_month_year
                    })
            else:
                emp_timesheet_leave_deduct = self.env['kw_timesheet_leave_deduct'].sudo().search([('employee_id', '=', timesheet_payroll.employee_id.id),
                                                                                                    ('timesheet_month', '=', timesheet_payroll.attendance_month),
                                                                                                    ('timesheet_year', '=', timesheet_payroll.attendance_year)])
                if not emp_timesheet_leave_deduct:
                    timesheet_leave_deduct.create({
                        'timesheet_payroll_report_id': timesheet_payroll.id,
                        'emp_code': timesheet_payroll.emp_code,
                        'employee_id': timesheet_payroll.employee_id.id,
                        'designation': timesheet_payroll.designation,
                        'department_id': timesheet_payroll.department_id,
                        'division': timesheet_payroll.division,
                        'parent_id': timesheet_payroll.parent_id,
                        'timesheet_month': timesheet_payroll.attendance_month,
                        'timesheet_year': timesheet_payroll.attendance_year,
                        'timesheet_el_deduct_in_days': timesheet_payroll.timesheet_el_days,
                        'attendance_month_year': timesheet_payroll.attendance_month_year
                    })

        self.env.user.notify_success(message='Timesheet EL data shared Successfully')