import re
import base64
import pytz
from odoo import http, api
from odoo.http import request
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo.addons.kw_utility_tools import kw_helpers


class EpfForm(http.Controller):

    @http.route('/employee-epf-form/', auth='public', method="post", website=True, csrf=False)
    def epf_form(self, **kw):
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        check_record = request.env['kw_epf'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id)])
        if not check_record:
            return http.request.render("kw_epf_form.kw_employee_epf_form")
        else:
            return http.request.redirect('/web')

    @http.route('/employee-epf-form-submit/', auth='public', methods=['POST', ], website=True, csrf=False)
    def epf_data(self, **kwargs):
        kw = kwargs
        if kw:
            check_record = request.env['kw_epf'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id)])
            if not check_record:
                temp_proj_seq = []
                # image = base64.encodestring(kw['upload_photo'].read())
                # hsc_image = base64.encodestring(kw['upload_hsc_photo'].read())
                epf_image = base64.encodestring(kw['upload_epf_photo'].read())

                digit = lambda x: re.search(r'\d+', x).group(0)
                record = {
                    "employee_id": request.env.user.employee_ids.id,
                    "member_name": kw['member_name'] if kw['member_name'] else "",
                    "uan_no": kw['uan_no'] if kw['uan_no'] else "",
                    "upload_epf_doc": epf_image if epf_image else "",
                    "service_period_year": kw['period_of_service_year_0'] if kw['period_of_service_year_0'] else "0",
                    "service_period_month": kw['period_of_service_month_0'] if kw['period_of_service_month_0'] else "0",
                    "epf_file_name": kw['hdnimageepf'] if kw['hdnimageepf'] else "",
                    'nominee_line_ids': [],
                }
                # "service_period": kw['period_of_service'] if kw['period_of_service'] else "",
                for key, value in kw.items():
                    temp_key = str(key)
                    if temp_key[0:9] == 'nominees_':
                        temp_seq = digit(key)
                        if temp_seq not in temp_proj_seq:
                            effec_frm_new_string = ''
                            temp_proj_seq.append(temp_seq)
                            if kw['txtDateOfBirth_' + temp_seq]:
                                effec_frm_string = kw['txtDateOfBirth_' + temp_seq]
                                sp_list = effec_frm_string.split("-")
                                effec_frm_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'

                            temp_data = {
                                'nominee_name': str(kw['nominees_name_' + temp_seq]),
                                'address': str(kw['nominees_address_' + temp_seq]),
                                'relation_with_member': str(kw['nominees_relationship_' + temp_seq]),
                                'minor_nominee': str(kw['nominees_minor_' + temp_seq]),
                            }
                            if effec_frm_new_string:
                                temp_data['dob'] = effec_frm_new_string
                            record['nominee_line_ids'].append([0, 0, temp_data])
                            emp_id = request.env.user.employee_ids
                            if emp_id:
                                if emp_id.date_of_joining:
                                    record['date_of_joining'] = emp_id.date_of_joining
                                record['bank'] = emp_id.bankaccount_id.name if emp_id.bankaccount_id.name else ""
                                record['bank_account'] = emp_id.bank_account if emp_id.bank_account else ""
                                record['grade'] = emp_id.grade.id if emp_id.grade.id else ""
                                record['band'] = emp_id.emp_band.id if emp_id.emp_band.id else ""
                            if emp_id.identification_ids:
                                for rec in emp_id.identification_ids:
                                    if rec.name == '5':
                                        record['aadhaar_no'] = rec.doc_number if rec.doc_number else ""
                                        record['upload_doc'] = rec.uploaded_doc if rec.uploaded_doc else ""
                                        record['file_name'] = rec.doc_file_name if rec.doc_file_name else ""
                                    if rec.name == '1':
                                        record['pan_no'] = rec.doc_number if rec.doc_number else ""
                                        record['upload_pan_doc'] = rec.uploaded_doc if rec.uploaded_doc else ""
                                        record['pan_file_name'] = rec.doc_file_name if rec.doc_file_name else ""
                            for rec in emp_id.educational_details_ids:
                                if rec.course_id.name == 'Intermediate':
                                    record['upload_hsc_doc'] = rec.uploaded_doc if rec.uploaded_doc else ""
                                    record['hsc_file_name'] = rec.doc_file_name if rec.doc_file_name else ""

                # print("record====",record)
                request.env['kw_epf'].sudo().create(record)
                return http.request.render("kw_epf_form.kw_employee_epf_submission_template")
                # return http.request.redirect('/web')
            else:
                return http.request.redirect('/web')
