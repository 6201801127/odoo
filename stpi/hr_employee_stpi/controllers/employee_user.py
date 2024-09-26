from odoo import http
from odoo.http import request
import json
import random
from datetime import datetime, timedelta, date

class CreateUser(http.Controller):


    @http.route(['/create_user'], type='http', auth='public', csrf=False, methods=['POST'])
    def create_hrmis_user(self, name=None, login=None, email=None, password=None, **kwargs):
        user_det = []
        if login and name and email and password:
            user_details_data = request.env['res.users'].sudo().create({
                'name': name,
                'login': login,
                'password': '1234',
                'confirm_password': '1234',
                'email': email,
                'notification_type': 'inbox',
                'sel_groups_1_9_10':1,
                    })
            if user_details_data:
                for rec in user_details_data:
                    vals = {
                        'name': name,
                        'login': login,
                        'email': email,
                        'password': password,
                    }
                    user_det.append(vals)
                loaded_r = json.dumps(dict(response=str(user_det)))
                return loaded_r
            else:
                message = "User not created"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r
        else:
            message = "Please pass login, email and name and password"
            loaded_r = json.dumps(dict(response=str(message)))
            return loaded_r



    @http.route(['/create_users'], type='json', auth='none', csrf=False,  methods=['POST'])
    def create_hrmis_users(self, name=None, login=None, email=None, password=None, **kwargs):
            user_det = []
            if login and name and email and password:
                user_details_data = request.env['res.users'].sudo().create({
                    'name': name,
                    'login': login,
                    'password': '1234',
                    'confirm_password': '1234',
                    'email': email,
                    'notification_type': 'inbox',
                    'sel_groups_1_9_10':1,
                        })
                if user_details_data:
                    for rec in user_details_data:
                        vals = {
                            'id': rec.id,
                            'name': name,
                            'login': login,
                            'email': email,
                            'password': password,
                        }
                        user_det.append(vals)
                    loaded_r = json.dumps(dict(response=str(user_det)))
                    return loaded_r
                else:
                    message = "User not created"
                    loaded_r = json.dumps(dict(response=str(message)))
                    return loaded_r
            else:
                message = "Please pass login, email and name and password"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r



    @http.route(['/update_pass'], type='json', auth='none', csrf=False,  methods=['POST'])
    def update_hrmis_users(self, id=None, login=None, password=None, **kwargs):
            user_det = []
            if (id or login) and password:
                user_details_data = request.env['res.users'].sudo().search(['|',('id', '=', id),('login', '=', login)], limit=1)
                if user_details_data:
                    for rec in user_details_data:
                        rec.write({
                            'password': password,
                            'confirm_password': 'confirm_password',
                        })
                        vals = {
                            'id': rec.id,
                            'login': rec.login,
                            'password': rec.password
                        }
                        user_det.append(vals)
                    loaded_r = json.dumps(dict(response=str(user_det)))
                    return loaded_r
                else:
                    message = "User not found"
                    loaded_r = json.dumps(dict(response=str(message)))
                    return loaded_r
            else:
                message = "Please pass login, email and name and password"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r



    @http.route(['/create_employee'], type='json', auth='none', csrf=False,  methods=['POST'])
    def create_hrmis_employee(self, salutation=None, name=None, department_id=None, job_id=None, parent_id=None, work_email=None, **kwargs):
            user_det = []
            if salutation and name and department_id and job_id and parent_id and work_email:
                user_details_data = request.env['hr.employee'].sudo().create({
                    'salutation': salutation,
                    'name': name,
                    'department_id': department_id,
                    'job_id': job_id,
                    'parent_id': parent_id,
                    'work_email': work_email
                        })
                if user_details_data:
                    for rec in user_details_data:
                        vals = {
                            'id': rec.id,
                            'salutation': salutation,
                            'name': name,
                            'department_id': department_id,
                            'job_id': job_id,
                            'parent_id': parent_id,
                            'work_email': work_email,
                        }
                        user_det.append(vals)
                    loaded_r = json.dumps(dict(response=str(user_det)))
                    return loaded_r
                else:
                    message = "Employee not created"
                    loaded_r = json.dumps(dict(response=str(message)))
                    return loaded_r
            else:
                message = "Please pass salutation, department_id and name and job_id and parent_id and work_email"
                loaded_r = json.dumps(dict(response=str(message)))
                return loaded_r

    @http.route(['/department_list'], type='json', auth='none', csrf=False, methods=['GET'])
    def department_list_hrmis(self, **kwargs):
        letter_details_data = request.env['hr.department'].sudo().search([])
        letter_det = []
        for rec in letter_details_data:
            vals={
                'id': rec.id,
                'name': rec.name,
                'manager_id': rec.manager_id.id,
                'parent_id': rec.parent_id.id,
            }
            letter_det.append(vals)
        data = {"response": letter_det}
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r

    @http.route(['/job_id_list'], type='json', auth='none', csrf=False, methods=['GET'])
    def job_list_hrmis(self, **kwargs):
        letter_details_data = request.env['hr.job'].sudo().search([])
        letter_det = []
        for rec in letter_details_data:
            vals={
                'id': rec.id,
                'name': rec.name
            }
            letter_det.append(vals)
        data = {"response": letter_det}
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r


    @http.route(['/get_salutation'], type='json', auth='none', csrf=False, methods=['GET'])
    def salutation_list_hrmis(self, **kwargs):
        letter_details_data = request.env['res.partner.title'].sudo().search([])
        letter_det = []
        for rec in letter_details_data:
            vals={
                'id': rec.id,
                'name': rec.name
            }
            letter_det.append(vals)
        data = {"response": letter_det}
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r

    @http.route(['/get_user'], type='json', auth='none', csrf=False, methods=['GET'])
    def user_list_hrmis(self, **kwargs):
        letter_details_data = request.env['res.users'].sudo().search([])
        letter_details_data = letter_details_data.filtered(lambda res:res.create_date.date() == date.today() or res.write_date.date() == date.today())
        letter_det = []
        token = random.randint(100000000000000, 999999999999999)
        if letter_details_data:
            for rec in letter_details_data:
                vals={
                    'id': rec.id,
                    'name': rec.name,
                    'login': rec.login,
                    'token': rec.token or 'TOKEN1234567890',
                    'branch':rec.branch_id.id if rec.branch_id else False
                }
                letter_det.append(vals)
        data = {"response": letter_det}
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r


    @http.route(['/get_employee'], type='json', auth='none', csrf=False, methods=['GET'])
    def employee_list_hrmis(self, **kwargs):
        letter_details_data = request.env['hr.employee'].sudo().search([])
        letter_details_data = letter_details_data.filtered(lambda res:res.create_date.date() == date.today() or res.write_date.date() == date.today())
        letter_det = []
        if letter_details_data:
            for rec in letter_details_data:
                vals={
                    'id': rec.id,
                    'salutation': rec.salutation.id,
                    'name': rec.name,
                    'location': rec.work_location,
                    'user_id': rec.user_id.id,
                    'recruitment_file_no': rec.recruitment_file_no,
                    'office_order_no': rec.office_file_no,
                    'recruitment_type': rec.recruitment_type,
                    'parent_id': rec.parent_id.id,
                    'department_id': rec.department_id.id,
                    'job_id': rec.job_id.id,
                    'work_phone': rec.work_phone,
                    'country_id': rec.country_id.id,
                    'identify_id': rec.identify_id,
                    'passport_id': rec.passport_id,
                    'pan_no': rec.pan_no,
                    'religion': rec.religion.id,
                    'gender': rec.gende,
                    'branch':rec.branch_id.id if rec.branch_id else False
                }
                letter_det.append(vals)
        data = {"response": letter_det}
        loaded_r = json.dumps(dict(response=str(letter_det)))
        return loaded_r