# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class AttendanceBioReport(models.Model):
    _name = "kw_attendance_bio_report"
    _description = "Employee Biometric Attendance Report"
    _rec_name = 'emp_name'
    _auto = False
    _order = 'login_time asc'

    emp_name = fields.Char(string='Employee Name')
    designation = fields.Char(string="Designation")
    department = fields.Char(string='Department')
    location = fields.Char(string='Location')
    bio_id = fields.Char(string='Biometric ID')
    login_date = fields.Date(string='Login Date')
    login_time = fields.Datetime(string='Login Time')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            with bio as
                    (
            select (date- time '05:30')::date, cast(enroll_no as varchar(30)), MIN(date- time '05:30' ) AS LoginTime 
            from kw_bio_atd_enroll_info 
            group by  (date- time '05:30')::date, enroll_no
            )
            
            select  row_number() over(ORDER BY LoginTime ASC) as id,CONCAT(emp.name,' (',emp.emp_code,')') as emp_name,job.name as designation,
            dept.name as department,branch.alias as location,
            bio.enroll_no as bio_id,
            bio.date::date as login_date,
            bio.LoginTime as login_time
            from bio

            join hr_employee emp on emp.biometric_id = bio.enroll_no
            left join hr_department dept on emp.department_id = dept.id
            left join hr_job job on emp.job_id = job.id
            left join kw_res_branch branch on emp.base_branch_id = branch.id

        )"""
        self.env.cr.execute(query)
