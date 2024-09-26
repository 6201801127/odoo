# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class AttendanceEmployeeWisePaycutWizard(models.TransientModel):
    _name = 'kw_attendance_employee_wise_paycut_take_action'
    _description = 'Employee Wise Attendance Paycut Take Action Wizard'

    @api.model
    def default_get(self, fields):
        res = super(AttendanceEmployeeWisePaycutWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({'paycut_attendance_ids': active_ids})
        return res

    remark = fields.Text(string='Remark', required=True,default="Manually Updated")

    paycut_attendance_ids = fields.Many2many(string='Employees',
                                             comodel_name='kw_attendance_employee_wise_paycut_report',
                                             relation='kw_employee_wise_attendance_paycut_wizard_rel',
                                             column1='attendance_id',
                                             column2='paycut_id',)

    @api.multi
    def update_attendance_details(self):
        remark = f"{self.remark}\n(Updated by {self.env.user.name}, on {datetime.now()})."
        manual_attendance_wizard = self.env['kw_manual_attendance_hr_wizard']
        # for attendance in self.paycut_attendance_ids:
        #     manual_attendance_wizard.create_employee_manual_attendance(
        #         attendance.employee_id, attendance.attendance_recorded_date, remark=remark)
        for emp_info in self.paycut_attendance_ids:
            start_date, end_date = emp_info.generate_start_end_date()

            attendance_records = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', emp_info.employee_id.id),
                 ('payroll_day_value', '<', 1),
                 ('is_on_tour', '=', False),
                 ('attendance_recorded_date', '>=', start_date),
                 ('attendance_recorded_date', '<=', end_date)])

            for attendance in attendance_records:
                manual_attendance_wizard.create_employee_manual_attendance(attendance.employee_id, attendance.attendance_recorded_date, remark=remark)

        self.env.user.notify_success("Attendance updated successfully.")
