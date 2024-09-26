# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from odoo import models,fields,api
from odoo.exceptions import ValidationError

class TrainingSchedule(models.Model):
    _inherit                = "kw_training_schedule"

    @api.model
    def get_meeting_domain(self):
        domain = []
        if 'default_schedule_id' in self._context:
            session = self.env['kw_training_schedule'].browse(self._context['default_schedule_id'])
            plan = session.training_id.plan_ids
            meeting_type_id = self.env.ref('kw_meeting_schedule.meeting_type_100').id
            from_date_time = datetime.strptime(session.date.strftime(
                "%Y-%m-%d") + ' ' + session.from_time, "%Y-%m-%d %H:%M:%S")
            to_date_time = datetime.strptime(session.date.strftime(
                "%Y-%m-%d") + ' ' + session.to_time, "%Y-%m-%d %H:%M:%S")
            difference_time = to_date_time - from_date_time
            duration = difference_time.seconds/3600
            # domain_search =
            domain += [
                ('kw_start_meeting_date', '=', session.date),
                ('kw_start_meeting_time', '=', session.from_time),
                ('duration', '=', duration),
                ('meeting_type_id','=',meeting_type_id),
                ('recurrency', '=', False)
                    ]
            # meetings = self.env['kw_meeting_events'].search(domain_search)
            # meetind_ids = meetings.filtered(lambda r: r.employee_ids <= plan.participant_ids)
            # domain += [('id', 'in', meetind_ids.ids)]
             
        else:
            domain += [('id','in',[])]
        # print("Generated domain is",domain)
        return domain         

    meeting_id              = fields.Many2one("kw_meeting_events",string="Meeting",domain=get_meeting_domain)
    venue                   = fields.Char(string="Venue", compute="_compute_if_venue")
    time_mismatch           = fields.Boolean(string="Meeting Time Behind..?",compute="compute_meeting_time",help="True if meeting time Less than session time")

    online_meeting          = fields.Boolean(string="Online Meeting ?",compute="compute_online_meeting")
    is_create_user          = fields.Boolean(string="Create User ?",compute="compute_online_meeting")
    participant_meeting    = fields.Boolean(string="Meeting Participant?",compute="compute_online_meeting")
    disable_meeting        = fields.Boolean(string="Disable Meeting",compute="compute_online_meeting")

    @api.multi
    def manage_meeting(self):
        _action = {
            'name'      : 'Manage Meeting',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_training_schedule',
            'res_id'    : self.ids[0],
            'view_type' : 'form',
            'target'    : 'new',
            'nodestroy' : True,
            'context'   : {},
            }
        if self.meeting_id:
            view_id = self.env.ref('kw_training_meeting_integration.view_kw_training_schedule_edit_remove_meeting_form').id
            _action['views']    = [(view_id, 'form')]
            _action['view_id']  = view_id
            if datetime.now() > self.meeting_id.start:
                _action['context']['hide_edit'] = True
            if self.attendance_id:
                _action['context']['hide_save'] = True
        else:
            view_id = self.env.ref('kw_training_meeting_integration.view_kw_training_schedule_create_tag_meeting_form').id
            _action['views']    = [(view_id, 'form')]
            _action['view_id']  = view_id
        return _action

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
                session_date_time   = datetime.strptime(session.date.strftime("%Y-%m-%d") + ' ' + session.from_time, "%Y-%m-%d %H:%M:%S")
                meeting_date_time   = datetime.strptime(meeting_date.strftime("%Y-%m-%d") + ' ' + meeting_time, "%Y-%m-%d %H:%M:%S")
                
                # user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                # curr_datetime = datetime.now(tz=user_tz).replace(tzinfo=None)

                if session_date_time > meeting_date_time:
                    session.time_mismatch = True

                # if curr_datetime > meeting_date_time:
                #     session.meeting_over = True

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
    def action_remove_meeting(self):
        self.write({"meeting_id":False})
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def schedule_meeting(self):
        current_date        = datetime.now().date()
        from_date_time      = datetime.strptime(self.date.strftime("%Y-%m-%d")+ ' ' + self.from_time, "%Y-%m-%d %H:%M:%S")
        to_date_time        = datetime.strptime(self.date.strftime("%Y-%m-%d")+ ' ' + self.to_time, "%Y-%m-%d %H:%M:%S")
        difference_time     = to_date_time - from_date_time
        duration            = difference_time.seconds/3600

        user_tz             = self.env.user.tz or 'UTC'
        local               = pytz.timezone(user_tz)
        utc_dt              = datetime.strftime(pytz.utc.localize(datetime.now()).astimezone(local), "%Y-%m-%d %H:%M:%S")
        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.strptime(utc_dt,"%Y-%m-%d %H:%M:%S")

        result_utc_datetime = from_date_time + UTC_OFFSET_TIMEDELTA
        stop                = result_utc_datetime + timedelta(hours=duration) - timedelta(seconds=1)

        if duration < 0.5:
            raise ValidationError("At least 30 minutes duration should be given.")
        if self.to_time < self.from_time:
            raise ValidationError("End time can't be less than Start time.")
        if self.from_time == self.to_time:
            raise ValidationError("End time should be greater than Start time.")
        if self.date < current_date:
            raise ValidationError("Meeting date should not be less than current date.")

        participants        = []
        if self.training_id.plan_ids and self.training_id.plan_ids[-1].participant_ids:
            participants    = self.training_id.plan_ids[-1].participant_ids.ids
        participants        += self.instructor.ids
        view_id             = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        training_tag        = self.env.ref('kw_meeting_schedule.meeting_type_100')

        return {
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_meeting_events',
            'view_mode' : 'form',
            'view_type' : 'form',
            'view_id'   : view_id,
            'target'    : 'self',
            'context'   : {
                'default_kw_start_meeting_date' : self.date,
                'default_kw_start_meeting_time' : self.from_time,
                'default_start'                 : result_utc_datetime,
                'default_stop'                  : stop,
                'default_start_datetime'        : result_utc_datetime,
                'default_stop_datetime'         : stop,
                'default_duration'              : duration,
                # 'default_online_meeting'      : self.session_type == 'online' and 'zoom' or False,
                'default_name'                  : f'{self.training_id.name} - {self.subject}',
                'default_email_subject_line'    : f'{self.training_id.name} - {self.subject}',
                'default_kw_duration'           : str(duration),
                'default_employee_ids'          : [(6, 0, participants)],
                'default_training_session_id'   : self.id,
                'default_meeting_category'      : 'general',
                'default_agenda_ids'            : [[0,0,{'name':self.subject}]],
                'default_meeting_type_id'       : training_tag.id,
                'default_categ_ids'             : [(6, 0, training_tag.ids)],
                # 'default_mom_required'        : True,
                # 'default_mom_controller_id'   : self.env.user.employee_ids and self.env.user.employee_ids[-1].id or False,
            }
        }
            
    @api.multi
    def view_meeting(self):
        view_id     = self.env.ref('kw_training_meeting_integration.view_kw_training_meeting_calendar_event_form').id
        target_id   = self.meeting_id.id
        return {
            'name'      : 'Meeting Activities',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_meeting_events',
            'res_id'    : target_id,
            'view_type' : 'form',
            'views'     : [(view_id, 'form')],
            'view_id'   : view_id,
            # 'flags'     : {'mode': 'readonly'},
        }
    
    @api.multi
    def write(self, values):
        result = super(TrainingSchedule, self).write(values)
        if 'meeting_id' in values and values['meeting_id']:
            meeting = self.env['kw_meeting_events'].browse(values['meeting_id'])
            for session in self:
                participants = self.env['hr.employee']
                if session.training_id.plan_ids and session.training_id.plan_ids[-1].participant_ids:
                    participants |= session.training_id.plan_ids[-1].participant_ids
                participants |= session.instructor
                participants |= meeting.employee_ids
                meeting.write({'employee_ids': [(6, 0, participants.ids)]})
        return result
    
