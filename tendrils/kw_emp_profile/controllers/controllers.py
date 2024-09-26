import requests, os, zipfile, base64, shutil, json
from zipfile import ZipFile
import werkzeug
from werkzeug.utils import redirect
from io import BytesIO
from mimetypes import guess_extension
from odoo import http
from odoo.http import request
from odoo.tools import pdf
from odoo.addons.web.controllers import main
from odoo.tools.mimetypes import guess_mimetype
from zipfile import ZipFile
from odoo.addons.web.controllers.main import content_disposition
from odoo.addons.restful.common import valid_response, invalid_response
from odoo.exceptions import AccessError,ValidationError
from odoo import models, fields


class kw_employee_update_data(http.Controller):

    @http.route('/get-pan-update-of-employee', auth='public', type='http', website=True, csrf=False)
    def get_checklist_report(self, **args):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            pan_log = request.env['kw_employee_update_pan_log'].search([('employee_id', '=', employee_id.id)])
            if pan_log.exists():
                skips_check = pan_log.skips_check
            else:
                skips_check = 0
            get_pan_no = request.env['kwemp_identity_docs'].sudo().search(
                [('emp_id', '=', employee_id.id), ('name', 'in', ['1'])])

            return http.request.render('kw_emp_profile.employee_pan_update_view', {'emp_name': employee_id.name,
                                                                                   'emp_pan': get_pan_no.doc_number.upper() if get_pan_no else 'NA',
                                                                                   'skips_check': skips_check})
        else:
            http.request.session['skip_pan'] = True
        return http.request.redirect('/web')

    @http.route('/employee-pan-submit', auth='public', website=True, csrf=False)
    def emp_pan_submit(self, **kw):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            # profile_id = request.env['kw_emp_profile'].sudo().search([('emp_id', '=', employee_id.id)])
            # get_pan_no = request.env['kwemp_identity_docs'].sudo().search(
            #     [('emp_id', '=', employee_id.id), ('name', 'in', ['1'])])
            pan_log = request.env['kw_employee_update_pan_log'].sudo().search([('employee_id', '=', employee_id.id)])
            if pan_log.exists():
                pan_log.write({'is_correct': True, 'is_submitted': True})
            else:
                request.env['kw_employee_update_pan_log'].sudo().create({'employee_id': employee_id.id,
                                                                         'is_correct': True,
                                                                         'is_submitted': True
                                                                         })
            # profile_id.write({'emp_pan_check_update': True})
        http.request.session['skip_pan'] = True
        return request.redirect('/web')

    @http.route('/employee-pan-update', auth='public', website=False, csrf=False)
    def update_data(self, **kwargs):
        emp_rec = request.env.user.employee_ids
        # view_manpower_requisition_form_treeprint("update_data-----------------",kwargs)
        if emp_rec:
            employee_id = emp_rec[0]
            # fetch pan details from employee identity details
            get_pan_no_emp = request.env['kwemp_identity_docs'].sudo().search(
                [('emp_id', '=', employee_id.id), ('name', '=', '1')])

            # fetch pan details from profile identity details
            profile_id = request.env['kw_emp_profile'].sudo().search([('emp_id', '=', employee_id.id)])
            get_pan_no_profile = request.env['kw_emp_profile_identity_docs'].sudo().search(
                [('emp_id', '=', profile_id.id), ('name', '=', '1')])

            file = kwargs['pandoc']
            uploaded_doc = base64.encodestring(kwargs['pandoc'].read())
            doc_number = kwargs['txtPAN']

            if get_pan_no_emp.exists():
                get_pan_no_emp.write({
                    'doc_number': doc_number,
                    'uploaded_doc': uploaded_doc,
                    'doc_file_name': file.filename,
                })
            else:
                request.env['kwemp_identity_docs'].sudo().create({
                    'emp_id': employee_id.id,
                    'name': '1',
                    'doc_number': doc_number,
                    'uploaded_doc': uploaded_doc,
                    'doc_file_name': file.filename,
                })
            if get_pan_no_profile.exists():
                get_pan_no_profile.write({
                    'doc_number': doc_number,
                    'uploaded_doc': uploaded_doc,
                    'doc_file_name': file.filename,
                })
            else:
                request.env['kw_emp_profile_identity_docs'].sudo().create({
                    'name': '1',
                    'emp_id': profile_id.id,
                    'doc_number': doc_number,
                    'uploaded_doc': uploaded_doc,
                    'doc_file_name': file.filename,
                })
            pan_log = request.env['kw_employee_update_pan_log'].sudo().search([('employee_id', '=', employee_id.id)])
            if pan_log.exists():
                pan_log.write({'is_submitted': True})
            else:
                request.env['kw_employee_update_pan_log'].sudo().create({'employee_id': employee_id.id,
                                                                         'is_submitted': True
                                                                         })

            # profile_id.write({'emp_pan_check_update': True})
            return werkzeug.utils.redirect('/web')
        else:
            return request.redirect('/web', )

    @http.route('/employee-pan-skip', auth='user', website=True, csrf=False)
    def skip_pan_skip(self, **kw):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            skip_log = http.request.env['kw_employee_update_pan_log'].search([('employee_id', '=', employee_id.id)],
                                                                             limit=1)

            if not skip_log:
                http.request.env['kw_employee_update_pan_log'].create(
                    {'employee_id': emp_rec.id, 'skips_check': 1})

            elif skip_log.skips_check < 3:
                skip_log.write({'skips_check': skip_log.skips_check + 1})

            http.request.session['skip_pan'] = True
            return http.request.redirect('/web')
        # else:
        #     return http.request.render('kw_emp_profile.employee_pan_update_view', {'skips_check':skip_log.skips_check})

    @http.route('/download_emp_all_update_doc/<int:id>/<int:rec_id>', type='http', auth="user")
    def get_download_zip(self, id=None, rec_id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        emp_educational_rec = request.env['kw_emp_profile_qualification'].sudo().search([
            ('emp_id.emp_id', '=', empObj.id), ('id', '=', rec_id)])
        if emp_educational_rec and emp_educational_rec.uploaded_doc:
            file_data = base64.b64decode(emp_educational_rec.uploaded_doc)
            return request.make_response(
                file_data,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.redirect('/')
                
    @http.route('/download_emp_identity_update_doc/<int:id>/<int:rec_id>', type='http', auth="user")
    def get_download_identity_doc(self, id=None,rec_id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id,rec_id)
        byte = BytesIO()
        emp_name = empObj.name.replace(" ", "_")
        
        emp_identity_rec = request.env['kw_emp_profile_identity_docs'].sudo().search([
            ('emp_id.emp_id', '=',empObj.id), ('id', '=', rec_id)])
        if emp_identity_rec and emp_identity_rec.uploaded_doc:
            file_data = base64.b64decode(emp_identity_rec.uploaded_doc)
            return request.make_response(
                file_data,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.redirect('/')
           
    @http.route('/download_emp_work_update_doc/<int:id>/<int:rec_id>', type='http', auth="user")
    def get_download_work_doc(self, id=None,rec_id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id)
        emp_work_rec = request.env['kw_emp_profile_work_experience'].sudo().search([
            ('emp_id.emp_id', '=',empObj.id),('id', '=', rec_id)])
        if emp_work_rec and emp_work_rec.uploaded_doc:
            file_data = base64.b64decode(emp_work_rec.uploaded_doc)
            return request.make_response(
                file_data,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.redirect('/')

    @http.route('/download_emp_cv_update_doc/<int:id>', type='http', auth="user")
    def get_download_cv_doc(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id)
        applicant = empObj.onboarding_id.applicant_id.document_ids[0].content_file if empObj.onboarding_id.applicant_id.document_ids else False
        if applicant:
            uploaded_doc_b64_string = base64.b64decode(applicant)
            return request.make_response(
                uploaded_doc_b64_string,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.redirect('/')
        
    @http.route('/download_emp_medical_update_doc/<int:id>', type='http', auth="user")
    def get_download_medical_doc(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        applicant = empObj.onboarding_id.medical_certificate
        if applicant:
            uploaded_doc_b64_string = base64.b64decode(applicant)
            if uploaded_doc_b64_string:
                return request.make_response(
                    uploaded_doc_b64_string,
                    headers=[('Content-Type', 'application/pdf'),
                            ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
                )
            else:
                return request.not_found("Content Not Found for your Medical Certificate")
        return request.not_found("Content Not Found for your Medical Certificate")

    @http.route('/download_emp_offer_update_doc/<int:id>', type='http', auth="user")
    def get_download_offer_doc(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id)
        offer_data = http.request.env['hr.applicant.offer'].sudo().search(
            [('applicant_id', '=', empObj.onboarding_id.applicant_id.id)], limit=1)
        if offer_data:
            if offer_data.offer_type == 'Intern':
                report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent').sudo().render_qweb_pdf(offer_data.id)
            elif offer_data.offer_type == 'Lateral':
                report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_lateral').sudo().render_qweb_pdf(offer_data.id)
            elif offer_data.offer_type == 'RET':
                report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_ret').sudo().render_qweb_pdf(offer_data.id)

            return request.make_response(
                report_template_id,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.not_found("Content Not Found for your Offer Letter")

    @http.route('/download_emp_probatinary_update_doc/<int:id>', type='http', auth="user")
    def get_download_probation_doc(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id)
        emp_name = empObj.name.replace(" ", "_")
        get_data = request.env['kw_feedback_details'].sudo().search(
            ['&', ('assessee_id', '=', empObj.id), ('feedback_status', '=', '6')], limit=1)

        if get_data:
            report_template_id = request.env.ref(
                'kw_assessment_feedback.probation_completion_pdf_report_id').render_qweb_pdf(get_data.id)
            return request.make_response(
                report_template_id,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{emp_name}.pdf"')]
            )
        return redirect('/')

    @http.route('/download_emp_exit_update_doc/<int:id>', type='http', auth="user")
    def get_download_exit_doc(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        # print("empObj==============================",empObj,id)
        exit_data = request.env['kw_resignation_experience_letter'].sudo().search(
            [('employee_id', '=', empObj.id)], limit=1)
        if exit_data:
            report_template_id = request.env.ref('kw_eos.report_letter_experience_letter').render_qweb_pdf(exit_data.id)
            return request.make_response(
                report_template_id,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{empObj.name}.pdf"')]
            )
        return request.redirect('/')


    @http.route('/get-posh-certificate-employee/<int:id>', type='http', auth="user")
    def get_checklist_report(self,id=None,  **args):
        empObj = request.env['hr.employee'].sudo().browse(id)
        employee_data = request.env['kw_employee_posh_induction_details'].search([('emp_id', '=', empObj.id),('induction_complete','=',True)])
        if  employee_data:
            report_template_id = request.env.ref('kw_onboarding_induction_feedback.download_posh_certification').sudo().render_qweb_pdf(employee_data.id)
        else:
            raise ValidationError("Certificate is not generated.")
        data_record = base64.b64encode(report_template_id[0])
        pdf_http_headers = [('Content-Type', 'application/pdf'),
                            ('Content-Disposition', f"attachment; filename={empObj.name.replace(' ', '-')}-POSH-Certificate.pdf"),
                            ('Content-Length', len(data_record))]
        return request.make_response(report_template_id[0], headers=pdf_http_headers)
        



