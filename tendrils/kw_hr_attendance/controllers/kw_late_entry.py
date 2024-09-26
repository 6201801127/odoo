# -*- coding: utf-8 -*-
import re
import base64
import pytz
from odoo import http, api
from odoo.http import request
from datetime import date, datetime 
from odoo.exceptions import ValidationError
from odoo.addons.kw_utility_tools import kw_helpers

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_EARLY_ENTRY,IN_STATUS_ON_TIME,IN_STATUS_LE,IN_STATUS_EXTRA_LE,IN_STATUS_LE_HALF_DAY,IN_STATUS_LE_FULL_DAY


class LateEntry(http.Controller):
    @http.route('/lateentry_reason/', auth='public', method="post", website=True, csrf=False)
    def lateentry_reason(self, **kw):
        if http.request.session.uid is None:
            return http.request.redirect('/web')
       
        try:
            if kw['late_entry_reason'] == "":
                raise ValidationError("Please submit your reason.")
            if (re.match('[ a-zA-Z0-9.,_-]', str(kw['late_entry_reason']))) is not None:
                kw_attendance_log = request.env['kw_daily_employee_attendance'].search(
                    [('employee_id', '=', request.env.user.employee_ids.id), ], limit=1)
                kw_attendance_log.write({'late_entry_reason': kw['late_entry_reason'],
                                         'le_state': '1'})

                # Edited By: Surya Prasad Tripathy
                # Call mail template when late entry state is 'Applied'
                if kw_attendance_log.late_entry_reason and kw_attendance_log.le_state == '1':
                    template = request.env.ref('kw_hr_attendance.kw_late_entry_apply_email_template')
                    encrypted_attendance_id = kw_helpers.encrypt_msg(str(kw_attendance_log.id))
                    encoded_attendance_id = base64.b64encode(encrypted_attendance_id).decode('utf8')

                    request.env['mail.template'].browse(template.id).with_context(attendance_id=encoded_attendance_id).send_mail(kw_attendance_log.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                return http.request.redirect('/web')
            else:
                raise ValidationError("Special Characters are not allowed.")
        except Exception as e:
            http.request._cr.rollback()
            kw['err_msg'] = e.args[0]
            return http.request.render("kw_hr_attendance.kw_employee_late_entry",kw)

    @http.route('/late_entry/<string:attendance_ciphered>', auth='public', method=['get','post'], website=True, csrf=False) #
    def late_entry(self,attendance_ciphered,**args):
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        try:
            daily_employee_attendance = request.env['kw_daily_employee_attendance']

            # print(type(attendance_ciphered)) 

            attendance_ciphered = base64.b64decode(attendance_ciphered)
            decodestr = kw_helpers.decrypt_msg(attendance_ciphered)
            # print(decodestr)

            attendance_info = decodestr.split('##')
            generated_time_str = attendance_info[2]

            # attendance_date      = attendance_info[0]
            attendance_log_id = attendance_info[1]
            if attendance_log_id:
                attendance_log_record = daily_employee_attendance.browse(int(attendance_log_id))

            date_time_obj = datetime.strptime(generated_time_str, '%Y-%m-%d %H:%M:%S.%f')
            duration = datetime.now() - date_time_obj  # For build-in functions
            duration_in_s = duration.total_seconds()
            hours = divmod(duration_in_s, 3600)[0]

            if (hours >= 1):
                raise ValidationError("The link has been expired.")

            elif (attendance_log_record and attendance_log_record.check_in_status in [IN_STATUS_LE, IN_STATUS_EXTRA_LE] \
                  and attendance_log_record.le_state in ['0', False]):

                kw_attendance_logs = daily_employee_attendance.search(
                    [('employee_id', '=', request.env.user.employee_ids.id),
                     ('attendance_recorded_date', '<', attendance_log_record.attendance_recorded_date),
                     ('check_in_status', 'in', [IN_STATUS_LE, IN_STATUS_EXTRA_LE])], limit=7)
                infodict = dict()  #
                attendance_logs = []
                emp_tz = request.env.user.employee_ids.tz or request.env.user.employee_ids.resource_calendar_id.tz or 'UTC'
                emp_timezone = pytz.timezone(emp_tz)
                for log_rec in kw_attendance_logs:
                    attendance_logs.append(dict(
                        check_in=datetime.strftime(log_rec.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%d-%b-%Y %H:%M %p") if log_rec.check_in else '',
                        late_entry_reason=log_rec.late_entry_reason)
                                           )
                infodict['late_entry_records'] = attendance_logs
                
                return http.request.render("kw_hr_attendance.kw_employee_late_entry", infodict)
            else:
                raise ValidationError("The late entry details have already been submitted.")

        except Exception as e:
            http.request._cr.rollback()
            args['link_err_msg'] = e.args[0]
            return http.request.render("kw_hr_attendance.kw_employee_late_entry", args)
