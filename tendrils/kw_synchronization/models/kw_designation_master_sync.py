# *******************************************************************************************************************
#  File Name             :   kw_designation_master_sync.py
#  Description           :   This model is used to sync data to Kwantify and create record in kw_emp_sync_log model. 
#  Created by            :   Asish ku Nayak
#  Created On            :   06-08-2020
#  Modified by           :   
#  Modified On           :   
#  Modification History  :   
# *******************************************************************************************************************


from odoo import models, fields, api
import json, requests


class kw_sync_designation(models.Model):
    _inherit = 'hr.job'

    sync_status = fields.Selection(
        string='Sync Status',
        selection=[('0', 'Not Required'), ('1', 'Pending'), ('2', 'Done')], compute='_check_sync_status')

    @api.multi
    def _check_sync_status(self):
        for record in self:
            log_record = self.env['kw_emp_sync_log'].sudo().search(
                ['&', ('model_id', '=', 'hr.job'), ('rec_id', '=', record.id)])
            if log_record:
                status = log_record.mapped('status')
                if 0 in status:
                    record.sync_status = '1'
                else:
                    record.sync_status = '2'
            else:
                record.sync_status = '0'

    # For designation Synchronization
    @api.model
    def action_sync_designation(self):
        mail_id_rec = self.env['res.config.settings'].sudo().search([])
        last_mail_id = mail_id_rec[-1].kw_sync_error_log_mail if mail_id_rec else 'girish.mohanta@csm.tech'
        # Mail sent
        template_id = self.env.ref('kw_synchronization.kw_failed_api_template')

        log_rec = self.env['kw_emp_sync_log'].sudo().search(['&', ('model_id', '=', 'hr.job'), ('status', '=', 0)])
        deg_sync = {}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kw_employee_sync')
        degurl = parameterurl + 'AddDesignationDetails'
        for rec in log_rec:
            deg_record = self.env['hr.job'].sudo().search([('id', '=', rec.rec_id)])
            deg_sync['ActionCode'] = 'DA' if deg_record.kw_id == 0 else 'DU'
            deg_sync['DesigName'] = deg_record.name
            deg_sync['DesigId'] = str(deg_record.kw_id)
            deg_sync['AliasName'] = deg_record.name
            deg_sync['UserType'] = "P"
            deg_sync['LocId'] = "All"
            deg_sync['CreatedBy'] = str(224)
            # str(self.env['hr.employee'].sudo().search([('user_id', '=', deg_record.create_uid.id)]).kw_id)
            deg_sync['UpdatedBy'] = str(224)
            # str(self.env['hr.employee'].sudo().search([('user_id', '=', deg_record.create_uid.id)]).kw_id)

            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.post(degurl, headers=header, data=json.dumps(deg_sync))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            if deg_sync['ActionCode'] == 'DA':
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        deg_record.write({'kw_id': json_record['id']})
                        rec.write({
                            'json_data': deg_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                               'new_record_log': deg_sync,
                                                                               'request_params': degurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': deg_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                               'new_record_log': deg_sync,
                                                                               'request_params': degurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': deg_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                           'new_record_log': deg_sync,
                                                                           'request_params': degurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')
            else:
                if resp.status_code == 200:
                    if json_record['status'] == 1:
                        rec.write({
                            'json_data': deg_sync,
                            'status': 1,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                               'new_record_log': deg_sync,
                                                                               'request_params': degurl,
                                                                               'response_result': resp.json()})
                    else:
                        rec.write({
                            'json_data': deg_sync,
                            'status': 0,
                            'response_result': resp.json()})
                        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                               'new_record_log': deg_sync,
                                                                               'request_params': degurl,
                                                                               'response_result': resp.json()})
                        template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                                 response_result=resp.json()).send_mail(rec.id)
                        self.env.user.notify_success(message='Mail sent successfully')
                else:
                    rec.write({
                        'json_data': deg_sync,
                        'status': 0,
                        'response_result': resp.json()})
                    self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Designation Sync Data',
                                                                           'new_record_log': deg_sync,
                                                                           'request_params': degurl,
                                                                           'response_result': resp.json()})
                    template_id.with_context(mail_id=last_mail_id, model_id=rec.model_id, record_id=rec.rec_id,
                                             response_result=resp.json()).send_mail(rec.id)
                    self.env.user.notify_success(message='Mail sent successfully')

    @api.model
    def check_designation_group(self):
        u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            return '1'

    # Create method for designation .....
    @api.model
    def create(self, vals):
        deg_record = super(kw_sync_designation, self).create(vals)
        log_rec = self.env['kw_emp_sync_log'].sudo().search(['&', '&', ('model_id', '=', 'hr.job'),
                                                             ('rec_id', '=', deg_record.id), ('status', '=', 0)])
        if len(log_rec) == 0:
            sync_data = self.env['kw_emp_sync_log'].create(
                {'model_id': 'hr.job', 'rec_id': deg_record.id, 'code': False, 'status': 0})
        return deg_record

# write method for designation ......
# @api.multi
# def write(self, vals):
#     deg_record = super(kw_sync_designation, self).write(vals)
#     w_id = self.env['hr.job'].sudo().search([('id','=',self.id)])
#     if w_id.write_uid.id != 1:
#         log_rec = self.env['kw_emp_sync_log'].sudo().search(['&','&',('model_id','=','hr.job'),
#         ('rec_id','=',w_id.id),('status','=',0)])
#         if len(log_rec) == 0:
#             sync_data = self.env['kw_emp_sync_log'].create({'model_id':'hr.job','rec_id':w_id.id,'code':False,'status':0})
#     return deg_record
