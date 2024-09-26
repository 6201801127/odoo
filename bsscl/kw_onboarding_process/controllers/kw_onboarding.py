# -*- coding: utf-8 -*-

from odoo import http, api

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


class kw_onboardging_process(http.Controller):

    def __init__(self):
        self.objpersonal = kw_personal_details.Personaldetails()
        self.objeduinfo = kw_educational_info.EducationalInfo()
        self.objworkexp = kw_work_experience.WorkExperience()
        self.objidentity = kw_identification_info.Identificationinfo()

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
            #         return http.request.render('kw_onboarding_process.kwonboard_personal_details', result_data)
            #     else:
            #         return http.request.redirect('/educationaldetails', )

            personaldict = self.objpersonal.getPersonaldetailsfromDB(enroll_data)
            return http.request.render('kw_onboarding_process.kwonboard_personal_details', personaldict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/personaldata/', auth='public', methods=['POST', ], website=True, csrf=False)
    def personaldata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            # print("inside personal data")        
            result_data = self.objpersonal.savePersonalInfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding_process.kwonboard_personal_details', result_data)
            else:
                return http.request.redirect('/educationaldetails', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/educationaldetails/', auth='public', website=True, csrf=False)
    def educationaldetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            edudict = self.objeduinfo.getEducationalInfofromDB(enroll_data)

            return http.request.render('kw_onboarding_process.kwonboard_educational_details', edudict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/educationaldata/', auth='public', methods=['POST', ], website=True, csrf=False)
    def educationaldata(self, **kw):
        # print(kw)
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objeduinfo.saveEducationalinfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding_process.kwonboard_educational_details', result_data)
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
            return http.request.render('kw_onboarding_process.kwonboard_work_experience_detail', workdict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/workexperiencedata/', methods=['POST', ], auth='public', website=True, csrf=False)
    def work_experiencedata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objworkexp.saveWorkinformation(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding_process.kwonboard_work_experience_detail', result_data)
            else:
                return http.request.redirect('/identificationdetails', )
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/identificationdetails/', auth='public', website=True, csrf=False)
    def identificationdetails(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            idendict = self.objidentity.getIdentificationdetailsfromDB(enroll_data)
            return http.request.render('kw_onboarding_process.kwonboard_identification_details', idendict)
        else:
            return http.request.redirect('/onboarding', )

    @http.route('/identificationdata/', auth='public', website=True, csrf=False)
    def identificationdata(self, **kw):
        enroll_data = self._validate_onboarding_session()
        if enroll_data:
            result_data = self.objidentity.saveIdentificationInfo(enroll_data, **kw)
            if 'err_msg' in result_data or ('draft' in result_data and 'success_msg' in result_data):
                return http.request.render('kw_onboarding_process.kwonboard_identification_details', result_data)
            else:
                email_cc = http.request.env['kwonboard_enrollment'].sudo().get_designation_cc(rec_set=enroll_data)
                candidate_template = http.request.env.ref('kw_onboarding_process.kw_candidate_submit_email_template')
                enroll_created_by = http.request.env['hr.employee'].sudo().search([('user_id', '=', enroll_data.create_uid.id)])
                email_fr = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.responsible_person')
                emp_id = int(email_fr) if email_fr != 'False' else False
                if enroll_data.create_uid.id == 1 and emp_id:
                    emp = http.request.env['hr.employee'].sudo().browse(emp_id)
                    email_to, email_name = emp.work_email, emp.name
                else:
                    emp = http.request.env['res.users'].sudo().browse(enroll_data.create_uid.id)
                    email_to, email_name = emp.email, emp.name
                http.request.env['mail.template'].sudo().browse(candidate_template.id).with_context(email_to=email_to, email_name=email_name, 
                        email_cc=email_cc).send_mail(enroll_data.id)
                return http.request.redirect('/thankyou', )
        else:
            return http.request.redirect('/onboarding', )

    # @http.route('/success/', auth='public', website=True)
    # def success(self, **args):
    #     return http.request.render('kw_onboarding_process.kwonboard_message_view')

    @http.route('/thankyou/', auth='public', website=True)
    def thankyou(self, **args):
        return http.request.render('kw_onboarding_process.kwonboard_message_view')

    @http.route('/onboarding/', auth='public', website=True)
    def onboarding(self, **args):
        return http.request.render('kw_onboarding_process.kwonboard_onboarding')

    @http.route('/searchMobNo/', type="json", auth='public', website=True)
    def searchMobNo(self, **args):
        model_data = http.request.env['kwonboard_enrollment'].sudo().search(
            [('mobile', '=', args['user_input_mobile']), ('state', '=', '1')])
        mobile_number = model_data.mobile
        reference_no_data = model_data.reference_no

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

            demo_mode_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.module_onboarding_mode_status')

            mail_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.module_onboarding_mail_status') or False

            sms_enabled = http.request.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.module_onboarding_sms_status') or False

            if demo_mode_enabled:
                otp_value = '1234'
            else:
                otp_value = ''.join(random.choice(string.digits) for _ in range(4))
            print("OTP is : ", otp_value)

            # insert in OTP log

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
                    template = http.request.env.ref('kw_onboarding_process.otp_email_template')
                    opt_email = http.request.env['mail.template'].sudo().browse(template.id).send_mail(model_data.id, force_send=True)

            email = model_data.email
            index = email.index("@")
            final_email = email[0:3] + re.sub("\w", "*", email[3:index]) + email[index:]
            return final_email
            # return otp_value

    @http.route('/searchOTP/', type="json", auth='public', website=True)
    def searchOTP(self, **args):
        otp_model = http.request.env['kwonboard_enrollment'].sudo().search(
            [('otp_number', '=', args['otp']), ('mobile', '=', args['mobile'])], limit=1)
        model_id = otp_model.id
        otp_mobile = otp_model.mobile
        current_dt = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
        current_dt = current_dt.strftime("%Y-%m-%d %H:%M:%S")
        expdatetime_value = otp_model.generate_time
        # enroll_model = self.env['kwonboard_enrollment'].search([('mobile','=',args['mob'])])
        ref_mobile = args['mobile']
        # print(ref_mobile)
        if otp_mobile != ref_mobile:
            return 'status0'
        elif (otp_model.otp_number != args['otp']) and model_id == 1:
            return 'status1'
        elif model_id == 0:
            return 'status2'
        elif str(current_dt) > str(expdatetime_value):
            return 'status3'
        else:
            http.request.session['id'] = model_id
            http.request.session['mobile'] = otp_mobile
            http.request.session['enrolment_id'] = model_id
            return model_id

    @http.route('/intermediateview/', auth='public', website=True)
    def intermediateview(self, **kw):
        http.request.render('kw_onboarding_process.kwonboard_intermediate_view')

    # @http.route('/message/', method=['POST'], auth='public', website=True)countryfilter
    # def intermediateview(self, **kw):
    #     http.request.render('kw_onboarding_process.kwonboard_message_view')
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
                    education_file = f'{education_path}/{rec.stream_id.name}{extension}'
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
                
        
        return request.make_response(byte.getvalue(),[('Content-Type', 'application/x-zip-compressed'),
                                            ('Content-Disposition', content_disposition(zip_filename))])