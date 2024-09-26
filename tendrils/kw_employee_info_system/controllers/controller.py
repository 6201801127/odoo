# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import http
import math
import json
import base64
from odoo.http import request
from odoo.exceptions import ValidationError


class EmployeeWishesData(http.Controller):
    @http.route("/emp_wishes/data", methods=['POST'], auth='public', type='json', cors='*')
    def check_emp_data(self, **args):
        birth_anniversary_yearofservice_query = f'''
            SELECT id FROM hr_employee 
            WHERE active = true and ((
                    date_part('day', birthday) in (date_part('day', CURRENT_DATE))
                                                
                    
                    AND date_part('month', birthday) = date_part('month', CURRENT_DATE)
                    
                    )
                OR

                    (
                    date_part('day', date_of_joining) in (date_part('day', CURRENT_DATE))
                                                    
                        
                    AND date_part('month', date_of_joining) = date_part('month', CURRENT_DATE)

                    ))
                        
        '''
        request.env.cr.execute(birth_anniversary_yearofservice_query)
        employee_ids = [id_tuple[0] for id_tuple in request.env.cr.fetchall()]
        current_date = date.today()

        birth_anniversary_year_of_service_data = request.env['hr.employee'].sudo().browse(employee_ids)

        birthday_data = birth_anniversary_year_of_service_data.filtered(
            lambda r: r.birthday and r.birthday.day in [current_date.day] and r.birthday.month == current_date.month)

        # anniversary_data = birth_anniversary_year_of_service_data.filtered(lambda r:r.wedding_anniversary and r.wedding_anniversary.day in [current_date.day] and r.wedding_anniversary.month == current_date.month)

        year_of_service_data = birth_anniversary_year_of_service_data.filtered(lambda r: r.date_of_joining and r.date_of_joining.day in [current_date.day] and r.date_of_joining.month == current_date.month)

        data_list = []
        data_list += [{"user_id": birth_data.id,
                       "user_name": birth_data.name,
                       "dept": birth_data.department_id.name,
                       "designation": birth_data.job_id.name,
                       "photo": f"/web/image?model=hr.employee&id={birth_data.id}&field=image",
                       "type": "1",
                       "date": birth_data.birthday.strftime('%d %b %Y'),
                       "gender": birth_data.gender
                       } for birth_data in birthday_data
                      ]

        data_list += [{"user_id": year_of_service.id,
                       "user_name": year_of_service.name,
                       "dept": year_of_service.department_id.name,
                       "designation": year_of_service.job_id.name,
                       "photo": f"/web/image?model=hr.employee&id={year_of_service.id}&field=image",
                       "type": "2",
                       "date": year_of_service.date_of_joining.strftime('%d %b %Y'),
                       "total_year": math.floor((current_date - year_of_service.date_of_joining).days / 365),
                       "gender": year_of_service.gender
                       } for year_of_service in year_of_service_data
                      ]

        # data_list += [{ "user_id":anniversary.id ,
        #                 "user_name":anniversary.name ,
        #                 "dept": anniversary.department_id.name,
        #                 "designation":anniversary.job_id.name,
        #                 "photo":f"/web/image?model=hr.employee&id={anniversary.id}&field=image",
        #                 "type": "4",
        #                 "date":anniversary.wedding_anniversary.strftime('%d %b %Y'),
        #                 "gender":anniversary.gender   
        #                 }for anniversary in anniversary_data 
        #                 ]

        return data_list

    @http.route("/ex-employee-information", methods=['POST'], auth='none', type='json', csrf=False, cors='*', website=False)
    def ex_emp_data(self, from_date='', to_date='', employee_id=''):
        resource_json_data = {
            "FromDate": from_date,
            "ToDate": to_date,
        }
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else False
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else False
        if (not from_date_obj or not to_date_obj) and not employee_id:
            return json.dumps([{'status': 401, 'message': 'Please enter correct from_date and to_date or employee id'}])
        if from_date_obj > to_date_obj:
            return json.dumps([{'status': 401, 'message': 'Please from_date less than to_date'}])

        data = []
        if from_date_obj and to_date_obj and not employee_id:
            emp_data = request.env['hr.employee'].sudo().search([('active', '=', False),
                                                                 ('last_working_day', '>=', from_date),
                                                                 ('last_working_day', '<=', to_date),
                                                                 ('date_of_joining', '!=', False)])
        elif employee_id:
            emp_data = request.env['hr.employee'].sudo().search([('active', '=', False), ('id', '=', employee_id),('date_of_joining', '!=', False)])
        # print("emp_data >>> ", emp_data)

        for emp_rec in emp_data:
            employee_id = emp_rec.id
            attachment_data = request.env['ir.attachment'].search(
                [('res_id', '=', employee_id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
            # emp_rec.image = attachment_data.id
            if attachment_data:
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                final_url = '%s/web/image/%s' % (base_url, attachment_data.id)
                # record.image_url = final_url

            profile_education_rec = request.env['kwemp_educational_qualification'].sudo().search(
                [('emp_id', '=', employee_id)])
            experience_letter = request.env['kw_resignation_experience_letter'].sudo().search(
                [('employee_id', '=', employee_id)])
            # resignation = request.env['kw_resignation'].sudo().search([('applicant_id', '=', employee_id)],order='id desc', limit=1)
            clearance = request.env['hr.employee.clearance'].sudo().search([('employee_id', '=', employee_id)], order='id desc', limit=1)

            temp_emp_dict = {
                "experience_letter_no": experience_letter.ref_code if experience_letter else '',
                "experience_letter_date": experience_letter.date.strftime('%d-%b-%Y') if experience_letter else '',
                "employee_id": emp_rec.id,
                "employee_code": emp_rec.emp_code if emp_rec.emp_code else "",
                "employee_name": emp_rec.name if emp_rec.name else '',
                "date_of_joining": emp_rec.date_of_joining.strftime('%d-%b-%Y') if emp_rec.date_of_joining.strftime('%d-%b-%Y') else "",
                "date_of_exit_at_CSM": emp_rec.last_working_day.strftime('%d-%b-%Y') if emp_rec.last_working_day.strftime('%d-%b-%Y') else "",
                "reporting_manager_name": emp_rec.parent_id.name if emp_rec.parent_id.name else '',
                "reporting_manager_designation": emp_rec.parent_id.job_id.name if emp_rec.parent_id.job_id.name else '',
                "reason_for_leaving": emp_rec.resignation_reason.name if emp_rec.resignation_reason.name else '',
                "hire_eligiblity": clearance.reason_for_re_hire if clearance.reason_for_re_hire else "NA",
                "final_settlement": clearance.reason_exit_settlement if clearance.reason_exit_settlement else "NA",
                "job_feedback": clearance.feedback if clearance.feedback else "NA",
                "designation": emp_rec.job_id.name if emp_rec.job_id.name else "",
                "mobile_no.": emp_rec.mobile_phone if emp_rec.mobile_phone else "",
                "email_id": emp_rec.personal_email if emp_rec.personal_email else "",
                "employee_image": final_url if final_url else "",
                "whatsApp_no.": emp_rec.whatsapp_no if emp_rec.whatsapp_no else "",
                "date_of_birth": emp_rec.birthday.strftime('%d-%b-%Y') if emp_rec.birthday else "",
                "department": emp_rec.department_id.name if emp_rec.department_id.name else "",
                "qualification": {rec.course_id.name for rec in profile_education_rec} if {rec.course_id.name for rec in
                                                                                           profile_education_rec} else '',
                "permanent_address": {
                    "street": emp_rec.permanent_addr_street if emp_rec.permanent_addr_street else '',
                    "street2": emp_rec.permanent_addr_street2 if emp_rec.permanent_addr_street2 else '',
                    "city": emp_rec.permanent_addr_city if emp_rec.permanent_addr_city else '',
                    "state": emp_rec.permanent_addr_state_id.name if emp_rec.permanent_addr_state_id.name else '',
                },
                "marital_status": emp_rec.marital_sts.name if emp_rec.marital_sts.name else "",
                "marriage_date": emp_rec.wedding_anniversary if emp_rec.wedding_anniversary else "",
                "uan": emp_rec.uan_id if emp_rec.uan_id else "",
            }
            data.append(temp_emp_dict)
        return data
