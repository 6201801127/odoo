from odoo import http, tools, SUPERUSER_ID, _
from odoo.addons.website.controllers.main import Website
from odoo.http import request
import json, sys, base64, pytz
from datetime import datetime, date, timedelta
from functools import reduce
from odoo import http
import logging, base64, io
import random, string
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class Maincontroller(Website):

    @http.route('/jobs', type='http', auth="public", website=True)
    def jobs(self, **kwargs):
        published_advertisements = request.env['hr.requisition.application'].sudo().search([('state', '=', 'published'), ('start_date', '<=', date.today()), ('last_date', '>=', date.today())])
        published_data = published_advertisements.mapped('published_advertisements')
        return request.render("recruitment_extended.recruitment_job_index", {
            'published_advertisements': published_data,
        })

    @http.route('/jobs/detail/<model("published.advertisement"):published_advertisement_id>', type='http', auth="public", website=True)
    def jobs_detail(self, published_advertisement_id, **kwargs):
        print(published_advertisement_id)
        return request.render("recruitment_extended.recruitment_job_detail", {
            'published_advertisement': published_advertisement_id.sudo(),
        })

    @http.route('/website_form/submit/form', type='http', auth="public", website=True, csrf=False)
    def create_hr_applicant_data_form(self, **kw):
        pass

    @http.route('/searchEmail', type="json", auth='public', website=True)
    def searchEmail(self, **args):
        data = {}
        try:
            if 'email' in args:
                recruitment_temp_model = request.env['hr_applicant_temp'].sudo()
                model_data = recruitment_temp_model.search([('email','=', args['email'])],limit=1)
                otp_value = 1234  # This line should be remove when go live
                # Uncomment this line to validate otp for applicant registration
                # otp_value = ''.join(random.choice(string.digits) for _ in range(4))
                template = request.env.ref('recruitment_extended.recruitment_email_otp_template')
                if model_data:
                    model_data.write({'otp':otp_value})
                    if template:
                        template.sudo().send_mail(model_data.id,notif_layout="mail.mail_notification_light")
                else:
                    new_created = recruitment_temp_model.create({
                        'email':args['email'],
                        'otp':otp_value,
                    })
                    if template:
                        template.sudo().send_mail(new_created.id,notif_layout="mail.mail_notification_light")

                data.update({'state':'200','email':args['email'],'otp':otp_value})   
            else:
                data.update({'state':'500'})
        except Exception as e:
            data.update({'state':'500',"error":str(e)})
        return data
    
    @http.route('/validateOTP', type="json", auth='public', website=True)
    def validateOTP(self, **args):
        data = {}
        if 'email' in args and 'otp' in args:
            recruitment_temp_model = request.env['hr_applicant_temp'].sudo()
            model_data = recruitment_temp_model.search([('email','=', args['email']),('otp','=', args['otp'])],limit=1)
            if model_data:
                request.session.update({'email': args['email']})
                data.update({'state':'200'})  
            else:
               data.update({'state':'500'})  
        else:
            data.update({'state':'500'})
        return data

    @http.route('/applicant_fees', type="json", auth='public', website=True)
    def get_applicant_fees(self, **args):
        amount = 0
        if 'published_advertisement_id' in args and 'gender' in args and 'category' in args:
            amount = request.env['hr.job'].sudo().get_application_fees(args['published_advertisement_id'],args['gender'],args['category'])
        return amount

    @http.route('''/jobs/apply/<model("published.advertisement"):published_advertisement>''', type='http', auth="public", website=True)
    def jobs_apply(self, published_advertisement, **kwargs):
        data = {'published_advertisement':published_advertisement.sudo()}
        template = "recruitment_extended.recruitment_email_web_template"

        if 'email' in request.session:
            exist_applicant_ids = request.env['hr_applicant_submitted_temp'].sudo().search([('email','=',request.session['email']),('advertisement_job_id','=',published_advertisement.sudo().job_id.id)])
            if exist_applicant_ids:
                data['exist_applicant'] = 1
            email_id = request.session['email']
            applicant_record = request.env['hr_applicant_temp'].sudo().search([('email','=',email_id)],limit=1)
            if applicant_record:
                data.update({'applicant_record': applicant_record,
                            'salutation': request.env['res.partner.title'].sudo().search([]),
                            'category': request.env['employee.category'].sudo().search([]),
                            'religion': request.env['employee.religion'].sudo().search([]),
                            'country': request.env['res.country'].sudo().search([('code','in',['BT','IN','NP'])]),
                            'state': request.env['res.country.state'].sudo().search([('country_id.code','in',['BT','IN','NP'])]),
                            'city': request.env['res.city'].sudo().search([('state_id.country_id.code','in',['BT','IN','NP'])]),
                            'nationality': request.env['applicant.nationality'].sudo().search([]),
                            'age_required':0,
                            'min_age':0,
                            'max_age':0,
                            })
                if applicant_record.state == 'draft':
                    data['exist_draft_applicant'] = 1

                if applicant_record.gender and applicant_record.category_id:
                    gender = applicant_record.gender
                    category_id = applicant_record.category_id.id
                    application_fees = request.env['hr.job'].sudo().get_application_fees(published_advertisement.id,gender,category_id)
                    if application_fees >0:
                        data['application_fees'] = application_fees

                if published_advertisement.sudo().job_id.age_required:
                    data['age_required'] = 1
                    data['min_age'] = published_advertisement.sudo().job_id.min_age
                    data['max_age'] = published_advertisement.sudo().job_id.max_age

                template = "website_hr_recruitment.apply"

        return request.render(template,data)
            
    @http.route('/website_form/submit/<model("published.advertisement"):published_advertisement>', type='json', auth="public", website=False, csrf=False,methods=['POST'])
    def submit_job_application_form(self,published_advertisement, **kw):
        url = ""
        data = {}
        address_ids = []
        education_ids = []
        experience_ids = []
        recruitment_temp_model = request.env['hr_applicant_temp'].sudo()
        recruitment_model = request.env['hr.applicant'].sudo()
        recruitment_submit_model = request.env['hr_applicant_submitted_temp'].sudo()
        try:
            stage_id = request.env['hr.recruitment.stage'].sudo().search([('sequence', '=', 1)], limit=1)
            if 'educational_details' in kw and kw['educational_details']:
                for educations in kw['educational_details']:
                    edu = {}
                    edu.update({
                        'grade':educations['grade'],
                        'field':educations['field'],
                        'stream':educations['stream'],
                        'school_name':educations['school_name'],
                        'passing_year': 'passing_year' in educations and educations['passing_year'] and int(educations['passing_year']) or False,
                        'percentage':educations['percentage'],
                        'certificate':educations.get('certificate',False),
                        'file_name':educations.get('file_name',False),
                        })
                    education_ids.append((0, 0, edu))

            if 'experience_details' in kw and kw['experience_details']:
                for experience in kw['experience_details']:
                    experience_ids.append((0, 0, {
                        'from_date':experience['from_date'] if experience['from_date'] else False,
                        'to_date':experience['to_date'] if experience['to_date'] else False,
                        'organization':experience['employer_name_address'],
                        'position':experience['position_held'],
                        'job_description':experience['job_description'],
                        'pay_scale':experience['pay_scale'],
                        'document':experience.get('document',False),
                        'file_name':experience.get('document_name',False),
                        # 'reasons':experience['reason'] if experience['reason'] else False,
                    }))

            if 'address_details' in kw and kw['address_details']:
                for address in kw['address_details']:
                    address_ids.append((0, 0, {
                        'address_type':address['address_type'],
                        'street':address['address_one'],
                        'street2':address['address_two'],
                        'city_id': int(address['city']),
                        'state_id': int(address['state']),
                        'country_id': int(address['country']),
                        'zip':address['pincode']
                    }))

            print(address_ids)
            if 'to_do' in kw:
                dict_data = {
                        'image': kw.get('image'),
                        'salutation': 'salutation' in kw and kw['salutation'] and int(kw.get('salutation')) or False,
                        'partner_first_name': kw.get('partner_first_name'),
                        'partner_middle_name': kw.get('partner_middle_name'),
                        'partner_last_name': kw.get('partner_last_name'),
                        'father_name':  kw.get('father_name'),
                        'mother_name': kw.get('mother_name'),
                        'email': kw.get('email_from'),
                        'mobile': kw.get('mobile'),
                        'phone_with_area_code': kw.get('phone_with_area_code'),
                        'aadhar': kw.get('aadhar_no'),
                        'pan': kw.get('pan_no'),
                        'dob': len(kw.get('dob','')) and kw['dob'] or False,
                        'gender': kw.get('gender'),
                        'category_id': 'category' in kw and kw['category'] and int(kw.get('category')) or False,
                        # 'nationality': kw.get('nationality'),
                        'nationality': 'nationality' in kw and kw['nationality'] and int(kw.get('nationality')) or False,
                        'religion': 'religion' in kw and kw['religion'] and int(kw.get('religion')) or False,
                        'ex_serviceman': kw.get('ex_service'),
                        'govt_employee': kw.get('govt_employee'),
                        'physically_handicapped': kw.get('physically_handicapped'),
                        'kind_of_disability': kw.get('kind_of_disability'),
                        'perc_disability': kw.get('perc_disability'),
                        'certificate_upload': kw.get('certificate_upload'),
                        'certificate_upload_filename': kw.get('certificate_upload_filename'),
                        'penalty': kw.get('penalty_last_10_year'),
                        'action_inquiry': kw.get('inquiry_going_on'),
                        'criminal': kw.get('criminal_case_pending'),
                        'relative_ccs': kw.get('relative_ccs'),
                        'relative_ccs_name': kw.get('relative_ccs_name'),
                        'addition_information': kw.get('additional_information'),
                        'achievements': kw.get('achievements'),
                        'address_ids': address_ids,
                        'education_ids': education_ids,
                        'experience_ids':experience_ids,
                        'signature_document':kw.get("signature"),
                        'signature_document_file_name': kw.get("signature_filename"),
                        'payment_document':kw.get("payment_document"),
                        'payment_document_file_name': kw.get("payment_filename"),
                        'other_doc':kw.get('other_doc'),
                        'other_doc_file_name':kw.get('other_doc_file_name'),
                        'dob_doc':kw.get('dob_doc'),
                        'dob_doc_file_name': kw.get('dob_doc_file_name'),
                        'aadhar_upload': kw.get('aadhar_upload'),
                        'aadhar_upload_filename': kw.get('aadhar_upload_filename'),
                        'pan_upload': kw.get('pan_upload'),
                        'pan_upload_filename': kw.get('pan_upload_filename'),
                        'nationality_upload': kw.get('nationality_upload'),
                        'nationality_upload_filename': kw.get('nationality_upload_filename'),

                        'payment_details': kw.get("payment_details"),
                        'state':'draft' if kw['to_do'] == 'draft' else 'submit',
                    }
                model_data = recruitment_temp_model.search([('email','=',kw.get('email_from'))],limit=1)
                if model_data:
                    model_data.education_ids = False 
                    model_data.experience_ids = False
                    model_data.address_ids = False
                    model_data.write(dict_data)
                else:
                    dict_data.update({'email': kw.get('email_from')})
                    recruitment_temp_model.create(dict_data)
                url = ''
                if kw['to_do'] == 'submit':
                    print("inside submit")
                    recruitment_submit_data = {
                        'advertisement_job_id': published_advertisement.sudo().job_id.id,
                        'advertisement_branch_id': published_advertisement.sudo().branch_id.id,
                        'image': kw.get('image'),
                        'salutation': 'salutation' in kw and kw['salutation'] and int(kw.get('salutation')) or False,
                        'partner_first_name': kw.get('partner_first_name'),
                        'partner_middle_name': kw.get('partner_middle_name'),
                        'partner_last_name': kw.get('partner_last_name'),
                        'father_name':  kw.get('father_name'),
                        'mother_name': kw.get('mother_name'),
                        'email': kw.get('email_from'),
                        'mobile': kw.get('mobile'),
                        'phone_with_area_code': kw.get('phone_with_area_code'),
                        'aadhar': kw.get('aadhar_no'),
                        'pan': kw.get('pan_no'),
                        'dob': len(kw.get('dob','')) and kw['dob'] or False,
                        'gender': kw.get('gender'),
                        'category_id': 'category' in kw and kw['category'] and int(kw.get('category')) or False,
                        # 'nationality': kw.get('nationality'),
                        'nationality': 'nationality' in kw and kw['nationality'] and int(kw.get('nationality')) or False,
                        'religion': 'religion' in kw and kw['religion'] and int(kw.get('religion')) or False,
                        'ex_serviceman': kw.get('ex_service'),
                        'govt_employee': kw.get('govt_employee'),
                        'physically_handicapped': kw.get('physically_handicapped'),
                        'kind_of_disability': kw.get('kind_of_disability'),
                        'perc_disability': kw.get('perc_disability'),
                        'certificate_upload': kw.get('certificate_upload'),
                        'certificate_upload_filename': kw.get('certificate_upload_filename'),
                        'penalty': kw.get('penalty_last_10_year'),
                        'action_inquiry': kw.get('inquiry_going_on'),
                        'criminal': kw.get('criminal_case_pending'),
                        'relative_ccs': kw.get('relative_ccs'),
                        'relative_ccs_name': kw.get('relative_ccs_name'),
                        'addition_information': kw.get('additional_information'),
                        'achievements': kw.get('achievements'),
                        'address_ids': address_ids,
                        'education_ids': education_ids,
                        'experience_ids':experience_ids,
                        'signature_document':kw.get("signature"),
                        'signature_document_file_name': kw.get("signature_filename"),
                        'payment_document':kw.get("payment_document"),
                        'payment_document_file_name': kw.get("payment_filename"),
                        'other_doc':kw.get('other_doc'),
                        'other_doc_file_name':kw.get('other_doc_file_name'),
                        'dob_doc':kw.get('dob_doc'),
                        'dob_doc_file_name': kw.get('dob_doc_file_name'),
                        'aadhar_upload': kw.get('aadhar_upload'),
                        'aadhar_upload_filename': kw.get('aadhar_upload_filename'),
                        'pan_upload': kw.get('pan_upload'),
                        'pan_upload_filename': kw.get('pan_upload_filename'),
                        'nationality_upload': kw.get('nationality_upload'),
                        'nationality_upload_filename': kw.get('nationality_upload_filename'),

                        'payment_details': kw.get("payment_details"),
                        'state':'draft' if kw['to_do'] == 'draft' else 'submit',
                    }
                    recruitment_dict = {
                        'title': int(kw.get('salutation')),
                        'name': kw.get('partner_first_name') + ' ' + kw.get('partner_middle_name') + ' ' + kw.get('partner_last_name'),
                        'personal_email': kw.get('email_from'),
                        'gende': kw.get('gender'),
                        'phone': kw.get('mobile'),
                        'pan_no': kw.get('pan_no'),
                        'aadhar_no': kw.get('aadhar_no'),
                        'religion_id': kw.get('religion'),
                        'category_id': kw.get('category'),
                        'ex_serviceman': kw.get('ex_service'), 
                        'dob': kw.get('dob'),
                        'nationality': int(kw.get('nationality')),
                        'differently_abled': kw.get('physically_handicapped'),
                        'kind_of_disability': kw.get('kind_of_disability'),
                        'perc_disability': kw.get('perc_disability'),
                        'certificate_upload': kw.get('certificate_upload'),
                        'certificate_upload_filename': kw.get('certificate_upload_filename'),
                        'address_ids': address_ids,
                        'prev_occu_ids':experience_ids,
                        'education_ids': education_ids,
                        'stage_id': stage_id.id,
                        'image':kw.get('image'),
                        # 'advertisement_line_id':advertisement_line.id,
                        'advertisement_id':published_advertisement.sudo().advertisement_id.id,
                        'job_id': published_advertisement.sudo().job_id.id,
                        'branch_id': published_advertisement.sudo().directorate_id.id,
                        'center_id': published_advertisement.sudo().branch_id.id,
                        
                        "achievements":kw.get("achievements"),
                        "additional_information":kw.get("additional_information"),
                        "penalty_last_10_year":kw.get("penalty_last_10_year"),
                        "inquiry_going_on":kw.get("inquiry_going_on"),
                        "criminal_case_pending":kw.get("criminal_case_pending"),
                        "relative_ccs":kw.get("relative_ccs"),
                        "relative_ccs_name":kw.get("relative_ccs_name"),
                        "applicable_fee":kw.get("applicable_fee"),
                        "signature":kw.get("signature"),
                        "signature_filename": kw.get('signature_filename'),
                        "fees_amount":kw.get("fees_amount"),
                        "payment_document":kw.get("payment_document"),
                        "payment_filename": kw.get('payment_filename'),
                        'other_doc':kw.get('other_doc'),
                        'other_doc_file_name':kw.get('other_doc_file_name'),
                        'dob_doc':kw.get('dob_doc'),
                        'dob_doc_file_name':kw.get('dob_doc_file_name'),
                        'aadhar_upload': kw.get('aadhar_upload'),
                        'aadhar_upload_filename': kw.get('aadhar_upload_filename'),
                        'pan_upload': kw.get('pan_upload'),
                        'pan_upload_filename': kw.get('pan_upload_filename'),
                        'nationality_upload': kw.get('nationality_upload'),
                        'nationality_upload_filename': kw.get('nationality_upload_filename'),
                    }
                    if published_advertisement.sudo().job_id.employee_type:
                        emp_type = published_advertisement.sudo().job_id.employee_type[0]
                        if emp_type.code =='regular':
                            recruitment_dict['employee_type'] = 'regular'

                        elif emp_type.code =='contract_agency':
                            recruitment_dict['employee_type'] = 'contractual_with_agency'

                        elif emp_type.code =='contract_stpi':
                            recruitment_dict['employee_type'] = 'contractual_with_stpi'

                    if published_advertisement.sudo().job_id.pay_level_id:
                            recruitment_dict['pay_level_id'] = published_advertisement.sudo().job_id.pay_level_id.id
                    
                    if published_advertisement.sudo().job_id.department_id:
                            recruitment_dict['department_id'] = published_advertisement.sudo().job_id.department_id.id

                    # recruitment_model_data = recruitment_model.search([('email_from','=',kw.get('email_from'))],limit=1)
                    # if recruitment_model_data:
                    #     recruitment_model_data.education_ids = False 
                    #     recruitment_model_data.prev_occu_ids = False
                    #     recruitment_model_data.write(recruitment_dict)
                    # else:
                    #     recruitment_dict.update({'email_from': kw.get('email_from')})
                    recruitment_submit_model.create(recruitment_submit_data)
                    recruitment_model.create(recruitment_dict)
                    url = '/recruitment-job-thank-you'
                # if 'email' in request.session:        
                #     request.session.pop('email')
                data.update({'success': True,'url': url})
            else:
                data.update({'success': False, 'url': url})
        except Exception as e:
            data.update({'success': False, 'url': url,'error':str(e)})
        return data

    @http.route(['/attachment/download',], type='http', auth='public')
    def download_attachment(self, attachment_id, document_id):

        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])
        document = request.env['educational_history_temp'].sudo().search([('id','=',int(document_id))])
        print(attachment)
        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/jobs')

        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.b64decode(attachment["datas"]))
            return http.send_file(data, filename=document['file_name'] if document['file_name'] else 'Document', as_attachment=True)
        else:
            return request.not_found()

    @http.route('/get_country_state/', type="json", auth='public', website=True)
    def search_country_state(self, **args):
        print(args)
        states = http.request.env['res.country.state'].sudo().search([('country_id', '=', int(args['country_id']))])
        return [(state.id,state.name) for state in states]

    @http.route('/get_state_city/', type="json", auth='public', website=True)
    def search_state_city(self, **args):
        print(args)
        cities = http.request.env['res.city'].sudo().search([('state_id', '=', int(args['state_id']))])
        return [(city.id,city.name) for city in cities]