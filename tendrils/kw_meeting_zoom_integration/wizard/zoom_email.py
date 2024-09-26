# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ..models.zoomus.client import ZoomClient
import json, requests
from odoo.exceptions import UserError, ValidationError, Warning


class EmailZoom(models.TransientModel):
    _name = 'zoom_email_employee'
    _description = 'Zoom Email for employee'

    zoom_id = fields.Char('Zoom Email ID')

    @api.multi
    def add_zoom_details(self):
        """ Add zoom email to company zoom account"""
        if not self.zoom_id:
            raise UserError(_("Please add Zoom email ID."))
        current_user = self.env.user
        if current_user and self.zoom_id:
            params = self.env['ir.config_parameter']
            jwt_api_key = str(params.sudo().get_param('kw_meeting_zoom_integration.api_key', False))
            jwt_api_secret = str(params.sudo().get_param('kw_meeting_zoom_integration.api_secret', False))
            # print('jwt_api_key : ', jwt_api_key, ' jwt_api_secret : ', jwt_api_secret)
            if jwt_api_key and jwt_api_secret:
                client = ZoomClient(jwt_api_key, jwt_api_secret)
                user_info = {
                    "email": self.zoom_id,
                    "type": 1,
                    "first_name": current_user.name[0:current_user.name.rindex(' ')] if ' ' in current_user.name else current_user.name,
                    "last_name": current_user.name[current_user.name.rindex(' ') + 1:] if ' ' in current_user.name else ''
                }
                zoom_response = client.user.create(action="create", user_info=user_info)
                # print(zoom_response)
                if zoom_response:
                    user_data = json.loads(zoom_response.content)
                    if user_data.get('code') == 1005:
                        raise UserError(_("Zoom User already exist in the account: %s.") % (self.zoom_id))
                    else:
                        if user_data.get('id'):
                            user_info['zoom_id'] = user_data.get('id')
                            user_info['user_id'] = current_user.id
                            zoom_user = self.env['kw_zoom_users'].find_or_create(user_info)
                            if zoom_user:
                                current_user.sudo().write({'zoom_id': zoom_user.id})
                                current_user.employee_ids.sudo().write({'zoom_email': user_info.get('email')})
                            self.env.user.notify_success(message='You might have got an email from zoom to authenticate.\nPlease approve the request.')
                else:
                    if zoom_response.status_code == 400:
                        raise ValidationError(_("Bad Request"))
                    if zoom_response.status_code == 409:
                        raise ValidationError(_("User with that email already exists: %s") % (self.zoom_id))
                    else:
                        raise UserError(_("Network error ! Please try again later.") % self.zoom_id)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

# try:
#                     zoom_response = client.user.create(action="create", user_info=user_info)
#                     # if zoom_response:
#                     user_data = json.loads(zoom_response.content)
#                     if user_data.get('id'):
#                         user_info['zoom_id'] = user_data.get('id')
#                         zoom_user = self.env['kw_zoom_users'].find_or_create(user_info)
#                         if zoom_user:
#                             current_user.sudo().write({'zoom_id': zoom_user.id})
#                             current_user.employee_ids.sudo().write({'zoom_email': user_info.get('email')})
#                         self.env.user.notify_success(message='You might have got an email from zoom to authenticate.\nPlease approve the request.')
#                 except:
#                     if user_data.get('code') == 1005:
#                         raise UserError(_("Email has already been used.: %s.") % (self.zoom_id))
#                     if user_data.get('code') == 409:
#                         raise UserError(_("User with that email already exists: %s.") % (self.zoom_id))     
#                 else:
#                     raise UserError(_("Network error ! Please try again later.") % self.zoom_id)
