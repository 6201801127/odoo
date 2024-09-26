# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from datetime import datetime
from odoo import api, fields, models
from .zoomus.client import ZoomClient
import json, requests


class ZoomMeeting(models.Model):
    _name = 'kw_zoom_meeting'
    _description = 'Zoom Meeting Information'
    _rec_name = 'topic'
    _order = "create_date desc"

    topic = fields.Char('Topic')
    agenda = fields.Char('Agenda')
    zoom_id = fields.Char('Zoom ID')
    uuid_zoom = fields.Char('UUID')
    host_id = fields.Char('Host ID')
    host_email = fields.Char('Host Email')
    """# 1-Instant meeting 2-Scheduled meeting 3- Recurring meeting with no fixed time 8-Recurring meeting with fix time"""
    type = fields.Integer('Type', default=2)
    start_time = fields.Char('Start Time')
    duration = fields.Char('Duration')  # In minutes
    schedule_for = fields.Char('Schedule For')
    timezone = fields.Char('Timezone')
    status = fields.Char('Status')
    created_at = fields.Char('Created at')
    start_url = fields.Char('Start URL')
    join_url = fields.Char('Join URL')
    password = fields.Char('Password')
    h323_password = fields.Char('H323 Password')
    pstn_password = fields.Char('PSTN Password')
    encrypted_password = fields.Char('Encr Password')
    misc_settings = fields.Text('Settings')
    meeting_id = fields.Many2one('kw_meeting_events', string='Meeting')

    def get_config_params(self, *args, **kwargs):
        param = self.env['ir.config_parameter'].sudo()
        return {
            "jwt_api_key": str(param.get_param('kw_meeting_zoom_integration.api_key')),
            "jwt_api_secret": str(param.get_param('kw_meeting_zoom_integration.api_secret')),
            "event_token": str(param.get_param('kw_meeting_zoom_integration.webhook_token'))
        }

    @api.multi
    def create_zoom_meeting(self, values):
        params = self.get_config_params()
        client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))
        if not values.get('start_datetime'):
            values['start_datetime'] = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        meeting_datetime = datetime.strptime(values.get('start_datetime'), "%Y-%m-%d %H:%M:%S")

        if self.env.user.zoom_id:
            """create zoom meeting api"""
            zoom_password = self.env.ref('kw_meeting_zoom_integration.kw_zoom_meeting_parameter').sudo().value
            # print(zoom_password,"zoom_password===============================")
            
            zoom_response = client.meeting.create(
                user_id=self.env.user.zoom_id.zoom_id,
                topic=values.get('name'),
                start_time=meeting_datetime,
                duration=values.get('duration') * 60,
                password=zoom_password)
            zvalues = json.loads(zoom_response.content)
            # print('zvalues >>>', zvalues)
            if zvalues.get('uuid'):
                z_ins = {
                    "zoom_id": zvalues.get('id'),
                    "uuid_zoom": zvalues.get('uuid') if zvalues.get('uuid') else '',
                    "topic": zvalues.get('topic') if zvalues.get('topic') else '',
                    "agenda": zvalues.get('agenda') if zvalues.get('agenda') else '',
                    "host_id": zvalues.get('host_id') if zvalues.get('host_id') else '',
                    "host_email": zvalues.get('host_email') if zvalues.get('host_email') else '',
                    "type": zvalues.get('type') if zvalues.get('type') else '',
                    "start_time": zvalues.get('start_time') if zvalues.get('start_time') else '',
                    "duration": zvalues.get('duration') if zvalues.get('duration') else '',
                    "schedule_for": zvalues.get('schedule_for') if zvalues.get('schedule_for') else '',
                    "timezone": zvalues.get('timezone') if zvalues.get('timezone') else '',
                    "status": zvalues.get('status') if zvalues.get('status') else '',
                    "created_at": zvalues.get('created_at') if zvalues.get('created_at') else '',
                    "start_url": zvalues.get('start_url') if zvalues.get('start_url') else '',
                    "join_url": zvalues.get('join_url') if zvalues.get('join_url') else '',
                    "password": zvalues.get('password') if zvalues.get('password') else '',
                    "h323_password": zvalues.get('h323_password') if zvalues.get('h323_password') else '',
                    "pstn_password": zvalues.get('pstn_password') if zvalues.get('pstn_password') else '',
                    "encrypted_password": zvalues.get('encrypted_password') if zvalues.get('encrypted_password') else '',
                    "misc_settings": zvalues.get('settings') if zvalues.get('settings') else '',
                }
                online_meet = self.create(z_ins)
                return online_meet
            else:
                return False
        else:
            return False

    @api.multi
    def update_zoom_meeting(self, values):
        params = self.get_config_params()
        client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))

        # meeting_datetime = datetime.strptime(self.start_datetime, "%Y-%m-%d %H:%M:%S")
        client.meeting.update(id=values.get("id"),
                              topic=values.get("topic"),
                              start_time=values.get("start_time"),
                              duration=values.get("duration")
                              )

        online_meet = self.search([('id', '=', values.get("meeting_id"))])
        online_meet.write({
            'topic': values.get("topic"),
            'start_time': values.get("start_time"),
            'duration': values.get("duration")
        })
        return True

    @api.model
    def delete_zoom_meeting(self, online_meet):
        params = self.get_config_params()
        client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))
        client.meeting.delete(id=online_meet.zoom_id)
        return online_meet.unlink() or False
