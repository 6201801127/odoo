# -*- coding: utf-8 -*-
import datetime
from datetime import date, datetime

from odoo import tools
from odoo import models, fields, api
# from datetime import datetime, date
# from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import WFH_STATUS, WFO_STATUS, \
#     WFA_STATUS  # LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF,


class EmployeeWorkstationhybridReport(models.Model):
    _name = "kw_employee_hybrid_report"
    _description = "Employee Hybrid Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_name = fields.Char(related="employee_id.name", string="Employee Name")
    emp_code = fields.Char(related="employee_id.emp_code", string="Employee Code")
    date_of_joining = fields.Date(string="Date of joining")
    work_location_type = fields.Selection([('onsite', 'Onsite'), ('offsite', 'Offsite'), ('wfa', 'WFA'),
                                           ('hybrid', 'Hybrid')], string="Location")
    department_id = fields.Many2one("hr.department", string='Department')
    job_id = fields.Many2one('hr.job', string="Designation")
    sbu = fields.Char(string="SBU")
    job_branch_id = fields.Many2one('kw_res_branch', string="Work location")
    ra_emp = fields.Many2one('hr.employee', related="employee_id.parent_id")
    work_email_emp = fields.Char(string='Work Email', related="employee_id.work_email")
    # project = fields.Char(string="Projects Tagged")
    # project_manager_id = fields.Char(string="Project Manager")
    workstation = fields.Char(string="Workstation")
    working_mode = fields.Char(string="Working Mode", compute="_check_working_mode")
    attendance_mode_ids = fields.Many2many('kw_attendance_mode_master', string="Attendance mode", related="employee_id.attendance_mode_ids")

    def _check_working_mode(self):
        today = date.today()
        for rec in self:
            check_assigned = self.env['kw_workstation_assign'].search(
                [('assign_date', '=', today), ('employee_id', '=', rec.employee_id.id)])
            if check_assigned.exists():
                rec.working_mode = 'WFO'
            else:
                rec.working_mode = 'WFH'

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
      SELECT
            ROW_NUMBER() OVER (ORDER BY emp.id) AS id,
            emp.id AS employee_id,
            emp.date_of_joining AS date_of_joining,
            emp.location AS work_location_type,
            emp.department_id AS department_id,
            emp.job_branch_id AS job_branch_id,
            emp.job_id AS job_id,
            (
                SELECT string_agg(kwm.name, ', ')
                FROM kw_workstation_master kwm
                JOIN kw_workstation_hr_employee_rel rel ON kwm.id = rel.wid
                WHERE rel.eid = emp.id
            ) AS workstation,
            sbu.name AS sbu
        FROM hr_employee emp  
        LEFT JOIN kw_sbu_master sbu ON  sbu.id = emp.sbu_master_id
        WHERE emp.location = 'hybrid' AND emp.active=True
        )"""
        self.env.cr.execute(query)
