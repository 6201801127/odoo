import base64
import datetime
import json
import logging
import werkzeug
# import werkzeug.exceptions
import werkzeug.utils
# import werkzeug.wrappers
# import werkzeug.wsgi
import requests
from ast import literal_eval
import pytz
from odoo import tools
from datetime import datetime, date
# import odoo.modules.registry
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo import http
from odoo.http import request  # content_disposition, dispatch_rpc,
from odoo.tools.translate import _
from Crypto.Cipher import AES
from Crypto import Random
import odoo.addons.web.controllers.main as main
from odoo.addons.kw_utility_tools import kw_helpers
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import binascii
from werkzeug.exceptions import Forbidden
import secrets
import re

_logger = logging.getLogger(__name__)


class Home(main.Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        # print("==========kw===========",kw,redirect,http.request.httprequest.full_path)
        #--------------------------START-------------------------

        parse_rex = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        url = request.httprequest.environ['HTTP_HOST']
        m = re.search(parse_rex, url)
        host_url = m.group('host')
        # print("base_url >> ", url, host_url, host_url[:-2], m.group('port'))

        base_url = http.request.httprequest.full_path
        result_url = base_url.split('redirect=') if 'redirect=' in base_url else False
        if result_url and len(result_url) > 1:
            # print("==1==",result_url)
            allowed_urls = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_login_allowed_urls')
            allowed_urls_list = allowed_urls.split(',')
            # print("allowed_urls================",allowed_urls,allowed_urls_list)
            if result_url[1] not in allowed_urls_list:
                # print("---------session log out--------------")
                return http.local_redirect('/web/session/logout', keep_hash=False)
        #---------------------------END------------------------
        # config_param = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_host_list_parameter')
        # print(config_param,"config_param=================")
        # allowed_host_list_str = config_param.get_param('kwantify_host_list_parameter')
        # print(allowed_host_list_str,"allowed_host_list_str=========================")
        allowed_host_list = ['localhost', '192.168.61.158', '192.168.61.235', '192.168.27.120', '164.164.122.169','192.168.27.189',
                             '10.1.1.164', '172.27.32.154','172.27.29.18','172.27.28.221','172.27.30.120','172.27.29.18','172.27.29.170','172.27.30.79','172.27.29.193']
        # allowed_host_list = config_param.split(',') if config_param else []
        if not host_url[:-2] in '127.0.0.1' and host_url not in allowed_host_list:
            # print(host_url, "----------------------------------------------------host header does not match----------------------------------------------------------------------")
            return Forbidden()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        if not request.uid:
            request.uid = SUPERUSER_ID
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'GET':
            alphabet = '0123456789abcdefABCDEF'
            random_val = ''.join(secrets.choice(alphabet) for _ in range(32))
            request.session['key'] = random_val

        values['key'] = request.session.get('key', None)
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                # Fetch the value from the session in Python
                # aes_key = request.session.get('auth_secret_key', None)
                aes_key = request.session.get('key', None)
                if not aes_key:
                    return werkzeug.utils.redirect('/web')
                    # AES Decryption
                login = request.params['login']
                password = request.params['password']

                # aes_key = "0123456789abcdef0123456789abcdef"
                key = binascii.unhexlify(aes_key)
                # Decryption
                cipher = AES.new(key, AES.MODE_ECB)
                decoded = binascii.a2b_base64(password)
                decrypted = unpad(cipher.decrypt(decoded), AES.block_size).decode('utf-8')

                login = decrypted
                uid = request.session.authenticate(request.session.db, request.params['login'], login)
                login_username = request.params['login']
                # request.params['login_success'] = True
                # print(f"USER ID IS {uid} == {login_username}")
                # ---odoo predefined ---##
                # request.params['login_success'] = True
                # http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                # ---odoo predefined ---##
                # print("request.env.user >>> ", request.env.user)
                # consultancy portal user login redirect to job list page
                # Add the password expiry check
                password_expired = False
                password_expired_message = ''
                # if login and password:
                user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                # print("users==========---------------------------------",user)
                if user and 'expiry_date' in user and user.expiry_date:
                    current_date = datetime.now().date()
                    expiry_date = user.expiry_date
                    # print("expiry date========================",expiry_date,current_date)
                    if current_date > expiry_date:
                        password_expired = True
                        password_expired_message = _(
                            'Your password has expired. Please contact the administrator to reset your password.')

                        values['password_expired'] = password_expired
                        values['password_expired_message'] = password_expired_message
                        request.session.logout(keep_db=True)

                        return request.render('kwantify_theme.kwantify_login_layout', values)

                if not redirect and not request.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
                    return http.local_redirect('/c/job-openings', keep_hash=False)

                if redirect != '':
                    return http.local_redirect(redirect, keep_hash=False)

                config_param = http.request.env['ir.config_parameter'].sudo()
                """# odoo attendance start"""
                attendance_enabled = config_param.get_param('kw_hr_attendance.module_kw_hr_attendance_status')
                late_entry_enabled = config_param.get_param('kw_hr_attendance.late_entry_screen_enable')
                excluded_grade_ids = literal_eval(config_param.get_param('kw_hr_attendance.attn_exclude_grade_ids', 'False'))
                if attendance_enabled and request.env.user.employee_ids:
                    # request.env.user.employee_ids.ensure_one()
                    try:
                        """LATE ENTRY screen redirect"""
                        if late_entry_enabled:
                            late_entry_url = request.env['hr.attendance'].show_late_entry_reason(employee_id=request.env.user.employee_ids[:1].id)
                            if late_entry_url and request.env.user.employee_ids.grade.id not in excluded_grade_ids:
                                return http.local_redirect(late_entry_url, keep_hash=True)

                        # #call user actions after odoo log-in
                        user_status, enc_user_activities = self.after_login_user_actions(request.env.user)
                        if len(user_status):
                            """LATE ENTRY screen redirect"""
                            if 'kwantify_late_entry_url' in user_status \
                                    and user_status['kwantify_late_entry_url'] \
                                    and not late_entry_enabled:
                                return werkzeug.utils.redirect(user_status['kwantify_late_entry_url'])

                            """PENDING ACTIVITY screen redirect"""
                            return werkzeug.utils.redirect(enc_user_activities)  # request.render("kw_auth.user_status", user_status)
                        else:
                            return werkzeug.utils.redirect('/web')
                    except Exception as e:
                        # values['error'] = e.args[0]
                        pass
                else:
                    res = self.after_login_check_attendance()
                    if res:
                        return res

                    if not redirect:
                        user_landing_url = request.env['hr.attendance']._user_landing_page()
                        # print(user_landing_url)
                        return http.local_redirect(user_landing_url)
                """#odoo attendance end"""

                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))

            except AccessDenied as e:
                failed_uid = request.uid
                request.uid = old_uid
                if e.args[0] == "already_logged_in":
                    values['error'] = "User already logged in. Log out from other devices and try again."
                    values['logout_all'] = True
                    values['failed_uid'] = failed_uid if failed_uid != SUPERUSER_ID else False

                    # print("inside kw auth--------")
                    # print(values)
                elif e.args == AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not tools.config['list_db']:
            values['disable_database_manager'] = True

        """# otherwise no real way to test debug mode in template as ?debug =>
        # values['debug'] = '' but that's also the fallback value when
        # missing variables in qweb"""
        if 'debug' in values:
            values['debug'] = True

        response = request.render("web.login", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _userstring(self, username):
        tz_india = pytz.timezone('Asia/Kolkata')
        # datetime_object = datetime.datetime.now(tz_india)
        datetime_object = datetime.now(tz_india)
        datetime_object = datetime_object.strftime("%Y-%m-%d %I:%M:%S %p")
        raw = f"username#{username}|timestamp#{datetime_object}"
        return raw

    def _encrypt(self, raw):
        # private_key = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_private_key')
        private_key = b"6ef93e5ca5f40780aee35aee6bf765aa"
        BLOCK_SIZE = 16
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

        raw = pad('b' + raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        enc = base64.b64encode(iv + cipher.encrypt(raw.encode("utf8")))
        # print(enc)
        return enc

    def after_login_user_actions(self, user, my_ofc_redirect=0, epf_status=0):
        """to be called after user login , to perform the task after the login
            params  : user record
            returns : user status key_value pairs
        """
        config_param = http.request.env['ir.config_parameter'].sudo()
        user_status, enc_user_activities = {}, ''

        # print("executed")
        # sync_enabled        = config_param.get_param('kw_auth.module_kw_auth_mode_status')
        cmn_url = config_param.get_param('kwantify_common_url')
        kw_v6_url = config_param.get_param('kwantify_v6_url')
        # url = cmn_url if cmn_url else "http://192.168.201.65/kwantify_v6"
        url = cmn_url if cmn_url else kw_v6_url
        sync_enabled = False
        if sync_enabled:
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            browser = request.httprequest.user_agent.browser

            le_check_url = config_param.get_param('kwantify_attendance_url')
            user_attendance_url = config_param.get_param('kwantify_user_attendance_url')
            # late_entry_check_url = le_check_url if le_check_url else "http://192.168.201.65/prd.service.portalV6.csmpl.com/OdooSynSVC.svc/UserAttendance"
            late_entry_check_url = le_check_url if le_check_url else user_attendance_url

            header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
            json_data = {"UserName": user.login, "Browser": browser, "IPAddress": ip_address}
            data = json.dumps(json_data)
            # print(data)
            resp = False
            try:
                resp_result = requests.post(late_entry_check_url, headers=header, data=data)
                resp = json.loads(resp_result.text)

                if resp:

                    raw = self._userstring(user.login)
                    # print(raw)
                    qs = self._encrypt(raw)
                    enc_uid = qs.decode('utf8')
                    if resp[0]['LateReasonPopUpOutput'] == '1':
                        user_status['kwantify_late_entry_url'] = f"{url}/Odoologin.aspx?q={enc_uid}&type=1"

                    for key, value in resp[0].items():
                        if value == '1':
                            # enc_uid=qs.decode('utf8')
                            # print(f"E")
                            if key == 'WhatsappPopupOutput':
                                user_status[key] = f"{url}/Odoologin.aspx?q={enc_uid}&type=3"
                            # elif key == "EPFPopupOutput":
                            #     user_status[key]=f"{url}/Odoologin.aspx?q={enc_uid}&type=2"
                            # modified for epf form development in odoo

                            elif key == "AttenSyncOutput":
                                user_status[key] = True
                            else:
                                user_status[key] = f"/auto-login-kwantify"

            except Exception as e:
                # print(e)                
                pass

        """# training start"""
        training_feedback_enabled = config_param.get_param('kw_training.module_kw_training_feedback_status')
        # print(training_feedback_enabled)
        if training_feedback_enabled:
            try:
                training_feedback_url = request.env['kw_training'].with_context(_uid=user.id).sudo().check_pending_feedback(user_id=user.id)
                # print("Training feedback url is", training_feedback_url)
                if training_feedback_url:
                    user_status['training_feedback_url'] = training_feedback_url
            except Exception:
                pass
        """# training end"""

        """Start : redirect to survey if the employee has not filled survey yet"""
        enable_work_from_home_survey = config_param.get_param('kw_surveys.enable_work_from_home_survey')
        if enable_work_from_home_survey and user.employee_ids:
            try:

                work_from_home_survey_url = request.env['kw_surveys_details']._give_feedback(user)

                if work_from_home_survey_url:
                    user_status['work_from_home_survey_url'] = work_from_home_survey_url
                    user_status['survey_type_codes'] = request.env['kw_surveys_details'].search([]).mapped('survey_id.survey_type.code')
                    user_status['survey_name'] = ','.join(request.env['kw_surveys_details'].search(
                        [('employee_ids', '=', request.env.user.employee_ids.id), ('state', 'in', ['1', '2']),
                         ('kw_surveys_id.end_date', '>=', date.today()),
                         ('kw_surveys_id.start_date', '<=', date.today())]).mapped('survey_name'))


            except Exception:
                pass
        """END : redirect to survey if the employee has not filled survey yet"""

        """ Vocalize form start """
        enable_vocalize_from = http.request.env['ir.config_parameter'].sudo().get_param('kw_vocalize.enable_vocalize_from')
        if enable_vocalize_from and request.env.user.employee_ids:
            try:
                enable_vocalize_url = "/vocalize-voting/"
                user_status['enable_vocalize_survey_url'] = enable_vocalize_url
            except Exception:
                pass
        """END : Start : redirect to vocalize form if the employee has not filled from yet"""

        # start : bank update check
        bank_update_check = config_param.get_param('payroll_inherit.check_bank_update')
        if bank_update_check:
            company_activity_login = request.env['login_activity_configuration'].sudo().search(
                [('view_name_code', '=', 'BANK'),
                 ('multi_company_ids', 'in', request.env.user.employee_ids.company_id.id)])
            if company_activity_login.exists():
                try:
                    bank_redirect_url = request.env['hr.contract'].sudo(user.id).check_pending_bank_details()
                    if bank_redirect_url:
                        user_status['bank_redirect_url'] = bank_redirect_url
                except Exception:
                    pass
        """NPS POP Up"""
        nps_update_check = config_param.get_param('check_nps_update')
        if nps_update_check == '1':
            company_activity_login = request.env['login_activity_configuration'].sudo().search(
                [('view_name_code', '=', 'NPS'),
                 ('multi_company_ids', 'in', request.env.user.employee_ids.company_id.id)])
            if company_activity_login.exists():
                try:
                    nps_redirect_url = request.env['hr.contract'].sudo(user.id).check_pending_nps_details()
                    if nps_redirect_url:
                        user_status['nps_redirect_url'] = nps_redirect_url
                except Exception:
                    pass

        
        """Onboarding Assessment Feedback Induction"""
        emp_induction_enabled = config_param.sudo().get_param('kw_skill_assessment.induction_assessment')
        if emp_induction_enabled:
            induction_assessment_config = request.env['kw_employee_induction_assessment'].sudo().search(
                [('emp_id', '=', request.env.user.employee_ids.id)])
            for rec in induction_assessment_config:
                assessmnet_given = request.env['kw_skill_answer_master'].sudo().search(
                    [('user_id', '=', rec.emp_id.user_id.id), ('set_config_id', '=', rec.assessment_id.id)])
                if bool(emp_induction_enabled) is True and request.env.user.employee_ids is not False and not assessmnet_given.exists():
                    emp_induction_url = request.env['kw_employee_induction_assessment'].sudo()._get_employee_induction_assessment_page(
                        request.env.user)
                    if emp_induction_url:
                        user_status['emp_induction_url'] = emp_induction_url

        # start : timesheet validation check
        timesheet_validation_enabled = config_param.get_param('kw_timesheets.one_day_validation_check')
        if timesheet_validation_enabled:
            try:
                timesheet_redirect_url, timesheet_date = request.env['account.analytic.line'].sudo(user.id).check_pending_timesheet()
                if timesheet_redirect_url:
                    user_status['timesheet_redirect_url'] = '/web'
                    user_status['timesheet_date'] = timesheet_date
            except Exception:
                pass
        # end : timesheet validation check

        """ Interview Feedback start """
        interview_feedback_enabled = config_param.sudo().get_param('kw_recruitment.interview_feedback_check')
        if interview_feedback_enabled and request.env.user.employee_ids:
            try:
                interview_feedback_url = request.env['survey.user_input'].check_pending_interview_feedback(request.env.user)
                if interview_feedback_url:
                    return werkzeug.utils.redirect(interview_feedback_url.get('url') if interview_feedback_url else '/web', 303)
                # else:
                #     user_status['InterviewFeedback'] = '/web'
            except Exception:
                pass
        """ Interview Feedback end """

        # start : RA, Project Manager, Reviewer timesheet validation check
        ra_pm_reviewer_validation_enabled = config_param.get_param('kw_timesheets.ra_pm_reviewer_validation_check')
        if ra_pm_reviewer_validation_enabled:
            try:
                # ra_pm_reviewer_to_validate_url,ra_pm_reviewer_validate_date,ra_pm_reviewer_validate_count = request.env['account.analytic.line'].sudo(user.id).check_ra_pm_reviewer_pending_validatations()
                ra_pm_reviewer_url, ra_pm_date = request.env['account.analytic.line'].sudo(user.id).check_ra_pm_reviewer_pending_validatations()
                if ra_pm_reviewer_url:
                    user_status['ra_pm_reviewer_url'] = '/web'
                    user_status['ra_pm_date'] = ra_pm_date
                    # user_status['ra_pm_reviewer_validate_count'] = ra_pm_reviewer_validate_count
            except Exception:
                pass
        # end : RA, Project Manager, Reviewer timesheet validation check

        if len(user_status) > 0 or epf_status:
            if my_ofc_redirect:
                user_status['my_ofc_redirect'] = my_ofc_redirect
            if epf_status:
                raw = self._userstring(user.login)
                # print(raw)
                qs = self._encrypt(raw)
                enc_uid = qs.decode('utf8')
                user_status['EPFPopupOutput'] = f"{url}/Odoologin.aspx?q={enc_uid}&type=2"

            enc_string_user_activities = kw_helpers.encrypt_msg(json.dumps(user_status))
            enc_user_activities = base64.b64encode(enc_string_user_activities).decode('utf8')

        return (user_status, '/after-login-activities/' + enc_user_activities) # if enc_user_activities else werkzeug.utils.redirect('/web'))

    def after_login_check_attendance(self):
        request.uid = request.session.uid
        employee_rec = request.env.user.employee_ids[0] if request.env.user.employee_ids else False
        employee_id = employee_rec.id if employee_rec else False
        emp_no_attendance = employee_rec.no_attendance if employee_rec else False
        """employee attendance data"""
        emp_atd_record = request.env['kw_daily_employee_attendance'].sudo().search(
            [('employee_id', '=', employee_id), ('attendance_recorded_date', '=', date.today())])
        """fetch employee attendance modes"""
        attendance_mode_alias = employee_rec.mapped('attendance_mode_ids').mapped('alias') if employee_rec else []

        """check if attendance mode is portal if Working Day(0) or Roaster Working Day(3)"""
        if (emp_atd_record.check_in == False and emp_atd_record.day_status in ['0', '3'] and 'portal' in attendance_mode_alias) \
                or (not emp_atd_record and 'portal' in attendance_mode_alias):
            action_id = request.env.ref('kw_hr_attendance.action_my_office_time').id
            menu_id = request.env.ref('hr_attendance.menu_hr_attendance_root').id or request.env.ref('kw_hr_attendance.menu_my_office_time').id
            if action_id and menu_id:
                redirect_url = f"/web#action={action_id}&menu_id={menu_id}"
                # print('redirect_url to dashboard ++++ ', redirect_url)
                return http.local_redirect(redirect_url, keep_hash=False)
        return False


class Session(main.Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        try:
            attendance_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_hr_attendance.module_kw_hr_attendance_status')
            if attendance_enabled and request.session.uid:
                # print('check out---------------')
                request.env['hr.attendance'].employee_portal_log_out(user_id=request.session.uid)

        except Exception as e:
            # values['error'] = e.args[0]
            # print(str(e.args[0]))
            pass
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
