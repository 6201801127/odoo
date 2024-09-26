# -*- coding: utf-8 -*-

import base64
import datetime
from mimetypes import guess_extension

import pytz
from odoo import http
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.web.controllers.main import content_disposition
import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import math, random, string,secrets


class OffboardingController(http.Controller):

    @http.route('/employee-experience-letter/<int:emp_id>', type="http", cors='*', auth="none", methods=["GET"], csrf=False)
    def download_experience_letter(self, emp_id=None, **kwargs):
        try:
            emp_rec = request.env['hr.employee'].sudo().search([('id', '=', emp_id), ('active', '=', False)])
            if not emp_rec.exists():
                return request.not_found()

            exit_data = request.env['kw_resignation_experience_letter'].sudo().search(
                [('employee_id', '=', emp_rec.id)], limit=1, order="id desc")
            if not exit_data.exists():
                return request.not_found()

            report_template_id = request.env.ref('kw_eos.report_letter_experience_letter').sudo().render_qweb_pdf(exit_data.id)
            extension = guess_extension(guess_mimetype(report_template_id[0]))

            emp_name = emp_rec.name.replace(" ", "_")
            filename = f"{emp_name}_{str(emp_rec.emp_code)}_experience_letter{extension}"

            return request.make_response(report_template_id, [('Content-Type', 'application/pdf'),
                                                              ('Content-Disposition', content_disposition(filename))])

        except Exception as e:
            return request.not_found(e)

    @http.route('/ex-employee-experience-letter', type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def api_ex_employee_payslip(self, emp_id=None):
        try:
            emp_rec = request.env['hr.employee'].sudo().search([('id', '=', emp_id), ('active', '=', False)])
            if not emp_rec.exists():
                return {'code': 500, 'message': 'Employee details not found.'}

            exit_data = request.env['kw_resignation_experience_letter'].sudo().search(
                [('employee_id', '=', emp_rec.id)], limit=1, order="id desc")
            if not exit_data.exists():
                return {'code': 500, 'message': 'Employee\'s experience letter not found.'}

            data_dict = {'code': 200, 'message': 'Success'}

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data_dict['url'] = f"{base_url}/employee-experience-letter/{emp_id}"
            return data_dict

        except Exception as e:
            msg_dic = {
                "code": 400,
                "message": str(e)
            }

    @http.route('/download-employee-experience-letter/<string:token>', methods=['GET'], csrf=False, type='http', auth="public", website=True)
    def download_employee_experience_letter(self, token):
        accesstoken = request.env['kw_resignation_experience_letter'].sudo().search([('token', '=', token)])
        # print("accesstoken >>>>>>>> ", accesstoken)
        if not accesstoken:
            return Forbidden()
        else:
            # generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
            generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))
            # if generate_otp:
            #     current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
            #     date_time = current_date_time + datetime.timedelta(0, 600)
            #     date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
            #     res = accesstoken.sudo().write({'otp': generate_otp, 'expire_time': date_time})
            #
            #     employee_id = accesstoken.sudo().employee_id
            #     template_obj = request.env.ref('kw_eos.experience_letter_downloar_verify_otp_mail_template')
            #     mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
			# 		name=employee_id.name,
			# 		mailto=employee_id.personal_email,
			# 		otp=generate_otp,
			# 	).send_mail(employee_id.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=True)
        return http.request.redirect(f'/download-experience-letter/{token}', )  
    
    @http.route('/download-experience-letter/<string:token>', methods=['GET'], csrf=False, type='http', auth="public", website=True)
    def accept_download_experience_letter(self, token, download=False, **args):
        accesstoken = request.env['kw_resignation_experience_letter'].sudo().search([('token', '=', token)])
        if not accesstoken:
            return Forbidden()
        else:
            employee_id = accesstoken.sudo().employee_id

            if not download:
                return http.request.render('kw_eos.kw_eos_experience_download_button_redirect',
											{'employee': employee_id, 'token': token}, )
            else:
                report_obj = request.env['kw_resignation_experience_letter'].sudo().search([('employee_id','=',employee_id.id)])
                report_template_id = request.env.ref('kw_eos.report_letter_experience_letter').sudo().render_qweb_pdf(report_obj.id)
                data_record = base64.b64encode(report_template_id[0])
                # print("data_recorddata_recorddata_record", data_record,report_obj)
                ir_values = {
                    'name': "Experience Letter",
                    'type': 'binary',
                    'datas': data_record,
                    'datas_fname': f"{report_obj.employee_id.name.replace(' ', '-')}-Experience-Letter.pdf",
                    'mimetype': 'application/x-pdf',
                }
                pdf_http_headers = [('Content-Type', 'application/pdf'),
									('Content-Disposition', f"attachment; filename={report_obj.employee_id.name.replace(' ', '-')}-Experience-Letter.pdf"),
									('Content-Length', len(data_record))]
                return request.make_response(report_template_id[0], headers=pdf_http_headers)

    @http.route('/eos/verify_experience_letter_download', type="json", auth="public", website=True, methods=["POST"], csrf=False, cors='*')
    def eos_otp_verified(self, token, otp):
        if token and otp:
            accesstoken = request.env['kw_resignation_experience_letter'].sudo().search([('token', '=', token)])

            employee_id = accesstoken.sudo().employee_id
            current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
            date_time = datetime.datetime.strptime(current_date_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

            if accesstoken:
                # print(f"mrftoken.expire_time >> {accesstoken.expire_time} >> {date_time} >> {accesstoken.otp} >> {otp}")
                if accesstoken.otp == otp:
                    if accesstoken.expire_time < date_time:
                        return 'expired'
                    else:
                        return 'success'
                else:
                    return 'invalid'
        else:
            return 'required'

    @http.route('/eos/send_otp/experience_letter', type="json", auth="public", website=True, methods=["POST"], csrf=False, cors='*')
    def eos_send_otp_download(self, name, email, token):
        current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
        date_time = current_date_time + datetime.timedelta(0, 600)
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        # generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
        generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))

        if generate_otp:
            accesstoken = request.env['kw_resignation_experience_letter'].sudo().search([('token', '=', token)])

            employee_id = accesstoken.sudo().employee_id
            accesstoken.sudo().write({'employee_id': employee_id.id, 'otp': generate_otp, 'expire_time': date_time})

            template_obj = request.env.ref('kw_eos.experience_letter_downloar_verify_otp_mail_template')
            mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
                name=name,
                mailto=email,
                otp=generate_otp,
            ).send_mail(employee_id.id,
                        notif_layout='kwantify_theme.csm_mail_notification_light',
                        force_send=True)
            request.env.user.notify_success("Mail sent successfully.")
            return {'success': 'yes'}
        

