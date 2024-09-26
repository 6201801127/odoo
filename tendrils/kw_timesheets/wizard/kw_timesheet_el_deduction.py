import calendar
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class kw_timesheet_el_deduction(models.TransientModel):
    _name = 'timesheet_el_deduction'
    _description = 'Timesheet EL Deduction'

    def _get_el_data(self):
        rec = self.env['kw_timesheet_leave_deduct'].browse(self.env.context.get('active_ids')).filtered(lambda d: not d.el_deducted)
        # print(rec)
        return rec

    timesheet_details_ids = fields.Many2many('kw_timesheet_leave_deduct', default=_get_el_data, string="Timesheet Leave Ids")

    @api.multi
    def approve_timesheet_el_deduction_btn(self):
        for record in self:
            # print('timesheet_details_ids',self.timesheet_details_ids)
            for timesheet in record.timesheet_details_ids:
                payroll_report_data = self.env['kw_timesheet_payroll_report'].sudo().search([('employee_id','=',timesheet.employee_id.id),('attendance_year','=',timesheet.timesheet_year),('attendance_month','=',timesheet.timesheet_month)])
                if timesheet.timesheet_month == '03' and timesheet.timesheet_year == 2023:
                    raise ValidationError(f'Cannot deduct El as encashment process is already done')
                if payroll_report_data:
                    formatNumber = lambda n: n if n % 1 else int(n)
                    db_month = calendar.month_name[int(payroll_report_data.attendance_month)]
                    db_year = payroll_report_data.attendance_year
                    required_effort_hour = formatNumber(payroll_report_data.required_effort_hour)
                    num_actual_effort=formatNumber(payroll_report_data.num_actual_effort)
                    total_effort_hr=formatNumber(payroll_report_data.total_effort)
                    timesheet_el_days=formatNumber(payroll_report_data.timesheet_el_days)
                    timesheet_paycut_days=formatNumber(payroll_report_data.timesheet_paycut_days)
                    self.env['hr.leave.allocation'].lapse_el_timesheet_integration(timesheet.employee_id.id, 'EL',timesheet.timesheet_el_deduct_in_days)
                    timesheet.write({'el_deducted': True})
                    timesheet_deducted = formatNumber(timesheet.timesheet_el_deduct_in_days)
                    template = self.env.ref('kw_timesheets.timesheet_el_deduction_mail')
                    template.with_context(timesheet_deducted=timesheet_deducted,db_month=db_month,db_year=db_year,required_effort_hour=required_effort_hour,num_actual_effort=num_actual_effort,
                    total_effort_hr=total_effort_hr,timesheet_el_days=timesheet_el_days,timesheet_paycut_days=timesheet_paycut_days).send_mail(timesheet.id,
                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success(message='EL has been deducted successfully!')
