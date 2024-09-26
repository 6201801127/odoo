from odoo import http, api
import werkzeug
import re
import math, random, string
import datetime
from datetime import date, timedelta

import pytz
from odoo.http import request
import requests, os, zipfile, base64, shutil
from mimetypes import guess_extension
from odoo.tools.mimetypes import guess_mimetype
from zipfile import ZipFile
from io import BytesIO
from odoo.addons.web.controllers.main import content_disposition
from odoo.exceptions import AccessError
from dateutil import tz
from pytz import timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii
# import secrets

from . import applicant_edu_details
from . import applicant_work_experience
# from . import kw_document_info


class PreInterviewApplicantData(http.Controller):

    def __init__(self):
        self.objeduinfo = applicant_edu_details.ApplicantEducationalInfo()
        self.objworkexp = applicant_work_experience.WorkExperience()

    # method to validate the onboarding session
    def _validate_recruitment_session(self):
        if 'applicant_id' in http.request.session:
            applicant_id = http.request.session['applicant_id']
            applicant_data = http.request.env['hr.applicant'].sudo().browse(applicant_id)
            if applicant_data.exists():
                return applicant_data if applicant_data.stage_id.id != 10 else False
            else:
                # del http.request.session['applicant_id']
                return False
        else:
            return False

    @http.route('/receducationaldata/', auth='public', website=True, csrf=False)
    def educationaldata(self, **kw):
        applicant_data = self._validate_recruitment_session()
        if applicant_data:
            edudict = self.objeduinfo.getEducationaldatafromDB(applicant_data)

            return http.request.render('kw_recruitment.kw_recruitment_educational_details', edudict)
        else:
            return http.request.redirect('/applicant-enrollment', )
        
    @http.route('/receducationalsavedata/', auth='public', methods=['POST', ], website=True, csrf=False)
    def educationalsavedata(self, **kw):
        # print(kw)
        applicant_data = self._validate_recruitment_session()
        if applicant_data:
            result_data = self.objeduinfo.saveEducationalinfo(applicant_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_recruitment.kw_recruitment_educational_details', result_data)
            else:
                return http.request.redirect('/appliworkexperiencedetails', )
        else:
            return http.request.redirect('/applicant-enrollment', )
        
    @http.route('/appliworkexperiencedetails/', auth='public', website=True, csrf=False)
    def work_experiencedetails(self, **kw):
        applicant_data = self._validate_recruitment_session()
        if applicant_data:
            workdict = self.objworkexp.getWorkexperiencedetailsfromDB(applicant_data)
            # print(workdict)
            return http.request.render('kw_recruitment.kw_applicant_work_experience_detail', workdict)
        else:
            return http.request.redirect('/applicant-enrollment', )

    @http.route('/appliworkexperiencedata/', methods=['POST', ], auth='public', website=True, csrf=False)
    def work_experiencedata(self, **kw):
        applicant_data = self._validate_recruitment_session()
        if applicant_data:
            result_data = self.objworkexp.saveWorkinformation(applicant_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_recruitment.kw_applicant_work_experience_detail', result_data)
            else:
                applicant_data.write({'submit_edu_work': True})
                applicant_created_by = http.request.env['hr.employee'].sudo().search(
                    [('user_id', '=', applicant_data.create_uid.id)])

                submit_mail_template = http.request.env.ref('kw_recruitment.kw_applicant_submit_email_template')
            email_cc = ''
            http.request.env['mail.template'].sudo().browse(submit_mail_template.id).with_context(
                email_to=applicant_created_by.work_email, email_name='All',
                email_cc=email_cc).send_mail(applicant_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            return http.request.redirect('/rec-thankyou', )
        else:
            return http.request.redirect('/applicant-enrollment', )

    @http.route('/rec-thankyou/', auth='public', website=True)
    def thankyou(self, **args):
        return http.request.render('kw_onboarding.kwrecruitment_message_view')
    
    # @http.route('/applicant-enrollment/', auth='public', website=True)
    # def applicant(self, **args):
    #     alphabet = '0123456789abcdefABCDEF'
    #     random_val = ''.join(random.choice(alphabet) for _ in range(32))
    #     # random_val = ''.join(secrets.choice(alphabet) for _ in range(32))
    #     request.session['key'] = random_val
    #     return http.request.render('kw_recruitment.kwinterview_applicant_template', {"key": random_val})

    @http.route('/getmaxtries/', type="json", auth='public', website=True)
    def getmaxtries(self, **args):
        if 'user_input_mobile' in args and args['user_input_mobile'] != '': 
            return_data = self.try_count(int(args['user_input_mobile']))
            return return_data
    
    def try_count(self,user_input_mobile):
        model_data = http.request.env['hr.applicant'].sudo().search(
                [('partner_mobile', '=', user_input_mobile), ("stage_id.id", '!=', 10)])
        if user_input_mobile:
            otp_record_set = http.request.env['otp_max_attempt_log']
            fetched_data = otp_record_set.sudo().search([('mobile', '=', user_input_mobile), ("applicant_id", '=', model_data.id),('date','=',date.today())], order='id desc', limit=1)
            # fetch data from log``
            if fetched_data:
                result = 0
                # last_rec = otp_record_set.sudo().search([('mobile', '=', user_input_mobile), ("applicant_id", '=', model_data.id),('date','=',date.today()),('max_attempts','=',5)], order='id desc', limit=1)
                last_rec = fetched_data if fetched_data.max_attempts == 1 else ''
                if last_rec:
                    result = (datetime.datetime.now() - last_rec.create_date).total_seconds()
                # else:
                    # result = datetime.datetime.now() - fetched_data.create_date
                    # result = 30
                comp = result > 3600
                # dt = (last_rec.create_date if last_rec else fetched_data.create_date) + timedelta(hours=1)
                now_utc = last_rec.create_date.replace(tzinfo=pytz.utc)
                # print("now_utc===",now_utc)
                dt = now_utc.astimezone(timezone('Asia/Kolkata')).replace(tzinfo=None) + timedelta(hours=1)
                # print("ccccccctime_stampcccccccccccc",dt)
                dt_sec = ((last_rec.create_date if last_rec else fetched_data.create_date) + timedelta(hours=1) - datetime.datetime.now()).total_seconds()
                if comp:
                    fetched_data.is_passed = True
                    return [5,comp,dt,dt_sec]
                elif fetched_data.max_attempts > 1:
                    return [fetched_data.max_attempts-1,comp,dt,dt_sec]
                else:
                    template = http.request.env.ref('kw_recruitment.applicant_otp_max_tries_exceeded')
                    max_attempted_email = http.request.env['mail.template'].sudo().browse(template.id).with_context(email_to=model_data.email_from, email_name=model_data.partner_name).send_mail(model_data.id, notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)

                    return [0,comp,dt,dt_sec]
            else:
                return [5]
    
    @http.route('/create_attempt_stats_log/', type="json", auth='public', website=True)
    def create_attempt_stats_log(self, **args):
        if 'user_input_mobile' in args and args['user_input_mobile'] != '':
            self.create_log(args['user_input_mobile'])
    
    def create_log(self,user_input_mobile):
        model_data = http.request.env['hr.applicant'].sudo().search(
                [('partner_mobile', '=', user_input_mobile), ("stage_id.id", '!=', 10)])
        log = http.request.env['otp_max_attempt_log']
        count = 0
        # fetch data from log
        pre_exist =log.sudo().search([('mobile', '=',int(model_data.partner_mobile)), ("applicant_id", '=', model_data.id),('date','=',date.today())], order='id desc', limit=1)
        if not pre_exist or pre_exist.max_attempts == 1:
            count = 5
        else:
            count = pre_exist.max_attempts - 1
        #insert new log with last count   
        data = log.sudo().create({
            'mobile':model_data.partner_mobile,
            'applicant_id':model_data.id,
            'date':date.today(),
            'max_attempts':count
        })

    @http.route('/searchMobNumber/', type="json", auth='public', website=True)
    def searchMobNumber(self, **args):
        model_data = http.request.env['hr.applicant'].sudo().search(
            [('partner_mobile', '=', args['user_input_mobile']), ("stage_id.id", '!=', 10)])
        mobile_number = model_data.partner_mobile
        reference_no_data = model_data.name
        request.session['user_input_mobile'] = args['user_input_mobile']

        if model_data.id == 0:
            return 'status0'
        elif model_data.emp_id.id:
            return 'status1'
        elif model_data.submit_edu_work == True:
            return 'status2'

        # elif not model_data.otp_number:
        #     otp_number =  http.request.env['kwonboard_enrollment'].sudo().create({'otp_number':value_of_otp,'generate_time':otp_generate_time})
        #     return otp_number

        else:
            current_date_time = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
            date_time = current_date_time + datetime.timedelta(0, 600)
            date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
            demo_mode_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mode_status')
            mail_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mail_status') or False
            sms_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_sms_status') or False

            if demo_mode_enabled:
                otp_value = '1234'
            else:
                otp_value = ''.join(random.choice(string.digits) for _ in range(4))
                # otp_value = ''.join(secrets.choice(string.digits) for _ in range(4))
            # print("OTP is : ", otp_value)

            # insert in OTP log
            otp = http.request.env['kw_applicant_generate_otp'].sudo().create(
                {'applicant_id': model_data.id,
                 'mobile_no': mobile_number,
                 'otp': otp_value,
                 'exp_date_time': date_time})

            if not demo_mode_enabled:
               
                if sms_enabled:
                    template = http.request.env['send_sms'].sudo().search([('name', '=', 'Onboarding_OTP')])
                    record_id = model_data.id
                    http.request.env['send_sms'].sudo().send_sms(template, record_id)

                # For Sending OTP to mail
                if mail_enabled:
                    template = http.request.env.ref('kw_recruitment.applicant_otp_email_template')
                    opt_email = http.request.env['mail.template'].sudo().browse(template.id).send_mail(otp.id, notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)

            email = model_data.email_from
            # print("email=====================", email)
            index = email.index("@")
            final_email = email[0:3] + re.sub("\w", "*", email[3:index]) + email[index:]
            return final_email

    @http.route('/searchOTPno/', type="json", auth='public', website=True)
    def searchOTPno(self, **args):
        # print("===args===",args,"session----------------------------------",request.session)
        mobile = request.session.get('user_input_mobile', None)
        if mobile:
            count = self.getmaxtries()
        else:
            pass
        # key = binascii.unhexlify(args['auth_secret_key'])
        key = binascii.unhexlify(request.session.get('key', None))
        # Decryption
        cipher = AES.new(key, AES.MODE_ECB)
        decoded = binascii.a2b_base64(args['otp'])
        decrypted = unpad(cipher.decrypt(decoded), AES.block_size).decode('utf-8')
        # print("decrypted====================================",decrypted)
        decoded_otp = decrypted
        otp_model = http.request.env['kw_applicant_generate_otp'].sudo().search(
            [('otp', '=', decoded_otp), ('mobile_no', '=', mobile)], limit=1, order="id desc")
        # print("otp===================", otp_model.mobile_no)
        model_id = otp_model.applicant_id.id
        otp_mobile = otp_model.mobile_no
        current_dt = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
        current_dt = current_dt.strftime("%Y-%m-%d %H:%M:%S")
        exp_datetime_value = otp_model.exp_date_time
        if otp_mobile != mobile:
            a = self.create_log(mobile)
            return 'status0'
        elif (otp_model.otp != decoded_otp) and model_id == 1:
            self.create_log(mobile)
            return 'status1'
        elif model_id == 0:
            self.create_log(mobile)
            return 'status2'
        elif str(current_dt) > str(exp_datetime_value):
            self.create_log(mobile)
            return 'status3'
        elif count == 0:
            return 'restrictLogin'
        else:
            http.request.session['id'] = model_id
            http.request.session['mobile'] = otp_mobile
            http.request.session['applicant_id'] = model_id
            return model_id

    @http.route('/intermediateview/', auth='public', website=True)
    def intermediateView(self, **kw):
        http.request.render('kw_recruitment.kwrecruitment_intermediate_view')

    @http.route('/employee-jd-view', auth='public', type='http', website=True,csrf=False)
    def employee_jd_details(self, **kw):
        emp_rec = request.env.user.employee_ids[0]
        if emp_rec:
            jd_emp = emp_rec.mrf_id.job_role_desc
            if not jd_emp:
                emp_role = request.env['hr.job.role'].sudo().search([('designations', '=', emp_rec.job_id.id)])
                jd_emp = emp_role.description
            employee_position = request.env.user.employee_ids.job_id.name
            return http.request.render('kw_recruitment.employee_jd_view', {'jd': jd_emp,
                                                                           'emp_job': employee_position})
        else:
            http.request.session['skip_jd'] = True
        return http.request.redirect('/web')
    
    @http.route('/employee-jd-submit', auth='public', website=True, csrf=False)
    def emp_jd_submit(self, **kw):
        # print("request.env.user.employee_ids[0].id >>> ", request.env.user.employee_ids)
        if request.env.user.employee_ids:
            record = request.env['kw_employee_onboarding_checklist'].sudo().search(
                [('employee_id', '=', request.env.user.employee_ids[0].id)])
            if record:
                record.sudo().write({'jd': 'yes'})
            else:
                request.session['skip_jd'] = True
        return request.redirect('/web')

    @http.route('/employee-jd-skip', auth='user', website=True, csrf=False)
    def skip_jd_submit(self, **kw):
        try:
            http.request.session['skip_jd'] = True
            return http.request.redirect('/web')
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
    
                
