# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models, _
from odoo.http import request
from datetime import datetime

import requests
import json
import logging
_logger = logging.getLogger(__name__)

class WebPushNotifiactions(models.Model):
    _name = 'pwa.push.notifications'
    _order = 'create_date desc'
    _description = "PWA Push Notifications"

    name = fields.Char(string='Title', required=True, translate=True)
    message = fields.Char(string='Body', required=True, translate=True)
    image = fields.Binary(string='Browse Logo')
    redirect_url = fields.Char(string='Target Link', required=True)
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validated'), ('sent', 'Sent'), ('cancel', 'Canceled'), ('error','Error')], default="draft", string="State")
    image_type = fields.Selection([ ('url', 'URL'),('base_64', 'Browse')], string="Select Logo", help="Select the log you want to display in the notification", required=True)
    image_url = fields.Char(string='Logo URL', help="URL of the image you want ot display ")
    summary = fields.Text(string="Sent Summary")
    last_sent_date = fields.Date(string="Last Sent Date")
    is_scheduled = fields.Selection([('y', 'Yes'),('n', 'No')], string="Schedule Notification", default="n")
    schedule_date = fields.Date(string="Schedule Date")
    send_to = fields.Selection(
        [('all', 'All'),
        ('odoo_users', 'Odoo Users'),
        ('public_users', 'Public Users'),
        ('portal_users', 'Website Users')],
        string='Target User Type',
        default='all',
        required=True,
        help="users for which you want send the notifications")

    @api.model
    def get_api_key(self):
        IrDefault = self.env['ir.default'].sudo()
        firebase_api_key = IrDefault.get('res.config.settings', 'pwa_firebase_server_key')
        return firebase_api_key

    def get_notification_data(self):
        self.ensure_one()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        data = {
            'title' : self.name,
            'body' : self.message,
            'icon' : '/odoo_ecommerce_pwa/static/src/img/launcher_192.png',
            'click_action' : self.redirect_url,
        }
        if self.image_type == 'url':
            data['icon'] = str(self.image_url)
        else:
            data['icon'] = str('%s/web/image/%s/%s/%s'% (base_url, 'pwa.push.notifications', self.id, 'image'))
        return data

    def send_pwa_push_notification(self):
        self.ensure_one()
        state = 'draft'
        msg = ''
        api_key = self.get_api_key()
        reg_keys = self.env["pwa.user.registrations"].get_registration_ids(type=self.send_to)
        if not api_key:
            state = 'error'
            msg = 'No api key found, please enter the api key in the configuration.'
        else:
            url = 'https://fcm.googleapis.com/fcm/send'
            body = {
                'registration_ids': reg_keys,
                'notification': self.get_notification_data(),
            }
            api_key = 'Key=%s' % api_key
            headers = {'Authorization':api_key,'Content-Type': 'application/json'}
            try:
                result = requests.post(url, data=json.dumps(body), headers=headers)
                _logger.info("-------------result----text-----%r-----------",result.text)
                result = eval(result.text)
                state = 'sent'
                msg = 'Message Broadcasted Successfully \n No of Success = %s \n No. of Failures = %s'%(result.get('success', 0), result.get('failure', 0))
            except Exception as e:
                state = 'error'
                msg = 'Error in Sending push notifications: %s' % e
        if state != 'draft':
            self.write({
                'state': state,
                'summary': msg,
                'last_sent_date': datetime.now(),
            })
        # return msg

    @api.model
    def send_pwa_scheduled_notifications(self):
        records = self.search([('state','=','validate'),('is_scheduled','=','y'),('schedule_date','=',fields.Date().today()),('send_to','!=',None)])
        for rec in records:
            rec.send_pwa_push_notification()

    def set_to_draft(self):
        self.state = 'draft'
        return True

    def validate_template_data(self):
        self.state = 'validate'
        return True

class UserRegistrations(models.Model):
    _name = 'pwa.user.registrations'
    _order = 'create_date'
    _description = "PWA Push Notifications"

    user_id = fields.Many2one(comodel_name='res.users', string="User")
    registration_key = fields.Char(string='Registration Key', required=True)

    @api.model
    def get_registration_ids(self, type=None):
        public_id = self.env.ref('base.group_public').id
        portal_id = self.env.ref('base.group_portal').id
        reg_keys = []
        records = self.search([])
        if type == 'all':
            reg_keys = records.mapped('registration_key')
        elif type == 'portal_users':
            sel_recs = records.filtered(lambda rec: portal_id in rec.user_id.groups_id.ids)
            reg_keys = sel_recs.mapped('registration_key')
        elif type == 'public_users':
            sel_recs = records.filtered(lambda rec: public_id in rec.user_id.groups_id.ids)
            reg_keys = sel_recs.mapped('registration_key')
        elif type == 'odoo_users':
            portal_id = self.env.ref('base.group_portal').id
            sel_recs = records.filtered(lambda rec: [public_id , portal_id] not in rec.user_id.groups_id.ids)
            reg_keys = sel_recs.mapped('registration_key')
        elif type == 'public_users':
            sel_recs = records.filtered(lambda rec: public_id in rec.user_id.groups_id.ids)
            reg_keys = sel_recs.mapped('registration_key')
        return reg_keys
