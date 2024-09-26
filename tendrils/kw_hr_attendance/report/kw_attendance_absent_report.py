# -*- coding: utf-8 -*-
from datetime import date
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING,DAY_STATUS_RWORKING

class AbsenteeReport(models.Model):
    _name           = "kw_attendance_absent_report"
    _description    = "Employee Attendance Absent Report"
    _auto           = False
    _rec_name       = 'emp_name'

    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    emp_name = fields.Char(string='Employee')
    branch = fields.Char(string="Location")
    department = fields.Char(string='Department')
    designation = fields.Char(string='Designation')
    ra_name = fields.Char(string='RA Name')
    absent_from = fields.Date("Absent After")
    total_absent_days = fields.Integer("No. Of Days Absent")
    employement_type = fields.Many2one('kwemp_employment_type', string="Employement Type ID")
    employement_type_name = fields.Char(string='Employement Type')

    @api.model_cr
    def init(self):
        # current_date = date.today().strftime('%Y-%m-%d')
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW %s as (
            
            with P as
            (
                select row_number() over(partition by employee_id order by attendance_recorded_date desc) as slno, employee_id, attendance_recorded_date from kw_daily_employee_attendance 
                where is_valid_working_day = True and (is_on_tour = True or check_in is not null or leave_day_value>0) and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}')
            )		
            select maintbl.employee_id as id,maintbl.attendance_recorded_date,maintbl.employee_id ,concat(b.name, ' (', b.emp_code, ')') as emp_name,job.name as designation, dept.name as department, branch.alias as branch
            , concat(ra.name, ' (', ra.emp_code, ')') as ra_name 
            , coalesce(P.attendance_recorded_date, b.date_of_joining) as absent_from
            , coalesce(maintbl.attendance_recorded_date::DATE - coalesce(P.attendance_recorded_date, b.date_of_joining)::DATE,0)as total_absent_days
	        ,b.employement_type 
            ,emp_type.name as employement_type_name
            from kw_daily_employee_attendance maintbl 
            inner join 
            (select max(attendance_recorded_date) as latest_attendance_recorded_date, employee_id from kw_daily_employee_attendance group by employee_id)latestbtl 

            on maintbl.attendance_recorded_date= latestbtl.latest_attendance_recorded_date and maintbl.employee_id= latestbtl.employee_id
            
            left join P on P.employee_id=maintbl.employee_id and P.slno=1 
            join hr_employee b on maintbl.employee_id = b.id 
            left join hr_employee ra on b.parent_id = ra.id
            left join kw_res_branch branch on b.job_branch_id = branch.id
            left join hr_job job on job.id=b.job_id
            left join hr_department dept on dept.id = b.department_id 
            left join kwemp_employment_type emp_type on emp_type.id=b.employement_type

            where is_valid_working_day = True and is_on_tour = False and check_in is null  and leave_day_value=0 and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and b.active=True and b.no_attendance = False

            order by total_absent_days desc

        )""" % (self._table)

        # print(query)
        self.env.cr.execute(query)

