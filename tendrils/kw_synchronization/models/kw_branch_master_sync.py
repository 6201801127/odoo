# *******************************************************************************************************************
#  File Name             :   kw_branch_master_sync.py
#  Description           :   This model is used to inherit branch model and sync data into Kwantify 
#  Created by            :   Asish ku Nayak
#  Created On            :   11-08-2020
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests


class kw_res_branch(models.Model):
    _inherit = 'res.company'

    kw_id = fields.Integer(string='Kw Id')


class kw_res_branch(models.Model):
    _inherit = 'kw_res_branch'

    # For Branch Synchronization
    @api.model
    def action_sync_branch(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        branch_rec = self.env['kw_emp_sync_log'].sudo().search(['&', ('model_id', '=', 'kw_res_branch'), ('status', '=', 0)])
        branch_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        branchurl = parameterurl + 'AddOfficeUnitDetails'
        for rec in branch_rec:
            branch_record = self.env['kw_res_branch'].sudo().search([('id', '=', rec.rec_id)])
            branch_sync['ActionCode'] = 'OUA' if branch_record.kw_id == 0 else 'OUU'
            branch_sync['OficId'] = str(branch_record.kw_id)
            branch_sync['CompanyName'] = branch_record.company_id.name
            branch_sync['LocId'] = str(branch_record.location.kw_id)
            branch_sync['OficAdd'] = branch_record.address
            branch_sync['OficTeleno1'] = str(branch_record.telephone_no)
            branch_sync['OficTeleno2'] = ""
            branch_sync['OficTeleno3'] = ""
            branch_sync['OficTeleno4'] = ""
            branch_sync['OficEmail'] = branch_record.email
            branch_sync['OficURL'] = branch_record.website
            branch_sync['OficFax'] = branch_record.fax
            branch_sync['OficProfile'] = branch_record.name
            branch_sync['OficPrefix'] = "05"
            branch_sync['CompanyId'] = branch_record.company_id.kw_id
            branch_sync['OficLatitude'] = ""
            branch_sync['OficLongitude'] = ""
            branch_sync['CreatedBy'] = str(self.env['hr.employee'].sudo().search([('user_id', '=', branch_record.create_uid.id)]).kw_id)
            branch_sync['UpdatedBy'] = str(self.env['hr.employee'].sudo().search([('user_id', '=', branch_record.create_uid.id)]).kw_id)

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(branchurl, headers=header, data=json.dumps(branch_sync))

            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            if branch_sync['ActionCode'] == 'OUA':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        branch_record.write({'kw_id': int(json_record['id'])})
                        rec.write({
                            'json_data': branch_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                               'new_record_log': branch_sync,
                                                                               'request_params': branchurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': branch_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                               'new_record_log': branch_sync,
                                                                               'request_params': branchurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': branch_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                           'new_record_log': branch_sync,
                                                                           'request_params': branchurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        rec.write({
                            'json_data': branch_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                               'new_record_log': branch_sync,
                                                                               'request_params': branchurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': branch_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                               'new_record_log': branch_sync,
                                                                               'request_params': branchurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': branch_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employee Category Sync Data',
                                                                           'new_record_log': branch_sync,
                                                                           'request_params': branchurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    @api.model
    def check_branch_group(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'

    # Create method for Branch master
    @api.model
    def create(self, vals):
        branch_record = super(kw_res_branch, self).create(vals)
        sync_data = self.env['kw_emp_sync_log'].create(
            {'model_id': 'kw_res_branch', 'rec_id': branch_record.id, 'code': False, 'status': 0})
        return branch_record

    # write method for Branch master
    @api.multi
    def write(self, vals):
        branch_record = super(kw_res_branch, self).write(vals)
        w_id = self.env['kw_res_branch'].sudo().search([('id', '=', self.id)])
        if w_id.write_uid.id != 1:
            log_rec = self.env['kw_emp_sync_log'].sudo().search(['&', '&', ('model_id', '=', 'kw_res_branch'),
                                                                 ('rec_id', '=', w_id.id), ('status', '=', 0)])
            if len(log_rec) == 0:
                sync_data = self.env['kw_emp_sync_log'].create(
                    {'model_id': 'kw_res_branch', 'rec_id': w_id.id, 'code': False, 'status': 0})
        return branch_record
