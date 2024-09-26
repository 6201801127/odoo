# This model is used to inherit kwemp_technical_category model and insert data into the kw_emp_sync_log
# created by - Asish Ku Nayak


from odoo import models, fields, api
import json, requests


class kwemp_technical_category(models.Model):
    _inherit = 'kwemp_technical_category'

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'kwemp_technical_category'), ('rec_id', '=', record.id)])
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
    def action_sync_skill(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        skill_rec = self.env['kw_emp_sync_log'].sudo().search(
            ['&', ('model_id', '=', 'kwemp_technical_category'), ('status', '=', 0)])
        skill_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        skillurl = parameterurl + 'AddTechSkillCatDetails'

        for rec in skill_rec:
            skill_record = self.env['kwemp_technical_category'].sudo().search([('id', '=', rec.rec_id)])
            skill_sync['ActionCode'] = 'TSCA' if skill_record.kw_id == 0 else 'TSCU'
            skill_sync['TecSkCatName'] = skill_record.name
            skill_sync['TecSkCatId'] = str(skill_record.kw_id)
            skill_sync['CreatedBy'] = str(
                self.env['hr.employee'].sudo().search([('user_id', '=', skill_record.create_uid.id)]).kw_id)
            skill_sync['UpdatedBy'] = str(
                self.env['hr.employee'].sudo().search([('user_id', '=', skill_record.create_uid.id)]).kw_id)

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(skillurl, headers=header, data=json.dumps(skill_sync))

            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)

            if skill_sync['ActionCode'] == 'TSCA':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        skill_record.write({'kw_id': json_record['id']})
                        rec.write({
                            'json_data': skill_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Technical Skill Category Sync Data',
                             'new_record_log': skill_sync,
                             'request_params': skillurl,
                             'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': skill_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Technical Skill Category Sync Data',
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
                    self.env['kw_kwantify_integration_log'].sudo().create(
                        {'name': 'Technical Skill Category Sync Data',
                         'new_record_log': skill_sync,
                         'request_params': skillurl,
                         'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        rec.write({
                            'json_data': skill_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Technical Skill Category Sync Data',
                             'new_record_log': skill_sync,
                             'request_params': skillurl,
                             'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': skill_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create(
                            {'name': 'Technical Skill Category Sync Data',
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
                    self.env['kw_kwantify_integration_log'].sudo().create(
                        {'name': 'Technical Skill Category Sync Data',
                         'new_record_log': skill_sync,
                         'request_params': skillurl,
                         'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    @api.model
    def check_sync_skill_group(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'

    # Create method for skill category
    @api.model
    def create(self, vals):
        skill_record = super(kwemp_technical_category, self).create(vals)
        sync_data = self.env['kw_emp_sync_log'].create(
            {'model_id': 'kwemp_technical_category', 'rec_id': skill_record.id, 'code': False, 'status': 0})
        return skill_record

    # write method for skill category
    @api.multi
    def write(self, vals):
        skill_record = super(kwemp_technical_category, self).write(vals)
        w_id = self.env['kwemp_technical_category'].sudo().search([('id', '=', self.id)])
        if w_id.write_uid.id != 1:
            sync_data = self.env['kw_emp_sync_log'].create(
                {'model_id': 'kwemp_technical_category', 'rec_id': w_id.id, 'code': False, 'status': 0})
        return skill_record
