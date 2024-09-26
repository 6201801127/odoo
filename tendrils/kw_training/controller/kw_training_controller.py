# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.exceptions import ValidationError

class Kw_Training_Survey(http.Controller):
    
    @http.route(['/training-feedback/<model("kw_training"):training_id>/<model("hr.employee"):employee_id>/<model("survey.survey"):survey_id>', ], type='http', auth='public', website=True)
    def start_feedback(self, training_id, employee_id, survey_id, ** post):
        if training_id.instructor_type == "internal":
            instructor_type = 'internal'
            instructors = training_id.plan_ids[0].internal_user_ids if training_id.plan_ids and training_id.plan_ids[0].internal_user_ids else[]
        else:
            instructor_type = 'external'
            instructors = [training_id.plan_ids[0].instructor_partner] if training_id.plan_ids and training_id.plan_ids[0].instructor_partner else []
        data = {
                'training':training_id,
                'employee': employee_id,
                'instructor_type': instructor_type,
                'instructors': instructors,
                'survey': survey_id,
                }
        return request.render('kw_training.kw_training_feedback_form',data)

    @http.route(['/feedback-submit/<model("kw_training"):training_id>/<model("hr.employee"):employee_id>/<model("survey.survey"):survey_id>', ], type='http', methods=['POST'], auth='public', website=True)
    def submit_feedback(self, training_id, employee_id, survey_id, ** post):
        Feedback = request.env['kw_training_feedback']
        UserInput = request.env['survey.user_input']
        instructor_type = post['instructor_type']
        instructor_id = int(post['instructor_id'])
        if instructor_type == "internal":
            given_status = Feedback.sudo().search(['&','&',('training_id','=',training_id.id),
                                            ('emp_id','=',employee_id.id),('instructor_id','=',instructor_id)])
        else:
            given_status = Feedback.search(['&','&',('training_id', '=', training_id.id),
                                            ('emp_id', '=', employee_id.id), ('ext_instructor', '=', instructor_id)])
        if len(given_status)>0:
            return request.render('kw_training.error', {'message': "Feedback is given"})
        else:
            if instructor_type == "internal":
                new_feedback = Feedback.create({
                    'financial_year': training_id.financial_year.id,
                    'training_id': training_id.id,
                    'instructor_id': int(instructor_id),
                    'emp_id': employee_id.id,
                    'survey_id': survey_id.id,
                })
            else:
                new_feedback = Feedback.create({
                    'financial_year': training_id.financial_year.id,
                    'training_id': training_id.id,
                    'emp_id': employee_id.id,
                    'ext_instructor': instructor_id,
                    'survey_id': survey_id.id,
                })
            vals = {'survey_id': survey_id.id,
                    'partner_id': request.env.user.partner_id.id,
                    'state':'done',
                    }
            v_list = [] 
            for question in survey_id.page_ids[0].question_ids:
                label_id = f"{survey_id.id}_{survey_id.page_ids[0].id}_{question.id}"
                comment = f"{survey_id.id}_{survey_id.page_ids[0].id}_{question.id}_comment"
                v_list.append([0,0,{
                    'question_id': question.id,
                    'answer_type': 'suggestion',
                    'value_suggested': int(post.get(label_id)) if post.get(label_id, False) else False,
                                }])
                v_list.append([0, 0, {
                    'question_id': question.id,
                    'answer_type': 'text',
                    'value_text': post.get(comment, ''),
                                }])
            vals['user_input_line_ids'] = v_list
            user_input = UserInput.create(vals)
            new_feedback.write({'response_id': user_input.id})
        return request.render('kw_training.feedback_submitted')

    @http.route(['/training-feedback-view/<model("kw_training_feedback"):feedback_id>'], type='http', auth='public', website=True)
    def view_given_feedback(self, feedback_id, ** post):
        data = {
            'training': feedback_id.training_id,
            'employee': feedback_id.emp_id,
            'instructors': feedback_id.instructor_id if feedback_id.instructor_id else feedback_id.ext_instructor,
            'survey': feedback_id.survey_id,
            'response': feedback_id.response_id,
            }
        return request.render('kw_training.kw_feedback_result_view_form', data)
    
    @http.route('/download_training_plan_update_doc/<int:id>', type='http', auth="public")
    def get_download_training_doc(self, id=None, **kwargs):
        training_data = request.env['kw_training_plan'].sudo().browse(id)
        training_plan_doc = training_data.plan_doc if training_data.plan_doc else False
        if training_plan_doc:
            uploaded_doc_b64_string = base64.b64decode(training_plan_doc)
            filename = training_data.plan_doc_name  
            if filename.endswith('.xlsx'):
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.endswith('.xls'):
                content_type = 'application/vnd.ms-excel'
            elif filename.endswith('.ods'):
                content_type = 'application/vnd.oasis.opendocument.spreadsheet'
            else:
                return request.make_response(
                    "Unsupported file format",
                    [('Content-Type', 'text/plain')]
                )

            return request.make_response(
                uploaded_doc_b64_string,
                headers=[('Content-Type', content_type),
                        ('Content-Disposition', f'attachment; filename="{filename}"')]
            )
        return request.redirect('/')

    @http.route('/get-generated-certificate-details/<int:id>/<int:rec_id>',  methods=['GET'], csrf=False, type='http', auth="public", website=True)
    def download_generate_certificate(self, id=None,rec_id=None, **kwargs):
        if not id or not rec_id:

            raise ValidationError("Invalid ID provided.")
            
        certificate = request.env['kw_training_certificate_generate'].sudo().search([('id','=',id),('trainee_id','=',rec_id)])
        if not certificate:
            raise ValidationError("Certificate not found for this ID.")

        pdf_content, content_type = request.env.ref('kw_training.download_training_certification').sudo().render_qweb_pdf([certificate.id])
        

        # report_template = request.env.ref('kw_training.download_training_certification').sudo().render_qweb_pdf([certificate.id])

        response = request.make_response(
            pdf_content,
            headers=[('Content-Type', 'application/pdf'),
                     ('Content-Disposition', f'attachment; filename="{certificate.trainee_id.name}.pdf"')]
        )
        
        return response

    # @http.route('/download-training-certificate/<string:token>', methods=['GET'], csrf=False, type='http', auth="public", website=True)
    # def download_training_certificate(self, token, download=False, **args):
    #     accesstoken = request.env['kw_training_certificate_generate'].sudo().search([('token', '=', token)])
    #     if not accesstoken:
    #         return Forbidden()
    #     else:
    #         employee_id = accesstoken.sudo().trainee_id

    #         if not download:
    #             return http.request.render('kw_training.kw_training_certificate_download_button_redirect',
	# 										{'employee': employee_id, 'token': token}, )
    #         else:
    #             report_obj = request.env['kw_training_certificate_generate'].sudo().search([('employee_id','=',employee_id.id)])
    #             report_template_id = request.env.ref('kw_training.download_training_certification').sudo().render_qweb_pdf(report_obj.id)
    #             data_record = base64.b64encode(report_template_id[0])
    #             # print("data_recorddata_recorddata_record", data_record,report_obj)
    #             ir_values = {
    #                 'name': "Training Certificate",
    #                 'type': 'binary',
    #                 'datas': data_record,
    #                 'datas_fname': f"{report_obj.employee_id.name.replace(' ', '-')}-training-certificate.pdf",
    #                 'mimetype': 'application/x-pdf',
    #             }
    #             pdf_http_headers = [('Content-Type', 'application/pdf'),
	# 								('Content-Disposition', f"attachment; filename={report_obj.employee_id.name.replace(' ', '-')}-training-certificate.pdf"),
	# 								('Content-Length', len(data_record))]
    #             return request.make_response(report_template_id[0], headers=pdf_http_headers)



  