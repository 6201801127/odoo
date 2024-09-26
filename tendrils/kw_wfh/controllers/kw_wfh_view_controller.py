import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request, Response
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
import odoo.addons.calendar.controllers.main as main
import datetime
from datetime import date
from werkzeug.exceptions import BadRequest, Forbidden
from odoo.addons.restful.common import invalid_response


class wfh_view_controller(http.Controller):

    @http.route('/wfh/view', type='http', auth="user", website=True)
    def view_wfh(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            wfhtoken = env['kw_wfh_action'].search([('access_token', '=', token)])
            if request.env.uid:
                if wfhtoken.wfh_id.employee_id.user_id.id == request.env.uid:
                    action_id = request.env.ref('kw_wfh.kw_wfh_requset_action')
                    return request.redirect('/web#id=%s&active_id=%s&model=kw_wfh&action=%s&view_type=form' %(wfhtoken.wfh_id.id, wfhtoken.wfh_id.id, action_id.id))
                else:
                    action_id = request.env.ref('kw_wfh.kw_wfh_requset_takeaction_window')
                    return request.redirect('/web#id=%s&active_id=%s&model=kw_wfh&action=%s&view_type=form' %(wfhtoken.wfh_id.id, wfhtoken.wfh_id.id, action_id.id))

    @http.route('/wfh/grant', type='http', auth="user", website=True)
    def grant_wfh(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            wfhtoken = env['kw_wfh_action'].search([('access_token', '=', token), ('status', '=', True)])
            if not wfhtoken:
                return Response("Token seems to have expired or invalid!!")
            else:
                if wfhtoken.ra_id.user_id.id != request.env.uid:
                    return Forbidden()
            
                lang = 'en_US'
                attn_mode = env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
                today_date = date.today()
                wfh_rec = wfhtoken.wfh_id
                if wfh_rec.request_from_date <= today_date <= wfh_rec.request_to_date:
                    emp_id = wfh_rec.employee_id
                    wfh_rec.enable_portal_mode(emp_id, attn_mode)

                wfhtoken.wfh_id.sudo().write({'state': 'grant',
                                              'approved_on': today_date,
                                              'approved_by': request.env.user.employee_ids.name,
                                              'action_taken_by': request.env.user.employee_ids.id,
                                              'wfh_active_link': True,
                                              'ra_remark':'Granted'})
                if wfh_rec.request_from_date == today_date:
                    attendance_report = env['kw_daily_employee_attendance'].sudo().search(
                        [('employee_id', '=', wfh_rec.employee_id.id), ('work_mode', '!=', '0'),
                         ('attendance_recorded_date', '=', wfh_rec.request_from_date)])
                    if attendance_report:
                        """ updating working mode through update query """
                        # query = f"UPDATE kw_daily_employee_attendance SET work_mode=0 WHERE id = {attendance_report.id}"
                        # request._cr.execute(query)
                        wfh_rec.sudo().update_daily_employee_attendance(attendance_report.id)
                
                if wfhtoken.wfh_id.state != 'hold':
                    wfhtoken.write({'status': False})
                
                mail_context = {'state': 'Granted'}
                """ User mail """
                act_id = request.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
                user_template_id = request.env.ref('kw_wfh.kw_wfh_emp_request_status_email_template')
                user_template_id.with_context(mail_context, rec_id=wfhtoken.wfh_id.id, act_id=act_id,
                                              db_name=request._cr.dbname, token=token).send_mail(wfhtoken.wfh_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                request.env.user.notify_success("Request has been approved.")
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_wfh.kw_wfh_button_redirect_view',
                                           {'datas': wfhtoken.wfh_id, 'id': wfhtoken.wfh_id.id},)

    @http.route('/wfh/hold', type='http', auth="user", website=True)
    def hold_wfh(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            wfhtoken = env['kw_wfh_action'].search([('access_token', '=', token), ('status', '=', True)])
            if not wfhtoken:
                return Response("Token seems to have expired or invalid!!")
            else:
                if wfhtoken.ra_id.user_id.id != request.env.uid:
                    return Forbidden()
                
                lang = 'en_US'
                wfhtoken.wfh_id.write({'state': 'hold',
                                       'approved_on': date.today(),
                                       'approved_by': request.env.user.employee_ids.name,
                                       'action_taken_by': request.env.user.employee_ids.id,
                                       'wfh_active_link': True,
                                       'ra_remark':'On-Hold'})
                # 'form_status': 'hold',

                if wfhtoken.wfh_id.state != 'hold':
                    wfhtoken.write({'status': False})
                
                mail_context = {'state': 'On Hold'}
                """ User mail """
                act_id = request.env.ref('kw_wfh.kw_wfh_requset_action').id
                user_template_id = request.env.ref('kw_wfh.kw_wfh_emp_request_hold_email_template')
                user_template_id.with_context(mail_context, rec_id=wfhtoken.wfh_id.id, act_id=act_id,
                                              db_name=request._cr.dbname, token=token).send_mail(wfhtoken.wfh_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                request.env.user.notify_success("Request has been approved.")
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_wfh.kw_wfh_button_redirect_view',
                                           {'datas': wfhtoken.wfh_id, 'id': wfhtoken.wfh_id.id},)
    
    @http.route('/wfh/reject', type='http', auth="user", website=True)
    def reject_wfh(self, db, token, action, view='calendar', id=''):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            wfhtoken = env['kw_wfh_action'].search([('access_token', '=', token), ('status', '=', True)])
            if not wfhtoken:
                return Response("Token seems to have expired or invalid!!")
            else:
                if wfhtoken.ra_id.user_id.id != request.env.uid:
                    return Forbidden()
                
                lang = 'en_US'
                wfhtoken.wfh_id.write({'state': 'reject',
                                       'approved_on': date.today(),
                                       'approved_by': request.env.user.employee_ids.name,
                                       'action_taken_by': request.env.user.employee_ids.id,
                                       'wfh_active_link': True,
                                       'ra_remark':'Rejected'})
                # 'form_status': 'reject',
                
                if wfhtoken.wfh_id.state != 'hold':
                    wfhtoken.write({'status': False})
                
                mail_context = {'state': 'Rejected'}
                """ User mail """
                act_id = request.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
                user_template_id = request.env.ref('kw_wfh.kw_wfh_emp_request_status_email_template')
                user_template_id.with_context(mail_context, rec_id=wfhtoken.wfh_id.id, act_id=act_id,
                                              db_name=request._cr.dbname, token=token).send_mail(wfhtoken.wfh_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                request.env.user.notify_success("Request has been approved.")
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_wfh.kw_wfh_button_redirect_view',
                                           {'datas': wfhtoken.wfh_id, 'id': wfhtoken.wfh_id.id},)
