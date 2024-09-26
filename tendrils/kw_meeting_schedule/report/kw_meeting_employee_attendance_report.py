# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class MeetingEmployeeAttendeeReport(models.Model):
    _name           = "kw_meeting_attendance_report"
    _description    = "Meeting Attendee Statistics"
    _auto           = False
    # _rec_name       = 'name'


   
    employee_id     = fields.Many2one(string='Employee',comodel_name='hr.employee',)
    
    attendance_status       = fields.Integer(string='Attendance')
    
    meeting_id      = fields.Many2one(string='Meeting',comodel_name='kw_meeting_events',)
    # start           = fields.Datetime(string='Start Datetime',)
    # stop            = fields.Datetime(string='stop',)
    duration        = fields.Float(string='Duration',)
    # meeting_year    = fields.Integer(string='Year',)

    @api.model_cr
    def init(self):
        # self._table = kw_meeting_tagwise_hour_expense_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            
            select id,event_id as meeting_id,(select ME.duration from kw_meeting_events ME where ME.id=MAT.event_id) as duration,employee_id as employee_id,
            CASE
                WHEN attendance_status=True THEN 1
                ELSE 0
            END as attendance_status from kw_meeting_attendee MAT where event_id not in (select id from kw_meeting_events where recurrency =True OR state ='cancelled')
            

        )""" % (self._table))