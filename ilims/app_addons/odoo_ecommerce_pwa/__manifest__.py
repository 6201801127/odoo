# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Website PWA (Progressive Web Application)",
  "summary"              :  """Progressive Web Applications uses web compatibilities and provides an application experience to the users. It is lightning fast in compared to the website and supports push notification.""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Progressive-Website-Application-PWA.html",
  "description"          :  """Odoo Website PWA
        Odoo PWA
        Progressive Web Application
        Push Notifications
        Offline Approach
        Offline Website
        Offline Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/demo_feedback?module=odoo_ecommerce_pwa",
  "depends"              :  ['website_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/config_demo_data.xml',
                             'data/push_notifications_cron.xml',
                             'views/template.xml',
                             'views/push_notifications_view.xml',
                             'views/res_config_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}