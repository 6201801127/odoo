# *******************************************************************************************************************
#  File Name             :   kw_country_sync_log.py
#  Description           :   This model is used to inherit res.country model and sync data into Kwantify 
#  Created by            :   Abhijit Swain
#  Created On            :   02-08-2020
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests


class kw_sync_country(models.Model):
    _inherit = 'res.country'

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'res.country'), ('rec_id', '=', record.id)])
            if log_record:
                status = log_record.mapped('status')
                if 0 in status:
                    record.sync_status = '1'
                else:
                    record.sync_status = '2'
            else:
                record.sync_status = '0'

    # For country Synchronization
    @api.model
    def action_sync_country(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        country_rec = self.env['kw_emp_sync_log'].sudo().search(['&', ('model_id', '=', 'res.country'), ('status', '=', 0)])
        country_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        countryurl = parameterurl + 'AddNewCountryDetails'
        for rec in country_rec:
            country_record = self.env['res.country'].sudo().search([('id', '=', rec.rec_id)])
            country_sync['ActionCode'] = 'A' if country_record.kw_id == 0 else 'U'
            country_sync['CountryName'] = country_record.name
            country_sync['CountryID'] = str(country_record.kw_id)
            country_sync['Description'] = 'Request for create' if country_record.kw_id == 0 else 'Request for update'
            country_sync['CreatedBy'] = str(self.env['hr.employee'].sudo().search([('user_id', '=', country_record.create_uid.id)]).kw_id)
            country_sync['UpdatedBy'] = str(self.env['hr.employee'].sudo().search([('user_id', '=', country_record.create_uid.id)]).kw_id)

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(countryurl, headers=header, data=json.dumps(country_sync))

            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            # "id": 0,"mesg": "Name Already available","status": 1
            if country_sync['ActionCode'] == 'A':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        country_record.write({'kw_id': json_record['id']})
                        rec.write({
                            'json_data': country_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                               'new_record_log': country_sync,
                                                                               'request_params': countryurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': country_sync,
                            'status': 0,
                            'response_result': resp.json()})

                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                               'new_record_log': country_sync,
                                                                               'request_params': countryurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

                else:
                    rec.write({
                        'json_data': country_sync,
                        'status': 0,
                        'response_result': resp.json()})

                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                           'new_record_log': country_sync,
                                                                           'request_params': countryurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        rec.write({
                            'json_data': country_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                               'new_record_log': country_sync,
                                                                               'request_params': countryurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': country_sync,
                            'status': 0,
                            'response_result': resp.json()})

                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                               'new_record_log': country_sync,
                                                                               'request_params': countryurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': country_sync,
                        'status': 0,
                        'response_result': resp.json()})

                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Country Sync Data',
                                                                           'new_record_log': country_sync,
                                                                           'request_params': countryurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    # Check user Group
    @api.model
    def check_sync_country(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'

    # Create method for country
    @api.model
    def create(self, vals):
        country_record = super(kw_sync_country, self).create(vals)
        sync_data = self.env['kw_emp_sync_log'].create(
            {'model_id': 'res.country', 'rec_id': country_record.id, 'code': False, 'status': 0})
        return country_record

    # write method for country
    @api.multi
    def write(self, vals):
        country_record = super(kw_sync_country, self).write(vals)
        w_id = self.env['res.country'].sudo().search([('id', '=', self.id)])
        if w_id.write_uid.id != 1:
            sync_data = self.env['kw_emp_sync_log'].create(
                {'model_id': 'res.country', 'rec_id': w_id.id, 'code': False, 'status': 0})
        return country_record
