# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import ATD_STATUS_PRESENT,ATD_STATUS_ABSENT,ATD_STATUS_TOUR,ATD_STATUS_LEAVE,IN_STATUS_EARLY_ENTRY,IN_STATUS_ON_TIME

class DeptAttendnaceSummaryReport(models.Model):
    
    _name           = "kw_dept_attendnace_summary_report"
    _description    = "Attendance Department Summary Report"
    _auto           = False
    _rec_name       = 'name'

   
    attendance_id               = fields.Many2one(string='Daily Attendance',comodel_name='kw_daily_employee_attendance',) 
    department_id               = fields.Many2one(string='Department',comodel_name='hr.department')    
    employee_id                 = fields.Many2one(string='Employee',comodel_name='hr.employee',) 
    name                        = fields.Char(string="Name")   
    attendance_recorded_date    = fields.Date(string='Attendance Date',)    
    absent_state                = fields.Integer(string='Absent',)
    normal_entry_state          = fields.Integer(string='In Time Login',)
    le_state                    = fields.Integer(string='Late Login',)
    state                       = fields.Selection(string="Attendance Status" ,selection=[(ATD_STATUS_PRESENT, 'Present'), (ATD_STATUS_ABSENT, 'Absent'),  (ATD_STATUS_TOUR, 'On Tour'),  (ATD_STATUS_LEAVE, 'On-leave')])
    
    @api.model_cr
    def init(self):
       
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
            SELECT EMP.id,EMP.id as employee_id,EMP.name,EMP.department_id,  ATD.id as attendance_id,ATD.state as state,ATD.attendance_recorded_date,(case when ATD.state ='{ATD_STATUS_ABSENT}' then 1 else 0 end) as absent_state,
            (case when ATD.state ='{ATD_STATUS_PRESENT}' and (ATD.check_in_status ='{IN_STATUS_EARLY_ENTRY}' or ATD.check_in_status = '{IN_STATUS_ON_TIME}') then 1 else 0 end) as normal_entry_state,
            (case when ATD.state ='{ATD_STATUS_PRESENT}' and (ATD.check_in_status !='{IN_STATUS_EARLY_ENTRY}' and ATD.check_in_status != '{IN_STATUS_ON_TIME}') then 1 else 0 end) as le_state

            FROM hr_employee EMP

            LEFT JOIN kw_daily_employee_attendance ATD ON EMP.id = ATD.employee_id
            WHERE EMP.department_id is not null

        )""" % (self._table))