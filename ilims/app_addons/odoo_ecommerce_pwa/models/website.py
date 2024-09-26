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
from odoo import api, fields, models

class Website(models.Model):
    _inherit = 'website'

    pwa_name = fields.Char("Name", help="Name is used in app install prompt.")
    pwa_short_name = fields.Char("Short Name", help="Short name is used on the user's home screen, launcher, or other places where space may be limited.")
    pwa_start_url = fields.Char("Start URL", help="Start URL tells the browser where your application should start when it is launched.")
    pwa_bk_color = fields.Char("Background Color", help="Background color property is used on the splash screen when the application is first launched.")
    pwa_theme_color = fields.Char("Theme Color", help="Theme color sets the color of the tool bar, and may be reflected in the app's preview in task switchers.")
    pwa_icon = fields.Binary("Icon(512x512)", help="Icons are used in places like the home screen, app launcher, task switcher, splash screen, etc.")
