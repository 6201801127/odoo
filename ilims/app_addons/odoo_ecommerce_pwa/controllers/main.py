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
from odoo import api, http, tools, _
from odoo.http import request
from odoo.tools.misc import file_open

import werkzeug
import json

import logging
_logger = logging.getLogger(__name__)

class WebsitePwa(http.Controller):

    @http.route('/pwa/offline', type='http', auth="public", website=True)
    def pwa_offline(self, **post):
        """Offline page stored in cache and used in offline mode"""
        return request.render("odoo_ecommerce_pwa.pwa_offline_page")

    @http.route(['/pwa_manifest'], type='http', auth="none", website=True)
    def get_pwa_manifest(self, **vals):
        """Return a json data used as manifest.json for PWA"""
        website = request.website
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        json_data = {
            "name": website.pwa_name,
            "short_name": website.pwa_short_name,
            "icons": [
                {
                    "src": str('%s/web/image/%s/%s/%s/48x48'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "48x48",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/72x72'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "72x72",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/96x96'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "96x96",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/144x144'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "144x144",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/152x152'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "152x152",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/168x168'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "168x168",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/192x192'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "192x192",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/256x256'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "256x256",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/384x384'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "384x384",
                    "type": "image/png"
                }, {
                    "src": str('%s/web/image/%s/%s/%s/512x512'% (base_url, 'website', website.id, 'pwa_icon')),
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "start_url": website.pwa_start_url,
            "display": "standalone",
            "background_color": website.pwa_bk_color,
            "theme_color": website.pwa_theme_color,
            "gcm_sender_id": "103953800507"
        }
        return request.make_response(json.dumps(json_data))

    @http.route(['/service_worker'], type='http', auth="none")
    def get_service_worker(self, **vals):
        """Return a service worker file in response, this URL used for providing root scope to our service worker script"""
        try:
            return http.Response(
                werkzeug.wsgi.wrap_file(
                    request.httprequest.environ,
                    file_open('odoo_ecommerce_pwa/static/src/js/service_worker.js', 'rb')
                ),
                content_type='application/javascript; charset=utf-8',
                headers=[('Cache-Control', 'max-age=36000')],
                direct_passthrough=True,
            )
        except IOError:
            _logger.debug("No moment locale for code service_worker",)
        return request.make_response("", headers=[
            ('Content-Type', 'application/javascript'),
            ('Cache-Control', 'max-age=36000'),
        ])

    @http.route(['/web_service_worker'], type='http', auth="none")
    def get_web_service_worker(self, **vals):
        """Return a service worker file in response for Web App, this URL used for providing root scope to our service worker script"""
        try:
            return http.Response(
                werkzeug.wsgi.wrap_file(
                    request.httprequest.environ,
                    file_open('odoo_ecommerce_pwa/static/src/js/web_service_worker.js', 'rb')
                ),
                content_type='application/javascript; charset=utf-8',
                headers=[('Cache-Control', 'max-age=36000')],
                direct_passthrough=True,
            )
        except IOError:
            _logger.debug("No moment locale for code service_worker",)
        return request.make_response("", headers=[
            ('Content-Type', 'application/javascript'),
            ('Cache-Control', 'max-age=36000'),
        ])

    @http.route(['/firebase-messaging-sw.js'], type='http', auth="none")
    def get_push_service_worker(self, **vals):
        """Return a service worker file in response, this URL used for providing root scope to our service worker script"""
        try:
            return http.Response(
                werkzeug.wsgi.wrap_file(
                    request.httprequest.environ,
                    file_open('odoo_ecommerce_pwa/static/src/js/push_sw.js', 'rb')
                ),
                content_type='application/javascript; charset=utf-8',
                headers=[('Cache-Control', 'max-age=36000')],
                direct_passthrough=True,
            )
        except IOError:
            _logger.debug("No moment locale for code service_worker",)
        return request.make_response("", headers=[
            ('Content-Type', 'application/javascript'),
            ('Cache-Control', 'max-age=36000'),
        ])

    @http.route('/pwa/user/registrations', type='json', auth='public')
    def pwa_user_registrations(self, token=False, **kw):
        if token:
            UserReg = request.env['pwa.user.registrations'].sudo()
            reg_obj = UserReg.search([('registration_key','=',token)])
            if reg_obj:
                return True
            vals = {
                'user_id' : int(request.uid),
                'registration_key' : token,
            }
            UserReg.create(vals)
            return True
        return False

    @http.route('/pwa/firebase/config', type='json', auth='public')
    def pwa_firebase_config(self, **kw):
        IrDefault = request.env['ir.default'].sudo()
        firebase_api_key = IrDefault.get('res.config.settings', 'pwa_firebase_api_key')
        firebase_auth_domain = IrDefault.get('res.config.settings', 'pwa_firebase_auth_domain')
        firebase_database_url = IrDefault.get('res.config.settings', 'pwa_firebase_database_url')
        firebase_project_id = IrDefault.get('res.config.settings', 'pwa_firebase_project_id')
        firebase_app_id = IrDefault.get('res.config.settings', 'pwa_firebase_app_id')
        firebase_sender_id = IrDefault.get('res.config.settings', 'pwa_firebase_sender_id')
        return {
            'apiKey' : firebase_api_key,
            'authDomain' : firebase_auth_domain,
            'databaseURL' : firebase_database_url,
            'projectId' : firebase_project_id,
            'appId' : firebase_app_id,
            'messagingSenderId' : firebase_sender_id
        }
        # return json.dumps(vals)
