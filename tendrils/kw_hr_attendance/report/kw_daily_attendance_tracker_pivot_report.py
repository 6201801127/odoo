# -*- coding: utf-8 -*-
# Added By (Gouranga) on 17-Feb-2021
# Outsource employees are removed from report 19 April 2021 (Gouranga)
# employee onsite ,offsite added and shift_id field removed 20 April 2021
from odoo import tools
from odoo import models, fields, api
from datetime import datetime,date
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import WFH_STATUS, WFO_STATUS, \
    WFA_STATUS  # LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF,


class DailyAttendanceTrackerPivotReport(models.Model):
    _name = "kw_daily_attendance_tracker_pivot_report"
    _description = "Employee Attendance Tracking Pivot Report"
    _auto = False
    _rec_name = 'attendance_recorded_date'

    attendance_recorded_date = fields.Date(string='Attendance Date')

    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_name = fields.Char(related="employee_id.name",string="Employee")
    emp_code = fields.Char(related="employee_id.emp_code",string="Employee Code")
    # employement_type = fields.Many2one('kwemp_employment_type',string="Employement Type")
    location = fields.Char(string='Office Location')
    branch_id = fields.Many2one("kw_res_branch", "Branch")
    department_id = fields.Many2one("hr.department", string='Department')
    # shift_id        = fields.Many2one('resource.calendar', "Shift")
    date_of_joining = fields.Date(string='Date of Joining')

    attendance_id = fields.Many2one('kw_daily_employee_attendance',string="Attendance ID")
    check_in_mode = fields.Selection(related="attendance_id.check_in_through",string="Check IN Mode")
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

    work_location_type = fields.Selection([('onsite','Onsite'),('offsite','Offsite'),('wfa','WFA')],string="Location Type")
    check_in_time = fields.Char(string="IN Time",related="attendance_id.check_in_time")
    check_out_time = fields.Char(string="OUT Time",related="attendance_id.check_out_time")
    gender = fields.Selection([('male','Male'),('female','Female'),('others','Others')],string="Gender")


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
            with project as (
                select  STRING_AGG(distinct p.name,', ') as project_name,
                        p.active as active_project,
                        STRING_AGG(distinct emp.name,', ') as project_manager_id,
                        rt.emp_id as employee_id
                        from kw_project_resource_tagging rt
                        join project_project p on p.id = rt.project_id
                        left join hr_employee emp on emp.id = p.emp_id
                        left join hr_department d on d.id = emp.department_id
                        left join hr_job j on emp.job_id = j.id
                        where rt.active = True and p.active = True 
                        group by rt.emp_id,p.active 
                        
            )
            select a.id, a.id as attendance_id,a.attendance_recorded_date,a.employee_id,
			b.date_of_joining as date_of_joining,b.gender as gender, b.location as work_location_type,
                case
                    when b.location='offsite'  then case
                                                        when infra.id is not null then bu.name 
                                                    else 'Offsite' end
                    when b.location='wfa' then 'Work from Anywhere'
                    else 'Onsite' end
                as location,
                a.branch_id,a.department_id,
                a.check_in as check_in,
				TO_CHAR(a.check_in, 'hh12:mi:ss AM') as check_in_time,
	            a.check_out as check_out,
				TO_CHAR(a.check_out, 'hh12:mi:ss AM') as check_out_time,
                a.worked_hours as worked_hours,
                CASE  WHEN a.check_in is not null THEN 1 ELSE 0 END as no_of_present,
                CASE  WHEN a.leave_day_value > 0 THEN 1 ELSE 0 END as no_of_leave,
                CASE  WHEN a.is_on_tour = True THEN 1 ELSE 0 END as no_of_tour,
                CASE  WHEN a.check_in is null and a.is_on_tour = False and a.leave_day_value in (null, 0) THEN 1 ELSE 0 END as no_of_absent,
                CASE  WHEN a.work_mode = '{WFH_STATUS}' and a.check_in is not null THEN 1 ELSE 0 END as no_of_wfh,
                CASE  WHEN a.work_mode = '{WFO_STATUS}' and a.check_in is not null THEN 1 ELSE 0 END as no_of_wfo,
                CASE  WHEN a.work_mode = '{WFA_STATUS}' and a.check_in is not null THEN 1 ELSE 0 END as no_of_wfa,
                bu.name as infra_location,infra.name as floor,kwm.name as workstation,
                (select name from kw_sbu_master where id = b.sbu_master_id) as sbu,
                p.project_name as project, p.project_manager_id as project_manager_id

                from kw_daily_employee_attendance a
                join hr_employee b on a.employee_id=b.id
                join kwemp_employment_type c on c.id=b.employement_type
                left join kw_workstation_hr_employee_rel rel on b.id = rel.eid
                left join kw_workstation_master kwm on kwm.id = rel.wid
                left join kw_workstation_infrastructure  infra on infra.id = kwm.infrastructure
                left join kw_res_branch_unit bu on infra.branch_unit_id = bu.id
                left join project p on p.employee_id = a.employee_id
                where c.code !='O' 
                order by attendance_recorded_date desc
                        
			
        )"""
        # print("pivot query",query)
        self.env.cr.execute(query)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        date_time_obj,date_time_end_obj = datetime.now(),datetime.now()
        if self._context.get('before_9am'):
            date_time_obj = datetime.strptime((str(datetime.now().date()) + ' 03:31:00'), '%Y-%m-%d %H:%M:%S')
            for dom in domain:
                if dom[0] == 'attendance_recorded_date':
                    date_time_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 03:31:00'
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            domain += [('check_in', '<', date_time_obj)]
        elif self._context.get('9am_to_9_30_am'):
            date_time_obj = datetime.strptime((str(datetime.now().date()) + ' 03:31:00'), '%Y-%m-%d %H:%M:%S')
            date_time_end_obj = datetime.strptime((str(datetime.now().date()) + ' 04:01:00'), '%Y-%m-%d %H:%M:%S')
            for dom in domain:
                if dom[0] == 'attendance_recorded_date':
                    date_time_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 03:31:00'
                    date_time_end_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 04:01:00'
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                    date_time_end_obj = datetime.strptime(date_time_end_str, '%Y-%m-%d %H:%M:%S')
            domain += [('check_in', '>=', date_time_obj), ('check_in', '<', date_time_end_obj)]
        elif self._context.get('9_31am_to_10_00_am'):
            date_time_obj = datetime.strptime((str(datetime.now().date()) + ' 04:01:00'), '%Y-%m-%d %H:%M:%S')
            date_time_end_obj = datetime.strptime((str(datetime.now().date()) + ' 04:31:00'), '%Y-%m-%d %H:%M:%S')

            for dom in domain:
                if dom[0] == 'attendance_recorded_date':
                    date_time_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 04:01:00'
                    date_time_end_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 04:31:00'
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                    date_time_end_obj = datetime.strptime(date_time_end_str, '%Y-%m-%d %H:%M:%S')
            domain += [('check_in', '>=', date_time_obj), ('check_in', '<', date_time_end_obj)]
        elif self._context.get('after_10am'):
            date_time_obj = datetime.strptime((str(datetime.now().date()) + ' 04:31:00'), '%Y-%m-%d %H:%M:%S')
            for dom in domain:
                if dom[0] == 'attendance_recorded_date':
                    date_time_str = (dom[2].replace(dom[2][dom[2].find('T'):],'') if dom[2].find('T') > 0 else dom[2]) + ' 04:31:00'
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            domain += [('check_in', '>', date_time_obj)]

        # print(domain)
        res = super(DailyAttendanceTrackerPivotReport, self).search_read(domain, fields, offset, limit, order)
        return res
