# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class MeetingAttendeeReport(models.Model):
    _name           = "kw_meeting_monthwise_attendee_report"
    _description    = "Meeting Attendee Statistics"
    _auto           = False
    _rec_name       = 'name'


    name            = fields.Char(string='Subject',) 
    employee_id     = fields.Many2one(string='Employee',comodel_name='hr.employee',)
    partner_id      = fields.Many2one(string='Partner',comodel_name='res.partner',)

    user_type       = fields.Selection(string='User Type',selection=[('internal', 'Internal Users(Employee)'),('external', 'External Participants')],)
    
    meeting_id      = fields.Many2one(string='Meeting',comodel_name='kw_meeting_events',)
    start           = fields.Datetime(string='Start Datetime',)
    # stop            = fields.Datetime(string='stop',)
    duration        = fields.Float(string='Duration',)
    meeting_year    = fields.Integer(string='Year',)

    @api.model_cr
    def init(self):
        # self._table = kw_meeting_tagwise_hour_expense_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            
            SELECT CONCAT(MS.id,'HR',ATTENDEE_TBL.employee_id,'PT',ATTENDEE_TBL.partner_id) as id,MS.id as meeting_id,MS.name,MS.start,MS.stop,MS.duration,MS.mom_controller_id, date_part('year', start)as meeting_year, ATTENDEE_TBL.employee_id, ATTENDEE_TBL.partner_id, ATTENDEE_TBL.user_type
            FROM kw_meeting_events MS
            INNER JOIN 
            (  select kw_meeting_events_id as event_id,hr_employee_id as employee_id,NULL as partner_id,'internal' as user_type from hr_employee_kw_meeting_events_rel
                union 
               select kw_meeting_events_id as event_id,NULL as employee_id,res_partner_id as partner_id,'external' as user_type from kw_meeting_schedule_res_partner_rel
            )as ATTENDEE_TBL 
            
            ON ATTENDEE_TBL.event_id = MS.id  AND MS.recurrency =	False AND MS.state !='cancelled'

        )""" % (self._table))