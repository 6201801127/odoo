# -*- coding: utf-8 -*-
import base64
import json
from odoo import http

from odoo.addons.kw_utility_tools import kw_helpers


class UserStatus(http.Controller):

    @http.route('/user-status/', auth='public', website=True)
    def kw_user_status(self, **args):
        return http.request.render('kw_auth.user_status')

    @http.route('/after-login-activities/<string:login_activities_ciphered>', auth='user', method=['get', 'post'],
                website=True, csrf=False)
    def after_login_actions(self, login_activities_ciphered, **args):
        # print("---------user-activeity-login--------",self,login_activities_ciphered,args)
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        try:
            login_activities_ciphered = base64.b64decode(login_activities_ciphered)
            decodestr = kw_helpers.decrypt_msg(login_activities_ciphered)
           

            # print('login_activities_ciphered>>>',login_activities_ciphered)
            # print('decodestr>>>',decodestr)
            res = json.loads(decodestr)
            # print('res>>>',res)
            return http.request.render('kw_auth.user_status', res)

        except Exception as e:
            http.request._cr.rollback()
            args['link_err_msg'] = e.args[0]
            return http.request.render("kw_auth.user_status", args)

    @http.route('/redirect_to_my_office_time', auth='user', website=True)
    def redirect_to_my_office_time(self, **args):
        http.request.session['skip_activities'] = 1
        user_landing_url = http.request.env['hr.attendance']._user_landing_page()
        return http.local_redirect(user_landing_url)
