# -*- coding: utf-8 -*-
"""# ################################
# # Mainly use for overriding the main home controller / web path after login
# # Implemented for late entry reason
# # Implemented for covid-19 survey
# # Created On : 25-Sep-2020, Created By: T Ketaki Debadarshini
# ###############################"""
from datetime import datetime, date
import logging
import werkzeug
import werkzeug.utils
from ast import literal_eval
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

import odoo.addons.web.controllers.main as main
import pytz

_logger = logging.getLogger(__name__)


class Home(main.Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        # print("web called---------------",kw)
        # import pdb
        # pdb.set_trace()
        base_url = http.request.httprequest.full_path
        result_url = base_url.split('redirect=') if 'redirect=' in base_url else False
        # print("==1==",result_url)
        if result_url and len(result_url) > 1:
            allowed_urls = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_login_allowed_urls')
            allowed_urls_list =allowed_urls.split(',')
            # print("allowed_urls================",allowed_urls,allowed_urls_list)
            if result_url[1] not in allowed_urls_list:
                # print("---------session log out--------------")
                return http.local_redirect('/web/session/logout', keep_hash=False)
        main.ensure_db()
        
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        employee_rec = request.env.user.employee_ids[0] if request.env.user.employee_ids else False
        employee_id = employee_rec.id if employee_rec else False
        emp_no_attendance = employee_rec.no_attendance if employee_rec else False

        try:
            """employee attendance data"""
            config_param = http.request.env['ir.config_parameter']
            emp_atd_record = request.env['kw_daily_employee_attendance'].sudo().search(
                [('employee_id', '=', employee_id), ('attendance_recorded_date', '=', date.today())])
                   
            """Start : redirect to late entry screen if the employee has logged in late"""
            # attendance_enabled = config_param.sudo().get_param('kw_hr_attendance.module_kw_hr_attendance_status')
            late_entry_enabled = config_param.sudo().get_param('kw_hr_attendance.late_entry_screen_enable')       
            excluded_grade_ids = literal_eval(config_param.sudo().get_param('kw_hr_attendance.attn_exclude_grade_ids','False'))
            if late_entry_enabled and request.env.user.employee_ids:
                try:
                    late_entry_url = request.env['hr.attendance'].show_late_entry_reason(employee_id = request.env.user.employee_ids[:1].id)
                    if late_entry_url and request.env.user.employee_ids.grade.id not in excluded_grade_ids:
                        return http.local_redirect(late_entry_url, query=request.params, keep_hash=True)
                except Exception:
                    pass
            """END : redirect to late entry screen if the employee has logged in late"""
            # """NPS Update Screen"""
            # nps_update_check = config_param.sudo().get_param('check_nps_update')
            # if nps_update_check == '1':
            #     company_activity_login = request.env['login_activity_configuration'].sudo().search(
            #         [('view_name_code', '=', 'NPS'),
            #         ('multi_company_ids', 'in', request.env.user.employee_ids.company_id.id)])
            #     if company_activity_login.exists():
            #             nps_redirect_url = request.env['hr.contract'].sudo(request.uid).check_pending_nps_details()
            #             if nps_redirect_url:
            #                 # user_status['nps_redirect_url'] = nps_redirect_url
            #                 return http.local_redirect(nps_redirect_url, query=request.params, keep_hash=True)
            """Start : redirect to survey if the employee has not filled survey yet"""
            enable_work_from_home_survey = config_param.sudo().get_param('kw_surveys.enable_work_from_home_survey')            
            enable_epf_status = config_param.sudo().get_param('kw_epf.epf_status')
            interview_feedback_enabled = config_param.sudo().get_param('kw_recruitment.interview_feedback_check')

            """fetch employee attendance modes"""
            attendance_mode_alias = employee_rec.mapped('attendance_mode_ids').mapped('alias') if employee_rec else []
            # print("attendance_mode_alias >> ", attendance_mode_alias)
            # print("emp_no_attendance >> ", emp_no_attendance)

            """check if attendance mode is portal if Working Day(0) or Roaster Working Day(3)"""
            if (emp_atd_record and emp_atd_record.check_in != False and emp_atd_record.day_status in ['0', '3']
                and 'portal' in attendance_mode_alias) \
                    or (emp_atd_record and emp_atd_record.day_status != False and emp_atd_record.day_status not in ['0', '3']) \
                    or (emp_atd_record and emp_atd_record.state == 4) \
                    or (emp_atd_record and emp_atd_record.day_status in ['0', '3'] and 'portal' not in attendance_mode_alias) \
                    or (not emp_atd_record and ('portal' not in attendance_mode_alias or emp_no_attendance)):
                """ EPF form start """
                if enable_epf_status and request.env.user.employee_ids:
                    try:
                        epf_url = request.env['kw_epf'].check_pending_epf(request.env.user)
                        if epf_url:
                            return http.local_redirect(epf_url, query=request.params, keep_hash=True)
                    except Exception:
                        pass
                """ EPF form end """

                """ Interview Feedback start """
                if interview_feedback_enabled and request.env.user.employee_ids:
                    try:
                        interview_feedback_url = request.env['survey.user_input'].check_pending_interview_feedback(request.env.user)
                        if interview_feedback_url.get('url') and not request.session.get('skip_interview_feedback_form', False):
                            return http.local_redirect(interview_feedback_url.get('url'), query=request.params, keep_hash=True)
                    except Exception:
                        pass
                """ Interview Feedback end """

                """ SURVEY form start """
                if enable_work_from_home_survey and request.env.user.employee_ids:
                    try:
                        work_from_home_survey_url = request.env['kw_surveys_details']._give_feedback(request.env.user)
                        if work_from_home_survey_url.get('url') and not request.session.get('skip_survey_feedback_form', False):
                            if work_from_home_survey_url:
                                return http.local_redirect(work_from_home_survey_url, query=request.params, keep_hash=True)
                    except Exception:
                        pass
                """END : Start : redirect to survey if the employee has not filled survey yet"""
                """skill survey page"""
                skill_survey_enabled = config_param.sudo().get_param('kw_resource_management.skill_survey_enabled')
                if skill_survey_enabled:
                    if request.env.user.employee_ids.department_id.code == 'BSS':
                        try:
                            emp_checklist = request.env['kw_employee_skill_expertise'].sudo().search([('emp_id', '=', request.env.user.employee_ids.id),('is_submitted', '=',True),('reopen_survey','=',False)])
                            if not emp_checklist and employee_id is not False \
                                    and not request.session.get('skip_skill', False):
                                url = request.env['kw_employee_skill_expertise'].sudo()._get_employee_skill_url(request.env.user)
                                return http.local_redirect(url, query=request.params, keep_hash=True)
                        except Exception:
                            pass

                # """ Vocalize form start """
                # enable_vocalize_from = config_param.sudo().get_param('kw_vocalize.enable_vocalize_from')
                # if enable_vocalize_from and request.env.user.employee_ids:
                #     try:
                #        enable_vocalize_url = "/vocalize-voting/"
                #        return http.local_redirect(enable_vocalize_url, query=request.params, keep_hash=True)
                #     except Exception:
                #         pass
                # """END : Start : redirect to vocalize form if the employee has not filled from yet"""

                """ Social Image form start"""
                social_picture_enable_form = http.request.env["ir.config_parameter"].sudo().get_param("social_picture_enable_form")
                if social_picture_enable_form == 'Yes':
                    social_image_url = request.env['kw_employee_social_image'].sudo().check_employee_social_image(request.env.user)
                    if social_image_url:
                        return http.local_redirect(social_image_url, query=request.params, keep_hash=True)
                """ Social Image form end"""

                """ Employee Handbook form start """
                employee_handbook_enable_form = http.request.env["ir.config_parameter"].sudo().get_param(
                    "employee_handbook_enable_form")
                # condition to run only on friday afternoon
                weekday = datetime.now().weekday()
                user_timezone = pytz.timezone(request.env.user.tz or 'UTC')
                current_time = datetime.strftime(datetime.now().replace(tzinfo=pytz.utc).astimezone(user_timezone), "%H")
                if weekday == 4 and int(current_time) >= 12 and employee_handbook_enable_form == 'Yes':
                    current_employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)], limit=1)
                    # handbook which have auth login true and all view access
                    handbook_auth_login = request.env['kw_onboarding_handbook'].sudo().search(
                        [('auth_login', '=', True), ('view_access', '=', 'All')])
                    # handbook which have auth login true and specific view access
                    handbook_auth_login += request.env['kw_onboarding_handbook'].sudo().search(
                        [('auth_login', '=', True), ('view_access', '=', 'Specific'),
                         ('employee_ids', '=', current_employee.id)])
                    # handbook understood by employee
                    handbook_understood = request.env['kw_handbook'].sudo().search(
                        [('employee_id', '=', current_employee.id), ('handbook_id', 'in', handbook_auth_login.ids)])
                    handbook_auth_login -= handbook_understood.mapped('handbook_id')

                    if handbook_auth_login:
                        enable_handbook_url = request.env['kw_handbook']._get_employee_handbook_url(request.env.user)
                        if enable_handbook_url and request.env.user.employee_ids and not request.session.get('skip_handbook', False):
                            return http.local_redirect(enable_handbook_url, query=request.params, keep_hash=True)

                    # Below code by santanu
                    # check_id = request.env['kw_handbook'].sudo().search([('employee_id', '=', current_employee.id),
                    #                                                      ('handbook_id', '=', handbook.id)])
                    # print("check_id---------------------------------",check_id)
                    # records = current_employee.handbook_info_details_ids.filtered(lambda r:r.employee_id==current_employee and r.understood==True)
                    # print("records============",records)
                    # if handbook and not check_id:
                    #     enable_handbook_url = request.env['kw_handbook']._get_employee_handbook_url(request.env.user)
                    #     if enable_handbook_url and request.env.user.employee_ids and not request.session.get(
                    #             'skip_handbook', False):
                    #         return http.local_redirect(enable_handbook_url, query=request.params, keep_hash=True)

                """END : Start : redirect to Employee Handbook """

                """ Enable Employee Certification form start"""
                employee_certification_enable_form = http.request.env["ir.config_parameter"].sudo().get_param("employee_certification_enable_form")
                day_list = [1, 2, 3, 4]
                current_day = date.today().day
                if current_day in day_list \
                        and employee_certification_enable_form == 'Yes' \
                        and not request.session.get('skip_certfication', False):
                    url = request.env['kw_update_employee_certification'].sudo()._get_employee_certfication_url(request.env.user)
                    return http.local_redirect(url, query=request.params, keep_hash=True)
                """ Enable Employee Certification form end"""
                
                """ Enable Employee Job description form start"""
                emp_jd_enabled = config_param.sudo().get_param('kw_recruitment.employee_jd_check')
                emp_checklist = request.env['kw_employee_onboarding_checklist'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id),('jd', '=','no')])

                if emp_jd_enabled and emp_checklist.exists() and employee_id is not False \
                        and not request.session.get('skip_jd', False):
                    url = request.env['hr.applicant'].sudo()._get_employee_jd_url(request.env.user)
                    return http.local_redirect(url, query=request.params, keep_hash=True)
                """ Enable Employee Job description form end"""
                
                """"Employee PAN FORM start"""
                emp_pan_enabled = config_param.sudo().get_param('kw_emp_profile.employee_pan_check')
                if bool(emp_pan_enabled) is True:
                    company_activity_login = request.env['login_activity_configuration'].sudo().search([('view_name_code','=','PAN'),('multi_company_ids','in',employee_rec.company_id.id)])
                    if company_activity_login.exists():
                        pan_log = request.env['kw_employee_update_pan_log'].search([('employee_id', '=', employee_id)])
                        if employee_id is not False \
                                and request.session.get('skip_pan', False) is False \
                                and (not pan_log.exists() or pan_log.is_submitted is False):
                            url = request.env['kw_emp_profile'].sudo()._get_employee_pan_url(request.env.user)
                            return http.local_redirect(url, query=request.params, keep_hash=True)
                    
                """"Employee PAN FORM End"""
                """Onboarding Assessment Feedback Induction"""
           
                """Health Insurance Home Page Start"""
                enable_health_insurance_form = http.request.env["ir.config_parameter"].sudo().get_param("payroll_inherit.enable_health_insurance_form")
                if enable_health_insurance_form and request.env.user.employee_ids \
                        and not request.session.get('skip_health_insurance', False) \
                        and kw.get('insurance', '0') != '1':
                    health_insurance_record_redirect = request.env['health_insurance_dependant'].check_employee_health_insurance(request.env.user)
                    # print(f"health_insurance_record_redirect {health_insurance_record_redirect}")
                    if not health_insurance_record_redirect:
                        return http.local_redirect('/health-insurance-for-dependant', query=request.params, keep_hash=True)
                """Health Insurance Home Page End"""

                """onboarding feedback induction login screen"""
                enable_onboarding_induction_feedback = config_param.sudo().get_param('kw_onboarding.onboarding_induction_check')
                if enable_onboarding_induction_feedback:
                    assessment_check = request.env['kw_onboard_induction_emp_tagged'].sudo().search(
                        [('emp_ids', 'in', employee_id), ('start_date', '<=', date.today())])
                    submit_feedback = request.env['kw_onboarding_feedback'].sudo().search([('emp_id', '=', employee_id)])
                    for rec in submit_feedback:
                        if assessment_check.exists() and employee_id is not False \
                                and rec.submit_bool is False and not request.session.get('skip_assessment', False):
                            url = request.env['kw_onboarding_feedback'].sudo()._get_employee_onboard_assessment_url(request.env.user)
                            return http.local_redirect(url, query=request.params, keep_hash=True)
                """end onboarding induction feedback """
               

                # """Start : Timesheets To Validate Page"""
            # one_day_timesheet_validation_enabled = http.request.env["ir.config_parameter"].sudo().get_param("kw_timesheets.one_day_validation_check")
            # if one_day_timesheet_validation_enabled and request.env.user.employee_ids and not request.session.get('skip_timesheet'):
            #     print("inside one_day_timesheet_validation_enabled -->",one_day_timesheet_validation_enabled)
            #     timesheets_record_redirect_url, _ = request.env['account.analytic.line'].sudo(request.env.user.id).check_pending_timesheet()
            #     if timesheets_record_redirect_url:
            #         request.session['skip_timesheet'] = True
            #         return http.local_redirect(timesheets_record_redirect_url, query=request.params, keep_hash=False)
            # """End : Timesheets To Validate Page"""

            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')

# class Action(main.Action):
#     @http.route('/web/action/load', type='json', auth="user")
#     def load(self, action_id, additional_context=None):
#         print("Action load method parameter is -->",action_id,additional_context)
#         Actions = request.env['ir.actions.actions']
#         value = False
#         try:
#             action_id = int(action_id)
#         except ValueError:
#             try:
#                 action = request.env.ref(action_id)
#                 assert action._name.startswith('ir.actions.')
#                 action_id = action.id
#             except Exception:
#                 action_id = 0   # force failed read

#         one_day_timesheet_validation_enabled = http.request.env["ir.config_parameter"].sudo().get_param("kw_timesheets.one_day_validation_check")
#         if one_day_timesheet_validation_enabled and request.env.user.employee_ids:
#             timesheets_record_redirect_url, _ = request.env['account.analytic.line'].sudo(request.env.user.id).check_pending_timesheet()
#             print("timesheets_record_redirect_url -->",timesheets_record_redirect_url)
#             if timesheets_record_redirect_url:
#                 action_id = request.env.ref('hr_timesheet.act_hr_timesheet_line').sudo().id

#         base_action = Actions.browse([action_id]).read(['type'])
#         if base_action:
#             ctx = dict(request.context)
#             action_type = base_action[0]['type']
#             if action_type == 'ir.actions.report':
#                 ctx.update({'bin_size': True})
#             if additional_context:
#                 ctx.update(additional_context)
#             request.context = ctx
#             action = request.env[action_type].browse([action_id]).read()
#             if action:
#                 value = main.clean_action(action[0])
#         print("Action in web/action/load -->",value.get('id'),value.get('name'))
#         return value
