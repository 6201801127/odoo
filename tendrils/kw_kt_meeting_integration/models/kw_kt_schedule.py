# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from odoo import models,fields,api
from odoo.exceptions import ValidationError

class KTSchedule(models.Model):
    _inherit                = "kw_time_line_plan"
 
    meeting_id              = fields.Many2one("kw_meeting_events",string="Meeting")
    venue                   = fields.Char(string="Venue", compute="_compute_if_venue")
    time_mismatch           = fields.Boolean(string="Meeting Time Behind..?",
                                            compute="compute_meeting_time",help="True if meeting time Less than session time")

    online_meeting          = fields.Boolean(string="Online Meeting ?",compute="compute_online_meeting")
    is_create_user          = fields.Boolean(string="Create User ?",compute="compute_online_meeting")
    participant_meeting    = fields.Boolean(string="Meeting Participant?",compute="compute_online_meeting")
    disable_meeting        = fields.Boolean(string="Disable Meeting",compute="compute_online_meeting") 




    @api.multi
    def compute_online_meeting(self):
        for session in self:
            if session.meeting_id:
                meeting                     = session.meeting_id
                session.online_meeting      = meeting.online_meeting
                session.is_create_user      = meeting.is_create_user
                session.participant_meeting = meeting.participant_meeeting

                if datetime.now() > session.meeting_id.start and datetime.now() < session.meeting_id.stop:
                    session.disable_meeting = True

    @api.multi
    def compute_meeting_time(self):
        for session in self:
            if session.meeting_id:
                meeting_date        = session.meeting_id.kw_start_meeting_date
                meeting_time        = session.meeting_id.kw_start_meeting_time
                session_date_time   = datetime.strptime(session.kt_date.strftime("%Y-%m-%d") + ' ' + session.start_time, "%Y-%m-%d %H:%M:%S")
                meeting_date_time   = datetime.strptime(meeting_date.strftime("%Y-%m-%d") + ' ' + meeting_time, "%Y-%m-%d %H:%M:%S")
                
                if session_date_time > meeting_date_time:
                    session.time_mismatch = True

    @api.multi
    def _compute_if_venue(self):
        for session in self:
            if session.meeting_id:
                session.venue = session.meeting_id.meeting_room_id.name

    @api.multi
    def action_start_online_meeting(self):
        return self.meeting_id.action_start_meeting()

    @api.multi
    def action_join_online_meeting(self):
        return self.meeting_id.action_join_meeting()
    
    @api.multi
    def schedule_meeting(self):
        current_date        = datetime.now().date()
        from_date_time      = datetime.strptime(self.kt_date.strftime("%Y-%m-%d")+ ' ' + self.start_time, "%Y-%m-%d %H:%M:%S")
        to_date_time        = datetime.strptime(self.kt_date.strftime("%Y-%m-%d")+ ' ' + self.end_time, "%Y-%m-%d %H:%M:%S")
        difference_time     = to_date_time - from_date_time
        duration            = difference_time.seconds/3600

        user_tz             = self.env.user.tz or 'UTC'
        local               = pytz.timezone(user_tz)
        utc_dt              = datetime.strftime(pytz.utc.localize(datetime.now()).astimezone(local), "%Y-%m-%d %H:%M:%S")
        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.strptime(utc_dt,"%Y-%m-%d %H:%M:%S")

        result_utc_datetime = from_date_time + UTC_OFFSET_TIMEDELTA
        stop                = result_utc_datetime + timedelta(hours=duration) - timedelta(seconds=1)

        # if duration < 0.5:
        #     raise ValidationError("At least 30 minutes duration should be given.")
        if self.end_time < self.start_time:
            raise ValidationError("End time can't be less than Start time.")
        if self.start_time == self.end_time:
            raise ValidationError("End time should be greater than Start time.")
        # if self.kt_date < current_date:
        #     raise ValidationError("Meeting date should not be less than current date.")

        participants        = (self.kt_view_id.applicant_id | self.employee_ids).ids
        
        view_id             = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        kt_tag              = self.env.ref('kw_meeting_schedule.meeting_type_104')
         
        return {
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_meeting_events',
            'view_mode' : 'form',
            'view_type' : 'form',
            'view_id'   : view_id,
            'target'    : 'self',
            'context'   : {
                'default_kw_start_meeting_date' : self.kt_date,
                'default_kw_start_meeting_time' : self.start_time,
                'default_start'                 : result_utc_datetime,
                'default_stop'                  : stop,
                'default_start_datetime'        : result_utc_datetime,
                'default_stop_datetime'         : stop,
                'default_duration'              : duration,
                # 'default_online_meeting'      : self.session_type == 'online' and 'zoom' or False,
                'default_name'                  : f'KT Meeting Schedule',
                'default_email_subject_line'    : f'KT Meeting Schedule',
                'default_kw_duration'           : str(duration),
                'default_employee_ids'          : [(6, 0, participants)],
                # 'default_training_session_id'   : self.id,
                'default_meeting_category'      : 'general',
                # 'default_agenda_ids'            : [[0,0,{'name':'KT Meeting Schedule'}]],
                'default_meeting_type_id'       : kt_tag.id,
                'pass_validation'               : 'True',
                # 'default_categ_ids'             : [(6, 0, kt_tag.ids)],
                # 'default_mom_required'        : True,
                # 'default_mom_controller_id'   : self.env.user.employee_ids and self.env.user.employee_ids[-1].id or False,
            }
        }
            
    @api.multi
    def view_meeting(self):
        view_id     = self.env.ref('kw_kt.view_kw_kt_meeting_calendar_event_form').id
        target_id   = self.meeting_id.id
        return {
            'name'      : 'Meeting Schedule',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_meeting_events',
            'res_id'    : target_id,
            'view_type' : 'form',
            'views'     : [(view_id, 'form')],
            'view_id'   : view_id,
            # 'flags'     : {'mode': 'readonly'},
        }

    

