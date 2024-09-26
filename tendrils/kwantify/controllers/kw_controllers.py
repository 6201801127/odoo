# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
from urllib.parse import urlparse
import pytz
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from Crypto.Cipher import AES
from Crypto import Random


class kwantify(http.Controller):

    @http.route('/auto-login/', auth='public', website=True, sitemap=False, methods=['GET'])
    def auto_login(self, *args, **kw):
        # return print(request.params)
        # content = base64.b64encode()
        # if 'qs' not in values and request.session.get('qs'):
        if 'qs' in request.params and request.params.get('qs') != '':
            login = request.params.get('qs')
            login_base64 = base64.b64decode(login)
        # return print(login_base64)
        return _login_and_redirect()
        # web_login

    def _login_and_redirect(self, db, login, key, redirect_url='/web'):
        uid = None
        dbname = None  
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()
        if not uid:
            uid = odoo.SUPERUSER_ID
        request.session.authenticate(db, login, key)
        return _set_cookie_and_redirect(redirect_url)

    def _set_cookie_and_redirect(self, redirect_url):
        redirect = werkzeug.utils.redirect(redirect_url, 303)
        redirect.autocorrect_location_header = False
        return redirect

    # method to redirect to kwantify v5
    @http.route('/auto-login-kwantify/', auth='user', methods=['GET'])
    def auto_login_kwantify(self, **kw):
        # kw_sync_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_auth.module_kw_auth_mode_status')
        kw_sync_enabled = True
        raw = url = ''
        if kw_sync_enabled:
            url = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_login_url')
            if not url or url is None:
                url = "https://portal.csmpl.com/OdooLogin.aspx"
                # url = "http://192.168.201.231/portal.csmpl.com/OdooLogin.aspx"
                # url = "http://172.27.34.48/prd.portalv6.csmpl.com/OdooLogin.aspx"
            raw = self._userstring(request.env.user.login)
            # raw = self._userstring('pradyut')#saisreer
            # print(raw)
            qs = self._encrypt(raw)
            url += '/?q=%s' % (qs.decode('utf8'))
            # print("urllllllllll================",request.url)
            new_url=http.request.httprequest.base_url
            parsed_url = urlparse(new_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            url += '?u=%s' % (base_url)

            # print("urllllllllll================",url)


            return werkzeug.utils.redirect(url)
        else:
            return werkzeug.utils.redirect('/web', )

    def _userstring(self, username):
        tz_india = pytz.timezone('Asia/Kolkata')
        datetime_object = datetime.datetime.now(tz_india)
        datetime_object = datetime_object.strftime("%Y-%m-%d %I:%M:%S %p")
        raw = f"username#{username}|timestamp#{datetime_object}"
        return raw

    def _encrypt(self, raw):
        # private_key = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_private_key')
        private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
        BLOCK_SIZE = 16
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

        raw = pad('b'+raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        enc = base64.b64encode(iv + cipher.encrypt(raw.encode("utf8")))
        # print(enc)
        return enc

    @http.route('/encryptuser/', methods=['POST'], auth='public', website=True, csrf=False, type='http', cors='*')
    def encrypt(self, **kw):
        try:
            raw = self._userstring(kw['username'])
            enc = self._encrypt(raw)
            return enc
        except ValueError as value_error:
            raise ValueError(value_error)

    @http.route('/decryptuser/', methods=['POST', ], auth='public', website=True, csrf=False, type='http', cors='*')
    def decrypt(self, **kw):
        # raise Warning('Lorem ipsum dolor sit amet')
        # Response.status = "400 Bad Request"
        # return
        try:
            # private_key = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_private_key')
            private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
            unpad = lambda s: s[:-ord(s[len(s) - 1:])]
            enc = kw['q'].replace(' ', '+')
            enc = base64.b64decode(enc)
            iv = enc[:16]
            cipher = AES.new(private_key, AES.MODE_CBC, iv)
            # cipher = AES.new(private_key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
            txt = unpad(cipher.decrypt(enc[16:]))
            # print(txt)
            return txt[1:]
        except ValueError as value_error:
            raise ValueError(value_error)

    @http.route('/about-us', auth='public', website=True)
    def aboutus(self, **args):
        return http.request.render('kwantify_theme.kwantify_about_us')

    @http.route(['/manifest.json'], type='http', auth="public")
    def robots(self, **kwargs):
        return request.render('kwantify.manifest', {'url_root': request.httprequest.url_root}, mimetype='application/json')
