# *******************************************************************************************************************
#  File Name             :   kw_emp_technical_skill_sync.py
#  Description           :   This model is used to inherit Techinical Skill model and sync data into Kwantify 
#  Created by            :   Asish ku Nayak
#  Created On            :   05-08-2020
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests


class kwemp_technical_skill(models.Model):
    _inherit = 'kwemp_technical_skill'

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'kwemp_technical_skill'), ('rec_id', '=', record.id)])
            if log_record:
                status = log_record.mapped('status')
                if 0 in status:
                    record.sync_status = '1'
                else:
                    record.sync_status = '2'
            else:
                record.sync_status = '0'

    # For skill category Synchronization
    @api.model
    def action_sync_skill_master(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        skill_rec = self.env['kw_emp_sync_log'].sudo().search(
            ['&', ('model_id', '=', 'kwemp_technical_skill'), ('status', '=', 0)])
        skill_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        skillurl = parameterurl + 'AddTechSkillDetails'
        for rec in skill_rec:
            skill_record = self.env['kwemp_technical_skill'].sudo().search([('id', '=', rec.rec_id)])
            created_by = str(self.env['hr.employee'].sudo().search([('user_id', '=', skill_record.create_uid.id)]).kw_id)

            skill_sync['ActionCode'] = 'TSA' if skill_record.kw_id == 0 else 'TSU'
            skill_sync['TechSkillName'] = skill_record.name
            skill_sync['TechSkillId'] = str(skill_record.kw_id)
            skill_sync['TechCatId'] = str(skill_record.category_id.kw_id)
            skill_sync['CreatedBy'] = created_by
            skill_sync['UpdatedBy'] = created_by

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(skillurl, headers=header, data=json.dumps(skill_sync))

            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            # "id": 0,"mesg": "Name Already available","status": 1
            if skill_sync['ActionCode'] == 'TSA':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        skill_record.write({'kw_id': int(json_record['id'])})
                        rec.write({
                            'json_data': skill_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                               'new_record_log': skill_sync,
                                                                               'request_params': skillurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': skill_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                               'new_record_log': skill_sync,
                                                                               'request_params': skillurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': skill_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                           'new_record_log': skill_sync,
                                                                           'request_params': skillurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        # print("UUPDATE ELSE PART EXECUTED")
                        rec.write({
                            'json_data': skill_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                               'new_record_log': skill_sync,
                                                                               'request_params': skillurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': skill_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                               'new_record_log': skill_sync,
                                                                               'request_params': skillurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': skill_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Technical Skill Sync Data',
                                                                           'new_record_log': skill_sync,
                                                                           'request_params': skillurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    @api.model
    def check_sync_skill_master_group(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'

    # Create method for skill master
    @api.model
    def create(self, vals):
        skill_record = super(kwemp_technical_skill, self).create(vals)
        sync_data = self.env['kw_emp_sync_log'].create(
            {'model_id': 'kwemp_technical_skill', 'rec_id': skill_record.id, 'code': False, 'status': 0})
        return skill_record

    # write method for skill master
    @api.multi
    def write(self, vals):
        skill_record = super(kwemp_technical_skill, self).write(vals)
        w_id = self.env['kwemp_technical_skill'].sudo().search([('id', '=', self.id)])
        if w_id.write_uid.id != 1:
            log_rec = self.env['kw_emp_sync_log'].sudo().search(['&', '&', ('model_id', '=', 'kwemp_technical_skill'),
                                                                 ('rec_id', '=', w_id.id), ('status', '=', 0)])
            if len(log_rec) == 0:
                sync_data = self.env['kw_emp_sync_log'].create(
                    {'model_id': 'kwemp_technical_skill', 'rec_id': w_id.id, 'code': False, 'status': 0})
        return skill_record
