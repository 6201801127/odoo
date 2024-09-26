import base64
import werkzeug
import odoo.http as http
from odoo.http import request
from werkzeug.exceptions import Forbidden
from datetime import date, datetime

from odoo.addons.kw_utility_tools import kw_helpers
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, LATE_WPC, LATE_WOPC


class AttendanceApproval(http.Controller):

    @http.route('/attendance-request/approve', type='http', auth="public", website=True)
    def attendance_request_approve(self, token):
        # user = request.env.user
        attendance_request = request.env['kw_employee_apply_attendance'].sudo().search(
            [('access_token', '=', token), ('state', '=', '2')])
        if not attendance_request:
            return request.not_found()
        else:
            # if attendance_request.employee_id.parent_id and attendance_request.employee_id.parent_id.user_id == user:
            parent_id = attendance_request.employee_id.parent_id
            attendance_request.write({'authority_remark': f'Approved Through Email ({parent_id.name})',
                                      # 'action_taken_by':user.employee_ids.id,
                                      'action_taken_by': parent_id.id,
                                      'state': '3',
                                      'action_taken_on': datetime.now()
                                      })
            attendance_request.create_daily_attendance()

            template = request.env.ref('kw_hr_attendance.kw_attendance_request_approved_email_template').sudo()
            template.send_mail(attendance_request.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            # else:
            #     return Forbidden()

            return http.request.render('kw_hr_attendance.kw_hr_attendance_approval_redirect',
                                       {'attendance_request': attendance_request})

    @http.route('/attendance-request/reject', type='http', auth="public", website=True)
    def attendance_request_reject(self, token):

        # user = request.env.user
        attendance_request = request.env['kw_employee_apply_attendance'].sudo().search(
            [('access_token', '=', token), ('state', '=', '2')])
        if not attendance_request:
            return request.not_found()
        else:
            # if attendance_request.employee_id.parent_id and attendance_request.employee_id.parent_id.user_id == user:
            parent_id = attendance_request.employee_id.parent_id
            attendance_request.write({'authority_remark': f'Rejected Through Email ({parent_id.name})',
                                      'action_taken_by': parent_id.id,
                                      'state': '5',
                                      'action_taken_on': datetime.now()
                                      })
            template = request.env.ref('kw_hr_attendance.kw_attendance_request_rejected_email_template').sudo()
            template.send_mail(attendance_request.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            # else:
            #     return Forbidden()

            return http.request.render('kw_hr_attendance.kw_hr_attendance_approval_redirect',
                                       {'attendance_request': attendance_request})

    @http.route('/late-entry-request/<mode>/<encrypted_attendance_id>', type='http', auth="public", website=True)
    def late_entry_request(self, mode, encrypted_attendance_id):
        # user = request.env.user
        decoded_cipher = base64.b64decode(encrypted_attendance_id)
        decoded_attendance_id = kw_helpers.decrypt_msg(decoded_cipher)

        attendance_obj = request.env['kw_daily_employee_attendance'].sudo().browse(int(decoded_attendance_id))

        if mode not in ['wpc', 'wopc'] or not attendance_obj.exists() or attendance_obj.le_state != '1':
            return request.not_found()
        else:
            # if attendance_obj.employee_id.parent_id and attendance_obj.employee_id.parent_id.user_id == user and attendance_obj.check_in_status in [IN_STATUS_LE,IN_STATUS_EXTRA_LE]:
            if attendance_obj.check_in_status in [IN_STATUS_LE, IN_STATUS_EXTRA_LE]:
                parent_id = attendance_obj.employee_id.parent_id
                if mode == 'wpc':
                    le_state = LATE_WPC
                    remark = f'Approved (with paycut) through email ({parent_id.name})'

                else:
                    le_state = LATE_WOPC
                    remark = f'Approved (without paycut) through email ({parent_id.name})'

                # step -1  insert into log
                request.env['kw_late_entry_approval_log'].sudo().create({
                    'daily_attendance_id': attendance_obj.id,
                    'forward_to': False,
                    'authority_remark': remark,
                    'action_taken_by': parent_id.id,
                    'state': le_state
                })

                # step-2 update attendance data
                attendance_obj.write({
                    'le_authority_remark': remark,
                    'le_action_taken_by': parent_id.id,
                    'le_state': '2',
                    'le_action_status': le_state,
                    'le_action_taken_on': datetime.now()
                })

                # step -3 send mail
                template = request.env.ref('kw_hr_attendance.kw_late_entry_approve_email_template').sudo()
                template.send_mail(attendance_obj.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                return Forbidden()

        return http.request.render('kw_hr_attendance.kw_hr_attendance_approval_redirect',
                                   {'attendance_obj': attendance_obj})
