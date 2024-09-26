# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class AttendanceRequest(models.Model):
    _name = "kw_attendance_request_report"
    _description = "Employee Attendance Request Report"
    _auto = False
    _rec_name = 'emp_name'

    emp_name = fields.Char(string='Employee')
    designation = fields.Char(string='Designation')
    department = fields.Char(string='Department')
    attendance_date = fields.Date(string="Attendance Date")
    check_in_datetime = fields.Datetime("Office-in Date & Time")
    check_out_datetime = fields.Datetime("Office-out Date & Time")
    applied_on = fields.Datetime("Applied On")
    status = fields.Char(string='Status')
    action_authority = fields.Char(string='Approval Authority')
    reason = fields.Char(string='Reason')
    authority_remark = fields.Char(string='Authority Remark')
    action_taken_on = fields.Datetime(string="Action Taken On")
    app_request_id = fields.Many2one('kw_employee_apply_attendance', string="Attendance Request Id")
    request_for = fields.Char("Request For", related="app_request_id.request_for")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select a.id,a.id AS app_request_id,emp.name AS emp_name,job.name AS designation,dept.name AS department,
            a.attendance_date,
            a.check_in_datetime,
            a.check_out_datetime,
            a.create_date AS applied_on,CASE WHEN a.state='1' THEN 'Draft'
                                            WHEN a.state='2' THEN 'Applied'
                                            WHEN a.state='3' THEN 'Approved'
                                            WHEN a.state='5' THEN 'Rejected'
                                            WHEN a.state='6' THEN 'Cancelled' END as status,
            action_taken.name AS action_authority,
            a.reason ,
            a.action_taken_on AS action_taken_on,
            a.authority_remark AS authority_remark 
            from kw_employee_apply_attendance a
            join hr_employee emp on a.employee_id = emp.id
            join hr_employee action_taken on a.action_taken_by = action_taken.id
            join hr_department dept on emp.department_id = dept.id
            join hr_job job on emp.job_id = job.id
        )"""
        self.env.cr.execute(query)

    @api.multi
    def view_request_details(self):
        view_id = self.env.ref('kw_hr_attendance.kw_employee_apply_attendance_report_view_form').id
        return {
            'name': 'Request Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_employee_apply_attendance',
            'res_id': self.ids[0],
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
        }
