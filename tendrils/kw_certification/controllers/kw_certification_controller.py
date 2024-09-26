from requests import request
from odoo import http
from werkzeug.exceptions import  Forbidden
from odoo.exceptions import ValidationError

class KwCertification(http.Controller):
    @http.route('/certification/accept/view', type='http', auth='public', website=True)
    def certification_accept_view_page(self, **post):
        record_id = post.get('record_id')
        emp_id = post.get('emp_id')
        env = http.request.env
        certification = env['kw_certification'].sudo().browse(int(record_id))
        temp_id = []
        employee_user_id = env['hr.employee'].sudo().search([('id', '=', int(emp_id))]).user_id.id
        if env.uid == employee_user_id:
            for rec in certification:
                accept_length = []
                if rec.assigned_emp_data:
                    for recc in rec.assigned_emp_data:
                        if recc.employee_id.id == int(emp_id) and recc.status_certification == 'Pending':
                            name_emp=recc.employee_id.name
                            recc.status_certification = 'Accepted'
                            department_head=rec.require_department_id.manager_id.user_id.employee_ids.work_email
                            template_obj = env.ref('kw_certification.email_template_for_assign_emp')
                            l_k_emp = env.ref("kw_certification.group_landk_module_kw_certification")
                            lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                            manager_emp = env.ref("kw_certification.group_manager_module_kw_certification")
                            manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                            cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(manager_emp_l.mapped('work_email')) or ''
                            email_to = department_head
                            mail = env['mail.template'].sudo().browse(template_obj.id).with_context(
                                    subject = 'Nomination for '+ rec.certification_type_id.name +' Certification Accepted !',
                                    mail_for='Accept',
                                    email_from= recc.employee_id.work_email,
                                    accepted_emp= name_emp,
                                    name= rec.require_department_id.manager_id.user_id.employee_ids.name,
                                    email_to=email_to,
                                    mail_cc=cc_mail,
                                    certification = rec.certification_type_id.name
                                ).send_mail(
                                    int(record_id),
                                    notif_layout="kwantify_theme.csm_mail_notification_light",
                                force_send=True)
                            env.user.notify_success("Mail Sent Successfully.")
                            temp_id.clear()
                            temp_id.append('kw_surveys.kwantify_surveys_thanks_pages')
                            rec.write({'action_log_table_ids': [[0, 0, {'state': 'Accepted',
                                                                        'designation': recc.employee_id.job_id.name,
                                                                        'action_taken_by': recc.employee_id.name,
                                                                        }]]})
                        elif recc.employee_id.id == int(emp_id) and recc.status_certification in ['Accepted', 'Rejected', 'Uploaded']:
                            temp_id.clear()
                            temp_id.append('kw_certification.kwantify_certification_thanks_pages')
                        if recc.status_certification == 'Accepted':
                            accept_length.append(recc.status_certification)
                if rec.no_of_candidate == len(accept_length):
                    rec.state = 'Approved'
                    l_k_emp = rec.env.ref("kw_certification.group_landk_module_kw_certification")
                    lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                    if lk_employees:
                        rec.pending_at = lk_employees.ids[0]
                        rec.assigned_user_ids = [(4, id, False) for id in lk_employees.ids]
                        rec.view_status_user_ids = [(4, id, False) for id in lk_employees.ids]
                        rec.take_action_user_ids = False
                        rec.take_action_user_ids = [(4, id, False) for id in lk_employees.ids]
                    else:
                        raise ValidationError('Please Give  L&K Access Rights to At least One Person.')
                    # rec.pending_at = rec.rcm_head_manager_id
            return http.request.render(temp_id[0])
        else:
            return Forbidden()

    @http.route('/certification/reject/view', type='http', auth='public', website=True)
    def certification_reject_view_page(self, **post):
        record_id = post.get('record_id')
        emp_id = post.get('emp_id')
        env = http.request.env
        certification = env['kw_certification'].sudo().browse(int(record_id))
        temp_id = []
        employee_user_id = env['hr.employee'].sudo().search([('id', '=', int(emp_id))]).user_id.id
        if env.uid == employee_user_id:
            for rec in certification:
                accept_length = []
                if rec.assigned_emp_data:
                    for recc in rec.assigned_emp_data:
                        if recc.employee_id.id == int(emp_id) and recc.status_certification == 'Pending':
                            name_emp=recc.employee_id.name
                            recc.status_certification = 'Rejected'
                            department_head=rec.require_department_id.manager_id.user_id.employee_ids.work_email
                            template_obj = env.ref('kw_certification.email_template_for_assign_emp')
                            l_k_emp = env.ref("kw_certification.group_landk_module_kw_certification")
                            lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                            manager_emp = env.ref("kw_certification.group_manager_module_kw_certification")
                            manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                            cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(manager_emp_l.mapped('work_email')) or ''
                            email_to = department_head
                            mail = env['mail.template'].sudo().browse(template_obj.id).with_context(
                                    subject='Nomination for '+ rec.certification_type_id.name +' Certification Rejected !',
                                    mail_for='Rejected',
                                    email_from= recc.employee_id.work_email,
                                    rejected_emp= name_emp,
                                    name= rec.require_department_id.manager_id.user_id.employee_ids.name,
                                    email_to=email_to,
                                    mail_cc=cc_mail,
                                    certification=rec.certification_type_id.name
                                ).send_mail(
                                    int(record_id),
                                    notif_layout="kwantify_theme.csm_mail_notification_light",
                                force_send=True)
                            env.user.notify_success("Mail Sent Successfully.")
                            temp_id.clear()
                            temp_id.append('kw_surveys.kwantify_surveys_thanks_pages')
                        elif recc.employee_id.id == int(emp_id) and recc.status_certification in ['Accepted', 'Rejected', 'Uploaded']:
                            temp_id.clear()
                            temp_id.append('kw_certification.kwantify_certification_thanks_pages')
                        if recc.status_certification == 'Rejected':
                            accept_length.append(recc.status_certification)
                if rec.no_of_candidate == len(accept_length):
                    rec.state = 'Approved'
                    l_k_emp = rec.env.ref("kw_certification.group_landk_module_kw_certification")
                    lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                    if lk_employees:
                        rec.pending_at = lk_employees.ids[0]
                        rec.assigned_user_ids = [(4, id, False) for id in lk_employees.ids]
                    else:
                        raise ValidationError('Please Give  L&K Access Rights to At least One Person.')
                    # rec.pending_at = rec.rcm_head_manager_id
            return http.request.render(temp_id[0])
        else:
            return Forbidden()
