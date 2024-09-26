# -*- coding: utf-8 -*-
from odoo import http
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
import urllib.parse
import hashlib
# from odoo.addons.kw_utility_tools import kw_helpers


class MedhaAI(http.Controller):
    @http.route('/go-for-medha/', auth='public', method="post", website=True, csrf=False)
    def button_click(self, **kw):
        raw = url = ''
        url = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_medha_url',False)
        if url:
            raw = self._userstring(request.env.user)
            # print(raw, '======================>>>>>>>>>>>>>>>>>')
            qs = self._encrypt(raw)
            raw_split = raw.split('|')
            employee_id = raw_split[0] 
            employee_name = urllib.parse.unquote(raw_split[2])
            user_name = raw_split[3]
            user_email = raw_split[5]
            project = 'kwantify'
            datetime_object = raw_split[4]
            employee_code = raw_split[1]
            country_name = raw_split[6]
            # url += 'home/'+base64.b64encode(f"{employee_id}/{employee_name}".encode('utf-8')).decode('utf-8')
            # url += 'home/' + urllib.parse.quote_plus(base64.b64encode(f"{employee_id}/{employee_name}".encode('utf-8')).decode('utf-8'))
            url += urllib.parse.unquote(base64.b64encode(f"{employee_id}/{employee_name}/{user_name}/{datetime_object}/{user_email}/{project}/{employee_code}/{country_name}".encode('utf-8')).decode('utf-8'))
            # print('url>>>>>>>>>>>>>>>>>>>>',url)
            return werkzeug.utils.redirect(url)
        else:
            return werkzeug.utils.redirect('/web')


    def _userstring(self, user):
        tz_india = pytz.timezone('Asia/Kolkata')
        datetime_object = datetime.datetime.now(tz_india)
        user_name = user.login
        employee_id = user.employee_ids.id
        employee_name = user.employee_ids.name
        employee_email = user.employee_ids.work_email
        employee_code = user.employee_ids.emp_code
        country_name = user.employee_ids.company_id.country_id.name
        # employee_name = employee_name.replace(" ", "")
        # print(employee_name,"employee------------------------------")
        datetime_object = datetime_object.strftime("%Y-%m-%d %I:%M:%S %p")
        raw = f"{employee_id}|{employee_name}|{user_name}|{datetime_object}|{employee_email}|{employee_code}|{country_name}"
        # raw = f"id#{employee_id}|name#{employee_name}|email#{empl_mail}|datetime#{datetime_object}"
        # print('raw_bas64----',raw,type(raw))
        return raw


    def _encrypt(self, raw):
        private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
        BLOCK_SIZE = 16
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        raw = pad('b' + raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        enc = iv + cipher.encrypt(raw.encode("utf8"))
        enc_b64 = base64.b64encode(enc)
        return enc_b64