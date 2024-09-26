# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, fields, models
from odoo.http import request
import json, requests
from base64 import b64encode
from .zoomus.client import ZoomClient
from odoo.exceptions import UserError, ValidationError, Warning


class MeetingEvent(models.Model):
    _inherit = 'res.company'

    zoom_id = fields.One2many(string='User', comodel_name='kw_zoom_users', inverse_name='company_id', )

    """JWT fields """
    jwt_api_key = fields.Char('API Key')
    jwt_api_secret = fields.Char('API Secret')
    jwt_user_id = fields.Char('Zoom User ID')
    event_token = fields.Char('Webhook Token', default='Z1sd0vIfTHib1PP4Q6WprA')

    """Auth2 fields """
    client_id = fields.Char('Client ID')
    client_secret_key = fields.Char('Client Secret')
    auth_url = fields.Char('Authorization URL', default="https://zoom.us/oauth/authorize")
    auth_token_url = fields.Char('Auth Token URL', default="https://zoom.us/oauth/token")
    base_url = fields.Char('Base URL', default="https://api.zoom.us/v2/")
    redirect_url = fields.Char('Redirect URL')
    auth_code = fields.Char('Auth Code', readonly="1")
    access_token = fields.Text('Access Token', readonly="1")
    refresh_token = fields.Text('Refresh Token', readonly="1")
    expires_in = fields.Integer('Expires In', readonly="1")
    token_type = fields.Char('Token Type', readonly="1")
    scope = fields.Text('Scope', readonly="1")

    @api.multi
    def connect_authorize(self):
        self.ensure_one()
        """Auth2 code """
        url = self.auth_url
        redirect_uri = self.redirect_url
        client_id = self.client_id
        request_url = url + '?' + 'response_type=code' + '&client_id=' + client_id + '&redirect_uri=' + redirect_uri
        return {
            'type': 'ir.actions.act_url',
            'url': request_url,
            'target': 'self',
        }

    @api.multi
    def refresh_token_action(self):
        self.ensure_one()
        """Auth2 code """
        request_url = self.auth_token_url + '?' + 'grant_type=refresh_token' + '&refresh_token=' + self.refresh_token

        client_key = "%s:%s" % (self.client_id, self.client_secret_key)
        basic = b64encode(client_key.encode("utf-8")).decode("utf-8")
        headers = {"Authorization": "Basic %s" % basic}
        result = requests.post(request_url, headers=headers)
        zoom_res = json.loads(result.content.decode("utf-8"))
        if not zoom_res.get('error'):
            res = self.write({
                'access_token': zoom_res.get('access_token'),
                'token_type': zoom_res.get('token_type'),
                'refresh_token': zoom_res.get('refresh_token'),
                'expires_in': zoom_res.get('expires_in'),
                'scope': zoom_res.get('scope'),
            })

        redirect_url = "/web#id=%i&model=res.company&view_type=form" % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': redirect_url,
            'target': 'self',
        }

    @api.multi
    def user_detail_action_test(self):
        # print('zoom_id >> ', self.env.user.zoom_id)
        pass

    @api.multi
    def past_meeting_participants(self, meeting_id):
        client = ZoomClient(self.jwt_api_key, self.jwt_api_secret)
        zoom_res = json.loads(client.past_meeting.get_participants(meeting_id=meeting_id).content)
        return True

    @api.multi
    def user_detail_action(self):
        if self.env.user:
            jwt_api_key = self.env.user.company_id.jwt_api_key
            jwt_api_secret = self.env.user.company_id.jwt_api_secret
        if self.id:
            jwt_api_key = self.jwt_api_key
            jwt_api_secret = self.jwt_api_secret

        """JWT Code"""
        if self.jwt_api_key and self.jwt_api_secret:
            client = ZoomClient(self.jwt_api_key, self.jwt_api_secret)
            user_list_response = client.user.list()
            user_list = json.loads(user_list_response.content)
            # print(user_list)
            self.env['kw_zoom_users'].search([]).write({'active': False, 'status': 'inactive'})
            for user in user_list['users']:
                # print('user---------->',user)
                user_id = user['id']
                zoom_res = json.loads(client.user.get(id=user_id).content)
                # print('zoom_res----->',zoom_res)
                if zoom_res.get('id'):  # and zoom_res.get('role_name') and zoom_res.get('role_name') == 'Owner':
                    zoom_res['zoom_id'] = zoom_res.get('id')
                    zoom_res['active'] = True
                    del zoom_res['id']
                    if 'location' in zoom_res:
                        del zoom_res['location']
                    if 'job_title' in zoom_res:
                        del zoom_res['job_title']
                    user_rec = self.env['res.users'].search([('email', '=', zoom_res.get('email'))])
                    if user_rec:
                        zoom_res['user_id'] = user_rec.id
                    """create or edit zoom user"""
                    zoom_rec = self.env['kw_zoom_users'].create_or_write(zoom_res)
                    """update zoom user id in res_user"""
                    if user_rec:
                        user_rec.write({'zoom_id': zoom_rec.id})
        else:
            raise ValidationError("Please enter Zoom API key and API secret details.")
        # print('User synced successfully.........')

        """Auth2 code """
        # request_url = self.base_url + 'users/me'
        # headers = {"Authorization": "Bearer %s" % self.access_token}
        # result = requests.get(request_url, headers=headers)
        # zoom_res = json.loads(result.content.decode("utf-8"))
        # print('---------------------user zoom---------------->', zoom_res)
        redirect_url = "/web#id=%i&model=res.company&view_type=form" % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': redirect_url,
            'target': 'self',
        }

    @api.multi
    def create_meeting_action(self):
        self.ensure_one()
        """JWT Code"""
        zoom_password = self.env.ref('kw_meeting_zoom_integration.kw_zoom_meeting_parameter').sudo().value
        # print(zoom_password,"zoom_password===============================")
        client = ZoomClient(self.jwt_api_key, self.jwt_api_secret)
        zoom_response = client.meeting.create(user_id=self.jwt_user_id, topic="JWT Test Meeting",
                                              start_time=datetime.fromisoformat("2020-07-03 10:30:00"), duration="10",
                                              password=zoom_password)
        # zoom_response = client.meeting.create(json.dumps(payload))
        meeting = json.loads(zoom_response.content)
        # print(meeting)
        """Auth2 code """
        # request_url = self.base_url + 'users/u9995QorQhW_EHkM6Y_b9A/meetings'
        #
        # headers = {'content-type': "application/json", "Authorization": "Bearer %s" % self.access_token}
        # # print('<>>>>>>>>>>>>>>', headers)
        # print('<>>>>>>>>>>>>>>', request_url)
        # payload = {"topic": "Test Meeting",
        #            "type": "2",
        #            "start_time": "2020-07-02T01:30:00Z",
        #            "duration": "10",
        #            "schedule_for": "",
        #            "timezone": "Asia/Calcutta",
        #            "password": "Csmpl@123",
        #            "agenda": "Info Test Meeting"}
        # result = requests.post(request_url, data=json.dumps(payload), headers=headers)
        # zoom_res = json.loads(result.content.decode("utf-8"))
        # print(zoom_res)

        redirect_url = "/web#id=%i&model=res.company&view_type=form" % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': redirect_url,
            'target': 'self',
        }

    # @api.multi
    # def create_user(self):
    #     """JWT Code"""
    #     client = ZoomClient(self.jwt_api_key, self.jwt_api_secret)
    #     user_info = {
    #         "email": "amulya.pati@csm.tech",
    #         "type": 1,
    #         "first_name": "Amulya",
    #         "last_name": "Pati"
    #     }
    #     zoom_response = client.user.create(action="create", user_info=user_info)
    #     user_data = json.loads(zoom_response.content)
    #     print("===================================")
    #     print(user_data)
    #
    #     redirect_url = "/web#id=%i&model=res.company&view_type=form" % self.id
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': redirect_url,
    #         'target': 'self',
    #     }`

    def get_config_params(self, *args, **kwargs):
        param = self.env['ir.config_parameter'].sudo()
        return {
            "jwt_api_key": str(param.get_param('kw_meeting_zoom_integration.api_key')),
            "jwt_api_secret": str(param.get_param('kw_meeting_zoom_integration.api_secret')),
            "event_token": str(param.get_param('kw_meeting_zoom_integration.webhook_token'))
        }
