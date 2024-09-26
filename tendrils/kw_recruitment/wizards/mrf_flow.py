# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from ast import literal_eval


class MRFholdConfirmation(models.TransientModel):
    _name = "kw.mrf.hold"
    _description = "MRF Hold"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)

    def save_message(self):
        # mail_activity = self.env['mail.activity']
        # res_model_id, res_id, _, _, _ = self.mrf_id.get_mail_activity_details()
        # activity = mail_activity.search(
        #     [('res_id', '=', res_id), ('res_model_id', '=', res_model_id), ('user_id', '=', self._uid)])
        # if activity:
        #         activity.action_feedback()
        self.mrf_id.write({'state': 'hold', 'note': self.note,'hold_user_id':self.env.user.id})
        logtable = self.env['kw_recruitment_requisition_log'].search(
            [('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'hold')],order="id desc",limit=1)
        template_obj = self.env.ref('kw_recruitment.template_for_hold_mrf')
        mrfview = self.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname
        param = self.env['ir.config_parameter'].sudo()
        to_user = literal_eval(param.get_param('kw_recruitment.rcm_head','[]'))
        tag_to = self.env['hr.employee'].browse(to_user)
        tag_to_mail = self.env['hr.employee'].browse(to_user).mapped('work_email')[0]
        cc_users = list(set(literal_eval(param.get_param('kw_recruitment.tag_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
        all_cc = set(cc_users + [self.mrf_id.create_uid.employee_ids.id])
        tag_cc_mail =','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
        # if self.mrf_id.approver_id and self.mrf_id.approver_id.user_id.id == self.env.user.id:
            # # PM --> AVP Flow
        if template_obj:
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                dbname=db_name,
                action_id=action_id,
                name=self.mrf_id.approver_id.name,
                receiver=tag_to.name,
                mailto=tag_to_mail, email_cc=tag_cc_mail).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
            self.env.user.notify_success("Mail sent successfully.")

        # elif self.mrf_id.approver_id and self.mrf_id.approver_id.user_id.id != self.env.user.id:
        #     # # PM --> AVP --> CEO Flow
        #     if template_obj:
        #         mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #             dbname=db_name,
        #             action_id=action_id,
        #             receiver=self.mrf_id.approver_id.name,
        #             name=self.env.user.name,
        #             mailto=self.mrf_id.approver_id.work_email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
        #         self.mrf_id.write({'state': 'hold', 'note': self.note,'hold_user_id':self.env.user.id})
        #         self.env.user.notify_success("Mail sent successfully.")
        # else:
        #     # # AVP --> CEO Flow (direct)
        #     if template_obj:
        #         mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #             dbname=db_name,
        #             action_id=action_id,
        #             receiver=self.mrf_id.create_uid.name,
        #             name=self.env.user.name,
        #             mailto=self.mrf_id.create_uid.email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
        #         self.mrf_id.write({'state': 'hold', 'note': self.note})
        #         self.env.user.notify_success("Mail sent successfully.")

        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MRFRcmValidation(models.TransientModel):
    _name = "kw.mrf.validate"
    _description = "MRF RCM Validation"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)

    def save_message(self):
        # print("id========",self.mrf_id.id)
        logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'draft')],order ='id desc',limit=1)
        # print('logtableeeeeeeeeee==================',logtable)
        template_obj = self.env.ref('kw_recruitment.rcm_validation_notification')
        mrfview = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname
        mrf_token = False
        if self.mrf_id.approver_id:
            mrf_token = self.env['kw_recruitment_requisition_approval'].create(
                {'mrf_id': self.mrf_id.id,
                'employee_id': self.mrf_id.approver_id.id})
        if template_obj:
            param = self.env['ir.config_parameter'].sudo()
            cc_users = list(set(literal_eval(param.get_param('kw_recruitment.rcm_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
            # ceo_id = self.env['hr.employee'].browse(set(literal_eval(param.get_param('kw_recruitment.second_level_approver_ids','[]'))))
            # print("print=====tag cc",cc_users)
            all_cc = set(cc_users)

            tag_cc = ','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
            # print("tag cc users======",tag_cc)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                receiver='TAG',
                raised_by_name=self.mrf_id.req_raised_by_id.user_id.name,
                name=self.env.user.name,
                dbname=db_name,
                token=mrf_token.access_token if mrf_token else '',
                action_id=action_id,
                mail_from = self.env.user.email,
                notify_cc=self.env.user.email,
                mailto=tag_cc).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
            data = {'state': 'approve', 'note': self.note,'approved_user_id':self.env.user.id}
            # if self.mrf_id.approver_id.id == ceo_id.id:
            #     data['forward_to_ceo'] = True
            self.mrf_id.write(data)
            self.env.user.notify_success("Mail sent successfully.")
        return {'type': 'ir.actions.act_window_close'}


class MRFForwardToCEO(models.TransientModel):
    _name = "kw.mrf.forward_to_ceo"
    _description = "MRF Forward To CEO"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)

    def save_message(self):
        logtable = self.env['kw_recruitment_requisition_log'].create({
            'mrf_id': self.mrf_id.id,
            'from_status': self.mrf_id.state,
            'to_status': 'forward',
            'approver_id': self.env.user.employee_ids.id
        })
        template_obj = self.env.ref('kw_recruitment.forward_to_ceo_notification')
        mrfview = self.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname
        mrf_token = False
        parameters = self.env['ir.config_parameter'].sudo()
        second_approver_list = self.env['hr.employee'].browse(literal_eval(parameters.get_param('kw_recruitment.second_level_approver_ids','[]')))
        if self.mrf_id.create_uid.in_first_level_employee() and second_approver_list:
            mrf_token = self.env['kw_recruitment_requisition_approval'].create(
                {'mrf_id': self.mrf_id.id,
                'employee_id': second_approver_list.id})
        if template_obj:
            param = self.env['ir.config_parameter'].sudo()
            cc_users = list(set(literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
            # print("print=====tag cc",cc_users)
            all_cc = set(cc_users + [self.mrf_id.create_uid.employee_ids.id])
            tag_cc = ','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                receiver=second_approver_list.name,
                name=self.env.user.name,
                dbname=db_name,
                token=mrf_token.access_token if mrf_token else '',
                action_id=action_id,
                mail_from = self.env.user.email,
                cc_notify=tag_cc,
                mailto=second_approver_list.work_email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
            self.mrf_id.write({'state': 'forward', 'note': self.note, 'forward_to_ceo':True})
            self.env.user.notify_success("Mail sent successfully.")

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MRFRejectConfirmation(models.TransientModel):
    _name = "kw.mrf.reject"
    _description = "MRF Reject"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note_check = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Note Check',)
    note = fields.Text('Comment', size=40)

    def save_message(self):
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
        budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(
            [('fiscalyr', '=', current_fiscal_year_id.id), ('mrf_id', '=', self.mrf_id.id),
             ('exp_year', '=', self.mrf_id.min_exp_year), ('status', '=', 'publish')])
        if budget_lines:
            budget_lines.write({
                'mrf_id': False,
            })
        if self.note_check == 'yes':
            self.mrf_id.write({'state': 'reject', 'note': self.note})
            mrfview = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
            action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
            db_name = self._cr.dbname
            param = self.env['ir.config_parameter'].sudo()
            cc_users = list(set(literal_eval(param.get_param('kw_recruitment.rcm_head','[]')) + literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
            all_cc = set(cc_users)
            tag_cc = ','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
            # if self.mrf_id.approver_id and self.mrf_id.approver_id.user_id.id == self.env.user.id:
            # #HOD  --> Decline Flow
            self.mrf_id.write({'state': 'reject', 'note': self.note})
            logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'reject')], order="id desc", limit=1)
            template_obj = self.env.ref('kw_recruitment.template_for_reject_first_mrf')
            if template_obj:
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    receiver="TAG",
                    name='RCM',
                    mailto=tag_cc,
                    email_cc=self.env.user.email,).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
                self.env.user.notify_success("Mail sent successfully.")

            # else:
            #     # # RCM Head --> Decline Flow (direct)
            #     template_obj = self.env.ref('kw_recruitment.template_for_reject_first_mrf')
            #     self.mrf_id.write({'state': 'reject', 'note': self.note})
            #     logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'reject')],order='id desc',limit=1)
            #     dept_head =self.mrf_id.approver_id.id
            #     all_cc = set(to_user + [self.mrf_id.approver_id.id])
            #     email_cc =','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
            #     if template_obj:
            #         mail = self.env['mail.template'].browse(template_obj.id).with_context(
            #             dbname=db_name,
            #             action_id=action_id,
            #             receiver=self.mrf_id.create_uid.name,
            #             name=self.env.user.name,
            #             mailto=self.mrf_id.create_uid.email,
            #             email_cc=email_cc,).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
            self.env.user.notify_success("MRF Rejected successfully.")
        elif self.note_check == 'no':
            pass
        else:
            raise ValidationError('Please select any one option (Yes/No).')
                
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MRFReviseConfirmation(models.TransientModel):
    _name = "kw.mrf.revise"
    _description = "MRF Revise"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)

    def save_message(self):
        # mail_activity = self.env['mail.activity']
        # res_model_id, res_id, _, _, _= self.mrf_id.get_mail_activity_details()
        # activity = mail_activity.search(
        #     [('res_id', '=', res_id), ('res_model_id', '=', res_model_id), ('user_id', '=', self._uid)])
        # if activity:
        #         activity.action_feedback()
        mrfview = self.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname
        if self.mrf_id.approver_id and self.mrf_id.approver_id.user_id.id == self.env.user.id:
            # # PM --> AVP Flow
            template_obj = self.env.ref('kw_recruitment.template_for_revise_mrf')
            if template_obj:
                self.mrf_id.write({'state': 'draft', 'note': self.note})
                logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'draft')],order="id desc",limit=1)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    receiver=self.mrf_id.create_uid.name,
                    name=self.mrf_id.approver_id.name,
                    mailto=self.mrf_id.create_uid.email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
                self.env.user.notify_success("Mail sent successfully.")

        elif self.mrf_id.approver_id and self.mrf_id.approver_id.user_id.id != self.env.user.id:
            # # PM --> AVP --> CEO Flow
            template_obj = self.env.ref('kw_recruitment.template_for_revise_mrf')
            if template_obj:
                self.mrf_id.write({'state': 'draft', 'note': self.note})
                logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'draft')])
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    receiver=self.mrf_id.approver_id.name,
                    name=self.env.user.name,
                    mailto=self.mrf_id.approver_id.work_email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
                self.env.user.notify_success("Mail sent successfully.")
        else:
            # # AVP --> CEO Flow (direct)
            template_obj = self.env.ref('kw_recruitment.template_for_revise_mrf')
            if template_obj:
                self.mrf_id.write({'state': 'draft', 'note': self.note})
                logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'draft')])
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    receiver=self.mrf_id.create_uid.name,
                    name=self.env.user.name,
                    mailto=self.mrf_id.create_uid.email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
                self.env.user.notify_success("Mail sent successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MRFapproveConfirmation(models.TransientModel):
    _name = "kw.mrf.approve"
    _description = "MRF Approve"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)
    check_salary = fields.Boolean('Check Salary')
    extra_load_on_budget = fields.Integer('Extra Load On Budget')

    def save_message(self):
        ## Approve & Forward
        # mail_activity = self.env['mail.activity']
        mrfview = self.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname

        Parameters = self.env['ir.config_parameter'].sudo()
        sec_approver_list = Parameters.get_param('kw_recruitment.second_level_approver_ids')
        coverted_sec = sec_approver_list.strip('][').split(', ')
        if coverted_sec:
            emps = self.env['hr.employee'].search([('id', 'in', [int(i) for i in coverted_sec])])
            self.mrf_id.write({'state': 'forward',
                               'last_approver_ids': [(6, 0, emps.ids)],
                               'forwared_note': self.note,
                               'forwarded_dt': datetime.date.today()})
            # mail_activity = self.env['mail.activity']
            # res_model_id, res_id, _, _, _ = self.mrf_id.get_mail_activity_details()
            # activity = mail_activity.search(
            #     [('res_id', '=', res_id), ('res_model_id', '=', res_model_id), ('user_id', '=', self._uid)])
            # if activity:
            #     activity.action_feedback()  # makes done activity
            logtable = self.env['kw_recruitment_requisition_log'].search(
                [('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'forward')], order="id desc", limit=1)
            template_obj = self.env.ref('kw_recruitment.approve_forward_request_template')
            approvers = self.env['hr.employee'].search([('id', 'in', [int(rec) for rec in coverted_sec])])
            # approvers = self.env['hr.employee'].search([('id', 'in', jobs.ids)])
            if approvers:
                for approver in approvers:
                    # res_model_id, res_id, date_deadline, note, activity_type_id = self.mrf_id.get_mail_activity_details()
                    # if approver.user_id:
                    #     mail_activity.create({
                    #         'res_model_id': res_model_id,
                    #         'activity_type_id': activity_type_id,
                    #         'res_id': res_id,
                    #         'date_deadline': date_deadline,
                    #         'user_id': approver.user_id.id,
                    #         'note': note})

                    # Generate Token
                    MRF_token = self.env['kw_recruitment_requisition_approval'].create(
                        {'mrf_id': self.mrf_id.id, 'employee_id': approver.id})
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                        dbname=db_name,
                        action_id=action_id,
                        token=MRF_token.access_token,
                        approver=approver.name,
                        mailto=approver.work_email).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=True)
                    self.env.user.notify_success("Mail sent successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class MRFapproveFinalConfirmation(models.TransientModel):
    _name = "kw.mrf.final.approve"
    _description = "MRF Approve"

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
    note = fields.Text('Comment', size=40)
    check_salary = fields.Boolean('Check Salary')
    extra_load_on_budget = fields.Integer('Extra Load On Budget')

    def save_message(self):
        # import pdb
        # pdb.set_trace()
        # if self._context.get('manpower'):
        self.mrf_id.write({'state': 'approve',
                           'approved_user_id': self.env.user.id,
                           'approved_note': self.note,
                           'approved_dt': datetime.date.today()})
        logtable = self.env['kw_recruitment_requisition_log'].search(
            [('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'approve')], order="id desc", limit=1)
        # mrfview = self.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
        # action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        # db_name = self._cr.dbname
        param = self.env['ir.config_parameter'].sudo()
        to_user = literal_eval(param.get_param('kw_recruitment.tag_head','[]'))
        tag_to = self.env['hr.employee'].browse(to_user).mapped('work_email')
        cc_users = list(set(literal_eval(param.get_param('kw_recruitment.approval_ids','[]')) + literal_eval(param.get_param('kw_recruitment.rcm_head','[]')) + literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))))
        all_cc = set(cc_users + [self.mrf_id.create_uid.employee_ids.id])
        tag_cc = ','.join(self.env['hr.employee'].browse(all_cc).mapped('work_email'))
        if self.mrf_id.approver_id:
            template_obj = self.env.ref('kw_recruitment.action_approval_final_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                # dbname=db_name,
                # action_id=action_id,
                email_to=tag_to[0],
                email_cc=tag_cc,
                approvedby=self.env.user.name,
                signuser=self.mrf_id.req_raised_by_id.user_id.signature,
                signusername=self.mrf_id.req_raised_by_id.user_id.name).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
            
        self.env.user.notify_success("Mail sent successfully.")
        return {'type': 'ir.actions.act_window_close'}
        
        # else:
        # ## Final Approval
        #     self.mrf_id.write({'state': 'approve',
        #                     'approved_user_id': self.env.user.id,
        #                     'approved_note': self.note,
        #                     'approved_dt': datetime.date.today()})
        #     logtable = self.env['kw_recruitment_requisition_log'].search(
        #         [('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'approve')], order="id desc", limit=1)
        #     mrfview = self.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
        #     action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        #     db_name = self._cr.dbname
        #     # Mark done activity if found for current user
        #     # mail_activity = self.env['mail.activity']
        #     # res_model_id, res_id, _, _, _ = self.mrf_id.get_mail_activity_details()
        #     # activity = mail_activity.search(
        #     #     [('res_id', '=', res_id), ('res_model_id', '=', res_model_id), ('user_id', '=', self._uid)])
        #     # if activity:
        #     #         activity.action_feedback()  # makes done activity
        #     if self.mrf_id.approver_id:
        #         template_obj = self.env.ref('kw_recruitment.action_approval_final_template')
        #     else:
        #         template_obj = self.env.ref('kw_recruitment.action_approval_template')
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #                 dbname=db_name,
        #                 action_id=action_id,
        #                 approvedby = self.env.user.name,
        #                 signuser = self.mrf_id.req_raised_by_id.user_id.signature,
        #                 signusername = self.mrf_id.req_raised_by_id.user_id.name).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
        #     # template = self.env.ref('kw_recruitment.acknowledgement_template')
        #     # template.with_context(
        #     #             dbname=db_name,
        #     #             action_id=action_id,
        #     #             mailfrom=self.mrf_id.forwarder_id.work_email if self.mrf_id.forwarder_id else self.mrf_id.req_raised_by_id.work_email,
        #     #             mailto=self.env.user.employee_ids.work_email,
        #     #             approver_name=self.env.user.employee_ids.name,
        #     #             signuser = self.mrf_id.forwarder_id.user_id.signature if self.mrf_id.forwarder_id else self.mrf_id.req_raised_by_id.user_id.signature,
        #     #             signusername = self.mrf_id.req_raised_by_id.user_id.name if self.mrf_id.forwarder_id else self.mrf_id.req_raised_by_id.user_id.name).send_mail(logtable.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        #     self.env.user.notify_success("Mail sent successfully.")
        #     return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

# class MRFEditedConfirmation(models.TransientModel):
#     _name = "kw.mrf.edited"
#     _description = "MRF Edited"

#     mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF')
#     note = fields.Text('Comment', size=40)

#     def save_message(self):
        
#         ## Mrf edited after approval
#         self.mrf_id.write({'state': 'approve','approved_user_id':self.env.user.id,'approved_note':self.note,'approved_dt':datetime.date.today()})
#         logtable = self.env['kw_recruitment_requisition_log'].search(
#             [('mrf_id', '=', self.mrf_id.id), ('to_status', '=', 'approve')],order="id desc",limit=1)
#         mrfview = self.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
#         action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
#         db_name = self._cr.dbname
      
#         if self.mrf_id.approver_id:
#             template_obj = self.env.ref('kw_recruitment.template_for_edited_mrf')
#         else:
#             template_obj = self.env.ref('kw_recruitment.action_approval_template')
#         mail = self.env['mail.template'].browse(template_obj.id).with_context(
#                     dbname=db_name,
#                     action_id=action_id,
#                     approvedby = self.env.user.name,
#                     signuser = self.mrf_id.req_raised_by_id.user_id.signature,
#                     signusername = self.mrf_id.req_raised_by_id.user_id.name).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=True)
        
#         self.env.user.notify_success("Mail sent successfully.")
#         return {'type': 'ir.actions.act_window_close'}

#     def cancel(self):
#         return {'type': 'ir.actions.act_window_close'}
