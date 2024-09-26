# -*- coding: utf-8 -*-

from odoo import models, fields, api
import calendar
from odoo.exceptions import ValidationError


class kw_timesheet_payroll_integration(models.Model):
    _inherit = "kw_payroll_monthly_attendance_report"

    timesheet_payroll_report_id = fields.Many2one('kw_timesheet_payroll_report', string="Timesheet Payroll Report Id")
    timesheet_paycut_in_day = fields.Float('Timesheet Paycut in Days (F)')
    timesheet_el_deduct_in_day = fields.Float('Timesheet EL Deduction')

    @api.onchange('num_leave_lwop', 'num_total_late_days_pc', 'num_absent_days', 'timesheet_paycut_in_day')
    def onchange_for_total_pay_cut(self):
        for rec in self:
            rec.total_pay_cut = rec.num_leave_lwop + rec.num_total_late_days_pc + rec.num_absent_days + rec.timesheet_paycut_in_day


class kw_payroll_integration_wizard(models.TransientModel):
    _name = 'kw_payroll_integration_wizard'
    _description = 'Payroll Integration wizard'

    def _get_payroll_integration_wizard(self):
        res = self.env['kw_timesheet_payroll_report'].browse(self.env.context.get('active_ids'))
        return res

    payroll_report_ids = fields.Many2many('kw_timesheet_payroll_report', default=_get_payroll_integration_wizard,
                                          string="Timesheet Payroll Record")

    def share_selected_timesheet_info_with_payroll_module(self):
        if self.payroll_report_ids:
            for monthly_timesheet_id in self.payroll_report_ids:
                tot_lwop = 0
                compare_payroll_record = self.env['kw_payroll_monthly_attendance_report'].sudo().search([
                    ('attendance_year', '=', monthly_timesheet_id.attendance_year),
                    ('attendance_month', '=', monthly_timesheet_id.attendance_month),
                    ('employee_id', '=', monthly_timesheet_id.employee_id.id)])
                if compare_payroll_record:
                    ir_config_params = self.env['ir.config_parameter'].sudo()
                    enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
                    result = 0
                    tot_lwop = compare_payroll_record.num_absent_days + compare_payroll_record.num_total_late_days_pc + compare_payroll_record.num_leave_lwop + monthly_timesheet_id.timesheet_paycut_days
                    if compare_payroll_record.emp_status == 1:
                        result = compare_payroll_record.month_days - (tot_lwop) if enable_month_days else compare_payroll_record.num_shift_working_days - (tot_lwop)
                    else:
                        result = (compare_payroll_record.num_present_days + compare_payroll_record.num_absent_days) - (tot_lwop)
                    compare_payroll_record.write({'timesheet_el_deduct_in_day': monthly_timesheet_id.timesheet_el_days,
                                                  'timesheet_paycut_in_day': monthly_timesheet_id.timesheet_paycut_days,
                                                  'total_pay_cut': tot_lwop,
                                                  'total_days_payable': result,
                                                  'timesheet_payroll_report_id': monthly_timesheet_id.id})

                # Share Timesheet Payroll Deduction
                # leave_deduction = self.env['timesheet_el_deduct_report'].sudo().search([
                #     ('attendance_year', '=', monthly_timesheet_id.attendance_year),
                #     ('attendance_month', '=', monthly_timesheet_id.attendance_month),
                #     ('employee_id', '=', monthly_timesheet_id.employee_id.id)
                # ])
                # if leave_deduction:
                #     pass
                # else:
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


class PayrollDeductEL(models.TransientModel):
    _name = 'kw_payroll_deduct_el_wizard'
    _description = 'Payroll Deduct EL Wizard'

    def _get_payroll_deduct_el_wizard(self):
        res = self.env['kw_timesheet_payroll_report'].browse(self.env.context.get('active_ids'))
        return res

    payroll_report_ids = fields.Many2many('kw_timesheet_payroll_report', default=_get_payroll_deduct_el_wizard,
                                          string="Timesheet Payroll Record")

    def deduct_el_timesheet_info_with_payroll(self):
        for record in self:
            for timesheet in record.payroll_report_ids:
                payroll_report_data = self.env['kw_timesheet_payroll_report'].sudo().search(
                    [('employee_id', '=', timesheet.employee_id.id), ('attendance_year', '=', timesheet.attendance_year),
                     ('attendance_month', '=', timesheet.attendance_month)])
                if timesheet.attendance_month == '03' and timesheet.attendance_year == 2023:
                    raise ValidationError(f'Cannot deduct El as encashment process is already done')
                if payroll_report_data:
                    formatNumber = lambda n: n if n % 1 else int(n)
                    db_month = calendar.month_name[int(payroll_report_data.attendance_month)]
                    db_year = payroll_report_data.attendance_year
                    required_effort_hour = formatNumber(payroll_report_data.required_effort_hour)
                    num_actual_effort = formatNumber(payroll_report_data.num_actual_effort)
                    total_effort_hr = formatNumber(payroll_report_data.total_effort)
                    timesheet_el_days = formatNumber(payroll_report_data.timesheet_el_days)
                    timesheet_paycut_days = formatNumber(payroll_report_data.timesheet_paycut_days)
                    self.env['hr.leave.allocation'].lapse_el_timesheet_integration(timesheet.employee_id.id, 'EL',
                                                                                   timesheet.timesheet_el_days)
                    timesheet.write({'el_deducted': True})
                    timesheet_deducted = formatNumber(timesheet.timesheet_el_days)
                    template = self.env.ref('kw_timesheets.timesheet_el_deduction_mail')
                    template.with_context(timesheet_deducted=timesheet_deducted, db_month=db_month, db_year=db_year,
                                          required_effort_hour=required_effort_hour,
                                          num_actual_effort=num_actual_effort,
                                          total_effort_hr=total_effort_hr, timesheet_el_days=timesheet_el_days,
                                          timesheet_paycut_days=timesheet_paycut_days).send_mail(timesheet.id,
                                                                                                 notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success(message='EL has been deducted successfully!')