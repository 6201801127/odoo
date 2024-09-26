# -*- coding: utf-8 -*-
import base64
import requests
import urllib.request
import json
import re
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api

PHONE_REX = "[^0-9+\/\-\s]"


class ApplicantSync(models.Model):
    _inherit = "hr.applicant"

    career_id = fields.Integer("Career Applicant ID")
    campus_id = fields.Integer("Campus Applicant ID")

    @api.model
    def sync_campus_applicant(self):
        # print("method called for campus applicant...........................")
        log = self.env["kw_recruitment_career_sync_log"].sudo()
        data_dict = {}
        # try:
        sync_url = self.env["ir.config_parameter"].sudo().get_param("kw_recruitment_career_applicant_sync_url")
        console_api_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_api_url")
        # url = sync_url or "http://192.168.103.229/CSM/api/consoleServices"
        url = sync_url or console_api_url
        data = json.dumps({"method": "campus_sync", "data": []})
        response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
        content = response_obj.content
        resp = json.loads(content.decode("utf-8"))

        location_id = self.env['kw_recruitment_location'].search([('code', '=', 'bhubaneswar')], limit=1)
        source_id = self.env.ref('kw_recruitment.source_006')
        other_qualification_id = self.env.ref('kw_recruitment.kw_qualificatio_data1').id
        initial_stage_id = self.env.ref('hr_recruitment.stage_job1').id

        """sync scheduler time update"""
        sync_scheduler = self.env.ref('kw_career_sync.kw_career_sync_campus_applicant_scheduler')
        if not len(resp['result']):
            sync_scheduler.sudo().write({'interval_number': 6, 'interval_type': 'hours'})
        else:
            sync_scheduler.sudo().write({'interval_number': 5, 'interval_type': 'minutes'})

        for payload in resp['result']:
            insert_log = log.create({"name": "Campus Applicant Sync", "payload": payload, 'status': 'Initiate'})
            data = {}
            existing_applicant = self.env['hr.applicant'].search([('campus_id', '=', payload['id'])], limit=1)
            if existing_applicant:

                insert_log.write({'status': 'Already Created'})
                data_dict[payload['id']] = existing_applicant.id
                '''
                {
                    "id":3,"job_id":3,"name":"Akshat Patra","email":"akshat@email.com","phone":"9876546598",
                    "qualification_id":2,"location":"Bhubaneswar","institute":141,"roll_no":"1701210208",
                    "cv_name":"5fa282bb8bb4c1604485819CV.pdf","cv_content":"JVBERi0xLj"
                }
                '''
            else:

                # try:
                data['campus_id'] = payload['id']
                data['stage_id'] = initial_stage_id
                data['job_position'] = payload['job_id']
                data['partner_name'] = payload['name']
                data['email_from'] = payload['email']
                data['partner_mobile'] = re.sub(PHONE_REX, "", payload['phone'])
                data['qualification'] = payload['qualification_id']
                data['qualification_ids'] = [[6, 0, [payload['qualification_id']]]]

                if payload['qualification_id'] == other_qualification_id:
                    data['other_qualification'] = 'Others'

                data['current_location'] = payload['location']
                data['job_location_id'] = location_id and location_id.id or False
                data['source_id'] = source_id.id
                data['code_ref'] = source_id.code
                data['institute_id'] = payload['institute']
                data['registration_number'] = payload['roll_no']

                if 'cv_name' and 'cv_content' in payload:
                    file_name = payload['cv_name']
                    doc_file = payload['cv_content']
                    if 'document_ids' in self.env['hr.applicant'].sudo()._fields:
                        data['document_ids'] = [[0, 0, {'content_file': doc_file, 'file_name': file_name}]]
                    # else:
                    #     data['attachment_ids'] = [[0, 0,
                    #                                {'name': file_name,
                    #                                 'datas_fname': file_name,
                    #                                 'datas': doc_file,
                    #                                 'res_name': payload['name'],
                    #                                 'res_model': 'hr.applicant',
                    #                                 'res_model_name': 'Applicant'
                    #                                 }
                    #                                ]]

                applicant = self.env['hr.applicant'].create(data)
                if applicant:
                    data_dict[payload['id']] = applicant.id
                    insert_log.write({'status': 'Success'})
                else:
                    insert_log.write({'status': 'Failed'})

        if len(data_dict):
            data = json.dumps({"method": "campus_update", "data": data_dict})

            # try:
            response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
            content = response_obj.content
            resp = json.loads(content.decode("utf-8"))

            # except Exception as e:
            # print("Acknowledge failure reason",e)

    @api.model
    def sync_career_applicant(self):
        # print("method called for sync applicant...........................")
        log = self.env["kw_recruitment_career_sync_log"].sudo()
        data_dict = {}
        # try:
        sync_url = self.env["ir.config_parameter"].sudo().get_param("kw_recruitment_career_applicant_sync_url")
        console_api_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_api_url")
        # url = sync_url or "http://192.168.103.229/CSM/api/consoleServices"
        url = sync_url or console_api_url
        data = json.dumps({"method": "walkin_sync", "data": []})
        response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
        content = response_obj.content
        resp = json.loads(content.decode("utf-8"))

        location_id = self.env['kw_recruitment_location'].search([('code', '=', 'bhubaneswar')], limit=1)
        source_id = self.env.ref('kw_recruitment.source_009')
        other_qualification_id = self.env.ref('kw_recruitment.kw_qualificatio_data1').id
        initial_stage_id = self.env.ref('hr_recruitment.stage_job1').id

        """sync scheduler time update"""
        sync_scheduler = self.env.ref('kw_career_sync.kw_career_sync_applicant_scheduler')
        if not len(resp['result']):
            sync_scheduler.sudo().write({'interval_number': 6, 'interval_type': 'hours'})
        else:
            sync_scheduler.sudo().write({'interval_number': 5, 'interval_type': 'minutes'})

        for payload in resp['result']:
            insert_log = log.create({"name": "Applicant Sync", "payload": payload, 'status': 'Initiate'})
            data = {}
            existing_applicant = self.env['hr.applicant'].search([('career_id', '=', payload['id'])], limit=1)
            if existing_applicant:
                insert_log.write({'status': 'Already Created'})
                data_dict[payload['id']] = existing_applicant.id
            else:

                # try:
                data['career_id'] = payload['id']
                data['stage_id'] = initial_stage_id
                data['job_position'] = payload['job_id']
                data['partner_name'] = payload['name']
                data['email_from'] = payload['email']
                data['partner_mobile'] = re.sub(PHONE_REX, "", payload['phone'])
                data['qualification'] = payload['qualification_id']
                data['qualification_ids'] = [[6, 0, [payload['qualification_id']]]]

                if payload['qualification_id'] == other_qualification_id:
                    data['other_qualification'] = 'Others'

                data['current_location'] = payload['location']
                data['current_ctc'] = int(payload['current_salary'])
                data['salary_expected'] = int(payload['expecetd_salary'])
                data['notice_period'] = int(payload['notice_period']) or int(payload['o_notice_period'])
                data['info_source_id'] = payload['source_info']
                data['walkin_employee_reference'] = payload['emp_name']
                data['other_info'] = payload['other_source']
                data['skill_ids'] = [[6, 0, [int(skill['skill_id']) for skill in payload['skills']]]]
                data['experience_ids'] = [[0, 0, {'job_role': role['role'], 'from_date': role['from'], 'to_date': role['to']}] for role in payload['experience']]
                # data['experience_ids']      = [[0, 0, {
                #                                        'job_role':role['role'], 
                #                                        'date_from': datetime.strptime('01/'+role['from'], '%d/%m/%Y'),
                #                                        'date_to': datetime.strptime('01/'+role['to'], '%d/%m/%Y')
                #                                        }] for role in payload['experience']]
                exp_month = 0
                for role in payload['experience']:
                    from_month, from_year = role['from'].split('/')
                    to_month, to_year = role['to'].split('/')
                    if all([int(from_month), int(from_year), int(to_month), int(to_year)]) > 0:
                        date_from = datetime.strptime('01/' + role['from'], '%d/%m/%Y').date()
                        date_to = datetime.strptime('01/' + role['to'], '%d/%m/%Y').date()
                        if date_to > date_from:
                            difference = relativedelta.relativedelta(date_to, date_from)
                            exp_month += difference.years * 12 + difference.months

                if exp_month > 0:
                    if exp_month >= 12:
                        year = exp_month // 12
                        month = exp_month - (year * 12)
                        data['exp_year'] = year
                        data['exp_month'] = month
                    else:
                        data['exp_month'] = exp_month

                data['mode_of_interview'] = payload['preference']
                data['description'] = payload['description']
                data['job_location_id'] = location_id and location_id.id or False
                data['source_id'] = source_id.id
                data['code_ref'] = source_id.code
                data['reference_walkindrive'] = 'Online Walk-in Drive ' + date.today().strftime("%d-%b-%Y")

                if 'cv_name' and 'cv_content' in payload:
                    file_name = payload['cv_name']

                    # doc_file = payload['cv_content']
                    upload_url = payload['cv_content']
                    response = urllib.request.urlopen(upload_url.replace(" ", "%20"))
                    doc_file = base64.b64encode(response.read())

                    if 'document_ids' in self.env['hr.applicant'].sudo()._fields:
                        data['document_ids'] = [[0, 0, {'content_file': doc_file, 'file_name': file_name}]]
                    # else:
                    #     data['attachment_ids'] = [[0, 0,
                    #                                {'name': file_name,
                    #                                 'datas_fname': file_name,
                    #                                 'datas': doc_file,
                    #                                 'res_name': payload['name'],
                    #                                 'res_model': 'hr.applicant',
                    #                                 'res_model_name': 'Applicant'
                    #                                 }
                    #                                ]]
                # print("data is",data)
                # try:
                applicant = self.env['hr.applicant'].create(data)
                if applicant:
                    data_dict[payload['id']] = applicant.id
                    insert_log.write({'status': 'Success'})

                else:
                    insert_log.write({'status': 'Failed'})

                    # except Exception as e:
                    # print('Exception in applicant create',e)
                    # insert_log.write({'status': 'Failed'})
                    # except Exception as e:
                    # print("Error while preparing data are",e)
                    # insert_log.write({'status': 'Failed'})

        # except Exception as e:
        # print("Final Exception is", e)
        # else:
        # send acknowledge to career server

        if len(data_dict):
            data = json.dumps({"method": "walkin_update", "data": data_dict})

            # try:
            response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
            content = response_obj.content
            resp = json.loads(content.decode("utf-8"))

            # except Exception as e:
            # print("Acknowledge failure reason",e)
