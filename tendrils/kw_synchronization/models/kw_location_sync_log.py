# *******************************************************************************************************************
#  File Name             :   kw_location_sync_log.py
#  Description           :   This model is used to inherit kw_location_master model and sync data into Kwantify 
#  Created by            :   Abhijit Swain
#  Created On            :   04-08-2020
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests


class kw_sync_location(models.Model):
    _inherit = 'kw_location_master'

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    # filter_sync_status = fields.Selection(
    #     string='Sync Status',
    #     selection=[('0', '0'), ('1', '1'), ('2', '2')])

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'kw_location_master'), ('rec_id', '=', record.id)])
            if log_record:
                status = log_record.mapped('status')
                if 0 in status:
                    record.sync_status = '1'
                    # record.write({'filter_sync_status' : '1'})
                else:
                    record.sync_status = '2'
                    # record.write({'filter_sync_status' : '2'})
            else:
                record.sync_status = '0'
                # record.write({'filter_sync_status' : '0'})

    # Create method for location
    @api.model
    def create(self, vals):
        location_record = super(kw_sync_location, self).create(vals)
        sync_data = self.env['kw_emp_sync_log'].create(
            {'model_id': 'kw_location_master', 'rec_id': location_record.id, 'code': False, 'status': 0})
        return location_record

    # write method for Location
    @api.multi
    def write(self, vals):
        location_record = super(kw_sync_location, self).write(vals)
        w_id = self.env['kw_location_master'].sudo().search([('id', '=', self.id)])
        if w_id.write_uid.id != 1:
            log_rec = self.env['kw_emp_sync_log'].sudo().search(['&', '&', ('model_id', '=', 'kw_location_master'),
                                                                 ('rec_id', '=', w_id.id), ('status', '=', 0)])
            if len(log_rec) == 0:
                sync_data = self.env['kw_emp_sync_log'].create(
                    {'model_id': 'kw_location_master', 'rec_id': w_id.id, 'code': False, 'status': 0})
        return location_record

    # Sync Location data
    @api.model
    def action_sync_location(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        location_rec = self.env['kw_emp_sync_log'].sudo().search(['&', ('model_id', '=', 'kw_location_master'),
                                                                  ('status', '=', 0)])
        location_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        locationurl = parameterurl + 'AddLocationDetails'

        for rec in location_rec:
            location_record = self.env['kw_location_master'].sudo().search([('id', '=', rec.rec_id)])
            location_sync['ActionCode'] = 'LA' if location_record.kw_id == 0 else 'LU'
            location_sync['LocationName'] = location_record.name
            location_sync['LocationID'] = str(location_record.kw_id)
            location_sync['CountryID'] = str(location_record.country_id.kw_id)
            location_sync['LocationDiff'] = '+06:30:00'
            location_sync['TimezoneId'] = '0'
            location_sync['CreatedBy'] = str(
                self.env['hr.employee'].sudo().search([('user_id', '=', location_record.create_uid.id)]).kw_id)
            location_sync['UpdatedBy'] = str(
                self.env['hr.employee'].sudo().search([('user_id', '=', location_record.create_uid.id)]).kw_id)

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(locationurl, headers=header, data=json.dumps(location_sync))

            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            # "id": 0,"mesg": "Name Already available","status": 1
            if location_sync['ActionCode'] == 'LA':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        location_record.write({'kw_id': int(json_record['id'])})
                        rec.write({
                            'json_data': location_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                               'new_record_log': location_sync,
                                                                               'request_params': locationurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': location_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                               'new_record_log': location_sync,
                                                                               'request_params': locationurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')

                else:
                    rec.write({
                        'json_data': location_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                           'new_record_log': location_sync,
                                                                           'request_params': locationurl,
                                                                           'response_result': resp.json()})
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        rec.write({
                            'json_data': location_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                               'new_record_log': location_sync,
                                                                               'request_params': locationurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': location_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                               'new_record_log': location_sync,
                                                                               'request_params': locationurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': location_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Location Master Sync Data',
                                                                           'new_record_log': location_sync,
                                                                           'request_params': locationurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    @api.model
    def check_location_group(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'
