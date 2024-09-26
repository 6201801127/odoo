import pytz
import datetime
from datetime import date
import base64
import io
import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import math, random, string
from ast import literal_eval

import odoo.addons.calendar.controllers.main as main
from odoo.api import Environment
import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.exceptions import ValidationError, AccessDenied
from ast import literal_eval



class RecruitmentMRFView(http.Controller):

    @http.route('/recruitment/requisition/view', type='http', auth="user", website=True)
    def view(self, db, id, action=None, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            # mrftoken = env['kw_recruitment_requisition_approval'].search([('access_token', '=', token)])
            # if not mrftoken:
            #     return request.not_found()
            # else:
            #     if mrftoken.employee_id.user_id.id != request.env.uid:
            #         return Forbidden()

                # mrf = env['kw_recruitment_requisition'].browse(mrftoken.mrf_id.id)
            mrf = env['kw_recruitment_requisition'].browse(id)
            if not mrf:
                return request.not_found()
            lang = 'en_US'
            if action is None:
                action = request.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window').id
            return werkzeug.utils.redirect(
                '/web?db=%s#id=%s&view_type=form&model=kw_recruitment_requisition&action=%s' % (db, id, action,))
    
    @http.route('/recruitment/mrf/view', type='http', auth="user", website=True)
    def mrf_view(self, db, id, action=None, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrf = env['kw_recruitment_requisition'].browse(id)
            if not mrf:
                return request.not_found()
            lang = 'en_US'
            if action is None:
                action = request.env.ref('kw_recruitment.manpower_requisition_form_act_window').id
            menu_id=request.env.ref('hr_recruitment.menu_hr_recruitment_root').id
            return werkzeug.utils.redirect(
                '/web?db=%s#id=%s&view_type=form&model=kw_recruitment_requisition&action=%s&menu_id=%s' % (db, id, action,menu_id,))

    @http.route('/recruitment/requisition/forward', type='http', auth="user", website=True)
    def forward(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            elif mrftoken.mrf_id.state != 'sent':
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()

                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                if record.max_sal < 1:
                    return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record, 'id': record.id, 'salary_info': True},)
 
                mrfview = request.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                Parameters = request.env['ir.config_parameter'].sudo()
                sec_approver_list = Parameters.get_param('kw_recruitment.second_level_approver_ids')
                coverted_sec = sec_approver_list.strip('][').split(', ')
                if coverted_sec:
                    emps = request.env['hr.employee'].search([('id', 'in', [int(i) for i in coverted_sec])])
                    forward = record.write({'state': 'forward',
                                            'last_approver_ids': [(6, 0, emps.ids)],
                                            'forwarded_dt': datetime.date.today()})
                    logtable = request.env['kw_recruitment_requisition_log'].search(
                        [('mrf_id', '=', record.id), ('to_status', '=', 'forward')])
                    template_obj = request.env.ref('kw_recruitment.approve_forward_request_template')
                    approvers = request.env['hr.employee'].search([('id', 'in', [int(rec) for rec in coverted_sec])])
                    # approvers = request.env['hr.employee'].search([('job_id', 'in', jobs.ids)])
                    if approvers:
                        for approver in approvers:
                            MRF_token = request.env['kw_recruitment_requisition_approval'].create({
                                'mrf_id': record.id,
                                'employee_id': approver.id})

                            mail = request.env['mail.template'].browse(template_obj.id).with_context(
                                dbname=db_name,
                                token=MRF_token.access_token,
                                action_id=action_id,
                                approver=approver.name,
                                mailto=approver.work_email).send_mail(logtable.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                mrftoken.write({'status': False})
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record, 'id': record.id},)

    @http.route('/recruitment/requisition/hold', type='http', auth="user", website=True)
    def hold(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()

                lang = 'en_US'

                template_obj = request.env.ref('kw_recruitment.template_for_hold_mrf')
                mrfview = request.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                if record.approver_id and record.approver_id.user_id.id == request.env.user.id:
                    if template_obj:
                        record.write({'state': 'hold',
                                      'hold_user_id': request.env.user.id})
                        logtable = request.env['kw_recruitment_requisition_log'].search(
                            [('mrf_id', '=', record.id), ('to_status', '=', 'hold')])
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            name=record.approver_id.name,
                            receiver=record.create_uid.name,
                            mailto=record.create_uid.email).send_mail(logtable.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                elif record.approver_id and record.approver_id.user_id.id != request.env.user.id:
                    if template_obj:
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.approver_id.name,
                            name=request.env.user.name,
                            mailto=record.create_uid.email).send_mail(record.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                        record.write({'state': 'hold',
                                      'hold_user_id': request.env.user.id})
                        request.env.user.notify_success("Mail sent successfully.")
                else:
                    if template_obj:
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.create_uid.name,
                            name=request.env.user.name,
                            mailto=record.create_uid.email).send_mail(record.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                        record.write({'state': 'hold'})
                        request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )

    @http.route('/recruitment/mrf/hold', type='http', auth="user", website=True)
    def mrf_hold(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()
                lang = 'en_US'
                template_obj = request.env.ref('kw_recruitment.template_for_hold_mrf')
                mrfview = request.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                param = request.env['ir.config_parameter'].sudo()
                to_user = literal_eval(param.get_param('kw_recruitment.rcm_head','[]'))
                tag_to = request.env['hr.employee'].browse(to_user)
                tag_to_mail = request.env['hr.employee'].browse(to_user).mapped('work_email')[0]
                cc_users = list(set(literal_eval(param.get_param('kw_recruitment.tag_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
                all_cc = set(cc_users + [mrftoken.mrf_id.create_uid.employee_ids.id])
                tag_cc_mail =','.join(request.env['hr.employee'].browse(all_cc).mapped('work_email'))
                if template_obj:
                    record.write({'state': 'hold',
                                    'pending_at':'',
                                    'hold_user_id': request.env.user.id})
                    logtable = request.env['kw_recruitment_requisition_log'].search(
                        [('mrf_id', '=', record.id), ('to_status', '=', 'hold')])
                    mail = request.env['mail.template'].browse(template_obj.id).with_context(
                        dbname=db_name,
                        action_id=action_id,
                        name=record.approver_id.name,
                        mailfrom=mrftoken.employee_id.work_email,
                        receiver=tag_to.name,
                        mailto=tag_to_mail, email_cc=tag_cc_mail).send_mail(logtable.id,
                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                    force_send=True)
                    request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )
    
    @http.route('/recruitment/mrf/reject', type='http', auth="user", website=True)
    def mrf_reject(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()
                mrftoken.write({'status': False})
                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                mrfview = request.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                param = request.env['ir.config_parameter'].sudo()
                to_user = literal_eval(param.get_param('kw_recruitment.rcm_head','[]'))
                tag_to = request.env['hr.employee'].browse(to_user)
                tag_to_email = request.env['hr.employee'].browse(to_user).mapped('work_email')[0]
                # print("=======",literal_eval(param.get_param('kw_recruitment.tag_head','[]')))
                # print("=======",list(request.mrf_id.create_uid.employee_ids.id))
                cc_users = list(set(literal_eval(param.get_param('kw_recruitment.tag_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]')))) 
                all_cc = set(cc_users + [mrftoken.mrf_id.create_uid.employee_ids.id])
                tag_cc =','.join(request.env['hr.employee'].browse(all_cc).mapped('work_email'))
                template_obj = request.env.ref('kw_recruitment.template_for_reject_first_mrf')
                if mrftoken.mrf_id.approver_id and mrftoken.mrf_id.approver_id.user_id.id == request.env.user.id:
                    if template_obj:
                        record.write({'state': 'reject','pending_at':'',})
                        logtable = request.env['kw_recruitment_requisition_log'].search(
                            [('mrf_id', '=', record.id), ('to_status', '=', 'reject')])
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.create_uid.name,
                            name=tag_to.name,
                            mailfrom=mrftoken.employee_id.work_email,
                            mailto=tag_to_email,
                            email_cc=tag_cc).send_mail(logtable.id,
                                                                        notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                        force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                else:
                    template_obj = request.env.ref('kw_recruitment.template_for_reject_first_mrf')
                    record.write({'state': 'reject'})
                    logtable = request.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', mrftoken.mrf_id.id), ('to_status', '=', 'reject')])
                    if template_obj:
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=mrftoken.mrf_id.create_uid.name,
                            name=request.env.user.name,
                            mailto=mrftoken.mrf_id.create_uid.email,
                            email_cc=tag_cc).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )

    @http.route('/recruitment/requisition/reject', type='http', auth="user", website=True)
    def reject(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()

                mrftoken.write({'status': False})

                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                mrfview = request.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                if record.approver_id and record.approver_id.user_id.id == request.env.user.id:
                    template_obj = request.env.ref('kw_recruitment.template_for_reject_first_mrf')
                    if template_obj:
                        record.write({'state': 'reject'})
                        logtable = request.env['kw_recruitment_requisition_log'].search(
                            [('mrf_id', '=', record.id), ('to_status', '=', 'reject')])
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.create_uid.name,
                            name=record.approver_id.name,
                            mailto=record.create_uid.email).send_mail(logtable.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                elif record.approver_id and record.approver_id.user_id.id != request.env.user.id:
                    template_obj = request.env.ref('kw_recruitment.template_for_reject_first_mrf')
                    if template_obj:
                        record.write({'state': 'reject'})
                        logtable = request.env['kw_recruitment_requisition_log'].search(
                            [('mrf_id', '=', record.id), ('to_status', '=', 'reject')])
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.approver_id.name,
                            name=request.env.user.name,
                            mailto=record.approver_id.work_email).send_mail(logtable.id,
                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                            force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                else:
                    template_obj = request.env.ref('kw_recruitment.template_for_reject_first_mrf')
                    if template_obj:
                        record.write({'state': 'reject'})
                        logtable = request.env['kw_recruitment_requisition_log'].search(
                            [('mrf_id', '=', record.id), ('to_status', '=', 'reject')])
                        mail = request.env['mail.template'].browse(template_obj.id).with_context(
                            dbname=db_name,
                            action_id=action_id,
                            receiver=record.create_uid.name,
                            name=request.env.user.name,
                            mailto=record.create_uid.email).send_mail(logtable.id,
                                                                      notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                      force_send=True)
                        request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )

    @http.route('/recruitment/mrf/forward', type='http', auth="user", website=True)
    def mrf_proceed(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()
                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                param = request.env['ir.config_parameter'].sudo()
                second_approver_list = literal_eval(param.get_param('kw_recruitment.second_level_approver_ids', '[]'))
                ceo_emp = request.env['hr.employee'].browse(second_approver_list)
                data = {'state': 'forward',
                              'pending_at':mrftoken.employee_id.id,
                              'approved_user_id': request.env.user.id,
                              'approved_dt': datetime.date.today()}
                if record.approver_id.id == ceo_emp.id:
                    data['forward_to_ceo'] = True
                record.write(data)
                logtable = request.env['kw_recruitment_requisition_log'].search(
                    [('mrf_id', '=', record.id), ('to_status', '=', 'forward')])
                mrfview = request.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                cc_users = set(literal_eval(param.get_param('kw_recruitment.rcm_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]')))
                tag_cc =','.join(request.env['hr.employee'].browse(cc_users).mapped('work_email'))
                template_obj = request.env.ref('kw_recruitment.rcm_validation_notification')
                mail = request.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    mailfrom=request.env.user.email,
                    approvedby=request.env.user.name,
                    notify_cc=tag_cc,
                    signuser=record.req_raised_by_id.user_id.signature,
                    signusername=record.req_raised_by_id.user_id.name,
                    mailto=mrftoken.mrf_id.approver_id.work_email).sudo().send_mail(logtable[0].id,
                                                                           notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                           force_send=True)
                mrftoken.write({'status': False})
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )  

    @http.route('/recruitment/requisition/approve', type='http', auth="user", website=True)
    def approve(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()

                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])

                if record.max_sal < 1:
                    return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record, 'id': record.id, 'salary_info': True},)


                record.write({'state': 'approve',
                              'approved_user_id': request.env.user.id,
                              'approved_dt': datetime.date.today()})
                logtable = request.env['kw_recruitment_requisition_log'].search(
                    [('mrf_id', '=', record.id), ('to_status', '=', 'approve')])
                mrfview = request.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                if record.approver_id:
                    template_obj = request.env.ref('kw_recruitment.action_approval_final_template')
                else:
                    template_obj = request.env.ref('kw_recruitment.action_approval_template')

                mail = request.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    mailfrom=mrftoken.employee_id.work_email,
                    approvedby=mrftoken.employee_id.name,
                    signuser=record.req_raised_by_id.user_id.signature,
                    signusername=record.req_raised_by_id.user_id.name).sudo().send_mail(logtable[0].id,
                                                                           notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                           force_send=True)
                # template = request.env.ref('kw_recruitment.acknowledgement_template')
                #
                # template.with_context(
                #     dbname=db_name,
                #     action_id=action_id,
                #     mailfrom=record.forwarder_id.work_email if record.forwarder_id and record.forwarder_id.id != mrftoken.employee_id.id  else record.req_raised_by_id.work_email,
                #     mailto=mrftoken.employee_id.work_email,
                #     approver_name=mrftoken.employee_id.name,
                #     signuser = record.forwarder_id.user_id.signature if record.forwarder_id else record.req_raised_by_id.user_id.signature,
                #     signusername = record.forwarder_id.user_id.name if record.forwarder_id else record.req_raised_by_id.user_id.name).send_mail(logtable.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                mrftoken.write({'status': False})
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )
    
    @http.route('/recruitment/mrf/approve', type='http', auth="user", website=True)
    def approve(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            mrftoken = env['kw_recruitment_requisition_approval'].search(
                [('access_token', '=', token), ('status', '=', True)])
            if not mrftoken:
                return request.not_found()
            else:
                if mrftoken.employee_id.user_id.id != request.env.uid:
                    return Forbidden()
                lang = 'en_US'
                record = request.env['kw_recruitment_requisition'].sudo().search([('id', '=', mrftoken.mrf_id.id)])
                record.write({'state': 'approve',
                              'pending_at':'',
                              'approved_user_id': request.env.user.id,
                              'approved_dt': datetime.date.today()})
                logtable = request.env['kw_recruitment_requisition_log'].search(
                    [('mrf_id', '=', record.id), ('to_status', '=', 'approve')])
                mrfview = request.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
                action_id = request.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
                db_name = request._cr.dbname
                param = request.env['ir.config_parameter'].sudo()
                to_user = literal_eval(param.get_param('kw_recruitment.tag_head','[]'))
                tag_to =request.env['hr.employee'].browse(to_user).mapped('work_email')
                cc_users = list(set(literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.rcm_head','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
                all_cc = set(cc_users + [mrftoken.mrf_id.create_uid.employee_ids.id])
                tag_cc =','.join(request.env['hr.employee'].browse(all_cc).mapped('work_email'))
                if record.approver_id:
                    template_obj = request.env.ref('kw_recruitment.action_approval_final_template')
                    mail = request.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    email_to =tag_to[0],
                    email_cc =tag_cc,
                    mailfrom=mrftoken.employee_id.work_email,
                    approvedby=mrftoken.employee_id.name,
                    signuser=record.req_raised_by_id.user_id.signature,
                    signusername=record.req_raised_by_id.user_id.name).sudo().send_mail(logtable[0].id,
                                                                           notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                           force_send=True)
                mrftoken.write({'status': False})
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_recruitment.kw_recruitment_button_redirect', {'datas': record}, )

    @http.route(['/cv/download/<string:attachment_id>/<string:document_id>', ], type='http', auth='public',
                methods=["GET"], csrf=False, cors='*', website=True)
    def download_attachment(self, attachment_id, document_id):
        # download document if endpoint hit with required parameters
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])
        document = request.env['kw_upload_cv'].sudo().search([('id', '=', int(document_id))])
        if attachment["datas"]:
            data = io.BytesIO(base64.b64decode(attachment["datas"]))
            return http.send_file(data, filename=document['file_name'] if document['file_name'] else 'Document',
                                  as_attachment=True)
        else:
            return request.not_found()
