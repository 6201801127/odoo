# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from datetime import datetime, date
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import WFH_STATUS, WFO_STATUS, \
    WFA_STATUS  # LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF,


class EmployeeWorkstationAttendanceReport(models.Model):
    _name = "kw_employee_workstation_attendance_report"
    _description = "Employee Workstation Attendance Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'assign_date asc'

    assign_id = fields.Many2one('kw_workstation_assign', string="Assign ID")
    assign_date = fields.Date(string='Assign Date')

    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_name = fields.Char(related="employee_id.name", string="Employee")
    emp_code = fields.Char(related="employee_id.emp_code", string="Employee Code")
    # employement_type = fields.Many2one('kwemp_employment_type',string="Employment Type")
    location = fields.Char(string='Office Location')
    branch_id = fields.Many2one("kw_res_branch", "Branch")
    department_id = fields.Many2one("hr.department", string='Department')
    # shift_id        = fields.Many2one('resource.calendar', "Shift")
    date_of_joining = fields.Date(string='Date of Joining')

    attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Attendance ID")
    check_in_mode = fields.Selection(related="attendance_id.check_in_through", string="Check IN Mode")
    no_of_present = fields.Integer("Present")
    no_of_absent = fields.Integer("Absent")
    no_of_leave = fields.Integer("Leave")
    no_of_tour = fields.Integer("Tour")
    no_of_wfo = fields.Integer("WFO")
    no_of_wfh = fields.Integer("WFH")
    no_of_wfa = fields.Integer("WFA")

    present = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="Present", compute="_compute_status")
    absent = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="Absent", compute="_compute_status")
    leave = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="Leave", compute="_compute_status")
    tour = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="Tour", compute="_compute_status")
    wfo = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="WFO", compute="_compute_status")
    wfh = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="WFH", compute="_compute_status")
    wfa = fields.Selection(selection=[('0', 'No'), ('1', 'Yes')], string="WFA", compute="_compute_status")

    status = fields.Char(string="Status", compute="_compute_status")
    mode = fields.Char(string="Mode", compute="_compute_status")
    floor = fields.Char(string="Floor")
    sbu = fields.Char(string="SBU")
    project = fields.Char(string="Projects Tagged")
    infra_location = fields.Char(string="Location")
    project_manager_id = fields.Char(string="Project Manager")
    workstation = fields.Char(string="Workstation")
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")

    work_location_type = fields.Selection(
        [('onsite', 'Onsite'), ('offsite', 'Offsite'), ('wfa', 'WFA'), ('hybrid', 'Hybrid')],
        string="Location Type")
    check_in_time = fields.Char(string="IN Time", related="attendance_id.check_in_time")
    check_out_time = fields.Char(string="OUT Time", related="attendance_id.check_out_time")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')], string="Gender")

    @api.multi
    def _compute_status(self):
        for report in self:
            status = "Absent"

            if report.no_of_tour:
                status = "On Tour"
            if report.no_of_leave:
                status = "On Leave"
            if report.no_of_present:
                status = "Present"

            mode = False
            if report.no_of_wfh:
                mode = "WFH"
            if report.no_of_wfo:
                mode = "WFO"
            if report.no_of_wfa:
                mode = "WFA"

            report.update({
                'present': str(report.no_of_present),
                'absent': str(report.no_of_absent),
                'leave': str(report.no_of_leave),
                'tour': str(report.no_of_tour),
                'wfo': str(report.no_of_wfo),
                'wfh': str(report.no_of_wfh),
                'wfa': str(report.no_of_wfa),
                'status': status,
                'mode': mode
            })

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            with project AS (
                SELECT  STRING_AGG(distinct p.name,', ') AS project_name,
                        p.active AS active_project,
                        STRING_AGG(distinct emp.name,', ') AS project_manager_id,
                        rt.emp_id AS employee_id
                        FROM kw_project_resource_tagging rt
                        JOIN project_project p ON p.id = rt.project_id
                        LEFT JOIN hr_employee emp ON emp.id = p.emp_id
                        LEFT JOIN hr_department d ON d.id = emp.department_id
                        LEFT JOIN hr_job j ON emp.job_id = j.id
                        WHERE rt.active = True AND p.active = True 
                        GROUP BY rt.emp_id, p.active 
            )

            SELECT  wa.id,  
            wa.id as assign_id, 
            wa.assign_date, 
            wa.employee_id,
			b.date_of_joining AS date_of_joining, 
			b.gender AS gender, 
			b.location AS work_location_type,
            CASE
                WHEN b.location='offsite'  THEN CASE
                                                    WHEN infra.id is not null then bu.name 
                                                ELSE 'Offsite' END
                WHEN b.location='wfa' THEN 'Work from Anywhere'
                ELSE 'Onsite' END
            AS location,
            a.id AS attendance_id, 
            a.branch_id, 
            a.department_id,
            a.check_in AS check_in, TO_CHAR(a.check_in, 'hh12:mi:ss AM') AS check_in_time,
            a.check_out AS check_out, TO_CHAR(a.check_out, 'hh12:mi:ss AM') AS check_out_time,
            a.worked_hours AS worked_hours,
            CASE  WHEN a.check_in is not null THEN 1 ELSE 0 END AS no_of_present,
            CASE  WHEN a.leave_day_value > 0 THEN 1 ELSE 0 END AS no_of_leave,
            CASE  WHEN a.is_on_tour = True THEN 1 ELSE 0 END AS no_of_tour,
            CASE  WHEN a.check_in is null and a.is_on_tour = False and a.leave_day_value in (null, 0) THEN 1 ELSE 0 END AS no_of_absent,
            CASE  WHEN a.work_mode = '{WFH_STATUS}' AND a.check_in is not null THEN 1 ELSE 0 END AS no_of_wfh,
            CASE  WHEN a.work_mode = '{WFO_STATUS}' AND a.check_in is not null THEN 1 ELSE 0 END AS no_of_wfo,
            CASE  WHEN a.work_mode = '{WFA_STATUS}' AND a.check_in is not null THEN 1 ELSE 0 END AS no_of_wfa,
            bu.name AS infra_location, 
            infra.name AS floor, 
            kwm.name AS workstation,
            (SELECT name FROM kw_sbu_master WHERE id = b.sbu_master_id) AS sbu,
            p.project_name AS project, 
            p.project_manager_id AS project_manager_id

            FROM kw_workstation_assign wa
            LEFT JOIN kw_daily_employee_attendance a ON a.employee_id=wa.employee_id AND a.attendance_recorded_date=wa.assign_date
            LEFT JOIN hr_employee b ON b.id=wa.employee_id
            LEFT JOIN kwemp_employment_type c ON c.id=b.employement_type
            LEFT JOIN kw_workstation_master kwm ON kwm.id = wa.workstation_id
            LEFT JOIN kw_workstation_infrastructure  infra ON infra.id = kwm.infrastructure
            LEFT JOIN kw_res_branch_unit bu ON infra.branch_unit_id = bu.id
            LEFT JOIN project p ON p.employee_id = wa.employee_id
            WHERE c.code !='O' AND b.active=True 
            ORDER BY assign_date desc
			
        )"""
        # print("pivot query",query)
        self.env.cr.execute(query)

