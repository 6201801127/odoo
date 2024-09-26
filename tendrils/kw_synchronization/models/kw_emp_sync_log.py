# *******************************************************************************************************************
#  File Name             :   kw_emp_sync_log.py
#  Description           :   This model is used to store log data for all master data to sync data to Kwantify. 
#  Created by            :   Abhijit Swain
#  Created On            :   02-08-2020
#  Modified by           :   Abhijit Swain
#  Modified On           :   05-08-2020
#  Modification History  :   Added Technical Skill code for Scheduler
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests, datetime

cur_dtime = datetime.datetime.now()
cur_dt = datetime.date(year=cur_dtime.year, month=cur_dtime.month, day=cur_dtime.day)


class KwEmpSyncLog(models.Model):
    _name = 'kw_emp_sync_log'
    _description = "Model used for syncing employee data with Kwantify"
    _rec_name = 'model_id'
    _order = 'id desc'

    model_id = fields.Char(string="Model Name")
    rec_id = fields.Integer(string="Record ID")
    code = fields.Integer(string="Code")
    json_data = fields.Char(string="Json Data")
    response_result = fields.Char(string="Response result")
    status = fields.Integer(string="Status")
    updated_status = fields.Boolean(string='Updated')
    
    # action_dict = {'create':'A','write':'U','unlink':'D'}

    def action_button_sync_record(self):
        self.employee_data_sync(single=True)

    def employee_data_sync(self, single=False):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')
        if single:
            rec = self.env['kw_emp_sync_log'].sudo().browse(self.id)
        else:
            rec = self.env['kw_emp_sync_log'].sudo().search([('status', '=', '0')], limit=10, order="id desc")
        # print("rec >>>> ", rec)
        # return
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        gender_dict = {"male": "M", "female": "F"}
        religion_dict = {"Hindu": "Hindu", "Muslim": "Muslim", "Sikhism": "Sikh"}
        maritalSet = {'M', 'U'}

        for r in rec:
            if r.status == 0:
                # --------Country Master sync Start--------
                if r.model_id == 'res.country':
                    country_rec = {}
                    country_record = self.env['res.country'].sudo().search([('id', '=', r.rec_id)])
                    country_rec['ActionCode'] = 'A' if country_record.kw_id == 0 else 'U'
                    country_rec['CountryName'] = country_record.name
                    country_rec['CountryID'] = str(country_record.kw_id)
                    country_rec['Description'] = 'Request for create' if country_record.kw_id == 0 else 'Request for update'
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', country_record.create_uid.id)])
                    country_rec['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    country_rec['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': country_rec})

                    categoryurl = parameterurl + 'AddNewCountryDetails'
                    resp = requests.post(categoryurl, headers=header, data=json.dumps(country_rec))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if country_rec['ActionCode'] == 'A':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                country_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': country_rec, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                       'new_record_log': country_rec,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': country_rec, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                       'new_record_log': country_rec,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': country_rec, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                   'new_record_log': country_rec,
                                                                                   'request_params': categoryurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': country_rec, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                       'new_record_log': country_rec,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': country_rec, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                       'new_record_log': country_rec,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': country_rec, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                                   'new_record_log': country_rec,
                                                                                   'request_params': categoryurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # -----------Country Master syn End -------------

                # ------ Specialization Master Start------
                if r.model_id == 'kwmaster_specializations':
                    specialization_sync = {}
                    specialization_record = self.env['kwmaster_specializations'].sudo().search([('id', '=', r.rec_id)])
                    specialization_sync['ActionCode'] = 'EQSPA' if specialization_record.kw_id == 0 else 'EQSPU'
                    specialization_sync['SpecName'] = specialization_record.name
                    specialization_sync['SpecId'] = str(specialization_record.kw_id)
                    specialization_sync['StreamId'] = str(specialization_record.stream_id.kw_id)
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', specialization_record.create_uid.id)])
                    specialization_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    specialization_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': specialization_sync})

                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    specializationurl = parameterurl + 'AddSpecializationDetails'
                    resp = requests.post(specializationurl, headers=header, data=json.dumps(specialization_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if specialization_sync['ActionCode'] == 'EQSPA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                specialization_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': specialization_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Specialization Master Sync Data',
                                     'new_record_log': specialization_sync,
                                     'request_params': specializationurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': specialization_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Specialization Master Sync Data',
                                     'new_record_log': specialization_sync,
                                     'request_params': specializationurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': specialization_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Specialization Master Sync Data',
                                 'new_record_log': specialization_sync,
                                 'request_params': specializationurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': specialization_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Specialization Master Sync Data',
                                     'new_record_log': specialization_sync,
                                     'request_params': specializationurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': specialization_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Specialization Master Sync Data',
                                     'new_record_log': specialization_sync,
                                     'request_params': specializationurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': specialization_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Specialization Master Sync Data',
                                 'new_record_log': specialization_sync,
                                 'request_params': specializationurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # ------ Specialization Master End ------

                # ------ Stream Master Start------
                if r.model_id == 'kwmaster_stream_name':
                    stream_sync = {}
                    stream_record = self.env['kwmaster_stream_name'].sudo().search([('id', '=', r.rec_id)])
                    stream_sync['ActionCode'] = 'EQSA' if stream_record.kw_id == 0 else 'EQSU'
                    stream_sync['StreamName'] = stream_record.name
                    stream_sync['StreamId'] = str(stream_record.kw_id)
                    stream_sync['CourseId'] = str(stream_record.course_id.kw_id)
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', stream_record.create_uid.id)])
                    stream_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    stream_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': stream_sync})

                    streamurl = parameterurl + 'AddEduQuaStreamDetails'
                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    resp = requests.post(streamurl, headers=header, data=json.dumps(stream_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if stream_sync['ActionCode'] == 'EQSA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                stream_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': stream_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Stream Master Sync Data',
                                     'new_record_log': stream_sync,
                                     'request_params': streamurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': stream_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Stream Master Sync Data',
                                     'new_record_log': stream_sync,
                                     'request_params': streamurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': stream_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Stream Master Sync Data',
                                                                                   'new_record_log': stream_sync,
                                                                                   'request_params': streamurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': stream_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Stream Master Sync Data',
                                     'new_record_log': stream_sync,
                                     'request_params': streamurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': stream_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Stream Master Sync Data',
                                     'new_record_log': stream_sync,
                                     'request_params': streamurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': stream_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Stream Master Sync Data',
                                                                                   'new_record_log': stream_sync,
                                                                                   'request_params': streamurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # ------ Stream Master End ------

                # ------- Type of employeement Master Sync Start -----
                if r.model_id == 'kwemp_employment_type':
                    emp_type_sync = {}
                    emp_type_record = self.env['kwemp_employment_type'].sudo().search([('id', '=', r.rec_id)])
                    emp_type_sync['ActionCode'] = 'TEA' if emp_type_record.kw_id == 0 else 'TEU'
                    emp_type_sync['RecName'] = emp_type_record.name
                    emp_type_sync['RecId'] = str(emp_type_record.kw_id)
                    emp_type_sync['RecCode'] = emp_type_record.code
                    emp_type_sync['Remarks'] = "Test"
                    emp_type_sync['UpdatedBy'] = str(self.env['hr.employee'].sudo().search([('user_id', '=', emp_type_record.create_uid.id)]).kw_id)
                    # r.write({'json_data': emp_type_sync})

                    emptypeurl = parameterurl + 'AddTypeOfEmplDetails'
                    resp = requests.post(emptypeurl, headers=header, data=json.dumps(emp_type_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if emp_type_sync['ActionCode'] == 'TEA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                emp_type_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': emp_type_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Type of employment Sync Data',
                                     'new_record_log': emp_type_sync,
                                     'request_params': emptypeurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': emp_type_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Type of employment Sync Data',
                                     'new_record_log': emp_type_sync,
                                     'request_params': emptypeurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': emp_type_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Type of employment Sync Data',
                                 'new_record_log': emp_type_sync,
                                 'request_params': emptypeurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': emp_type_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Type of employment Sync Data',
                                     'new_record_log': emp_type_sync,
                                     'request_params': emptypeurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': emp_type_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Type of employment Sync Data',
                                     'new_record_log': emp_type_sync,
                                     'request_params': emptypeurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': emp_type_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Type of employment Sync Data',
                                 'new_record_log': emp_type_sync,
                                 'request_params': emptypeurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # --------------Type of employeement Master sync End---------

                # ------ Skill Category Master Start------
                if r.model_id == 'kwemp_technical_category':
                    skill_sync = {}
                    skill_record = self.env['kwemp_technical_category'].sudo().search([('id', '=', r.rec_id)])
                    skill_sync['ActionCode'] = 'TSCA' if skill_record.kw_id == 0 else 'TSCU'
                    skill_sync['TecSkCatName'] = skill_record.name
                    skill_sync['TecSkCatId'] = str(skill_record.kw_id)
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', skill_record.create_uid.id)])
                    skill_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    skill_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': skill_sync})

                    skillurl = parameterurl + 'AddTechSkillCatDetails'
                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    resp = requests.post(skillurl, headers=header, data=json.dumps(skill_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if skill_sync['ActionCode'] == 'TSCA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                skill_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': skill_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Category Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Category Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Technical Skill Category Sync Data',
                                 'new_record_log': skill_sync,
                                 'request_params': skillurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': skill_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Category Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Category Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Technical Skill Category Sync Data',
                                 'new_record_log': skill_sync,
                                 'request_params': skillurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # ------ Skill Category Master End ------

                # ------- Skill Master Sync Start -----
                if r.model_id == 'kwemp_technical_skill':
                    skill_sync = {}
                    skill_record = self.env['kwemp_technical_skill'].sudo().search([('id', '=', r.rec_id)])
                    skill_sync['ActionCode'] = 'TSA' if skill_record.kw_id == 0 else 'TSU'
                    skill_sync['TechSkillName'] = skill_record.name
                    skill_sync['TechSkillId'] = str(skill_record.kw_id)
                    skill_sync['TechCatId'] = str(skill_record.category_id.kw_id)
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', skill_record.create_uid.id)])
                    skill_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    skill_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': skill_sync})

                    skillurl = parameterurl + 'AddTechSkillDetails'
                    resp = requests.post(skillurl, headers=header, data=json.dumps(skill_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if skill_sync['ActionCode'] == 'TSA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                skill_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': skill_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                                   'new_record_log': skill_sync,
                                                                                   'request_params': skillurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': skill_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Technical Skill Sync Data',
                                     'new_record_log': skill_sync,
                                     'request_params': skillurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': skill_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                                   'new_record_log': skill_sync,
                                                                                   'request_params': skillurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # --------------Skill Master sync End---------

                # -------Location Master sync start------
                if r.model_id == 'kw_location_master':
                    location_sync = {}
                    location_record = self.env['kw_location_master'].sudo().search([('id', '=', r.rec_id)])
                    location_sync['ActionCode'] = 'LA' if location_record.kw_id == 0 else 'LU'
                    location_sync['LocationName'] = location_record.name
                    location_sync['LocationID'] = str(location_record.kw_id)
                    location_sync['CountryID'] = str(location_record.country_id.kw_id)
                    location_sync['LocationDiff'] = '+06:30:00'
                    location_sync['TimezoneId'] = '0'
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', location_record.create_uid.id)])
                    location_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    location_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': location_sync})

                    locationurl = parameterurl + 'AddLocationDetails'
                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    resp = requests.post(locationurl, headers=header, data=json.dumps(location_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if location_sync['ActionCode'] == 'LA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                location_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': location_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Location Master Sync Data',
                                     'new_record_log': location_sync,
                                     'request_params': locationurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': location_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Location Master Sync Data',
                                     'new_record_log': location_sync,
                                     'request_params': locationurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': location_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                                   'new_record_log': location_sync,
                                                                                   'request_params': locationurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': location_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Location Master Sync Data',
                                     'new_record_log': location_sync,
                                     'request_params': locationurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': location_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Location Master Sync Data',
                                     'new_record_log': location_sync,
                                     'request_params': locationurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': location_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                                   'new_record_log': location_sync,
                                                                                   'request_params': locationurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # -------Location Master sync End--------

                # ------ Designation Master Sync Start------
                if r.model_id == 'hr.job':
                    deg_sync = {}
                    deg_record = self.env['hr.job'].sudo().search([('id', '=', r.rec_id)])
                    deg_sync['ActionCode'] = 'DA' if deg_record.kw_id == 0 else 'DU'
                    deg_sync['DesigName'] = deg_record.name
                    deg_sync['DesigId'] = str(deg_record.kw_id)
                    deg_sync['AliasName'] = deg_record.name
                    deg_sync['UserType'] = "P"
                    deg_sync['LocId'] = "All"
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', deg_record.create_uid.id)])
                    deg_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    deg_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': deg_sync})

                    parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')

                    degurl = parameterurl + 'AddDesignationDetails'

                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    resp = requests.post(degurl, headers=header, data=json.dumps(deg_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if deg_sync['ActionCode'] == 'DA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                deg_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': deg_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Designation Master Sync Data',
                                     'new_record_log': deg_sync,
                                     'request_params': degurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': deg_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Designation Master Sync Data',
                                     'new_record_log': deg_sync,
                                     'request_params': degurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': deg_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Designation Master Sync Data',
                                 'new_record_log': deg_sync,
                                 'request_params': degurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': deg_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Designation Master Sync Data',
                                     'new_record_log': deg_sync,
                                     'request_params': degurl,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': deg_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Designation Master Sync Data',
                                     'new_record_log': deg_sync,
                                     'request_params': degurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': deg_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create(
                                {'name': 'Designation Master Sync Data',
                                 'new_record_log': deg_sync,
                                 'request_params': degurl,
                                 'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # ------ Designation Master Sync End ------

                # ------ Grade Master Sync Start------
                if r.model_id == 'kwemp_grade':
                    grade_sync = {}
                    grade_record = self.env['kwemp_grade'].sudo().search([('id', '=', r.rec_id)])
                    grade_sync['ActionCode'] = 'GBA' if grade_record.kw_id == 0 else 'GBU'
                    grade_sync['GradeName'] = grade_record.name
                    grade_sync['GradeId'] = str(grade_record.kw_id)
                    grade_sync['Description'] = "Test Grade"
                    grade_sync['LocId'] = "All"
                    grade_sync['SortNum'] = "127"
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', grade_record.create_uid.id)])
                    grade_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    grade_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': grade_sync})

                    gradeurl = parameterurl + 'AddGradeBandDetails'
                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    resp = requests.post(gradeurl, headers=header, data=json.dumps(grade_sync))

                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if grade_sync['ActionCode'] == 'GBA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                grade_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': grade_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                       'new_record_log': grade_sync,
                                                                                       'request_params': gradeurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': grade_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                       'new_record_log': grade_sync,
                                                                                       'request_params': gradeurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': grade_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                   'new_record_log': grade_sync,
                                                                                   'request_params': gradeurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': grade_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                       'new_record_log': grade_sync,
                                                                                       'request_params': gradeurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': grade_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                       'new_record_log': grade_sync,
                                                                                       'request_params': gradeurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': grade_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Grade Master Sync Data',
                                                                                   'new_record_log': grade_sync,
                                                                                   'request_params': gradeurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # ------ Grade Master Sync End ------

                # --------Category Master sync Start--------
                if r.model_id == 'kwmaster_category_name':
                    category_sync = {}
                    category_record = self.env['kwmaster_category_name'].sudo().search([('id', '=', r.rec_id)])
                    category_sync['ActionCode'] = 'ECA' if category_record.kw_id == 0 else 'ECU'
                    category_sync['EmpCatName'] = category_record.name
                    category_sync['EmpCatId'] = str(category_record.kw_id)
                    category_sync['EmpRoleId'] = str(category_record.role_ids.kw_id)
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', category_record.create_uid.id)])
                    category_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    category_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': category_sync})

                    categoryurl = parameterurl + 'AddEmpCatDetails'
                    resp = requests.post(categoryurl, headers=header, data=json.dumps(category_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if category_sync['ActionCode'] == 'ECA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                category_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': category_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                       'new_record_log': category_sync,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': category_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                       'new_record_log': category_sync,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                        else:
                            r.write({'json_data': category_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                   'new_record_log': category_sync,
                                                                                   'request_params': categoryurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': category_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                       'new_record_log': category_sync,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': category_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                       'new_record_log': category_sync,
                                                                                       'request_params': categoryurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': category_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Category Sync Data',
                                                                                   'new_record_log': category_sync,
                                                                                   'request_params': categoryurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # -----------Category Master syn End -------------

                # --------------Employee sync Start---------

                if r.model_id == 'hr.employee':
                    emp_search = self.env['hr.employee']
                    employee_record = emp_search.sudo().browse(r.rec_id)
                    emp_kw_id = employee_record.kw_id

                    if r.code == 1 and emp_kw_id > 0:
                        employee_update_sync = {}
                        # print('update employee call', employee_update_sync)

                        if employee_record.no_attendance is False:
                            attTypDic = {'portal': '0', 'bio_metric': '1', 'manual': '3'}
                            attendance_rec = employee_record.attendance_mode_ids.mapped('alias')
                            bothLis = ['portal', 'bio_metric']
                            if len(attendance_rec) == 2:
                                if all(item in attendance_rec for item in bothLis):
                                    employee_update_sync['AttendanceMode'] = "2"
                            else:
                                employee_update_sync['AttendanceMode'] = attTypDic.get(str(attendance_rec[0]))
                        else:
                            employee_update_sync['AttendanceMode'] = "0"

                        employee_update_sync['Fullname'] = employee_record.name
                        employee_update_sync['Email'] = employee_record.work_email
                        if employee_record.practise:
                            employee_update_sync['DepartmentId'] = str(employee_record.practise.kw_id)
                        elif employee_record.section:
                            employee_update_sync['DepartmentId'] = str(employee_record.section.kw_id)
                        elif employee_record.division:
                            employee_update_sync['DepartmentId'] = str(employee_record.division.kw_id)
                        else:
                            employee_update_sync['DepartmentId'] = str(employee_record.department_id.kw_id)

                        employee_update_sync['DesgId'] = str(employee_record.job_id.kw_id)
                        employee_update_sync['GradeId'] = str(self.env['kwemp_grade'].sudo().search(
                            ['&', ('grade_id', '=', employee_record.grade.id),
                             ('band_id', '=', employee_record.emp_band.id)]).kw_id)
                        employee_update_sync['Location'] = str(employee_record.base_branch_id.location.kw_id)
                        employee_update_sync['DOJ'] = employee_record.date_of_joining.strftime('%d-%b-%y')
                        employee_update_sync['ProbetionComplitionDate'] = employee_record.date_of_completed_probation.strftime(
                            '%d-%b-%y') if employee_record.on_probation else employee_record.date_of_joining.strftime(
                            '%d-%b-%y')
                        employee_update_sync['ConfirmationStatus'] = "1" if employee_record.on_probation else "0"
                        employee_update_sync['DateofLeaving'] = employee_record.last_working_day.strftime('%d-%b-%y') if employee_record.last_working_day  else ''

                        employee_update_sync['Religion'] = religion_dict[
                            employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"

                        employee_update_sync['Gender'] = gender_dict[employee_record.gender] if employee_record.gender in gender_dict else ""
                        employee_update_sync['IsAdmin'] = "no" 
                        employee_update_sync['Attendance'] = "No" if employee_record.no_attendance == True else "Yes"

                        employee_update_sync['OfcId'] = str(employee_record.base_branch_id.kw_id)
                        employee_update_sync['RptDept'] = str(employee_record.parent_id.department_id.kw_id)
                        employee_update_sync['RptAuthority'] = str(employee_record.parent_id.kw_id)
                        employee_update_sync['DOB'] = employee_record.birthday.strftime('%d-%b-%y')
                        employee_update_sync['ActiveStatus'] = "Yes" if employee_record.active == True else "No"
                        employee_update_sync['UserId'] = "0" if employee_record.kw_id == 0 else employee_record.kw_id
                        employee_update_sync['EmploymentType'] = employee_record.employement_type.code
                        employee_update_sync['ShiftId'] = str(employee_record.resource_calendar_id.kw_id)
                        employee_update_sync['EmployeeRole'] = str(employee_record.emp_role.kw_id)
                        employee_update_sync['EmployeeCategory'] = str(employee_record.emp_category.kw_id)
                        employee_update_sync['EmpCode'] = employee_record.emp_code
                        # employee_update_sync['HierarchyID'] = '--'
                        # employee_update_sync['LevelID'] = '--'

                        employee_update_sync['Int_SbuID'] = employee_record.sbu_master_id.kw_id if employee_record.sbu_master_id and employee_record.sbu_master_id.kw_id else 0
                        if not employee_record.image_url:
                            employee_record.image_url = employee_record.get_url(update=False)
                        employee_update_sync['PhotoFile'] = employee_record.image_url
                        # r.write({'json_data': employee_update_sync})
                        # print("employee_update_sync >>>>>>>> ", employee_update_sync)

                        employee_update_url = self.env['ir.config_parameter'].sudo().get_param('kw_employee_update_sync')
                        employee_user_update_url = employee_update_url + 'Update_User_Details'
                        resp = requests.post(employee_user_update_url, headers=header, data=json.dumps(employee_update_sync))
                        json_data = json.dumps(resp.json())
                        json_record = json.loads(json_data)[0]
 
                        if resp.status_code == 200 or json_record['Status'] == '2':
                            if json_record['Status'] == '2':
                                r.write({'json_data': employee_update_sync,
                                         'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee update Sync Data',
                                     'new_record_log': employee_update_sync,
                                     'request_params': employee_user_update_url,
                                     'response_result': resp.json()})
                            else:
                                r.write({'json_data': employee_update_sync,
                                         'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee update Sync Data',
                                     'new_record_log': employee_update_sync,
                                     'request_params': employee_user_update_url,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': employee_update_sync,
                                     'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee update Sync Data',
                                                                                   'new_record_log': employee_update_sync,
                                                                                   'request_params': employee_user_update_url,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                     response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                    # For code reference check kw_sync_hr_employee.py file
                    # Add User Data sync
                    if r.code == 1 and emp_kw_id == 0:
                        employee_sync = {}
                        # emp_search = self.env['hr.employee']
                        # employee_record = emp_search.sudo().search([('id', '=', r.rec_id)])
                        if employee_record.no_attendance is False:
                            attTypDic = {'portal': '0', 'bio_metric': '1', 'manual': '3'}
                            attendance_rec = employee_record.attendance_mode_ids.mapped('alias')
                            bothLis = ['portal', 'bio_metric']
                            if len(attendance_rec) == 2:
                                if all(item in attendance_rec for item in bothLis):
                                    employee_sync['AttendanceType'] = "2"
                            else:
                                employee_sync['AttendanceType'] = attTypDic.get(str(attendance_rec[0]))
                        else:
                            employee_sync['AttendanceType'] = "0"

                        if employee_record.practise:
                            employee_sync['UserDept'] = str(employee_record.practise.kw_id)
                        elif employee_record.section:
                            employee_sync['UserDept'] = str(employee_record.section.kw_id)
                        elif employee_record.division:
                            employee_sync['UserDept'] = str(employee_record.division.kw_id)
                        else:
                            employee_sync['UserDept'] = str(employee_record.department_id.kw_id)

                        employee_sync['Attendance'] = "No" if employee_record.no_attendance == True else "Yes"
                        employee_sync['ConfStatus'] = "1" if employee_record.on_probation else "0"
                        employee_sync['CreatedBy'] = "224"  # To be sent static value as create_uid is Odoo bot
                        employee_sync['DateOfBirth'] = employee_record.birthday.strftime('%d-%b-%y')
                        employee_sync['dateOfjoin'] = employee_record.date_of_joining.strftime('%d-%b-%y')
                        employee_sync['Designation'] = str(employee_record.job_id.kw_id)
                        employee_sync['DomainName'] = employee_record.domain_login_id if employee_record.domain_login_id else ''
                        employee_sync['EmailId'] = employee_record.work_email
                        employee_sync['IsAdmin'] = "no"  # To be sent static value 0
                        employee_sync['EmployeeCategory'] = str(employee_record.emp_category.kw_id)
                        employee_sync['EmployeeType'] = str(employee_record.emp_role.kw_id)
                        employee_sync['EmpType'] = employee_record.employement_type.code
                        employee_sync['Fullname'] = employee_record.name
                        employee_sync['Gender'] = gender_dict[employee_record.gender] if employee_record.gender in gender_dict else ""
                        employee_sync['Grade'] = str(self.env['kwemp_grade'].sudo().search(['&', ('grade_id', '=', employee_record.grade.id), ('band_id', '=', employee_record.emp_band.id)]).kw_id)

                        employee_sync['MDate'] = employee_record.wedding_anniversary.strftime('%d-%b-%y') if employee_record.wedding_anniversary else "1-Jan-00"
                        employee_sync['ModuleId'] = "0"  # To be sent static data always
                        employee_sync['OfficeType'] = str(employee_record.base_branch_id.kw_id)
                        employee_sync['Password'] = "5F4DCC3B5AA765D61D8327DEB882CF99"  # employee_record.conv_pwd password to be sent static
                        employee_sync['Payroll'] = 'Yes' if employee_record.enable_payroll == 'yes' else 'No'
                        employee_sync['PhotoFileName'] = employee_record.image_url
                        employee_sync['PositionId'] = str(employee_record.job_id.kw_id)
                        employee_sync['ProbComplDate'] = employee_record.date_of_completed_probation.strftime(
                            '%d-%b-%y') if employee_record.on_probation else employee_record.date_of_joining.strftime(
                            '%d-%b-%y')
                        employee_sync['Religion'] = religion_dict[employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"
                        employee_sync['repoauthority2'] = str(employee_record.coach_id.kw_id)
                        employee_sync['ReportingAuthority'] = str(employee_record.parent_id.kw_id)
                        employee_sync['Shift'] = str(employee_record.resource_calendar_id.kw_id)
                        employee_sync['UserId'] = "0" if employee_record.kw_id == 0 else employee_record.kw_id
                        employee_sync['UserLocation'] = str(employee_record.base_branch_id.location.kw_id)
                        employee_sync['UserName'] = employee_record.user_id.login
                        employee_sync['EmpCode'] = employee_record.emp_code
                        employee_sync['Gratuity'] = 'Yes' if employee_record.enable_gratuity == 'yes' else 'No'
                        employee_sync['EPF'] = '0'
                        employee_sync['CTC'] = '0'
                        employee_sync['LatestCTC'] = '0'
                        employee_sync['BasicSal'] = '0'
                        employee_sync['MedicalReum'] = '0'
                        employee_sync['Transport'] = '0'
                        employee_sync['ProdBonous'] = '0'
                        employee_sync['ComBonous'] = '0'
                        employee_sync['HRA'] = '0'
                        employee_sync['Conveyance'] = '0'
                        employee_sync['AccountNo'] = ''
                        employee_sync['Bankname'] = ''
                        employee_sync['BillingAmt'] = '0'
                        # if employee_record.emp_refered.code == 'employee':
                        #     employee_sync['RefferedBy'] = str(employee_record.emp_employee_referred.name)
                        # if employee_record.emp_refered.kw_id > 0:
                        #     employee_sync['RefMode'] = employee_record.emp_refered.kw_id
                        employee_sync['Int_SbuID'] = employee_record.sbu_master_id.kw_id if employee_record.sbu_master_id and employee_record.sbu_master_id.kw_id else 0

                        employee_sync['RefMode'] = employee_record.emp_refered.kw_id if employee_record.emp_refered.kw_id > 0 else 0
                        # employee_sync['RefferedBy'] = str(employee_record.emp_employee_referred.name) if employee_record.emp_refered.code == 'employee' else ''
                        if employee_record.emp_refered.code == 'employee':
                            employee_sync['RefferedBy'] = str(employee_record.emp_employee_referred.kw_id)
                        elif employee_record.emp_refered.code == 'job':
                            employee_sync['RefferedBy'] = 1
                        elif employee_record.emp_refered.code == 'exemployee':
                            emp_data = emp_search.sudo().search([('active', '=', False), ('id', '=', r.rec_id)])
                            employee_sync['RefferedBy'] = str(emp_data.kw_id)
                        elif employee_record.emp_refered.code == 'client':
                            employee_sync['RefferedBy'] = str(employee_record.emp_reference)
                        elif employee_record.emp_refered.code == 'website':
                            employee_sync['RefferedBy'] = 'CSM Career'
                        elif employee_record.emp_refered.code == 'career':
                            employee_sync['RefferedBy'] = 'career@csm.co.in'
                        elif employee_record.emp_refered.code == 'walkindrive':
                            employee_sync['RefferedBy'] = str(employee_record.emp_reference_walkindrive)
                        elif employee_record.emp_refered.code == 'institute':
                            employee_sync['RefferedBy'] = str(employee_record.emp_institute_id.name)
                        elif employee_record.emp_refered.code == 'social':
                            employee_sync['RefferedBy'] = str(employee_record.emp_media_id.name)
                        elif employee_record.emp_refered.code == 'csmdatabase':
                            employee_sync['RefferedBy'] = str(employee_record.emp_reference)
                        elif employee_record.emp_refered.code == 'jobfair':
                            employee_sync['RefferedBy'] = str(employee_record.emp_reference_job_fair)
                        elif employee_record.emp_refered.code == 'printmedia':
                            employee_sync['RefferedBy'] = str(employee_record.emp_reference_print_media)
                        elif employee_record.emp_refered.code == 'consultancy':
                            employee_sync['RefferedBy'] = str(employee_record.emp_consultancy_id.name)
                        elif employee_record.emp_refered.code == 'partners':
                            employee_sync['RefferedBy'] = str(employee_record.emp_service_partner_id.name)
                        else:
                            employee_sync['RefferedBy'] = 0
                        # r.write({'json_data': employee_sync})

                        employeeurl = parameterurl + 'AddNewUserDetails'


                        resp = requests.post(employeeurl, headers=header, data=json.dumps(employee_sync))
                        json_data = json.dumps(resp.json())
                        json_record = json.loads(json_data)

                        if employee_sync['UserId'] == "0":
                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    employee_record.write({'kw_id': json_record['id']})
                                    r.write({'json_data': employee_sync,
                                             'status': 1,
                                             'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                           'new_record_log': employee_sync,
                                                                                           'request_params': employeeurl,
                                                                                           'response_result': resp.json()})
                                else:
                                    r.write({'json_data': employee_sync,
                                             'status': 0,
                                             'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                           'new_record_log': employee_sync,
                                                                                           'request_params': employeeurl,
                                                                                           'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id,
                                                             record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')
                            else:
                                r.write({'json_data': category_sync,
                                         'status': 0,
                                         'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                       'new_record_log': employee_sync,
                                                                                       'request_params': employeeurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    r.write({'json_data': employee_sync,
                                             'status': 1,
                                             'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                           'new_record_log': employee_sync,
                                                                                           'request_params': employeeurl,
                                                                                           'response_result': resp.json()})
                                else:
                                    r.write({'json_data': employee_sync,
                                             'status': 0,
                                             'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                           'new_record_log': employee_sync,
                                                                                           'request_params': employeeurl,
                                                                                           'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id,
                                                             record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')
                            else:
                                r.write({'json_data': employee_sync,
                                         'status': 0,
                                         'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data',
                                                                                       'new_record_log': employee_sync,
                                                                                       'request_params': employeeurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id,
                                                         response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                    # For code reference check kw_sync_hr_employee.py file
                    # Personal Info Data Sync
                    if r.code == 3:
                        personal_info_sync = {}
                        employee_personal_record = self.env['hr.employee'].sudo().search([('id', '=', r.rec_id)])
                        if employee_personal_record.kw_id != 0:
                            personal_info_sync['ActionType'] = 'DPI'
                            personal_info_sync['CreatedBy'] = str(employee_personal_record.kw_id)
                            personal_info_sync['Directory'] = '122555625'
                            personal_info_sync['EmailId'] = employee_personal_record.personal_email
                            personal_info_sync['EmgrAddress'] = '--'
                            personal_info_sync['EmgrCity'] = '--'
                            personal_info_sync['EmgrState'] = '--'
                            personal_info_sync['EmgrTelNo'] = '--'
                            personal_info_sync['EmgrContactPerson'] = employee_personal_record.emergency_contact
                            personal_info_sync['EmgrCountry'] = '1'  # passed static as error is displaying without country id
                            personal_info_sync['EmgrMobile'] = employee_personal_record.emergency_phone
                            personal_info_sync['MaritalSts'] = employee_personal_record.marital_sts.code if employee_personal_record.marital_sts.code in maritalSet else "O"
                            personal_info_sync['MobileNumber'] = employee_personal_record.mobile_phone
                            personal_info_sync['Nationality'] = "Indian" if employee_personal_record.country_id.id == 104 else "Other"
                            personal_info_sync['OfficeExetension'] = employee_personal_record.epbx_no
                            personal_info_sync['OffPreTelephoneNo'] = '--'
                            personal_info_sync['PermanentAddress'] = employee_personal_record.permanent_addr_street
                            personal_info_sync['PermanentCity'] = employee_personal_record.permanent_addr_city
                            personal_info_sync['PermanentCountry'] = str(employee_personal_record.permanent_addr_country_id.kw_id)
                            personal_info_sync['PermanentState'] = str(employee_personal_record.permanent_addr_state_id.name)
                            personal_info_sync['PerTelephoneNo'] = '--'
                            personal_info_sync['PresentAddress'] = employee_personal_record.present_addr_street
                            personal_info_sync['PresentCity'] = employee_personal_record.present_addr_city
                            personal_info_sync['PresentCountry'] = str(employee_personal_record.present_addr_country_id.kw_id)
                            personal_info_sync['PresentState'] = str(employee_personal_record.present_addr_state_id.name)
                            personal_info_sync['Religion'] = religion_dict[employee_personal_record.emp_religion.name] if employee_personal_record.emp_religion.name in religion_dict else "Other"
                            personal_info_sync['ResPreTelephoneNo1'] = '--'
                            personal_info_sync['UserId'] = str(employee_personal_record.kw_id)
                            personal_info_sync['LinkedInURL'] = str(employee_personal_record.linkedin_url)
                            personal_info_sync['Ldata'] = []

                            statDict = {'good': "1", "fair": "2", "slight": "3"}
                            if employee_personal_record.known_language_ids:
                                for rec in employee_personal_record.known_language_ids:
                                    val = {
                                        'LNID': str(rec.language_id.kw_id),
                                        'RNID': statDict[rec.reading_status],
                                        'WNID': statDict[rec.writing_status],
                                        'SPID': statDict[rec.speaking_status],
                                        'UNID': statDict[rec.understanding_status]
                                    }
                                    personal_info_sync['Ldata'].append(val)
                            # r.write({'json_data': personal_info_sync})

                            personalinfourl = parameterurl + 'AddPersonalInfoDetails'
                            resp = requests.post(personalinfourl, headers=header, data=json.dumps(personal_info_sync))
                            j_data = json.dumps(resp.json())
                            json_record = json.loads(j_data)

                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    r.write({'json_data': personal_info_sync, 'status': 1, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee personal details Sync Data',
                                         'new_record_log': personal_info_sync,
                                         'request_params': personalinfourl,
                                         'response_result': resp.json()})
                                else:
                                    r.write({'json_data': personal_info_sync, 'status': 0, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee personal details Sync Data',
                                         'new_record_log': personal_info_sync,
                                         'request_params': personalinfourl,
                                         'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')
                            else:
                                r.write({'json_data': personal_info_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee personal details Sync Data',
                                     'new_record_log': personal_info_sync,
                                     'request_params': personalinfourl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                    # For code reference check kw_sync_hr_employee.py file
                    # Identification Info data sync                                                                    
                    if r.code == 2:
                        identificationDict = {}
                        employee_record = self.env['hr.employee'].sudo().search([('id', '=', r.rec_id)])
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

                        if employee_record.kw_id != 0:
                            identificationDict['ActionCode'] = 'AID'
                            identificationDict['BloodGroup'] = employee_record.blood_group.name
                            identificationDict['NoofRecord'] = str(len(employee_record.identification_ids)) if len(employee_record.identification_ids) > 0 else '0'
                            identificationDict['CreatedBy'] = str(employee_record.kw_id)
                            identificationDict['UserId'] = str(employee_record.kw_id)
                            identificationDict['MSADet'] = []
                            if employee_record.identification_ids:
                                for rec in employee_record.identification_ids:
                                    attachment_data = self.env['ir.attachment'].sudo().search(
                                        [('res_id', '=', rec.id),
                                         ('res_model', '=', 'kwemp_identity_docs'),
                                         ('res_field', '=', 'uploaded_doc')])
                                    if attachment_data:
                                        attachment_data.write({'public': True})

                                    val = {
                                        'IDTYPEID': rec.name,
                                        'DOCNO': rec.doc_number,
                                        'DTISSUE': rec.date_of_issue.strftime('%d-%b-%y') if rec.date_of_issue else "1-Jan-00",
                                        'DTEXP': rec.date_of_expiry.strftime('%d-%b-%y') if rec.date_of_expiry else "1-Jan-00",
                                        'URL': f"{base_url}/web/content/{attachment_data.id}" if attachment_data else '',
                                        'DOCUMENTNAME': rec.doc_file_name if rec.doc_file_name else 'Demo.png',
                                        'RENAPPLIED': 'Y' if rec.renewal_sts else 'N'
                                    }
                                    identificationDict['MSADet'].append(val)
                            # r.write({'json_data': identificationDict})

                            identificationurl = parameterurl + 'AddIdentification'
                            resp = requests.post(identificationurl, headers=header, data=json.dumps(identificationDict))
                            j_data = json.dumps(resp.json())
                            json_record = json.loads(j_data)

                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    r.write({'json_data': identificationDict, 'status': 1, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Identification details Sync Data',
                                         'new_record_log': identificationDict,
                                         'request_params': identificationurl,
                                         'response_result': resp.json()})
                                else:
                                    r.write({'json_data': identificationDict, 'status': 0, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Identification details Sync Data',
                                         'new_record_log': identificationDict,
                                         'request_params': identificationurl,
                                         'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')
                            else:
                                r.write({'json_data': identificationDict, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee Identification details Sync Data',
                                     'new_record_log': identificationDict,
                                     'request_params': identificationurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                    # For code reference check kw_sync_hr_employee.py file
                    # Work Experience Data Sync
                    if r.code == 5:
                        workExpDict = {}
                        profDict = {'1': 'Excellent', '2': 'Good', '3': 'Average'}
                        employee_record = self.env['hr.employee'].sudo().search([('id', '=', r.rec_id)])
                        if employee_record.kw_id != 0:
                            workExpDict['CreatedBy'] = str(employee_record.kw_id)
                            workExpDict['UserId'] = str(employee_record.kw_id)
                            workExpDict['ActionCode'] = 'AWTD'
                            workExpDict['LWkEData'] = []
                            workExpDict['NoofRecord'] = str(len(employee_record.technical_skill_ids)) if len(employee_record.technical_skill_ids) > 0 else '0'
                            if employee_record.work_experience_ids:
                                experience_country_rec = employee_record.work_experience_ids.mapped('country_id.kw_id')
                                experience_country = ",".join(str(x) for x in experience_country_rec)

                                for rec in employee_record.work_experience_ids:
                                    val = {
                                        'COUNTRYNAME': rec.country_id.name,
                                        'COUNTRYID': str(rec.country_id.kw_id),
                                        'WORKEXPID': '0',
                                        'ORGNAME': rec.name,
                                        'JOBPROFILE': rec.designation_name,
                                        'ORGTYPENAME': rec.organization_type.name,
                                        'ORGTYPEID': str(rec.organization_type.kw_id),
                                        'INDTYPENAME': rec.industry_type.name,
                                        'INDTYPEID': str(rec.industry_type.kw_id),
                                        'EFFROM': rec.effective_from.strftime('%d-%b-%Y'),
                                        'EFTO': rec.effective_to.strftime('%d-%b-%Y'),
                                        'DOC': rec.doc_file_name if rec.doc_file_name else 'Demo.png'
                                    }
                                    workExpDict['LWkEData'].append(val)

                            workExpDict['PermanentCountry'] = experience_country

                            workExpDict['LTsQData'] = []
                            if employee_record.technical_skill_ids:
                                for rec in rec.technical_skill_ids:
                                    val = {'TECID': '0', 'CATNAME': rec.category_id.name,
                                           'CATID': str(rec.category_id.kw_id),
                                           'SKILLNAME': rec.skill_id.name, 'SKILLID': str(rec.skill_id.kw_id),
                                           'PROFILVLNAME': profDict.get(rec.proficiency),
                                           'PROFILVL': rec.proficiency}
                                    workExpDict['LTsQData'].append(val)
                            # r.write({'json_data': workExpDict})
                            # print(workExpDict)

                            expurl = parameterurl + 'AddWorkExp'
                            resp = requests.post(expurl, headers=header, data=json.dumps(workExpDict))
                            j_data = json.dumps(resp.json())
                            json_record = json.loads(j_data)

                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    r.write({'json_data': workExpDict, 'status': 1, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Work Experience details Sync Data',
                                         'new_record_log': workExpDict,
                                         'request_params': expurl,
                                         'response_result': resp.json()})
                                else:
                                    r.write({'json_data': workExpDict, 'status': 0, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Work Experience details Sync Data',
                                         'new_record_log': workExpDict,
                                         'request_params': expurl,
                                         'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')

                            else:
                                r.write({'json_data': workExpDict, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee Work Experience details Sync Data',
                                     'new_record_log': workExpDict,
                                     'request_params': expurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                    # For code reference check kw_sync_hr_employee.py file
                    # Educational Info Data Sync
                    if r.code == 4:
                        educationTrainingDict = {}
                        employee_record = self.env['hr.employee'].sudo().search([('id', '=', r.rec_id)])
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        if employee_record.kw_id != 0:
                            educationTrainingDict['UserId'] = str(employee_record.kw_id)
                            educationTrainingDict['LEddata'] = [
                                {"SID": "0", "PID": "0", "DID": "0", "QID": "0", "PRID": "0", "AID": "0", "RID": "0",
                                 "TID": "0"}]  # To be sent static
                            educationTrainingDict['LQudata'] = []
                            rcount = 1
                            if employee_record.educational_details_ids:
                                edu_length = 0
                                str_passing_details = ""
                                for rec in employee_record.educational_details_ids:
                                    if rec.course_type == '1':
                                        edu_length += 1
                                    if rec.passing_details:
                                        for p_detail in rec.passing_details:
                                            str_passing_details += str(p_detail.kw_id) + ','
                                    attachment_data = self.env['ir.attachment'].sudo().search(
                                        [('res_id', '=', rec.id),
                                         ('res_model', '=', 'kwemp_educational_qualification'),
                                         ('res_field', '=', 'uploaded_doc')])
                                    if attachment_data:
                                        attachment_data.write({'public': True})

                                    val = {'INT_QUALIF_ID': '0',
                                           'INT_STREAM_ID': str(rec.stream_id.kw_id),
                                           'VCH_BOARD_NAME': rec.university_name.name,
                                           'VCH_PASSING_DTLS': str_passing_details if rec.passing_details else 'NA',
                                           'INT_PASSING_YEAR': rec.passing_year,
                                           'VCH_DIVISION_GRADE': rec.division,
                                           'DEC_PERCENTAGE': str(rec.marks_obtained),
                                           'INT_PQSTREAM_ID': '0',
                                           'INT_CERTTYPE_ID': '0',
                                           'INT_POSITION': str(rcount),
                                           'FILE_NAME': rec.doc_file_name if rec.doc_file_name else 'Demo.png',
                                           'URL': f"{base_url}/web/content/{attachment_data.id}" if attachment_data else '',
                                           'VCH_INNERACTION': 'Y'}
                                    rcount += 1
                                    educationTrainingDict['LQudata'].append(val)

                            educationTrainingDict['strMetricStatus'] = 'yes' if edu_length >= 1 else 'no'
                            educationTrainingDict['strPlus2Status'] = 'yes' if edu_length >= 2 else 'no'
                            educationTrainingDict['strPlus3Status'] = 'yes' if edu_length >= 3 else 'no'
                            # r.write({'json_data': educationTrainingDict})

                            educationalurl = parameterurl + 'AddEducationTrainingDetails'
                            resp = requests.post(educationalurl, headers=header, data=json.dumps(educationTrainingDict))
                            j_data = json.dumps(resp.json())
                            json_record = json.loads(j_data)

                            if resp.status_code == 200:
                                if json_record['status'] == 1:
                                    r.write({'json_data': educationTrainingDict, 'status': 1, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Educational details Sync Data',
                                         'new_record_log': educationTrainingDict,
                                         'request_params': educationalurl,
                                         'response_result': resp.json()})
                                else:
                                    r.write({'json_data': educationTrainingDict, 'status': 0, 'response_result': resp.json()})
                                    self.env['kw_kwantify_integration_log'].sudo().create(
                                        {'name': 'Employee Educational  details Sync Data',
                                         'new_record_log': educationTrainingDict,
                                         'request_params': educationalurl,
                                         'response_result': resp.json()})
                                    template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                    self.env.user.notify_success(message='Mail sent successfully')

                            else:
                                r.write({'json_data': educationTrainingDict, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create(
                                    {'name': 'Employee Educational details Sync Data',
                                     'new_record_log': educationTrainingDict,
                                     'request_params': educationalurl,
                                     'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')

                # --------------- Employee sync end------------------

                # --------Branch Master sync Start--------
                # if r.model_id == 'kw_res_branch':
                #     branch_sync = {}
                #     branch_record = self.env['kw_res_branch'].sudo().search([('id', '=', r.rec_id)])
                #     branch_sync['ActionCode'] = 'OUA' if branch_record.kw_id == 0 else 'OUU'
                #     branch_sync['OficId'] = str(branch_record.kw_id)
                #     # branch_sync['CompanyName'] = branch_record.company_id.name
                #     branch_sync['CompanyName'] = branch_record.name
                #     branch_sync['OficProfile'] = branch_record.name
                #     branch_sync['LocId'] = str(branch_record.location.kw_id)
                #     branch_sync['OficAdd'] = branch_record.address
                #     branch_sync['OficTeleno1'] = str(branch_record.telephone_no)
                #     branch_sync['OficTeleno2'] = ""
                #     branch_sync['OficTeleno3'] = ""
                #     branch_sync['OficTeleno4'] = ""
                #     branch_sync['OficEmail'] = branch_record.email if branch_record.email else ""
                #     branch_sync['OficURL'] = branch_record.website if branch_record.website else ""
                #     branch_sync['OficFax'] = branch_record.fax
                #     branch_sync['OficPrefix'] = "05"
                #     branch_sync['CompanyId'] = branch_record.company_id.kw_id
                #     branch_sync['OficLatitude'] = ""
                #     branch_sync['OficLongitude'] = ""
                #     created_by = self.env['hr.employee'].sudo().search([('user_id', '=', branch_record.create_uid.id)]).kw_id
                #     branch_sync['CreatedBy'] = str(created_by)
                #     branch_sync['UpdatedBy'] = str(created_by)

                #     branchurl = parameterurl + 'AddOfficeUnitDetails'
                #     resp = requests.post(branchurl, headers=header, data=json.dumps(branch_sync))

                #     j_data = json.dumps(resp.json())
                #     json_record = json.loads(j_data)
                #     if branch_sync['ActionCode'] == 'OUA':
                #         if resp.status_code == 200:
                #             if json_record['status'] == 1:
                #                 branch_record.write({'kw_id': json_record['id']})
                #                 r.write({'json_data': branch_sync, 'status': 1, 'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                        'new_record_log': branch_sync,
                #                                                                        'request_params': branchurl,
                #                                                                        'response_result': resp.json()})
                #             else:
                #                 r.write({'json_data': branch_sync, 'status': 0, 'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                        'new_record_log': branch_sync,
                #                                                                        'request_params': branchurl,
                #                                                                        'response_result': resp.json()})
                #                 template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                #                 self.env.user.notify_success(message='Mail sent successfully')

                #         else:
                #             r.write({'json_data': branch_sync, 'status': 0, 'response_result': resp.json()})
                #             self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                    'new_record_log': branch_sync,
                #                                                                    'request_params': branchurl,
                #                                                                    'response_result': resp.json()})
                #             template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                #             self.env.user.notify_success(message='Mail sent successfully')
                #     else:
                #         if resp.status_code == 200:
                #             if json_record['status'] == 1:
                #                 r.write({'json_data': branch_sync, 'status': 1, 'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                        'new_record_log': branch_sync,
                #                                                                        'request_params': branchurl,
                #                                                                        'response_result': resp.json()})
                #             else:
                #                 r.write({'json_data': branch_sync, 'status': 0, 'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                        'new_record_log': branch_sync,
                #                                                                        'request_params': branchurl,
                #                                                                        'response_result': resp.json()})
                #                 template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                #                 self.env.user.notify_success(message='Mail sent successfully')
                #         else:
                #             r.write({'json_data': branch_sync, 'status': 0, 'response_result': resp.json()})
                #             self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Branch Sync Data',
                #                                                                    'new_record_log': branch_sync,
                #                                                                    'request_params': branchurl,
                #                                                                    'response_result': resp.json()})
                #             template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                #             self.env.user.notify_success(message='Mail sent successfully')

                # -----------Branch Master syn End -------------

                # --------Language Master sync Start--------
                if r.model_id == 'kwemp_language_master':
                    language_sync = {}
                    language_record = self.env['kwemp_language_master'].sudo().search([('id', '=', r.rec_id)])
                    language_sync['ActionCode'] = 'LNA' if language_record.kw_id == 0 else 'LNU'
                    language_sync['LangName'] = language_record.name
                    language_sync['LangId'] = str(language_record.kw_id)
                    language_sync['Description'] = "test1"
                    created_by = self.env['hr.employee'].sudo().search([('user_id', '=', language_record.create_uid.id)])
                    language_sync['CreatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    language_sync['UpdatedBy'] = '224' if len(created_by) > 1 else str(created_by.kw_id)
                    # r.write({'json_data': language_sync})

                    languageurl = parameterurl + 'AddLanguageDetails'
                    resp = requests.post(languageurl, headers=header, data=json.dumps(language_sync))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    if language_sync['ActionCode'] == 'LNA':
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                language_record.write({'kw_id': json_record['id']})
                                r.write({'json_data': language_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                       'new_record_log': language_sync,
                                                                                       'request_params': languageurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': language_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                       'new_record_log': language_sync,
                                                                                       'request_params': languageurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': language_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                   'new_record_log': language_sync,
                                                                                   'request_params': languageurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')
                    else:
                        if resp.status_code == 200:
                            if json_record['status'] == 1:
                                r.write({'json_data': language_sync, 'status': 1, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                       'new_record_log': language_sync,
                                                                                       'request_params': languageurl,
                                                                                       'response_result': resp.json()})
                            else:
                                r.write({'json_data': language_sync, 'status': 0, 'response_result': resp.json()})
                                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                       'new_record_log': language_sync,
                                                                                       'request_params': languageurl,
                                                                                       'response_result': resp.json()})
                                template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                                self.env.user.notify_success(message='Mail sent successfully')
                        else:
                            r.write({'json_data': language_sync, 'status': 0, 'response_result': resp.json()})
                            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'language Sync Data',
                                                                                   'new_record_log': language_sync,
                                                                                   'request_params': languageurl,
                                                                                   'response_result': resp.json()})
                            template_id.with_context(mail_id=last_mail_id, model_id=r.model_id, record_id=r.rec_id, response_result=resp.json()).send_mail(r.id)
                            self.env.user.notify_success(message='Mail sent successfully')

                # -----------Language Master syn End -------------

                # --------------Employee sync Start---------
                # if r.model_id == 'hr.employee':
                #     employee_sync = {}
                #     employee_record = self.env['hr.employee'].sudo().search([('id','=',r.rec_id)])
                #     employee_sync['AccountNo'] = str(employee_record.bank_account_id.acc_number)
                #     employee_sync['Attendance'] = "Yes" # "Yes" if employee_record.no_attendance == True else "No"
                #     employee_sync['AttendanceType'] = "2" # fetch from attendace type master
                #     employee_sync['Bankname'] = employee_record.bank
                #     employee_sync['BasicSal'] = str(employee_record.basic_at_join_time)
                #     employee_sync['BillingAmt'] = str(employee_record.proj_bill_amnt)
                #     employee_sync['ConfStatus'] = "0" if employee_record.date_of_completed_probation > cur_dt else "1"
                #     employee_sync['CreatedBy'] = "224" # self.env['hr.employee'].search([('user_id','=',employee_record.create_uid.id)]).kw_id
                #     employee_sync['CTC'] = str(employee_record.at_join_time_ctc)
                #     employee_sync['DateOfBirth'] = employee_record.birthday.strftime('%d-%b-%y')
                #     employee_sync['dateOfjoin'] = employee_record.date_of_joining.strftime('%d-%b-%y')
                #     employee_sync['Designation'] = str(employee_record.job_id.kw_id)
                #     employee_sync['DomainName'] = employee_record.domain_login_id
                #     employee_sync['EmailId'] = employee_record.work_email
                #     employee_sync['EmployeeCategory'] = str(employee_record.emp_category.kw_id)
                #     employee_sync['EmployeeType'] = str(employee_record.emp_role.kw_id)
                #     employee_sync['EmpType'] = employee_record.employement_type.code
                #     employee_sync['EPF'] = '1' if employee_record.enable_payroll == 'yes' else '0'
                #     employee_sync['Fullname'] = employee_record.name
                #     employee_sync['Gender'] = gender_dict[employee_record.gender] if employee_record.gender in gender_dict else ""
                #     employee_sync['Grade'] = "73" # need to get kw_id from kwemp_grade
                #     employee_sync['Gratuity'] = 'Yes' if employee_record.enable_gratuity == 'yes' else 'No'
                #     employee_sync['LatestCTC'] = str(employee_record.current_ctc)
                #     employee_sync['MDate'] = employee_record.wedding_anniversary.strftime('%d-%b-%y') if employee_record.wedding_anniversary else "1-Jan-00"
                #     employee_sync['ModuleId'] = "487" # kw_id doesn't exist in crm_lead
                #     employee_sync['OfficeType'] = str(employee_record.base_branch_id.kw_id)
                #     employee_sync['Password'] = employee_record.conv_pwd
                #     employee_sync['Payroll'] = 'Yes' if employee_record.enable_payroll == 'yes' else 'No'
                #     employee_sync['PhotoFileName'] = employee_record.image_url
                #     employee_sync['PositionId'] = str(employee_record.job_id.kw_id) 
                #     employee_sync['ProbComplDate'] = employee_record.date_of_completed_probation.strftime('%d-%b-%y')
                #     employee_sync['Religion'] = religion_dict[employee_record.emp_religion.name] if employee_record.emp_religion.name in religion_dict else "Other"
                #     employee_sync['repoauthority2'] = str(employee_record.coach_id.kw_id)
                #     employee_sync['ReportingAuthority'] = str(employee_record.parent_id.kw_id)
                #     employee_sync['Shift'] = "57" # need updated code to check if kw_id exists
                #     employee_sync['UserDept'] = str(employee_record.department_id.kw_id)
                #     employee_sync['UserId'] = "0" if employee_record.kw_id == 0 else employee_record.kw_id
                #     employee_sync['UserLocation'] = str(employee_record.base_branch_id.location.kw_id)
                #     employee_sync['UserName'] = employee_record.user_id.login
                #     employee_sync['MedicalReum'] = str(employee_record.medical_reimb)
                #     employee_sync['Transport'] = str(employee_record.transport)
                #     employee_sync['ProdBonous'] = str(employee_record.productivity)
                #     employee_sync['ComBonous'] = str(employee_record.commitment)

                #     employeeurl = parameterurl + 'AddNewUserDetails'
                #     resp = requests.post(employeeurl, headers=header, data=json.dumps(employee_sync))
                #     json_data = json.dumps(resp.json())
                #     json_record = json.loads(json_data)

                #     if employee_sync['UserId'] == "0": 
                #         if resp.status_code == 200:
                #             if json_record['status'] == 1:
                #                 employee_record.write({'kw_id': json_record['id']})
                #                 r.write({'json_data': employee_sync, 
                #                         'status': 1, 'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                         'new_record_log': employee_sync,
                #                                                                         'request_params': employeeurl, 
                #                                                                         'response_result': resp.json()})
                #             else:
                #                 r.write({
                #                     'json_data': employee_sync,
                #                     'status' : 0,
                #                     'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                     'new_record_log': employee_sync,
                #                                                                     'request_params': employeeurl, 
                #                                                                     'response_result': resp.json()})
                #         else:
                #             r.write({
                #                 'json_data': employee_sync,
                #                 'status' : 0,
                #                 'response_result': resp.json()})
                #             self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                     'new_record_log': employee_sync,
                #                                                                     'request_params': employeeurl,
                #                                                                     'response_result': resp.json()}) 
                #     else:
                #         if resp.status_code == 200:
                #             if json_record['status'] == 1:
                #                 r.write({
                #                     'json_data': employee_sync,
                #                     'status' : 1,
                #                     'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                     'new_record_log': employee_sync,
                #                                                                     'request_params': employeeurl, 
                #                                                                     'response_result': resp.json()})
                #             else:
                #                 r.write({
                #                     'json_data': employee_sync,
                #                     'status' : 0,
                #                     'response_result': resp.json()})
                #                 self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                     'new_record_log': employee_sync,
                #                                                                     'request_params': employeeurl, 
                #                                                                     'response_result': resp.json()})
                #         else:
                #             r.write({
                #                     'json_data': employee_sync,
                #                     'status' : 0,
                #                     'response_result': resp.json()})
                #             self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Sync Data', 
                #                                                                     'new_record_log': employee_sync,
                #                                                                     'request_params': employeeurl, 
                #                                                                     'response_result': resp.json()})

                # --------------Employee sync End---------
