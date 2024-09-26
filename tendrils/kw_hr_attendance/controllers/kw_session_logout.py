# -*- coding: utf-8 -*-
import logging
import datetime
import werkzeug
import pytz

import odoo
import pytz
from odoo import http
from odoo.http import request

import odoo.addons.web.controllers.main as main
from odoo.addons.kw_utility_tools import kw_helpers

_logger = logging.getLogger(__name__)


class Session(main.Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        try:
            # timezone            = pytz.timezone(request.env.user.employee_ids.tz or 'UTC')
            check_out_utc = datetime.datetime.now()

            # print('check out---------------')
            # print(request.env.user)   
            if request.session.uid:
                user = request.env['res.users'].sudo().browse(request.session.uid)
                # print(user)
                hr_attendance_log = request.env['kw_hr_attendance_log']
                latest_log_rec = hr_attendance_log.sudo(user.id).search(
                    [('employee_id', '=', user.employee_ids.id), ('check_out', '=', False), ('check_in_mode', '=', 0)],
                    limit=1)
                # and not ('bio' in has_only_bio_mode and len(has_only_bio_mode) ==1)
                if latest_log_rec and not latest_log_rec.check_out:
                    latest_log_rec.sudo(user.id).write(
                        {'check_out': check_out_utc, 'out_ip_address': kw_helpers.get_ip()})

                    # clear user session  :: used for restrict login/logouts
                # user._clear_session()

        except Exception as e:
            # values['error'] = e.args[0]
            # print(str(e.args[0]))
            pass
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
