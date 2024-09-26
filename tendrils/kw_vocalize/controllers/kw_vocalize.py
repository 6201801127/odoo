import base64
import datetime
import pytz
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi

import odoo.modules.registry
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response

from Crypto.Cipher import AES
from Crypto import Random


class VocalizeForm(http.Controller):

    @http.route('/go-for-voting/', auth='public', method="post", website=True, csrf=False)
    def button_click(self, **kw):
        kw_sync_enabled = True
        raw = url = ''
        if kw_sync_enabled:
            url = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_vocalize_url')
            if not url or url is None:
                # url = "http://164.164.122.169:8060/Vocalizelocals_stg/voting"
                url = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_vocalize_voting_url')
                # url = "http://192.168.201.231/portal.csmpl.com/OdooLogin.aspx"
                # url = "http://172.27.34.48/prd.portalv6.csmpl.com/OdooLogin.aspx"
            raw = self._userstring(request.env.user)
            # raw = self._userstring('pradyut')#saisreer
            # print('raw=====', raw)
            qs = self._encrypt(raw)
            qs = base64.b64encode(qs)
            url += '/%s' % (qs.decode('utf8'))
            return werkzeug.utils.redirect(url)
        else:
            return werkzeug.utils.redirect('/web', )

        # return request.render('kw_vocalize.button_click_template')

    def _userstring(self, user):
        tz_india = pytz.timezone('Asia/Kolkata')
        datetime_object = datetime.datetime.now(tz_india)
        employee_name = user.employee_ids.name
        empl_mail = user.employee_ids.work_email

        datetime_object = datetime_object.strftime("%Y-%m-%d %I:%M:%S %p")
        raw = f"name#{employee_name}|email#{empl_mail}|datetime#{datetime_object}"

        # print('raw_bas64----',raw,type(raw))
        return raw

    def _encrypt(self, raw):
        # private_key = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_private_key')
        private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
        BLOCK_SIZE = 16
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        raw = pad('b' + raw)
        # print('rawbyte', raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        enc = base64.b64encode(iv + cipher.encrypt(raw.encode("utf8")))
        # print(enc)
        return enc

    # @http.route('/encryptuser/', methods=['POST'], auth='public', website=True, csrf=False, type='http', cors='*')
    # def encrypt(self, **kw):
    #     try:
    #         raw = self._userstring(kw['name','email','datetime'])
    #         enc = self._encrypt(raw)
    #         return enc
    #     except ValueError as value_error:
    #         raise ValueError(value_error)

    @http.route('/decryptuser/', methods=['POST', ], auth='public', website=False, csrf=False, type='http', cors='*')
    def decrypt(self, **kw):
        # Response.status = "400 Bad Request"
        try:
            # private_key = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_private_key')
            private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
            unpad = lambda s: s[:-ord(s[len(s) - 1:])]
            enc = kw['q'].replace(' ', '+')
            # enc = kw['q']
            # print(enc)
            enc = base64.b64decode(enc)
            iv = enc[:16]
            cipher = AES.new(private_key, AES.MODE_CBC, iv)
            # cipher = AES.new(private_key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
            txt = unpad(cipher.decrypt(enc[16:]))
            # print('decypt----', txt)
            return txt[1:]
        except ValueError as value_error:
            raise ValueError(value_error)

    @http.route('/vocalize-voting/', auth='public', method="post", website=True, type='http', csrf=False)
    def vocalize_user(self, **kw):
        # print('vocal call')
        return request.render('kw_vocalize.vocalize_voting_template')

    @http.route('/skip-voting/', auth='public', method="post", website=True, csrf=False)
    def vocalize_voting_skip(self, **kw):
        return werkzeug.utils.redirect('/web', )
