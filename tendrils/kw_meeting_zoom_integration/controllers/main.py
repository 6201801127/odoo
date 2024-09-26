# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request, Response
from base64 import b64encode
import json, requests
import werkzeug


class ZoomMeet(http.Controller):

    @http.route(['/zoom-events'], type='json', auth="public", methods=['POST'], csrf=False)
    def create_zoom_events_log(self, *args):
        payload_data = request.jsonrequest
        headers = request.httprequest.headers

        event_token = request.env['ir.config_parameter'].sudo().get_param('kw_meeting_zoom_integration.webhook_token')
        if not event_token:
            # Response.status = '403'
            return "Request cannot be validated."

        if event_token != headers.get('authorization'):
            # Response.status = '403'
            return "You are not authorised to access."

        if payload_data:
            log = request.env['kw_zoom_event_log'].sudo().create(payload_data)

        event_name = payload_data.get('event', '')
        payload = payload_data.get('payload', '')
        zoom_obj = payload.get('object')
        if event_name in ["user.created", "user.invitation_accepted", "user.activated"]:
            obj = request.env['kw_zoom_users'].update_zoom_user(zoom_obj)
        elif payload_data.get('event') in ["user.deactivated"]:
            obj = request.env['kw_zoom_users'].deactivate_zoom_user(zoom_obj)
        elif payload_data.get('event') in ["user.disassociated", "user.deleted"]:
            obj = request.env['kw_zoom_users'].unlink_zoom_user_webhook(zoom_obj)
        elif payload_data.get('event') == "meeting.participant_joined":
            obj = request.env['kw_meeting_events'].update_participant_webhook(zoom_obj)

        return {'status': True}

    @http.route(['/get_auth_credentials', '/get_auth_credentials?code=<string:code>'], type='http', auth="none")
    def get_auth_code(self, code=None, **kw):
        if code:
            user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
            company = user.company_id
            url = 'https://zoom.us/oauth/token' + '?grant_type=authorization_code' + '&code=' + code + '&redirect_uri=' + company.redirect_url

            client_key = "%s:%s" % (company.client_id, company.client_secret_key)

            basic = b64encode(client_key.encode("utf-8")).decode("utf-8")
            headers = {"Authorization": "Basic %s" % basic}
            result = requests.post(url, headers=headers)
            zoom_res = json.loads(result.content.decode("utf-8"))
            if not zoom_res.get('error'):
                res = company.sudo().write({'auth_code': code,
                                            'access_token': zoom_res.get('access_token'),
                                            'token_type': zoom_res.get('token_type'),
                                            'refresh_token': zoom_res.get('refresh_token'),
                                            'expires_in': zoom_res.get('expires_in'),
                                            'scope': zoom_res.get('scope'),

                                            })
            # else:
        redirect_url = "/web#id=%i&model=res.company&view_type=form" % company.id
        return werkzeug.utils.redirect(redirect_url or '', 301)
