# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import ATD_STATUS_SHALF_ABSENT, \
    ATD_STATUS_FHALF_ABSENT, ATD_STATUS_ABSENT, ATD_STATUS_PRESENT


class AttendancePaycutReport(models.Model):
    _name = "kw_attendance_employee_wise_paycut_report"
    _description = "Employee Wise Attendance Paycut Report"
    _rec_name = 'emp_name'
    # _order = "attendance_recorded_date desc"
    _auto = False

    # attendance_recorded_date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', string="Employee")

    emp_name = fields.Char(string='Name')
    department = fields.Many2one('hr.department', 'Department', related="employee_id.department_id")
    designation = fields.Many2one('hr.job', "Designation", related="employee_id.job_id")
    branch_id = fields.Many2one("kw_res_branch", "Branch", related="employee_id.job_branch_id")
    attendance_month = fields.Selection(string="Attendance Month", selection=[
        ('01', "January"), ('02', "February"), ('03', "March"), ('04', "April"), ('05', "May"), ('06', "June"),
        ('07', "July"), ('08', "August"), ('09', "September"), ('10', "October"), ('11', "November"),
        ('12', "December")])
    attendance_year = fields.Integer("Attendance Year")
    attendance_month_year = fields.Date(string="Attendance Month/Year/Day")
    first_half_absent = fields.Float(string="First Half Absent")
    second_half_absent = fields.Float(string="Second Half Absent")
    full_day_absent = fields.Float(string="Full Day Absent")
    total_absent = fields.Float(string="Total Absent")
    date_of_joining = fields.Date('Date Of Join',related="employee_id.date_of_joining") 
    last_working_day = fields.Date(string='Date of Leaving',related="employee_id.last_working_day")

    def generate_start_end_date(self):
        self.ensure_one()

        end_date = date(year=int(self.attendance_year), month=int(self.attendance_month), day=25)  #
        start_date = end_date + relativedelta(months=-1, days=+1)
        # print(start_date,end_date)
        return start_date, end_date

    @api.multi
    def view_details(self):
        start_date, end_date = self.generate_start_end_date()
        tree_view_id = self.env.ref('kw_hr_attendance.view_kw_attendance_paycut_report_tree').id
        pivot_view_id = self.env.ref('kw_hr_attendance.view_kw_attendance_paycut_report_pivot').id
        return {
            'name': 'View Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_attendance_paycut_report',
            'target': 'same',
            'view_mode': 'tree,pivot',
            'views': [(tree_view_id, 'tree'), (pivot_view_id, 'pivot')],
            # 'flags': {'mode': 'edit', },
            'context': {'create': False},
            'domain': [('employee_id', '=', self.employee_id.id), ('attendance_recorded_date', '>=', start_date),
                       ('attendance_recorded_date', '<=', end_date),
                       ('attendance_recorded_date', '!=', datetime.now().date())]
        }

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select CAST(concat(employee_id,to_char(date_trunc('month', attendance_month_year), 'MM'),substring(CAST(attendance_year as text), 3, 2)) AS BIGINT) AS id,
            TBL.employee_id,
            concat(emp.name,'(',emp.emp_code,')') as emp_name,
            to_char(date_trunc('month', attendance_month_year), 'MM') as attendance_month,
            TBL.attendance_month_year,
            TBL.attendance_year,
            TBL.first_half_absent,
            TBL.second_half_absent,
            TBL.full_day_absent,
            TBL.total_absent from  
            (
                
                select 
                employee_id,         
                date_trunc('month', attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY') ::timestamp without time zone::date AS attendance_month_year, 
                EXTRACT(year from attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY') as attendance_year,                
                SUM(CASE  WHEN a.state = '7' and a.payroll_day_value = 0.5 THEN 0.5 ELSE 0 END) as first_half_absent,
                SUM(CASE  WHEN a.state = '8' and a.payroll_day_value = 0.5 THEN 0.5 ELSE 0 END) as second_half_absent,
                SUM(CASE  WHEN a.payroll_day_value=0 THEN 1 ELSE 0 END) as full_day_absent,
                SUM(CASE  WHEN a.payroll_day_value=0 THEN 1 WHEN a.payroll_day_value=0.5 THEN 0.5 END) as total_absent
                from kw_daily_employee_attendance a
                where a.payroll_day_value <1 and a.is_on_tour = False and a.attendance_recorded_date < CURRENT_DATE and a.attendance_recorded_date > date_trunc('month', CURRENT_DATE) - INTERVAL '2 year'
                group by employee_id,date_trunc('month', attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY'),EXTRACT(year from attendance_recorded_date + INTERVAL '1 MONTH - 25 DAY')
            ) TBL 
            left join hr_employee emp on TBL.employee_id = emp.id
            where emp.employement_type in (select id from kwemp_employment_type where code in ('P','S','C')) and emp.no_attendance = False
        )"""
        self.env.cr.execute(query)
