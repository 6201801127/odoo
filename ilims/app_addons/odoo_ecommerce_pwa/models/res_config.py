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
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pwa_name = fields.Char(related="website_id.pwa_name", string="Name", readonly=False, help="Name is used in app install prompt.")
    pwa_short_name = fields.Char(related="website_id.pwa_short_name", string="Short Name", readonly=False, help="Short name is used on the user's home screen, launcher, or other places where space may be limited.")
    pwa_start_url = fields.Char(related="website_id.pwa_start_url", string="Start URL", readonly=False, help="Start URL tells the browser where your application should start when it is launched.")
    pwa_bk_color = fields.Char(related="website_id.pwa_bk_color", string="Background Color", readonly=False, help="Background color property is used on the splash screen when the application is first launched.")
    pwa_theme_color = fields.Char(related="website_id.pwa_theme_color", string="Theme Color", readonly=False, help="Theme color sets the color of the tool bar, and may be reflected in the app's preview in task switchers.")
    pwa_icon = fields.Binary(related="website_id.pwa_icon", string="Icon(512x512)", readonly=False, help="Icons are used in places like the home screen, app launcher, task switcher, splash screen, etc.")
    pwa_firebase_server_key = fields.Char(string="FCM Server Key", help="Firebase Cloud Messaging Server Key." ,readonly=False)
    pwa_firebase_api_key = fields.Char(string="FCM Api Key", help="FCM API Key(apiKey), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)
    pwa_firebase_sender_id = fields.Char(string="FCM Messaging Sender ID", help="FCM Messaging Sender ID(messagingSenderId), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)
    pwa_firebase_auth_domain = fields.Char(string="FCM Auth Domain", help="FCM Auth Domain(authDomain), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)
    pwa_firebase_database_url = fields.Char(string="FCM Database URL", help="FCM Database URL(databaseURL), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)
    pwa_firebase_project_id = fields.Char(string="FCM Project ID", help="FCM Project ID(projectId), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)
    pwa_firebase_app_id = fields.Char(string="FCM App ID", help="FCM App ID(appId), you can find this in firebase configuration(firebaseConfig)." ,readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings','pwa_firebase_server_key', self.pwa_firebase_server_key)
        IrDefault.set('res.config.settings','pwa_firebase_api_key', self.pwa_firebase_api_key)
        IrDefault.set('res.config.settings','pwa_firebase_sender_id', self.pwa_firebase_sender_id)
        IrDefault.set('res.config.settings','pwa_firebase_auth_domain', self.pwa_firebase_auth_domain)
        IrDefault.set('res.config.settings','pwa_firebase_database_url', self.pwa_firebase_database_url)
        IrDefault.set('res.config.settings','pwa_firebase_project_id', self.pwa_firebase_project_id)
        IrDefault.set('res.config.settings','pwa_firebase_app_id', self.pwa_firebase_app_id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'pwa_firebase_server_key' : IrDefault.get('res.config.settings','pwa_firebase_server_key', self.pwa_firebase_server_key),
            'pwa_firebase_api_key' : IrDefault.get('res.config.settings','pwa_firebase_api_key', self.pwa_firebase_api_key),
            'pwa_firebase_sender_id' : IrDefault.get('res.config.settings', 'pwa_firebase_sender_id', self.pwa_firebase_sender_id),
            'pwa_firebase_auth_domain' : IrDefault.get('res.config.settings','pwa_firebase_auth_domain', self.pwa_firebase_auth_domain),
            'pwa_firebase_database_url': IrDefault.get('res.config.settings', 'pwa_firebase_database_url', self.pwa_firebase_database_url),
            'pwa_firebase_project_id' : IrDefault.get('res.config.settings','pwa_firebase_project_id', self.pwa_firebase_project_id),
            'pwa_firebase_app_id' : IrDefault.get('res.config.settings', 'pwa_firebase_app_id', self.pwa_firebase_app_id),
        })
        return res
