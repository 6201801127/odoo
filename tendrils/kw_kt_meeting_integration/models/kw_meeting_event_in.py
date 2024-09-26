# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api


class MeetingScheduleIn(models.Model):
    _inherit = "kw_meeting_events"

    @api.model
    def create(self, values):
        meeting = super(MeetingScheduleIn, self).create(values)
        if 'active_model' and 'active_id' in self._context and self._context['active_model'] == 'kw_time_line_plan':
            kt_time_line_plan = self.env['kw_time_line_plan'].browse(self._context['active_id'])
            if kt_time_line_plan and not meeting.recurrency and not meeting.parent_id:
                meeting_datetime = datetime.strptime(meeting.kw_start_meeting_date.strftime(
                    "%Y-%m-%d") + ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S")
                hours, minutes = divmod(meeting.duration * 60, 60)
                end_datetime = meeting_datetime + timedelta(hours=hours, minutes=minutes)
                end_time = end_datetime.strftime('%H:%M:%S')
                data = {
                    'meeting_id': meeting.id,
                    'kt_date': meeting.kw_start_meeting_date,
                    'start_time': meeting.kw_start_meeting_time,
                    'end_time': end_time
                }

                kt_time_line_plan.write(data)
        return meeting

    @api.multi
    def write(self, values):
        result = super(MeetingScheduleIn, self).write(values)
        for meeting in self:
            kt_time_line_plan = self.env['kw_time_line_plan'].sudo().search([('meeting_id', '=', meeting.id)])
            if kt_time_line_plan:
                meeting_datetime = datetime.strptime(meeting.kw_start_meeting_date.strftime(
                    "%Y-%m-%d") + ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S")
                hours, minutes = divmod(meeting.duration * 60, 60)
                end_datetime = meeting_datetime + timedelta(hours=hours, minutes=minutes)
                end_time = end_datetime.strftime('%H:%M:%S')
                data = {
                    'kt_date': meeting.kw_start_meeting_date,
                    'start_time': meeting.kw_start_meeting_time,
                    'end_time': end_time
                }

                kt_time_line_plan.write(data)
        return result
