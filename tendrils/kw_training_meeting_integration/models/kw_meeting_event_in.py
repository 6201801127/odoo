# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api
# from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class MeetingScheduleIn(models.Model):
    _inherit = "kw_meeting_events"

    @api.model
    def create(self, values):
        meeting = super(MeetingScheduleIn, self).create(values)
        if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_training_schedule':
            session = self.env['kw_training_schedule'].browse(self._context['active_id'])
            if session and not meeting.recurrency and not meeting.parent_id:
                
                meeting_datetime    = datetime.strptime(meeting.kw_start_meeting_date.strftime(
                    "%Y-%m-%d") + ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S")
                hours, minutes      = divmod(meeting.duration * 60, 60)
                end_datetime        = meeting_datetime + timedelta(hours=hours, minutes=minutes)
                end_time            = end_datetime.strftime('%H:%M:%S')
                data                = {
                    'meeting_id':meeting.id,
                    'date': meeting.kw_start_meeting_date,
                    'from_time': meeting.kw_start_meeting_time,
                    'to_time': end_time
                }
                if meeting.location_id and meeting.meeting_room_id:
                    data['session_type'] = 'inside'
                elif (meeting.online_meeting and not meeting.meeting_room_id and not meeting.location_id) or (meeting.online_meeting and meeting.location_id and not meeting.meeting_room_id):
                    data['session_type'] = 'online'
                # print("create data is", data)
                session.write(data)
        return meeting
    
    @api.multi
    def write(self, values):
        result = super(MeetingScheduleIn, self).write(values)
        for meeting in self:
            session = self.env['kw_training_schedule'].sudo().search([('meeting_id', '=', meeting.id)])
            if session:

                meeting_datetime    = datetime.strptime(meeting.kw_start_meeting_date.strftime(
                    "%Y-%m-%d") + ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S")
                hours, minutes      = divmod(meeting.duration * 60, 60)
                end_datetime        = meeting_datetime + timedelta(hours=hours, minutes=minutes)
                end_time            = end_datetime.strftime('%H:%M:%S')
                data                = {
                    'date': meeting.kw_start_meeting_date,
                    'from_time': meeting.kw_start_meeting_time,
                    'to_time': end_time
                }
                if meeting.location_id and meeting.meeting_room_id:
                    data['session_type'] = 'inside'
                elif (meeting.online_meeting and not meeting.meeting_room_id and not meeting.location_id) or (meeting.online_meeting and meeting.location_id and not meeting.meeting_room_id):
                    data['session_type'] = 'online'
                # print("Write data is",data)
                session.write(data)
        return result
