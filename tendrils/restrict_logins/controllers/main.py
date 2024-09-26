# -*- coding: utf-8 -*-

import re
import math, random, string,secrets
import datetime
import pytz
import os

import werkzeug
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.addons.web.controllers import main

import odoo
import odoo.modules.registry
from odoo import SUPERUSER_ID
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import Response
from odoo.http import request
from odoo.service import security
from odoo.tools.translate import _


def clear_session_history(u_sid, f_uid=False):
    """ Clear all the user session histories for a particular user """
    path = odoo.tools.config.session_dir
    store = werkzeug.contrib.sessions.FilesystemSessionStore(
        path, session_class=odoo.http.OpenERPSession, renew_missing=True)
    session_fname = store.get_session_filename(u_sid)
    try:
        os.remove(session_fname)
        return True
    except OSError:
        print(OSError)
        pass
    return False


def super_clear_all():
    """ Clear all the user session histories """
    path = odoo.tools.config.session_dir
    store = werkzeug.contrib.sessions.FilesystemSessionStore(
        path, session_class=odoo.http.OpenERPSession, renew_missing=True)
    for fname in os.listdir(store.path):
        path = os.path.join(store.path, fname)
        try:
            os.unlink(path)
        except OSError:
            pass
    return True


class Session(main.Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.session.uid)])
        # print("inside restrict logout ----")
        # clear user session
        user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/clear_all_sessions', type='http', auth="none")
    def logout_all(self, redirect='/web', f_uid=False):
        # print("method called-------",args['fuid'])
        """ Log out from all the sessions of the current user """
        if f_uid:
            user = request.env['res.users'].with_user(1).browse(int(f_uid))
            if user:
                # clear session session file for the user
                session_cleared = clear_session_history(user.sid, f_uid)
                if session_cleared:
                    # clear user session
                    user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/super/logout_all', type='http', auth="none")
    def super_logout_all(self, redirect='/web'):
        """ Log out from all the sessions of all the users """
        users = request.env['res.users'].with_user(1).search([])
        for user in users:
            # clear session session file for the user
            session_cleared = super_clear_all()
            if session_cleared:
                # clear user session
                user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)


class Home(main.Home):

    @http.route('/restrict_logins/', auth='public', website=True)
    def restrict_logins(self, **args):
        return http.request.render('restrict_logins.restrict_login_template')

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db,
                                                   request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                failed_uid = request.uid
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                elif e.args[0] == "already_logged_in":
                    values['error'] = "You have already logged in. Log out from other devices and try again."
                    values['logout_all'] = True
                    values['failed_uid'] = failed_uid if failed_uid != SUPERUSER_ID else False
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/auth/generate-otp/', type="json", auth='public', website=True)
    def generate_login_otp(self, **args):
        failed_uid = args['fuid']
        username = args['uname']
        # print(args)
        user_data = http.request.env['res.users'].sudo().search([('login', '=', username), ('id', '=', failed_uid)])
        # print(user_data)
        if user_data:
            user_mobile = False
            user_email = False

            employee_data = http.request.env['hr.employee'].sudo().search([('user_id', '=', user_data.id)])

            if employee_data:
                # print('work_email: ', employee_data.work_email)
                # print('mobile_phone: ', employee_data.mobile_phone)
                current_date_time = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
                date_time = current_date_time + datetime.timedelta(0, 600)
                date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")

                demo_mode_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mode_status')
                mail_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mail_status') or False
                sms_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_sms_status') or False

                if demo_mode_enabled:
                    otp_value = '1234'
                else:
                    # otp_value = ''.join(random.choice(string.digits) for _ in range(4))
                    otp_value = ''.join(secrets.choice(string.digits) for _ in range(4))

                # # insert in OTP log
                otp_model = http.request.env['kw_generate_otp'].sudo()
                otp_data = otp_model.search([('user', '=', username)], order='id desc', limit=1)
                if otp_data:
                    otp_value = otp_data.otp
                    otp_data.write({'otp': otp_value, 'exp_date_time': date_time})
                else:
                    otp_model.create({'user': username, 'otp': otp_value, 'exp_date_time': date_time})

                # print("OTP is : ", otp_value)
                user_data.write({'verification_code': otp_value, 'verification_expiry': date_time})

                # For Sending OTP to mobile number
                if sms_enabled and employee_data.mobile_phone:
                    template = http.request.env['send_sms'].sudo().search([('name', '=', 'Login_OTP_SMS')])
                    http.request.env['send_sms'].sudo().send_sms(template, user_data.id)
                    user_mobile = employee_data.mobile_phone

                # For Sending OTP to mail
                if mail_enabled:
                    template = http.request.env.ref('restrict_logins.restrict_login_otp_email_template')
                    opt_email = http.request.env['mail.template'].sudo().browse(template.id).send_mail(user_data.id, force_send=True)
                    user_email = employee_data.work_email

                # print("mobile : ", user_mobile)
                # print("email : ", user_email)

                index = user_email.index("@") if user_email else False
                ret_email = user_email[0:3] + re.sub("\w", "*", user_email[3:index]) + user_email[index:] if user_email else False
                ret_mobile = user_mobile[0:2] + re.sub("\w", "*", user_mobile[2:-3]) + user_mobile[-3:] if user_mobile else False

                return failed_uid, ret_mobile, ret_email
            else:
                return False
        else:
            return False

    @http.route('/auth/validate-otp/', type="json", auth='public', website=True)
    def validate_otp(self, **args):
        # print(args)
        otp_model = http.request.env['kw_generate_otp'].sudo().search(['&', ('otp', '=', args['otpnum']), ('user', '=', args['uname'])], order='exp_date_time desc', limit=1)
        otp_num = otp_model.otp
        # print('OTP : ', otp_num, ' -----------------------------')
        expdatetime_value = otp_model.exp_date_time
        current_dt = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
        current_dt = current_dt.strftime("%Y-%m-%d %H:%M:%S")

        if otp_num != args['otpnum']:
            return 'status0', False
        elif str(current_dt) > str(expdatetime_value):
            return 'status1', False
        else:
            otp_model.unlink()
            return 'status2', args['fuid']


class RootExt(odoo.http.Root):

    def get_response(self, httprequest, result, explicit_session):
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except Exception as e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise

        if isinstance(result, (bytes, str)):
            response = Response(result, mimetype='text/html')
        else:
            response = result

        save_session = (not request.endpoint) or request.endpoint.routing.get('save_session', True)
        if not save_session:
            return response

        if httprequest.session.should_save:
            if httprequest.session.rotate:
                self.session_store.delete(httprequest.session)
                httprequest.session.sid = self.session_store.generate_key()
                if httprequest.session.uid:
                    httprequest.session.session_token = security.compute_session_token(httprequest.session, request.env)
                httprequest.session.modified = True
            self.session_store.save(httprequest.session)
        # We must not set the cookie if the session id was specified using a http header or a GET parameter.
        # There are two reasons to this:
        # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
        #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
        #   (the one using the cookie). That is a special feature of the Session Javascript class.
        # - It could allow session fixation attacks.
        if not explicit_session and hasattr(response, 'set_cookie'):
            response.set_cookie('session_id', httprequest.session.sid, max_age=60 * 60, httponly=True)

        return response


root = RootExt()
odoo.http.Root.get_response = root.get_response
