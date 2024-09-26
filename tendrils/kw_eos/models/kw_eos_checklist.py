# -*- coding: utf-8 -*-
from xml.dom import ValidationErr
from odoo import fields, models, api
import requests, json


class kw_eos_checklist_activity(models.Model):
    _name = 'kw_eos_checklist_activity'
    _description = "EOS Checklist Activities"

    eos_rel_id = fields.Many2one('kw_eos_checklist')
    name = fields.Char('Activity Name')
    applied = fields.Char('Applied')
    pending = fields.Char('Pending')


class kw_eos_checklist_reason(models.Model):
    _name = 'kw_eos_checklist_reason'
    _description = "EOS Checklist Reason"

    eos_rel_id = fields.Many2one('kw_eos_checklist')
    name = fields.Char('Name')
    status = fields.Char('Status')


class kw_eos_checklist(models.Model):
    _name = 'kw_eos_checklist'
    _description = 'EOS Clearance'
    _rec_name = "application_id"
    _order = 'id desc'

    @api.model
    def _ra_display_name(self):
        for record in self:
            record.display_name = 'Apply EOS'

    @api.depends('user_id')
    def _get_current_user(self):
        for res in self:
            if res.user_id.has_group('kw_employee.group_hr_ra'):
                res.is_RA = True

    display_name = fields.Char(string="Name", default="Apply EOS", compute='_ra_display_name')
    eos_apply_for = fields.Selection(string="EOS Apply for", selection=[('self', 'Self'), ('sub', 'Others')],
                                     default="self")
    application_id = fields.Many2one('kw_resignation', string="Applicant")
    applicant_id = fields.Many2one('hr.employee', string="Applicant")
    applicant_name = fields.Char(related='applicant_id.name', string="Name")
    applicant_code = fields.Char(related='applicant_id.emp_code', string="Code")

    activity_ids = fields.One2many('kw_eos_checklist_activity', 'eos_rel_id', string="Activities")
    reason_ids = fields.One2many('kw_eos_checklist_reason', 'eos_rel_id', string="Reasons")
    pending_checklist = fields.Boolean(default=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    is_RA = fields.Boolean(compute='_get_current_user')
    eos_log_ids = fields.One2many('kw_eos_checklist_log', 'eos_id', string="Checklist Details")

    @api.onchange('eos_apply_for')
    def onchange_eos_apply_for(self):
        if self.eos_apply_for == 'sub':
            employee_list = []
            employee_ids = self.env['hr.employee'].sudo().search([])
            reg_id = self.env['kw_resignation'].sudo().search(
                [('applicant_id', 'in', employee_ids.ids), ('state', '=', 'grant')])
            for reg in reg_id:
                eos_list = self.env['kw_eos_checklist'].sudo().search(
                    [('applicant_id', '=', reg.applicant_id.id), ('state', '!=', 'Rejected')])
                if not eos_list:
                    employee_list.append(reg.applicant_id.id)

            return {'domain': {'applicant_id': [('id', 'in', employee_list)]}}

    def menu_render(self):
        if (self.env.user.has_group('kw_eos.group_kw_eos_manager')
                or self.env.user.has_group('kw_eos.group_kw_eos_officer')):
            view_id = self.env.ref('kw_eos_integrations.kw_eos_checklist_view_tree').id
            form_view_id = self.env.ref('kw_eos.kw_eos_checklist_view_form').id
            return {
                'name': 'EOS Apply',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_eos_checklist',
                'view_mode': 'tree,form',
                'views': [(view_id, 'tree'), (form_view_id, 'form')],
            }
        else:
            # print("------------------------##############-------------------------------------")
            resignation_id = self.env['kw_resignation'].sudo().search(
                [('applicant_id', '=', self.env.user.employee_ids.id), ('state', '=', 'grant')]).id
            # print("resignaticon_id==", resignation_id)
            rec = self.env['kw_eos_checklist'].sudo().search(
                [('applicant_id', '=', self.env.user.employee_ids.id), ('state', '!=', 'Rejected')])
            if resignation_id:
                # rec.offboarding_type = resignation_id
                view_id = self.env.ref('kw_eos.kw_eos_checklist_view_form').id
                return {
                    'name': 'EOS Apply',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_eos_checklist',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'res_id': rec.id if rec else self.id,
                    'context': {'default_applicant_id': self.env.user.employee_ids.id,'default_offboarding_type': resignation_id},
                }
            else:
                view_id = self.env.ref('kw_eos.kw_eos_checklist_validate_wizard').id
                return {
                    'name': 'Validation Error',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_eos_checklist',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'target': 'new',
                }
                # raise ValidationErr("You can apply for EOS only when you have applied Offboarding and it is Granted.")

    # @api.model
    # def default_get(self, fields):
    #     res = super(kw_eos_checklist, self).default_get(fields)
    #     parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
    #     EOSurl = parameterurl + 'ManageEOSDetails'
    #     header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    #     userId = str(self.env.user.employee_ids.kw_id)

    #     EOSDict = {
    #     "userId": userId
    #     }
    #     resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
    #     j_data = json.dumps(resp.json())
    #     json_record = json.loads(j_data)
    #     print(json_record)
    #     if json_record.get('Userstatus') == '1':
    #         if json_record.get('retEOSActDa'):
    #             pending_status = False
    #             for actdata in json_record.get('retEOSActDa'):
    #                 if int(actdata.get('Pendings')) > 0:
    #                     pending_status = True
    #         if json_record.get('retEOSDa'):
    #             reason_status = False
    #             for resdata in json_record.get('retEOSDa'):
    #                 if resdata.get('Status') not in ["Completed","Not Decided","Not","Not Applied"]:
    #                     reason_status = True
    #         pending_checklist = False
    #         if reason_status == True or pending_status == True:
    #             pending_checklist = True

    #         if json_record.get('retEOSActDa'):
    #             activityvals=[]
    #             for rec in json_record.get('retEOSActDa'):
    #                 activityvals.append([0,0,{
    #                                 'name': rec['Activity_Name'],
    #                                 'applied': rec['Applied'],
    #                                 'pending': rec['Pendings'],
    #                             }])
    #         if json_record.get('retEOSDa'):
    #             reasonvals=[]
    #             for rec in json_record.get('retEOSDa'):
    #                 reasonvals.append([0,0,{
    #                                 'name': rec['Reason'],
    #                                 'status': rec['Status'],
    #                             }])
    #         self.env['kw_eos_log'].sudo().create({'req_data': EOSDict,'response_res':json_record,'type': 'ManageEOSDetails'})

    #         res.update({
    #                 'pending_checklist':pending_checklist,
    #                 'activity_ids':activityvals,
    #                 'reason_ids':reasonvals,
    #                })
    #     return res

    # @api.onchange('application_id')
    # def onchange_application_id(self):
    #     for res in self:
    #         res.applicant_id = res.application_id.applicant_id.id

    # @api.onchange('applicant_id')
    # def onchange_applicant(self):
    #     parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
    #     EOSurl = parameterurl + 'ManageEOSDetails'
    #     header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    #     userId = self.applicant_id.kw_id
    #     EOSDict = {
    #     "userId": userId
    #     }
    #     resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
    #     j_data = json.dumps(resp.json())
    #     json_record = json.loads(j_data)
    #     if json_record.get('Userstatus') == '1':
    #         if json_record.get('retEOSActDa'):
    #             pending_status = False
    #             for actdata in json_record.get('retEOSActDa'):
    #                 if int(actdata.get('Pendings')) > 0:
    #                     pending_status = True
    #         if json_record.get('retEOSDa'):
    #             reason_status = False
    #             for resdata in json_record.get('retEOSDa'):
    #                 if resdata.get('Status') not in ["Completed","Not Decided","Not","Not Applied"]:
    #                     reason_status = True

    #         if reason_status == True or pending_status == True:
    #             self.pending_checklist = True
    #         else:
    #             self.pending_checklist = False

    #         self.activity_ids = False
    #         self.reason_ids = False
    #         if json_record.get('retEOSActDa'):
    #             activityvals=[]
    #             for rec in json_record.get('retEOSActDa'):
    #                 activityvals.append([0,0,{
    #                                 'name': rec['Activity_Name'],
    #                                 'applied': rec['Applied'],
    #                                 'pending': rec['Pendings'],
    #                             }])
    #             self.activity_ids = activityvals
    #         if json_record.get('retEOSDa'):
    #             reasonvals=[]
    #             for rec in json_record.get('retEOSDa'):
    #                 reasonvals.append([0,0,{
    #                                 'name': rec['Reason'],
    #                                 'status': rec['Status'],
    #                             }])
    #             self.reason_ids = reasonvals
    #         self.env['kw_eos_log'].sudo().create({'req_data': EOSDict,'response_res':json_record,'type': 'ManageEOSDetails'})
