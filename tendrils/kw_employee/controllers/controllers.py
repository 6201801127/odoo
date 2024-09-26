# -*- coding: utf-8 -*-

import requests, os, zipfile, base64, shutil, json
from zipfile import ZipFile
from io import BytesIO
from mimetypes import guess_extension
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.web.controllers.main import content_disposition
from odoo.addons.restful.common import valid_response, invalid_response


class WebSearchReadExtension(main.DataSet):
    def do_search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        if model == 'hr.employee':
            Model = request.env[model]
            records = Model.search_read(domain, fields, offset=offset or 0, limit=limit or False, order=sort or False)
            if not records:
                return {
                    'length': 0,
                    'records': []
                }
            if limit and len(records) == limit:
                length = Model.search_count(Model.get_domain(domain))
            else:
                length = len(records) + (offset or 0)
            return {
                'length': length,
                'records': records
            }

        return super().do_search_read(model, fields, offset, limit, domain, sort)


class kw_postonboard_checklist_data(http.Controller):

    @http.route('/get_checklist_report', type='json', auth="user", website=True)
    def get_checklist_report(self, **args):
        # post_onboarding_data = dict()
        # post_onboarding_data['employee_name_dict'] = []
        # post_onboarding_data['joining_kit_dict'] = []
        # post_onboarding_data['doc_collection_dict'] = []
        # post_onboarding_data['kw_profile_update_dict'] = []
        # post_onboarding_data['hard_copy_verification_dict'] = []
        # post_onboarding_data['kw_id_generation_dict'] = []
        # post_onboarding_data['email_id_creation_dict'] = []
        # post_onboarding_data['telephone_extention_dict'] = []
        # post_onboarding_data['health_insurance_dict'] = []
        # post_onboarding_data['esi_dict'] = []
        # post_onboarding_data['accident_policy_dict'] = []
        # post_onboarding_data['gratuity_dict'] = []
        # post_onboarding_data['pf_dict'] = []
        # post_onboarding_data['work_station_dict'] = []
        # post_onboarding_data['hr_induction_dict'] = []
        # post_onboarding_data['jd_dict'] = []
        # post_onboarding_data['bond_formality_dict'] = []
        # post_onboarding_data['appointment_letter_dict'] = []
        # post_onboarding_data['id_card_dict'] = []
        # post_onboarding_data['criminal_record_verification_dict'] = []
        # post_onboarding_data['background_verification_dict'] = []
        # post_onboarding_data['status_dict'] = []
        # post_onboarding_data['joining_date_dict'] = []
        #
        # checklist_recs = request.env['kw_employee_onboarding_checklist'].sudo().search([])
        #
        # for rec in checklist_recs:
        #     emp_rec = request.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id)])
        #     post_onboarding_data['employee_name_dict'].append(f"{emp_rec.name} ({emp_rec.emp_code})")
        #     post_onboarding_data['joining_kit_dict'].append(rec.joining_kit)
        #     post_onboarding_data['doc_collection_dict'].append(rec.doc_collection)
        #     post_onboarding_data['kw_profile_update_dict'].append(rec.kw_profile_update)
        #     post_onboarding_data['hard_copy_verification_dict'].append(rec.hard_copy_verification)
        #     post_onboarding_data['kw_id_generation_dict'].append(rec.kw_id_generation)
        #     post_onboarding_data['email_id_creation_dict'].append(rec.email_id_creation)
        #     post_onboarding_data['telephone_extention_dict'].append(rec.telephone_extention)
        #     post_onboarding_data['health_insurance_dict'].append(rec.health_insurance)
        #     post_onboarding_data['esi_dict'].append(rec.esi)
        #     post_onboarding_data['accident_policy_dict'].append(rec.accident_policy)
        #     post_onboarding_data['gratuity_dict'].append(rec.gratuity)
        #     post_onboarding_data['pf_dict'].append(rec.pf)
        #     post_onboarding_data['work_station_dict'].append(rec.work_station)
        #     post_onboarding_data['hr_induction_dict'].append(rec.hr_induction)
        #     post_onboarding_data['jd_dict'].append(rec.jd)
        #     post_onboarding_data['bond_formality_dict'].append(rec.bond_formality)
        #     post_onboarding_data['appointment_letter_dict'].append(rec.appointment_letter)
        #     post_onboarding_data['id_card_dict'].append(rec.id_card)
        #     post_onboarding_data['criminal_record_verification_dict'].append(rec.criminal_record_verification)
        #     post_onboarding_data['background_verification_dict'].append(rec.background_verification)
        #     post_onboarding_data['status_dict'].append(rec.status)
        #     if emp_rec.date_of_joining:
        #         post_onboarding_data['joining_date_dict'].append(emp_rec.date_of_joining.strftime('%d-%b-%Y'))
        #     else:
        #         post_onboarding_data['joining_date_dict'].append(False)

        return dict()


class EmployeeDocDownload(http.Controller):

    @http.route('/download_employee_doc/<int:id>', type='http', auth="user")
    def get_download_zip(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        applicant = empObj.onboarding_id.applicant_id.document_ids[0].content_file if empObj.onboarding_id.applicant_id else False
        empDir = str(empObj.id)
        byte = BytesIO()
        zf = ZipFile(byte, "w")
        emp_name = empObj.name.replace(" ", "_")
        zip_filename = emp_name + '_' + str(empObj.emp_code) + '.zip'
        mainDirectory = 'EmployeeDocs'

        profile_flag, identification_flag, education_flag, workexperience_flag, exitletter_flag, probationcomplete_flag = False, False, False, False, False, False
        flagdict = {'profile_flag': False, 'medical_certificate_flag': False, 'identification_flag': False,
                    'education_flag': False, 'workexperience_flag': False, 'offerletter_flag': False,'cv_flag': False, 'exitletter_flag': False, 'probationcomplete_flag':False}
        if not os.path.exists(mainDirectory):
            os.makedirs(mainDirectory)

        profile_path = os.path.join(mainDirectory, empDir, 'profilepic')
        medical_certificate_path = os.path.join(mainDirectory, empDir, 'medicalcertificate')
        identification_path = os.path.join(mainDirectory, empDir, 'identification')
        education_path = os.path.join(mainDirectory, empDir, 'education')
        workexp_path = os.path.join(mainDirectory, empDir, 'workexperience')
        offerletter_path = os.path.join(mainDirectory, empDir, 'offerletter')
        cv_applicant = os.path.join(mainDirectory, empDir, 'cv')
        exitletter_path = os.path.join(mainDirectory, empDir, 'exitletter')
        probation_completion_path = os.path.join(mainDirectory, empDir, 'probationcomplete')
        # Create folder depending on records in respective fields

        if empObj.image:
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            flagdict['profile_flag'] = True
            uploaded_doc_b64_string = base64.b64decode(empObj.image)
            extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
            profile_file = f'{profile_path}/{empObj.name}{extension}'
            with open(profile_file, 'wb') as fp:
                fp.write(uploaded_doc_b64_string)
            zf.write(profile_file)

        if empObj.medical_certificate:
            if not os.path.exists(medical_certificate_path):
                os.makedirs(medical_certificate_path)
            flagdict['medical_certificate_flag'] = True
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
                    flagdict['identification_flag'] = True
                    identification_type = dict(request.env['kwemp_identity_docs']._fields['name'].selection).get(rec.name)
                    uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                    extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                    identification_file = f'{identification_path}/{identification_type}{extension}'
                    with open(identification_file, 'wb') as fp:
                        fp.write(uploaded_doc_b64_string)
                    zf.write(identification_file)

        if empObj.educational_details_ids:
            if not os.path.exists(education_path):
                os.makedirs(education_path)
            for rec in empObj.educational_details_ids:
                if rec.uploaded_doc:
                    flagdict['education_flag'] = True
                    uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                    extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                    education_file = f'{education_path}/{rec.course_id.name}{extension}'
                    with open(education_file, 'wb') as fp:
                        fp.write(uploaded_doc_b64_string)
                    zf.write(education_file)

        if empObj.id:
            if not os.path.exists(probation_completion_path):
                os.makedirs(probation_completion_path)
            get_data = request.env['kw_feedback_details'].sudo().search(['&',('assessee_id', '=', empObj.id),('feedback_status','=','6')],limit=1)  

            if get_data:
                report_template_id = request.env.ref('kw_assessment_feedback.probation_completion_pdf_report_id').render_qweb_pdf(get_data.id)
                flagdict['probationcomplete_flag'] = True
                extension = guess_extension(guess_mimetype(report_template_id[0]))
                probation_file = f'{probation_completion_path}/{get_data.id}{extension}'
                with open(probation_file, 'wb') as fp:
                    fp.write(report_template_id[0])
                zf.write(probation_file)

        if empObj.id:
            if not os.path.exists(exitletter_path):
                os.makedirs(exitletter_path)
            exit_data = request.env['kw_resignation_experience_letter'].sudo().search(
                [('employee_id', '=', empObj.id)], limit=1)  
            if exit_data:
                report_template_id = request.env.ref('kw_eos.report_letter_experience_letter').render_qweb_pdf(exit_data.id)
                flagdict['exitletter_flag'] = True
                extension = guess_extension(guess_mimetype(report_template_id[0]))
                exitletter_file = f'{exitletter_path}/{exit_data.id}{extension}'
                with open(exitletter_file, 'wb') as fp:
                    fp.write(report_template_id[0])
                zf.write(exitletter_file)

        if empObj.work_experience_ids:
            if not os.path.exists(workexp_path):
                os.makedirs(workexp_path)
            for rec in empObj.work_experience_ids:
                if rec.uploaded_doc:
                    flagdict['workexperience_flag'] = True
                    uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                    extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                    workexp_file = f'{workexp_path}/{rec.name}{extension}'
                    with open(workexp_file, 'wb') as fp:
                        fp.write(uploaded_doc_b64_string)
                    zf.write(workexp_file)
                    
        if applicant:
            if not os.path.exists(cv_applicant):
                os.makedirs(cv_applicant)
                uploaded_doc_b64_string = base64.b64decode(applicant)
                extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                cv_file = f'{cv_applicant}/{empObj.name}{extension}'
                with open(cv_file, 'wb') as fp:
                    fp.write(uploaded_doc_b64_string)
                zf.write(cv_file)


        # if empObj.onboarding_id.applicant_id:
        #     if not os.path.exists(offerletter_path):
        #         os.makedirs(offerletter_path)
        #     offer_data = http.request.env['hr.applicant.offer'].sudo().search(
        #         [('applicant_id', '=', empObj.onboarding_id.applicant_id.id)], limit=1)
        #     if offer_data:
        #         if offer_data.offer_type == 'Intern':
        #             report_template_id = request.env.ref(
        #                 'kw_recruitment.report_letter_appointment_permanent').sudo().render_qweb_pdf(offer_data.id)
        #         elif offer_data.offer_type == 'Lateral':
        #             report_template_id = request.env.ref(
        #                 'kw_recruitment.report_letter_appointment_permanent_lateral').sudo().render_qweb_pdf(offer_data.id)
        #         elif offer_data.offer_type == 'RET':
        #             report_template_id = request.env.ref(
        #                 'kw_recruitment.report_letter_appointment_permanent_ret').sudo().render_qweb_pdf(offer_data.id)
        #         flagdict['offerletter_flag'] = True
        #         extension = guess_extension(guess_mimetype(report_template_id[0]))
        #         offerletter_file = f'{offerletter_path}/{offer_data.name}{extension}'
        #         with open(offerletter_file, 'wb') as fp:
        #             fp.write(report_template_id[0])
        #         zf.write(offerletter_file)

        zf.close()
        shutil.rmtree(os.path.join(mainDirectory, empDir))
        if any(flagdict):
            return request.make_response(byte.getvalue(), [('Content-Type', 'application/x-zip-compressed'),
                                                           ('Content-Disposition', content_disposition(zip_filename))])
        else:
            return request.not_found()