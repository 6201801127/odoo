# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import ATD_STATUS_PRESENT,ATD_STATUS_ABSENT,ATD_STATUS_FHALF_ABSENT,ATD_STATUS_SHALF_ABSENT,DAY_STATUS_WORKING,DAY_STATUS_RWORKING,IN_STATUS_EARLY_ENTRY,IN_STATUS_ON_TIME

class AttendnaceSummaryReport(models.Model):
    
    _name           = "kw_attendance_summary_report"
    _description    = "Attendance Summary Report"
    _auto           = False
    _rec_name       = 'employee_id'

   
    employee_id                 = fields.Many2one(string='Employee',comodel_name='hr.employee',) 
    # department_id               = fields.Many2one(string='Department',comodel_name='hr.department')    
    # attendance_status           = fields.Integer(string='Attendance')    
    attendance_recorded_date    = fields.Date(string='Attendance Date',)    
    present_state               = fields.Integer(string='Present',)
    normal_entry_state          = fields.Integer(string='Normal Entry',)
    lwpc_state                  = fields.Integer(string='With Pay Cut',)
    lwopc_state                 = fields.Integer(string='With out Pay Cut',)

    state                       = fields.Selection(string="Attendance Status" ,selection=[('1', 'Present'), ('2', 'Absent'),  ('3', 'On Tour'),  ('4', 'On-leave')])
    day_status                  = fields.Selection(string="Day Status" ,selection=[('1', 'WeekHoliday'), ('0', 'Workingday'),('2', 'Holiday'),('3','RoasterWorkingDay'),('4', 'RoasterWeekHoliday')])
    shift_name                  = fields.Char(string='Shift Name', )
    check_in                    = fields.Datetime(string="Check In")
    check_out                   = fields.Datetime(string="Check Out")

    check_in_status             = fields.Selection(string='Office-in Status',selection=[('0', 'Early Entry'),('1', 'On Time'),('2', 'Late Entry'),('3', 'Extra Late Entry'),('4', 'Late Entry Half Day Leave'),('5', 'Late Entry Full Day Leave')])
    check_out_status            = fields.Selection(string='Office-out Status',selection=[('0', 'Early Exit'),('1', 'On Time'),('2', 'Late Exit'),('3', 'Extra Late Exit'),('4', 'Early Exit Half Day Leave')])
    le_state                    = fields.Selection(string="Late Entry Status" ,selection=[('0', 'Draft'),('1', 'Applied'), ('2', 'Granted'),('3', 'Forwarded')])
    le_action_status            = fields.Selection(string="Late Entry Action Status" ,selection=[('1', 'LateWPC'), ('2', 'LateWOPC')]) 

    @api.model_cr
    def init(self):
       
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
            SELECT id,employee_id,attendance_recorded_date,check_in,check_out,check_in_status,state,day_status ,le_action_status, le_state,shift_name,check_out_status,
            (case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') then 1 else 0 end) as present_state,
            (case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and (check_in_status ='{IN_STATUS_EARLY_ENTRY}' or check_in_status = '{IN_STATUS_ON_TIME}') then 1 else 0 end) as normal_entry_state,
            (case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and le_action_status ='1' then 1 else 0 end) as lwpc_state,
            (case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and le_action_status ='2' then 1 else 0 end) as lwopc_state

            FROM kw_daily_employee_attendance AT where day_status ='{DAY_STATUS_WORKING}' or day_status ='{DAY_STATUS_RWORKING}'
            

        )""" % (self._table))