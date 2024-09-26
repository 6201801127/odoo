# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import  WFH_STATUS,  WFO_STATUS#LEAVE_STS_ALL_DAY, LEAVE_STS_FHALF, LEAVE_STS_SHALF,


class DailyAttendanceTracker(models.Model):
    _name = "kw_daily_attendance_tracker"
    _description = "Employee Attendance Tracking Report"
    _auto = False
    _rec_name = 'attendance_recorded_date'

    attendance_recorded_date = fields.Date(string='Date')
    branch_id   = fields.Many2one("kw_res_branch","Branch")
    department_id = fields.Many2one("hr.department",string='Department')
    shift_id = fields.Many2one('resource.calendar',"Shift")
    no_of_present = fields.Integer("Present")
    no_of_absent = fields.Integer("Absent")
    no_of_leave = fields.Integer("Leave")
    no_of_tour = fields.Integer("Tour")
    no_of_wfo = fields.Integer("WFO")
    no_of_wfh = fields.Integer("WFH")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select  row_number() over() as id,
            TBL.attendance_recorded_date,
            TBL.branch_id,
            TBL.department_id,
            TBL.shift_id,
            TBL.no_of_present,
            TBL.no_of_absent,
            TBL.no_of_leave,
            TBL.no_of_tour,
            TBL.no_of_wfo ,
            TBL.no_of_wfh from  
            (
            select attendance_recorded_date, branch_id,department_id,shift_id,                           
            SUM(CASE  WHEN a.check_in is not null THEN 1 ELSE 0 END) as no_of_present,
            SUM(CASE  WHEN a.leave_day_value > 0 THEN 1 ELSE 0 END) as no_of_leave,
            SUM(CASE  WHEN a.is_on_tour = True THEN 1 ELSE 0 END) as no_of_tour,
            SUM(CASE  WHEN a.check_in is null and a.is_on_tour = False and a.leave_day_value in (null,0) THEN 1 ELSE 0 END) as no_of_absent,
            SUM(CASE  WHEN a.work_mode = '{WFH_STATUS}' THEN 1 ELSE 0 END) as no_of_wfh,
            SUM(CASE  WHEN a.work_mode = '{WFO_STATUS}' THEN 1 ELSE 0 END) as no_of_wfo
            
            from kw_daily_employee_attendance a 
            group by branch_id,department_id,attendance_recorded_date,shift_id order by attendance_recorded_date desc
            ) TBL 
        )"""
        # print("tracker quey",query)
        self.env.cr.execute(query)
