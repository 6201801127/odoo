# -*- coding: utf-8 -*-

from odoo import http, api
from datetime import date, timedelta

import re
import math, random, string
import datetime
import pytz
from odoo.http import request
import requests, os, zipfile, base64, shutil
from mimetypes import guess_extension
from odoo.tools.mimetypes import guess_mimetype
from zipfile import ZipFile
from io import BytesIO
from odoo.addons.web.controllers.main import content_disposition

from . import kw_personal_details
from . import kw_educational_info
from . import kw_work_experience
from . import kw_identification_info
from . import kw_document_info
from dateutil import tz
from pytz import timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii
# import secrets

class kw_onboarding(http.Controller):

    def __init__(self):
        self.objpersonal = kw_personal_details.Personaldetails()
        self.objeduinfo = kw_educational_info.EducationalInfo()
        self.objworkexp = kw_work_experience.WorkExperience()
        self.objidentity = kw_identification_info.Identificationinfo()
        self.objdocument = kw_document_info.DocumentInfo()

    # method to validate the onboarding session
    def _validate_onboarding_session(self):
        if 'enrolment_id' in http.request.session:
            enrolment_id = http.request.session['enrolment_id']
            enroll_data = http.request.env['kwonboard_enrollment'].sudo().browse(enrolment_id)
            if enroll_data and enroll_data.state == '1':
                return enroll_data
            else:
                return False
        else:
            return False

    @http.route('/personaldetails/', auth='public', website=True, csrf=False)
    def personaldetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            # print(kw)
            # ##if form data submitted
            # if 'draft' in kw or 'next' in kw:
            #     result_data     = self.objpersonal.savePersonalInfo(enroll_data,**kw)
            #     ##if error occured or draft mode
            #     if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
            #         return http.request.render('kw_onboarding.kwonboard_personal_details', result_data)
            #     else:
            #         return http.request.redirect('/educationaldetails', )

            personaldict = self.objpersonal.getPersonaldetailsfromDB(enroll_data)
            return http.request.render('kw_onboarding.kwonboard_personal_details', personaldict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/personaldata/', auth='public', methods=['POST', ], website=True, csrf=False)
    def personaldata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            # print("inside personal data-----------",enroll_data,enroll_data.applicant_id)        
            result_data = self.objpersonal.savePersonalInfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding.kwonboard_personal_details', result_data)
            # elif enroll_data.applicant_id.submit_edu_work is True:
            #     # print("in elif of submit educational and work experience ")
            #     return http.request.redirect('/identificationdetails', )
            else:
                return http.request.redirect('/educationaldetails', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/educationaldetails/', auth='public', website=True, csrf=False)
    def educationaldetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            edudict = self.objeduinfo.getEducationalInfofromDB(enroll_data)

            return http.request.render('kw_onboarding.kwonboard_educational_details', edudict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/educationaldata/', auth='public', methods=['POST', ], website=True, csrf=False)
    def educationaldata(self, **kw):
        # print(kw)
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objeduinfo.saveEducationalinfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding.kwonboard_educational_details', result_data)
            else:
                return http.request.redirect('/workexperiencedetails', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/workexperiencedetails/', auth='public', website=True, csrf=False)
    def work_experiencedetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            workdict = self.objworkexp.getWorkexperiencedetailsfromDB(enroll_data)
            # print(workdict)
            return http.request.render('kw_onboarding.kwonboard_work_experience_detail', workdict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/workexperiencedata/', methods=['POST', ], auth='public', website=True, csrf=False)
    def work_experiencedata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objworkexp.saveWorkinformation(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding.kwonboard_work_experience_detail', result_data)
            else:
                return http.request.redirect('/identificationdetails', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/identificationdetails/', auth='public', website=True, csrf=False)
    def identificationdetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            idendict = self.objidentity.getIdentificationdetailsfromDB(enroll_data)
            return http.request.render('kw_onboarding.kwonboard_identification_details', idendict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/identificationdata/', auth='public', website=True, csrf=False)
    def identificationdata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objidentity.saveIdentificationInfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding.kwonboard_identification_details', result_data)
            else:
                return http.request.redirect('/documentdetails', )
        #     else:
        #         email_cc = http.request.env['kwonboard_enrollment'].sudo().get_designation_cc(rec_set=enroll_data)
        #         candidate_template = http.request.env.ref('kw_onboarding.kw_candidate_submit_email_template')
        #         enroll_created_by = http.request.env['hr.employee'].sudo().search([('user_id', '=', enroll_data.create_uid.id)])
        #         email_fr = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        #         emp_id = int(email_fr) if email_fr != 'False' else False
        #         if enroll_data.create_uid.id == 1 and emp_id:
        #             emp = http.request.env['hr.employee'].sudo().browse(emp_id)
        #             email_to, email_name = emp.work_email, emp.name
        #         else:
        #             emp = http.request.env['res.users'].sudo().browse(enroll_data.create_uid.id)
        #             email_to, email_name = emp.email, emp.name
        #         http.request.env['mail.template'].sudo().browse(candidate_template.id).with_context(email_to=email_to, email_name=email_name, 
        #                 email_cc=email_cc).send_mail(enroll_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        #         return http.request.redirect('/thankyou', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/saveDocumentDetailsOnchange/', auth="public", type="json", website=True, csrf=False)
    def saveDocumentDetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            docdic = self.objdocument.saveDocumentOnchange(enroll_data, **kw)
            return docdic
        return True

    @http.route('/documentdetails/', auth='public', website=True, csrf=False)
    def documentdetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            docdic = self.objdocument.getDocumentdetailsfromDB(enroll_data)
            return http.request.render('kw_onboarding.kwonboard_document_details', docdic) 
            # idendict
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/documentdetailsdata/', auth='public', website=True, csrf=False)
    def documentdetailsdata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            enroll_data.write({'state':'2',
                            'create_full_profile':True})
            # return http.request.redirect('/thankyou', )
            # result_data = self.objdocument.saveDocumentdetailsInfo(enroll_data, **kw)
            # if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
            #     return http.request.render('kw_onboarding.kwonboard_document_details', result_data)
            email_cc = http.request.env['kwonboard_enrollment'].sudo().get_designation_cc(rec_set=enroll_data)
            candidate_template = http.request.env.ref('kw_onboarding.kw_candidate_submit_email_template')
            enroll_created_by = http.request.env['hr.employee'].sudo().search([('user_id', '=', enroll_data.create_uid.id)])
            email_fr = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
            emp_id = int(email_fr) if email_fr != 'False' else False
            
            if enroll_data.create_uid.id == 1 and emp_id:
                
                emp = http.request.env['hr.employee'].sudo().browse(emp_id)
                email_to, email_name = emp.work_email, emp.name
            else:
                emp = http.request.env['res.users'].sudo().browse(enroll_data.create_uid.id)
                email_to, email_name = emp.email, emp.name
            http.request.env['mail.template'].sudo().browse(candidate_template.id).with_context(email_to=email_to, email_name=email_name, 
                    email_cc=email_cc).send_mail(enroll_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            return http.request.redirect('/thankyou', )
        else:
            return http.request.redirect('/onboarding', )

    # @http.route('/success/', auth='public', website=True)
    # def success(self, **args):
    #     return http.request.render('kw_onboarding.kwonboard_message_view')

    @http.route('/thankyou/', auth='public', website=True)
    def thankyou(self, **args):
        return http.request.render('kw_onboarding.kwonboard_message_view')

    @http.route('/onboarding/', auth='public', website=True)
    def onboarding(self, **args):
        alphabet = '0123456789abcdefABCDEF'
        random_val = ''.join(random.choice(alphabet) for _ in range(32))
        # random_val = ''.join(secrets.choice(alphabet) for _ in range(32))
        request.session['key'] = random_val
        return http.request.render('kw_onboarding.kwonboard_onboarding_template',{"key":random_val})

    @http.route('/getmaxtries_onboarding/', type="json", auth='public', website=True)
    def getmaxtries(self, **args):
        if 'user_input_mobile' in args and args['user_input_mobile'] != '': 
            return_data = self.try_count(int(args['user_input_mobile']))
            return return_data
    
    def try_count(self,user_input_mobile):
        model_data = http.request.env['kwonboard_enrollment'].sudo().search(
            [('mobile', '=', user_input_mobile), ('state', '=', '1')])
        if user_input_mobile:
            otp_record_set = http.request.env['otp_onboarding_max_attempt_log']
            fetched_data = otp_record_set.sudo().search(
                [('mobile', '=', user_input_mobile), ("enrollment_id", '=', model_data.id),
                 ('date', '=', date.today())], order='id desc', limit=1)
            # fetch data from log``
            if fetched_data:
                result = 0
                # last_rec = otp_record_set.sudo().search(
                #     [('mobile', '=', user_input_mobile), ("enrollment_id", '=', model_data.id),('date','=',date.today()),('max_attempts','=',1)], order='id desc', limit=1)
                last_rec = fetched_data if fetched_data.max_attempts == 1 else ''
                if last_rec:
                    result = (datetime.datetime.now() - last_rec.create_date).total_seconds()
                # else:
                #     result = datetime.datetime.now() - fetched_data.create_date
                comp = result > 3600
                # dt = (last_rec.create_date if last_rec else fetched_data.create_date) + timedelta(hours=1)
                now_utc = last_rec.create_date.replace(tzinfo=pytz.utc)
                # print("now_utc===",now_utc)
                dt = now_utc.astimezone(timezone('Asia/Kolkata')).replace(tzinfo=None) + timedelta(hours=1)
                # print("ccccccctime_stampcccccccccccc",dt)
                # dt = (last_rec.create_date if last_rec else fetched_data.create_date) + timedelta(hours=1)
                dt_sec = ((last_rec.create_date if last_rec else fetched_data.create_date) + timedelta(hours=1) - datetime.datetime.now()).total_seconds()
                if comp:
                    fetched_data.is_passed = True
                    return [5,comp,dt,dt_sec]
                elif fetched_data.max_attempts > 1:
                    return [fetched_data.max_attempts-1,comp,dt,dt_sec]
                else:
                    template = http.request.env.ref('kw_recruitment.onboarding_otp_max_tries_exceeded')
                    max_attempted_email = http.request.env['mail.template'].sudo().browse(template.id).with_context(email_to=model_data.email, email_name=model_data.name).send_mail(model_data.id, notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)
                    return [0, comp, dt, dt_sec]
            else:
                return [5]
    
    @http.route('/create_attempt_stats_log/', type="json", auth='public', website=True)
    def create_attempt_stats_log(self, **args):
        if 'user_input_mobile' in args and args['user_input_mobile'] != '':
            self.create_log(args['user_input_mobile'])
    
    def create_log(self,user_input_mobile):
        model_data = http.request.env['kwonboard_enrollment'].sudo().search(
            [('mobile', '=', user_input_mobile), ('state', '=', '1')])
        log = http.request.env['otp_onboarding_max_attempt_log']
        count = 0
        # fetch data from log
        pre_exist =log.sudo().search([('mobile', '=',int(model_data.mobile)), ("enrollment_id", '=', model_data.id),('date','=',date.today())], order='id desc', limit=1)
        if not pre_exist or pre_exist.max_attempts == 1:
            count = 5
        else:
            count = pre_exist.max_attempts - 1
        #insert new log with last count   
        data = log.sudo().create({
            'mobile':model_data.mobile,
            'enrollment_id':model_data.id,
            'date':date.today(),
            'max_attempts':count
        })

    @http.route('/searchMobNo/', type="json", auth='public', website=True)
    def searchMobNo(self, **args):
        model_data = http.request.env['kwonboard_enrollment'].sudo().search(
            [('mobile', '=', args['user_input_mobile']), ('state', '=', '1')])
        mobile_number = model_data.mobile
        reference_no_data = model_data.reference_no
        request.session['user_input_mobile'] = args['user_input_mobile']

        if model_data.id == 0:
            return 'status0'
        elif model_data.emp_id.id:
            return 'status1'
        elif model_data.state != "1":
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
            http.request.env['kw_generate_otp'].sudo().create({'mobile_no': mobile_number, 'otp': otp_value, 'exp_date_time': date_time})

            # update enrollment table with new OTP and time
            enroll_obj = model_data.sudo().write({'otp_number': otp_value, 'generate_time': date_time})

            # for sending otp to mail and mobile number
            if not demo_mode_enabled:
                # For Sending OTP to mobile number
                if sms_enabled:
                    template = http.request.env['send_sms'].sudo().search([('name', '=', 'Onboarding_OTP')])
                    record_id = model_data.id
                    http.request.env['send_sms'].sudo().send_sms(template, record_id)

                # For Sending OTP to mail
                if mail_enabled:
                    template = http.request.env.ref('kw_onboarding.otp_email_template')
                    opt_email = http.request.env['mail.template'].sudo().browse(template.id).send_mail(model_data.id, notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)

            email = model_data.email
            index = email.index("@")
            final_email = email[0:3] + re.sub("\w", "*", email[3:index]) + email[index:]
            return final_email
            # return otp_value

    @http.route('/searchOTP/', type="json", auth='public', website=True)
    def searchOTP(self, **args):
        # print("===args=onbo==",args)
        # key = binascii.unhexlify(args['auth_secret_key'])
        key = binascii.unhexlify(request.session.get('key', None))
        mobile = request.session.get('user_input_mobile', None)
        # Decryption
        cipher = AES.new(key, AES.MODE_ECB)
        decoded = binascii.a2b_base64(args['otp'])
        decrypted = unpad(cipher.decrypt(decoded), AES.block_size).decode('utf-8')
        # print("decrypted=========onbo===========================",decrypted)
        decoded_otp = decrypted
        otp_model = http.request.env['kwonboard_enrollment'].sudo().search(
            [('otp_number', '=', decoded_otp), ('mobile', '=', mobile)], limit=1)
        model_id = otp_model.id
        otp_mobile = otp_model.mobile
        current_dt = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
        current_dt = current_dt.strftime("%Y-%m-%d %H:%M:%S")
        expdatetime_value = otp_model.generate_time
        # enroll_model = self.env['kwonboard_enrollment'].search([('mobile','=',args['mob'])])
        # ref_mobile = args['mobile']
        # print(ref_mobile)
        if otp_mobile != mobile:
            self.create_log(mobile)
            return 'status0'
        elif (otp_model.otp_number != decoded_otp) and model_id == 1:
            self.create_log(mobile)
            return 'status1'
        elif model_id == 0:
            self.create_log(mobile)
            return 'status2'
        elif str(current_dt) > str(expdatetime_value):
            self.create_log(mobile)
            return 'status3'
        else:
            http.request.session['id'] = model_id
            http.request.session['mobile'] = otp_mobile
            http.request.session['enrolment_id'] = model_id
            return model_id

    @http.route('/intermediateview/', auth='public', website=True)
    def intermediateview(self, **kw):
        http.request.render('kw_onboarding.kwonboard_intermediate_view')

    # @http.route('/message/', method=['POST'], auth='public', website=True)countryfilter
    # def intermediateview(self, **kw):
    #     http.request.render('kw_onboarding.kwonboard_message_view')
    @http.route('/countryfilter/', type="json", auth='public', website=True)
    def searchcountry(self, **args):
        # print("Method called")

        model_data = http.request.env['res.country.state'].sudo().search(
            [('country_id', '=', int(args['country_id']))], )
        if len(model_data) > 0:
            states = dict()
            for state in model_data:
                states[state.id] = state.name
            # print(states)
            return states
        return 'None'

    # filter specialization as per the selected stream
    @http.route('/getStreamwisespecialization/', type="json", auth='public', website=True)
    def getStreamwisespecialization(self, **args):
        stream_id = int(args['stream_id']) if args['stream_id'] else 0
        specialization_data = http.request.env['kwmaster_specializations'].sudo().search(
            [('stream_id', '=', stream_id)])
        if len(specialization_data) > 0:
            specializations = []
            for record in specialization_data:
                specializations.append(dict(id=record.id, name=record.name))
            return specializations
        return 'None'

    # @http.route('/uploadify', type='http', auth='public', website=True, csrf=False)
    # def uploadify(self, **kw):
    #     print('now we can save data',kw)
    #     # print('now we can save data',self)
    #     image = base64.encodestring(kw['Filedata'].read())
    #     # medic_certificate = base64.encodestring(kw['medicPhoto'].read())
    #     personal_data = {
    #         'image': image,
    #         # 'medical_certificate': medic_certificate
    #     }
    #     # # if image != b'':
    #     # #     personal_data['image'] = image
    #     # # if medic_certificate != b'':
    #     # #     personal_data['medical_certificate'] = medic_certificate
    #     # kw.sudo().write(personal_data)        
    #     print('image upload',personal_data)
    #     # courses = http.request.env['kwmaster_course_name'].sudo().search([])
    #     # for course in courses:
    #     #     course_id = course.id
    #     #     education_data = kw.educational_ids
    #     #     print(education_data)
    #     #     uploaddoc = base64.encodestring(kw['ddlFile'].read()) 
    #     #     print('education_data',uploaddoc)
    #     #     file_name = kw['hidDllFile']
    #     #     education_datas = {'uploaded_doc': uploaddoc, 'filename': file_name}
    #     # kw.sudo().write(education_datas)                             
    #     # return 


# ===== Documents download in zip ====
class EnrollDocDownload(http.Controller):

    @http.route('/download_enroll_doc/<int:id>', type='http', auth="user")
    def get_download_zip(self, id=None, **kwargs):
        empObj = request.env['kwonboard_enrollment'].sudo().browse(id)
        applicant = empObj.applicant_id.document_ids[0].content_file if empObj.applicant_id.document_ids else False
        empDir = str(empObj.id)
        byte = BytesIO()
        zf = ZipFile(byte, "w")
        emp_name = empObj.name.replace(" ", "_")
        zip_filename = emp_name + '_' + str(empObj.id) + '.zip'
        mainDirectory = 'EnrollmentDocs'
        try:
            if not os.path.exists(mainDirectory):
                os.makedirs(mainDirectory)

            profile_path = os.path.join(mainDirectory, empDir, 'profile_picture')
            cv_applicant = os.path.join(mainDirectory, empDir, 'cv')
            medical_certificate_path = os.path.join(mainDirectory, empDir, 'medical_certificate')
            identification_path = os.path.join(mainDirectory, empDir, 'identification')
            education_path = os.path.join(mainDirectory, empDir, 'education')
            workexp_path = os.path.join(mainDirectory, empDir, 'work_experience')

            # Create folder depending on records in respective fields
            
            if applicant:
                if not os.path.exists(cv_applicant):
                    os.makedirs(cv_applicant)
                uploaded_doc_b64_string = base64.b64decode(applicant)
                extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                cv_file = f'{cv_applicant}/{empObj.name}{extension}'
                with open(cv_file, 'wb') as fp:
                    fp.write(uploaded_doc_b64_string)
                zf.write(cv_file)

            if empObj.image:
                if not os.path.exists(profile_path):
                    os.makedirs(profile_path)
                uploaded_doc_b64_string = base64.b64decode(empObj.image)
                extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                profile_file = f'{profile_path}/{empObj.name}{extension}'
                with open(profile_file, 'wb') as fp:
                    fp.write(uploaded_doc_b64_string)
                zf.write(profile_file)

            if empObj.medical_certificate:
                if not os.path.exists(medical_certificate_path):
                    os.makedirs(medical_certificate_path)
                uploaded_doc_b64_string = base64.b64decode(empObj.medical_certificate)
                # extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                medical_certificate_file = f'{medical_certificate_path}/{empObj.certificate_name}'
                with open(medical_certificate_file, 'wb') as fp:
                    fp.write(uploaded_doc_b64_string)
                zf.write(medical_certificate_file)

            if empObj.identification_ids:
                if not os.path.exists(identification_path):
                    os.makedirs(identification_path)
                for rec in empObj.identification_ids:
                    if rec.uploaded_doc:
                        identification_type = dict(request.env['kwonboard_identity_docs']._fields['name'].selection).get(rec.name)
                        uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                        extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                        identification_file = f'{identification_path}/{identification_type}{extension}'
                        with open(identification_file, 'wb') as fp:
                            fp.write(uploaded_doc_b64_string)
                        zf.write(identification_file)

            if empObj.educational_ids:
                if not os.path.exists(education_path):
                    os.makedirs(education_path)
                for rec in empObj.educational_ids:
                    if rec.uploaded_doc:
                        uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                        extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                        name = rec.stream_id.name
                        f_name = name.replace('/','-')
                        education_file = f'{education_path}/{f_name}{extension}'
                        with open(education_file, 'wb') as fp:
                            fp.write(uploaded_doc_b64_string)
                        zf.write(education_file)

            if empObj.work_experience_ids:
                if not os.path.exists(workexp_path):
                    os.makedirs(workexp_path)
                for rec in empObj.work_experience_ids:
                    if rec.uploaded_doc:
                        uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                        extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                        workexp_file = f'{workexp_path}/{rec.name}{extension}'
                        with open(workexp_file, 'wb') as fp:
                            fp.write(uploaded_doc_b64_string)
                        zf.write(workexp_file)

            zf.close()

            shutil.rmtree(os.path.join(mainDirectory, empDir))

            return request.make_response(byte.getvalue(), [('Content-Type', 'application/x-zip-compressed'),
                                                        ('Content-Disposition', content_disposition(zip_filename))])
        except Exception as e:
            request.env['onboading_document_download_log'].sudo().create({'applicant_id':empObj.name,'onboarding_id':empObj.id,'error_msg':e})
            