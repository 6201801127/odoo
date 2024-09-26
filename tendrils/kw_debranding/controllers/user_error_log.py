# -*- coding: utf-8 -*-
import base64
import json
from odoo import http

from odoo.addons.kw_utility_tools import kw_helpers


class UserErrorLog(http.Controller):


    @http.route('/update/user/error/log',type="json", auth='user', website=True)
    def redirect_to_my_office_time(self, **args):
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        else:
            log = http.request.env['user_error_log'].sudo().create({
                'employee_id':http.request.env['hr.employee'].sudo().search([('user_id','=',http.request.session.uid )],limit=1).id,
                'payload':args['error'],
                'status':500,
            })