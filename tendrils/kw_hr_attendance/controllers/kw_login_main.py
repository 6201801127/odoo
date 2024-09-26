# -*- coding: utf-8 -*-

import logging
import werkzeug
import werkzeug.utils
from ast import literal_eval
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

import odoo.addons.web.controllers.main as main

_logger = logging.getLogger(__name__)


class Home(main.Home):
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        main.ensure_db()
        
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        # print(kw)
        try:
            attendance_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_hr_attendance.module_kw_hr_attendance_status')
            late_entry_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_hr_attendance.late_entry_screen_enable')
            excluded_grade_ids = literal_eval( http.request.env['ir.config_parameter'].sudo().get_param('kw_hr_attendance.attn_exclude_grade_ids','False'))
            
            if attendance_enabled and request.env.user.employee_ids:
                request.env.user.employee_ids.ensure_one()
                if late_entry_enabled:
                    late_entry_url = request.env['kw_hr_attendance_log'].show_late_entry_reason(employee_id = request.env.user.employee_ids.id )
                    
                    if late_entry_url and request.env.user.employee_ids.id.grade.id not in excluded_grade_ids:
                        return http.local_redirect(late_entry_url, query=request.params, keep_hash=True)

            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
