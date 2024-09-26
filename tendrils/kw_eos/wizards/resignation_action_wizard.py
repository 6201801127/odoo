# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import json
import requests
import calendar
from ast import literal_eval


class ForwardWizard(models.TransientModel):
    _name = "kw_resignation_forward_wizard"
    _description = "kw_resignation_forward_wizard"
    _order = 'id'

    @api.multi
    def _forward_to_emp(self):
        emp_rec = self.env['hr.employee'].sudo().search([]) - self.env.user.employee_ids
        reg_id = self._context.get('default_resignation_id')
        reg_rec = self.env['kw_resignation'].sudo().search([('id', '=', reg_id)])
        user_type = emp_rec - reg_rec.applicant_id
        return [('id', 'in', user_type.ids)]

    resignation_id = fields.Many2one('kw_resignation', string="Resignation Id")
    forward_to = fields.Many2one('hr.employee', string="User", domain=_forward_to_emp)
    forward_reason = fields.Text(string="Forward Reason")

    def save_inform(self):
        # import pdb
        # pdb.set_trace()
        # if self.resignation_id:
        #     self.resignation_id.sudo().write({
        #         'forward_by': self.env.user.employee_ids.id,
        #         'remark': self.forward_reason,
        #         'state': 'forward',
        #         # 'forward_to': self.forward_to.id,
        #     })
        resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                       limit=1)
        if resignation_log:
            # print("resignation log====================",resignation_log)
            # for reg in resignation_log:
            self.env['kw_resignation_log'].create({
                'applicant_id': self.env.user.employee_ids.id,
                # 'date': self.resignation_id.effective_form,
                'state': self.resignation_id.state,
                'remark': self.forward_reason,
                'last_working_date': self.resignation_id.last_working_date,
                'reg_id': self.resignation_id.id,
            })
        if self.env.context.get('cancel_request'):
            template_obj = self.env.ref('kw_eos.rl_forward_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                forwardby=self.env.user.employee_ids.name, emailf=self.env.user.employee_ids.work_email,
                emialt=self.forward_to.work_email).send_mail(self.resignation_id.id,
                                                             notif_layout='kwantify_theme.csm_mail_notification_light',
                                                             force_send=False)
            self.env.user.notify_success("Cancellation Request forwarded successfully.")
        else:
            #  Mail to Forwarded User
            kt_required = 'Yes' if self.resignation_id.kt_required == 'Yes' else 'No'
            template_obj = self.env.ref('kw_eos.resignation_forward_mail_template')
            mail_cc = self.resignation_id.get_cc(dept_head=True, deg_group=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                forwardby=self.env.user.employee_ids.name,
                emailf=self.env.user.employee_ids.work_email,
                emialt=self.forward_to.work_email,
                mail_cc=mail_cc,
                emialtname=self.forward_to.name,
                applicant_name=self.resignation_id.applicant_id.name,
                applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                remark=self.forward_reason,
                effective_from=datetime.strptime(str(self.resignation_id.effective_form), "%Y-%m-%d").strftime(
                    "%d-%b-%Y"),
                last_working_date=datetime.strptime(str(self.resignation_id.last_working_date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y"),
                reason=self.resignation_id.reason,
                reg_type=self.resignation_id.reg_type.name,
                offboarding_type = self.resignation_id.offboarding_type.name,
                write_date=datetime.strptime(str(self.resignation_id.write_date),
                                             "%Y-%m-%d %H:%M:%S.%f").date().strftime("%d-%b-%Y"),
                kt_required=kt_required,
                department_id=self.resignation_id.department_id.name,
                division=self.resignation_id.division.name,
                section=self.resignation_id.section.name,
                practise=self.resignation_id.practise.name,
                job_id=self.resignation_id.job_id.name,
                branch_alias=self.resignation_id.base_branch_id.alias,
                date_of_joining=datetime.strptime(str(self.resignation_id.date_of_joining), "%Y-%m-%d").strftime(
                    "%d-%b-%Y"),
            ).send_mail(self.resignation_id.resignation_ids.ids[0],
                        notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            template_obj = self.env.ref('kw_eos.resignation_forward_user_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                forwardby=self.env.user.employee_ids.name,
                emailf=self.env.user.employee_ids.work_email,
                emialt=self.forward_to.work_email,
                emialtname=self.forward_to.name,
                applicant_email=self.resignation_id.applicant_id.work_email,
                applicant_name=self.resignation_id.applicant_id.name,
                remark=self.forward_reason,
                effective_from=datetime.strptime(str(self.resignation_id.effective_form), "%Y-%m-%d").strftime(
                    "%d-%b-%Y"),
                last_working_date=datetime.strptime(str(self.resignation_id.last_working_date), "%Y-%m-%d").strftime(
                    "%d-%b-%Y"),
                reason=self.resignation_id.reason,
                reg_type=self.resignation_id.reg_type.name,
                offboarding_type = self.resignation_id.offboarding_type.name,
                write_date=datetime.strptime(str(self.resignation_id.write_date),
                                             "%Y-%m-%d %H:%M:%S.%f").date().strftime("%d-%b-%Y"),
                kt_required=kt_required, ).send_mail(self.resignation_id.resignation_ids.ids[0],
                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
                                                     force_send=False)
            self.env.user.notify_success("Resignation forwarded successfully.")
            
            if self.resignation_id:
                self.resignation_id.sudo().write({
                    'forward_by': self.env.user.employee_ids.id,
                    'remark': self.forward_reason,
                    'state': 'forward',
                    'forward_to': self.forward_to.id,
                })

            action_id = self.env.ref('kw_eos.resignation_action').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class RemarkWizard(models.TransientModel):
    _name = "kw_resignation_remark_wizard"
    _description = "kw_resignation_remark_wizard"
    _order = 'id'

    resignation_id = fields.Many2one('kw_resignation', string="Ref")
    remark = fields.Text('Remarks')

    def save(self):
        # print("reject wizard called=================")
        # import pdb
        # pdb.set_trace()
        # print("data===================================",self.resignation_id.sudo())
        if self.env.context.get('reject') or self.env.context.get('dept_head_reject'):
            self.resignation_id.sudo().write({
                'state': 'reject',
                'remark': self.remark,
                'action_to_be_taken_by': False
            })
            #Making notice period and resignation reason value blank in employee if resignation is rejected  
            notice_period_employee = self.env['hr.employee'].sudo().search([('id','=',self.resignation_id.applicant_id.id)])
            if notice_period_employee:
                notice_period_employee.write({
                    'in_noticeperiod': False,
                    'resignation_reason': False,
                })
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            # self.resignation_id.applicant_id.sudo().resignation_aplied = False     #do
            if resignation_log:
                self.env['kw_resignation_log'].create({
                    'applicant_id': self.resignation_id.applicant_id.id,
                    'date': self.resignation_id.effective_form,
                    'state': self.resignation_id.state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.last_working_date,
                    'reg_id': self.resignation_id.id,
                })

            template_obj = self.env.ref('kw_eos.resignation_reject_mail_template')
            email_cc = self.resignation_id.get_cc(deg_group=True, dept_head=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(get_cc=email_cc,
                                                                                  actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email,
                                                                                  forwardby=self.env.user.employee_ids.name,
                                                                                  applicant_name=self.resignation_id.applicant_id.name,
                                                                                  create_date=datetime.strptime(
                                                                                      str(self.resignation_id.create_date),
                                                                                      "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                      "%d-%b-%Y"),
                                                                                  reason=self.resignation_id.reason,
                                                                                  reg_type=self.resignation_id.reg_type.name,
                                                                                  offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                  effective_form=datetime.strptime(
                                                                                      str(self.resignation_id.effective_form),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.resignation_id.last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  remark=self.remark,
                                                                                  ).send_mail(resignation_log.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id

            template_obj = self.env.ref('kw_eos.resignation_reject_hr_mail_template')
            email_to = self.resignation_id.get_cc(deg_group=True, ra=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(email_to=email_to,
                                                                                  actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email,
                                                                                  applicant_name=self.resignation_id.applicant_id.name,
                                                                                  applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                  remark=self.remark,
                                                                                  effective_from=datetime.strptime(
                                                                                      str(self.resignation_id.effective_form),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.resignation_id.last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  reason=self.resignation_id.reason,
                                                                                  reg_type=self.resignation_id.reg_type.name,
                                                                                  offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                  write_date=datetime.strptime(
                                                                                      str(self.resignation_id.write_date),
                                                                                      "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                      "%d-%b-%Y"),
                                                                                  kt_required='Yes' if self.resignation_id.kt_required == 'yes' else 'No',
                                                                                  department_id=self.resignation_id.department_id.name,
                                                                                  division=self.resignation_id.division.name,
                                                                                  section=self.resignation_id.section.name,
                                                                                  practise=self.resignation_id.practise.name,
                                                                                  job_id=self.resignation_id.job_id.name,
                                                                                  branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                  date_of_joining=datetime.strptime(
                                                                                      str(self.resignation_id.date_of_joining),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),

                                                                                  ).send_mail(
                resignation_log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

        # elif self.env.context.get('termination'):
        #     self.resignation_id.sudo().write({
        #         'state':'grant',
        #         'action_to_be_taken_by':False,
        #     })
        #     template_obj = self.env.ref('kw_eos.termination_mail_template')
        #     email_cc = self.resignation_id.get_cc(dept_head=True,resource_head=True)
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #     email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
        #     self.env.user.notify_success("Terminated successfully.")

        # elif self.env.context.get('termination_reject'):
        #     self.resignation_id.sudo().write({
        #         'state':'reject',
        #         'action_to_be_taken_by':False,
        #     })
        #     self.env.user.notify_success("Termination Rejected.")

        # elif self.env.context.get('demise'):
        #     self.resignation_id.sudo().write({
        #         'state':'grant',
        #         'action_to_be_taken_by':False,
        #     })
        #     template_obj = self.env.ref('kw_eos.demise_mail_template')
        #     email_cc = self.resignation_id.get_cc(dept_head=True,resource_head=True,ceo=True,hrd=True)
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #     email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
        #     self.env.user.notify_success("Demise Mail sent successfully.")

        # elif self.env.context.get('demise_reject'):
        #     self.resignation_id.sudo().write({
        #         'state':'reject',
        #         'action_to_be_taken_by':False,
        #     })
        #     self.env.user.notify_success("Demise Rejected.")

        elif self.env.context.get('ra_approve'):
            if self.resignation_id.applicant_id.id == self.resignation_id.applicant_id.department_id.manager_id.id or self.resignation_id.applicant_id.id == self.resignation_id.applicant_id.sbu_master_id.representative_id.id:
                self.resignation_id.sudo().write({
                'state': 'grant',
                'remark': self.remark,
                'dept_manager_id': self.resignation_id.user_id.employee_ids.department_id.manager_id.id,
                'forward_to': False,
                })
                """ eos api called to fetch asset data """
                assetdata = self.resignation_id.sudo().get_asset_data()
                advances_data = False
                petty_cash_data = False
                advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                if not advance_checklist:
                    advances_data = self.resignation_id.sudo().get_advance_details(self.resignation_id.sudo().applicant_id)
                    petty_cash_data = self.resignation_id.sudo().get_petty_cash_details(self.resignation_id.sudo().applicant_id).mapped('advance_amt')
                    # print("petty cash data==========================",petty_cash_data)
                """ api end """
                template_obj = self.env.ref('kw_eos.resignation_grant_mail_template')
                email_to = self.resignation_id.sudo().get_cc(deg_group=True, hrd=True, dept_head=True,account=True, it=True, admin=True,
                                                    upper_ra=True, ra=True)
                
                tour_clearance = self.resignation_id.sudo().tour_clearance if self.resignation_id.sudo().tour_clearance else 'No tour settlement is pending'
                sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
                petty_cash_clearance = sum(petty_cash_data) if petty_cash_data else 'NIL'
                # print("sum of petty cash=========================",petty_cash_clearance)
                asset_clearance = len(assetdata) if assetdata else 'NIL'
                mail = self.env['mail.template'].browse(template_obj.id).with_context(email_to=email_to,
                                                                                    remark=self.remark,
                                                                                    applicant_name=self.resignation_id.sudo().applicant_id.name,
                                                                                    applicant_emp_code=self.resignation_id.sudo().applicant_id.emp_code,
                                                                                    actionby=self.env.user.name,
                                                                                    actionby_code =self.env.user.employee_ids.emp_code,
                                                                                    emailfrom=self.env.user.employee_ids.work_email,
                                                                                    tour_clearance=tour_clearance,
                                                                                    sal_adv_clearance=sal_adv_clearance,
                                                                                    petty_cash_clearance=petty_cash_clearance,
                                                                                    assetdata=assetdata,
                                                                                    asset_clearance=asset_clearance,
                                                                                    write_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().write_date),
                                                                                        "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                        "%d-%b-%Y"),
                                                                                    reason=self.resignation_id.sudo().reason,
                                                                                    reg_type=self.resignation_id.sudo().reg_type.name,
                                                                                    offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                    branch_alias=self.resignation_id.sudo().base_branch_id.alias,
                                                                                    kt_required='Yes' if self.resignation_id.sudo().kt_required == 'yes' else 'NO',
                                                                                    effective_form=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().effective_form),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    last_working_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().last_working_date),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    department_id=self.resignation_id.sudo().department_id.name,
                                                                                    division=self.resignation_id.sudo().division.name,
                                                                                    section=self.resignation_id.sudo().section.name,
                                                                                    practise=self.resignation_id.sudo().practise.name,
                                                                                    job_id=self.resignation_id.sudo().job_id.name,
                                                                                    date_of_joining=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().date_of_joining),
                                                                                        "%Y-%m-%d").strftime(
                                                                                        "%d-%b-%Y")).send_mail(
                    self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)

                template_obj = self.env.ref('kw_eos.resignation_grant_user_mail_template')
                users_data = self.env['res.users'].sudo().search([])
                rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
                rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
                mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                    actionby_code =self.env.user.employee_ids.emp_code,
                                                                                    email_to=self.resignation_id.sudo().applicant_id.work_email,
                                                                                    remark=self.remark,
                                                                                    cc = rcm_work_email,
                                                                                    applicant_name=self.resignation_id.sudo().applicant_id.name,
                                                                                    applicant_emp_code=self.resignation_id.sudo().applicant_id.emp_code,
                                                                                    emailfrom=self.env.user.employee_ids.work_email,
                                                                                    write_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().write_date),
                                                                                        "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                        "%d-%b-%Y"),
                                                                                    reason=self.resignation_id.sudo().reason,
                                                                                    reg_type=self.resignation_id.sudo().reg_type.name,
                                                                                    offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                    kt_required='Yes' if self.resignation_id.sudo().kt_required == 'yes' else 'NO',
                                                                                    effective_form=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().effective_form),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    last_working_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().last_working_date),
                                                                                        "%Y-%m-%d").strftime(
                                                                                        "%d-%b-%Y"), ).send_mail(
                    self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)
                resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                            limit=1)
                if resignation_log:
                    self.env['kw_resignation_log'].sudo().create({
                        'applicant_id': self.env.user.employee_ids.id,
                        'date': self.resignation_id.sudo().effective_form,
                        'state': self.resignation_id.sudo().state,
                        'remark': self.remark,
                        'last_working_date': self.resignation_id.sudo().last_working_date,
                        'reg_id': self.resignation_id.sudo().id,
                    })

                self.env.user.notify_success("Resignation Granted successfully.")
                action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
             
            else:  
                self.resignation_id.sudo().write({
                    'state': 'confirm',
                    'remark': self.remark,
                    'dept_manager_id': self.resignation_id.user_id.employee_ids.department_id.manager_id.id,
                    'forward_to': False,
                })
            
                template_obj = self.env.ref('kw_eos.resignation_approved_mail_template')
                users_data = self.env['res.users'].sudo().search([])
                rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
                rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
                email_to = self.resignation_id.applicant_id.sbu_master_id.representative_id.work_email if self.resignation_id.applicant_id.sbu_master_id else self.resignation_id.applicant_id.department_id.manager_id.work_email
                email_cc = (rcm_work_email +','+ self.resignation_id.sudo().get_cc(deg_group=True, upper_ra=True,sbu=True))
                # print("111111111111========1=1=1=1=1==1=1",email_cc)
                hod_name = self.resignation_id.applicant_id.sbu_master_id.representative_id.name if self.resignation_id.applicant_id.sbu_master_id else self.resignation_id.sudo().applicant_id.department_id.manager_id.name

                mail = self.env['mail.template'].browse(template_obj.id).with_context(state='Approved',
                                                                                    actionby=self.env.user.name,
                                                                                    actionby_code=self.env.user.employee_ids.emp_code,
                                                                                    emailfrom=self.env.user.employee_ids.work_email,
                                                                                    email_to=email_to,
                                                                                    email_cc=email_cc,
                                                                                    hod_name=hod_name,
                                                                                    remark=self.remark,
                                                                                    reg_type=self.resignation_id.reg_type.name,
                                                                                    offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                    applicant_name=self.resignation_id.applicant_id.name,
                                                                                    applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                    sbu_type=self.resignation_id.applicant_id.sbu_master_id.type if self.resignation_id.applicant_id.sbu_master_id.type else '',
                                                                                    sbu=self.resignation_id.applicant_id.sbu_master_id.name if self.resignation_id.applicant_id.sbu_master_id else '',
                                                                                    write_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().write_date),
                                                                                        "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                        "%d-%b-%Y"),
                                                                                    reason=self.resignation_id.reason,
                                                                                    branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                    kt_required='Yes' if self.resignation_id.kt_required == 'yes' else 'NO',
                                                                                    effective_form=datetime.strptime(
                                                                                        str(self.resignation_id.effective_form),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    last_working_date=datetime.strptime(
                                                                                        str(self.resignation_id.last_working_date),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    department_id=self.resignation_id.department_id.name,
                                                                                    division=self.resignation_id.division.name,
                                                                                    section=self.resignation_id.section.name,
                                                                                    practise=self.resignation_id.practise.name,
                                                                                    job_id=self.resignation_id.job_id.name,
                                                                                    date_of_joining=datetime.strptime(
                                                                                        str(self.resignation_id.date_of_joining),
                                                                                        "%Y-%m-%d").strftime(
                                                                                        "%d-%b-%Y")).send_mail(
                    self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)

                # template_obj = self.env.ref('kw_eos.resignation_approved_hr_mail_template')
                # email_cc = self.resignation_id.get_cc(hrd=True)
                # mail = self.env['mail.template'].browse(template_obj.id).with_context(state='Approved',
                #                                                                       actionby=self.env.user.name,
                #                                                                       emailfrom=self.env.user.employee_ids.work_email,
                #                                                                       email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                template_obj = self.env.ref('kw_eos.resignation_approved_user_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(state='Approved',
                                                                                    cc=rcm_work_email,
                                                                                    actionby=self.env.user.name,
                                                                                    actionby_code =self.env.user.employee_ids.emp_code,
                                                                                    email_to=self.resignation_id.applicant_id.work_email,
                                                                                    emailfrom=self.env.user.employee_ids.work_email,
                                                                                    applicant_name=self.resignation_id.applicant_id.name,
                                                                                    applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                    offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                    write_date=datetime.strptime(
                                                                                        str(self.resignation_id.sudo().write_date),
                                                                                        "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                        "%d-%b-%Y"),
                                                                                    reason=self.resignation_id.reason,
                                                                                    reg_type=self.resignation_id.reg_type.name,
                                                                                    kt_required='Yes' if self.resignation_id.kt_required == 'yes' else 'NO',
                                                                                    effective_form=datetime.strptime(
                                                                                        str(self.resignation_id.effective_form),
                                                                                        "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                    remark=self.remark,
                                                                                    last_working_date=datetime.strptime(
                                                                                        str(self.resignation_id.last_working_date),
                                                                                        "%Y-%m-%d").strftime(
                                                                                        "%d-%b-%Y"), ).send_mail(
                    self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)
                resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                            limit=1)
                if resignation_log:
                    self.env['kw_resignation_log'].sudo().create({
                        'applicant_id': self.env.user.employee_ids.id,
                        'date': self.resignation_id.effective_form,
                        'state': self.resignation_id.sudo().state,
                        'remark': self.remark,
                        'last_working_date': self.resignation_id.last_working_date,
                        'reg_id': self.resignation_id.id,
                    })
            ir_config_params = self.env['ir.config_parameter'].sudo()
            # end_date = ir_config_params.get_param('tds.actual_end_date') or False
            # end = datetime.strptime(end_date, "%Y-%m-%d")
            current_fiscal = self.env['account.fiscalyear'].sudo().search([('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            declaration = self.env['hr.declaration'].sudo().search([('date_range', '=',current_fiscal.id),('employee_id', '=',self.resignation_id.applicant_id.id)])
            # print('declaration tax==================',declaration)
            if declaration and declaration.total_tax_payable > 0:
                # self.resignation_id.tax_given = True
                self.resignation_id.sudo().write({
                'tax_given': True,
            })
                # print("inside if===========",declaration.total_tax_payable)
                inform_template = self.env.ref('kw_eos.tds_verification_template')
                inform_template.with_context(
                current_fiscal=current_fiscal.name,
                applicant_name=self.resignation_id.applicant_id.name,
                applicant_work_email=self.resignation_id.applicant_id.work_email).send_mail(self.resignation_id.sudo().resignation_ids.ids[0], notif_layout="kwantify_theme.csm_mail_notification_light")
            """" Email Sent To TAG,RCM,SBU Head if Replacement required for the current leaving Employee. """
            if self.resignation_id.replacement_required == 'yes':
                users_data = self.env['res.users'].sudo().search([])
                rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
                rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
                # param = self.env['ir.config_parameter'].sudo()
                # rcm_head=literal_eval(param.get_param('kw_recruitment.rcm_head','[]'))
                # work_email =self.env['hr.employee'].browse(rcm_head).mapped('work_email')[0]
                replacement_template = self.env.ref('kw_eos.replacement_required_email_notification_template')
                mail = self.env['mail.template'].browse(replacement_template.id).with_context(actionby=self.env.user.name,
                                                                                            email_to=self.resignation_id.applicant_id.sbu_master_id.representative_id.work_email if self.resignation_id.applicant_id.sbu_master_id else '',
                                                                                            email_cc=rcm_work_email,
                                                                                            applicant_name=self.resignation_id.applicant_id.name,
                                                                                            applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                            sbu_type=self.resignation_id.applicant_id.sbu_master_id.type if self.resignation_id.applicant_id.sbu_master_id.type else '',
                                                                                            sbu=self.resignation_id.applicant_id.sbu_master_id.name if self.resignation_id.applicant_id.sbu_master_id else '',
                                                                                            sbu_head = self.resignation_id.applicant_id.sbu_master_id.representative_id.name if self.resignation_id.applicant_id.sbu_master_id else '',
                                                                                            branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                            last_working_date=datetime.strptime(str(self.resignation_id.last_working_date),"%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                            department_id=self.resignation_id.department_id.name,
                                                                                            division=self.resignation_id.division.name,
                                                                                            section=self.resignation_id.section.name,
                                                                                            practise=self.resignation_id.practise.name,
                                                                                            job_id=self.resignation_id.job_id.name,
                                                                                            ).send_mail(
                self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)

            self.env.user.notify_success("Resignation Approved successfully.")
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

        elif self.env.context.get('manager_submit'):
            self.resignation_id.sudo().write({
                'state': 'grant',
                'remark': self.remark,
                'action_to_be_taken_by': False,
            })
            # self.resignation_id.applicant_id.sudo().write({
            #     'in_noticeperiod':True,
            #     'resignation_reason': self.resignation_id.reg_type.id
            # })

            """ eos api called to fetch asset data """
            assetdata = self.resignation_id.sudo().get_asset_data()
            advances_data = False
            petty_cash_data = False
            advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
            if not advance_checklist:
                advances_data = self.resignation_id.sudo().get_advance_details(self.resignation_id.sudo().applicant_id)
                petty_cash_data = self.resignation_id.sudo().get_petty_cash_details(self.resignation_id.sudo().applicant_id).mapped('advance_amt')
                # print("petty cash data==========================",petty_cash_data)
            """ api end """
            template_obj = self.env.ref('kw_eos.resignation_grant_mail_template')
            email_to = self.resignation_id.sudo().get_cc(deg_group=True, hrd=True, dept_head=True,account=True, it=True, admin=True,
                                                  upper_ra=True, ra=True)
            
            tour_clearance = self.resignation_id.sudo().tour_clearance if self.resignation_id.sudo().tour_clearance else 'No tour settlement is pending'
            sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
            petty_cash_clearance = sum(petty_cash_data) if petty_cash_data else 'NIL'
            # print("sum of petty cash=========================",petty_cash_clearance)
            asset_clearance = len(assetdata) if assetdata else 'NIL'
            mail = self.env['mail.template'].browse(template_obj.id).with_context(email_to=email_to,
                                                                                  remark=self.remark,
                                                                                  applicant_name=self.resignation_id.sudo().applicant_id.name,
                                                                                  applicant_emp_code=self.resignation_id.sudo().applicant_id.emp_code,
                                                                                  actionby=self.env.user.name,
                                                                                  actionby_code =self.env.user.employee_ids.emp_code,
                                                                                  emailfrom=self.env.user.employee_ids.work_email,
                                                                                  tour_clearance=tour_clearance,
                                                                                  sal_adv_clearance=sal_adv_clearance,
                                                                                  petty_cash_clearance=petty_cash_clearance,
                                                                                  assetdata=assetdata,
                                                                                  asset_clearance=asset_clearance,
                                                                                  write_date=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().write_date),
                                                                                      "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                      "%d-%b-%Y"),
                                                                                  reason=self.resignation_id.sudo().reason,
                                                                                  reg_type=self.resignation_id.sudo().reg_type.name,
                                                                                  offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                  branch_alias=self.resignation_id.sudo().base_branch_id.alias,
                                                                                  kt_required='Yes' if self.resignation_id.sudo().kt_required == 'yes' else 'NO',
                                                                                  effective_form=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().effective_form),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  department_id=self.resignation_id.sudo().department_id.name,
                                                                                  division=self.resignation_id.sudo().division.name,
                                                                                  section=self.resignation_id.sudo().section.name,
                                                                                  practise=self.resignation_id.sudo().practise.name,
                                                                                  job_id=self.resignation_id.sudo().job_id.name,
                                                                                  date_of_joining=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().date_of_joining),
                                                                                      "%Y-%m-%d").strftime(
                                                                                      "%d-%b-%Y")).send_mail(
                self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                force_send=False)

            template_obj = self.env.ref('kw_eos.resignation_grant_user_mail_template')
            users_data = self.env['res.users'].sudo().search([])
            rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
            rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
            mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                actionby_code =self.env.user.employee_ids.emp_code,
                                                                                  email_to=self.resignation_id.sudo().applicant_id.work_email,
                                                                                  remark=self.remark,
                                                                                  cc = rcm_work_email,
                                                                                  applicant_name=self.resignation_id.sudo().applicant_id.name,
                                                                                  applicant_emp_code=self.resignation_id.sudo().applicant_id.emp_code,
                                                                                  emailfrom=self.env.user.employee_ids.work_email,
                                                                                  write_date=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().write_date),
                                                                                      "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                      "%d-%b-%Y"),
                                                                                  reason=self.resignation_id.sudo().reason,
                                                                                  reg_type=self.resignation_id.sudo().reg_type.name,
                                                                                  offboarding_type = self.resignation_id.offboarding_type.name,
                                                                                  kt_required='Yes' if self.resignation_id.sudo().kt_required == 'yes' else 'NO',
                                                                                  effective_form=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().effective_form),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.resignation_id.sudo().last_working_date),
                                                                                      "%Y-%m-%d").strftime(
                                                                                      "%d-%b-%Y"), ).send_mail(
                self.resignation_id.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                force_send=False)
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })

            self.env.user.notify_success("Resignation Granted successfully.")
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

        elif self.env.context.get('ra_approve_cancel'):
            self.resignation_id.sudo().write({
                'state': 'confirm',
                'remark': self.remark,
                'action_to_be_taken_by': self.resignation_id.sudo().user_id.employee_ids.department_id.manager_id.id,
                'dept_manager_id': self.resignation_id.sudo().user_id.employee_ids.department_id.manager_id.id,
            })

            template_obj = self.env.ref('kw_eos.rl_approved_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(state='Approved',
                                                                                  actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email).send_mail(
                self.resignation_id.sudo().id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })
            self.env.user.notify_success("Resignation Cancellation Approved successfully.")
        elif self.env.context.get('hold_cancel') or self.env.context.get('dept_head_hold_cancel'):
            self.resignation_id.sudo().write({
                'prev_state': self.resignation_id.sudo().state,
                'state': 'hold',
                'remark': self.remark,
            })
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })
            template_obj = self.env.ref('kw_eos.rl_hold_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email).send_mail(
                self.resignation_id.sudo().id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

        elif self.env.context.get('dept_head_approve_cancel'):
            self.resignation_id.sudo().write({
                'state': 'cancel',
                'remark': self.remark,
                'action_to_be_taken_by': False,
            })
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })
            template_obj = self.env.ref('kw_eos.rl_approved_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(state='Granted',
                                                                                  actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email).send_mail(
                self.resignation_id.sudo().id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            self.env.user.notify_success("Resignation Request Cancelled successfully.")

        elif self.env.context.get('unhold_cancel'):
            self.resignation_id.sudo().write({
                'state': self.resignation_id.sudo().prev_state,
                'remark': self.remark,
            })
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })
            template_obj = self.env.ref('kw_eos.rl_unhold_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email).send_mail(
                self.resignation_id.sudo().id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

        elif self.env.context.get('reject_cancel') or self.env.context.get('dept_head_reject_cancel'):
            self.resignation_id.sudo().write({
                'state': 'reject',
                'remark': self.remark,
                'action_to_be_taken_by': False
            })
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.resignation_id.id)],
                                                                           limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.sudo().effective_form,
                    'state': self.resignation_id.sudo().state,
                    'remark': self.remark,
                    'last_working_date': self.resignation_id.sudo().last_working_date,
                    'reg_id': self.resignation_id.sudo().id,
                })
            template_obj = self.env.ref('kw_eos.rl_reject_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                  emailfrom=self.env.user.employee_ids.work_email).send_mail(
                self.resignation_id.sudo().id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

        # elif self.env.context.get('manager_submit'):
        #     self.resignation_id.sudo().write({
        #         'prev_state': self.resignation_id.state,
        #         'state':'grant',
        #         'remark': self.remark,
        #     })
        #     template_obj = self.env.ref('kw_eos.resignation_grant_mail_template')
        #     email_cc = self.resignation_id.get_cc(grant=True)
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #     email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
        #     self.env.user.notify_success("Granted.")

        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class CancelWizard(models.TransientModel):
    _name = "kw_resignation_cancellation_wizard"
    _description = "kw_resignation_cancellation_wizard"
    _order = 'id'

    resignation_id = fields.Many2one('kw_resignation', string="Ref")
    cancel_reason = fields.Text(string="Reason for Cancellation")

    def save_info(self):
        # import pdb; pdb.set_trace();
        if self.resignation_id:

            # if self.resignation_id.state in ['apply','confirm','forward','grant']:
            if self.resignation_id.state == 'apply':
                self.resignation_id.sudo().write({
                    'cancel_reason': self.cancel_reason,
                    'remark': self.cancel_reason,
                    'state': 'cancel',
                    'cancel_process': True,
                })
                self.env.user.employee_ids.regignation_aplied = False
                self.resignation_id.applicant_id.sudo().write({
                    'in_noticeperiod':False,
                    'resignation_reason': False
                })

                resignation_log = self.env['kw_resignation_log'].sudo().search(
                    [('reg_id', '=', self.resignation_id.id)], limit=1)
                if resignation_log:
                    self.env['kw_resignation_log'].create({
                        'applicant_id': self.env.user.employee_ids.id,
                        'date': self.resignation_id.effective_form,
                        'state': 'cancel',
                        'remark': self.cancel_reason,
                        'last_working_date': self.resignation_id.last_working_date,
                        'reg_id': self.resignation_id.id,
                    })
                template_obj = self.env.ref('kw_eos.rl_canceled_mail_template')
                email_cc = self.resignation_id.get_cc(hrd=True, dept_head=True, deg_group=True,sbu=True)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                      mailra=self.resignation_id.applicant_id.parent_id.name,
                                                                                      mto=self.resignation_id.applicant_id.parent_id.work_email,
                                                                                      mfrom=self.env.user.employee_ids.work_email,
                                                                                      mailtn=self.resignation_id.applicant_id.name,
                                                                                      mailfn=self.env.user.employee_ids.name,
                                                                                      cancel_reason=self.cancel_reason,
                                                                                      applicant_name=self.resignation_id.applicant_id.name,
                                                                                      applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                      effective_from=datetime.strptime(
                                                                                          str(self.resignation_id.effective_form),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(self.resignation_id.last_working_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      reason=self.resignation_id.reason,
                                                                                      reg_type=self.resignation_id.reg_type.name,
                                                                                      write_date=datetime.strptime(
                                                                                          str(self.resignation_id.write_date),
                                                                                          "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      department_id=self.resignation_id.department_id.name,
                                                                                      division=self.resignation_id.division.name,
                                                                                      section=self.resignation_id.section.name,
                                                                                      practise=self.resignation_id.practise.name,
                                                                                      job_id=self.resignation_id.job_id.name,
                                                                                      branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                      date_of_joining=datetime.strptime(
                                                                                          str(self.resignation_id.date_of_joining),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"), ).send_mail(
                    self.resignation_id.resignation_ids.ids[0],
                    notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Resignation cancelled successfully.")
            else:
                self.resignation_id.sudo().write({
                    'cancel_reason': self.cancel_reason,
                    'remark': self.cancel_reason,
                    'state': 'waiting_for_rl_cancellation',
                    'cancel_process': True,
                    'prev_state': self.resignation_id.state,
                })
                resignation_log = self.env['kw_resignation_log'].sudo().search(
                    [('reg_id', '=', self.resignation_id.id)], limit=1)
                if resignation_log:
                    self.env['kw_resignation_log'].create({
                        'applicant_id': self.env.user.employee_ids.id,
                        'date': self.resignation_id.effective_form,
                        'state': 'waiting_for_rl_cancellation',
                        'remark': self.cancel_reason,
                        'last_working_date': self.resignation_id.last_working_date,
                        'reg_id': self.resignation_id.id,
                    })

                template_obj = self.env.ref('kw_eos.rl_cancel_reqest_mail_template')
                email_cc = self.resignation_id.get_cc(hrd=True, dept_head=True, deg_group=True,sbu=True)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                      mailra=self.resignation_id.applicant_id.parent_id.name,
                                                                                      mto=self.resignation_id.applicant_id.parent_id.work_email,
                                                                                      mfrom=self.env.user.employee_ids.work_email,
                                                                                      mailtn=self.resignation_id.applicant_id.name,
                                                                                      mailfn=self.env.user.employee_ids.name,
                                                                                      cancel_reason=self.cancel_reason,
                                                                                      applicant_emp_code=self.resignation_id.applicant_id.emp_code,
                                                                                      effective_from=datetime.strptime(
                                                                                          str(self.resignation_id.effective_form),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(self.resignation_id.last_working_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      reason=self.resignation_id.reason,
                                                                                      reg_type=self.resignation_id.reg_type.name,
                                                                                      create_date=datetime.strptime(
                                                                                          str(self.resignation_id.create_date),
                                                                                          "%Y-%m-%d %H:%M:%S.%f").date().strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      department_id=self.resignation_id.department_id.name,
                                                                                      division=self.resignation_id.division.name,
                                                                                      section=self.resignation_id.section.name,
                                                                                      practise=self.resignation_id.practise.name,
                                                                                      job_id=self.resignation_id.job_id.name,
                                                                                      branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                      date_of_joining=datetime.strptime(
                                                                                          str(self.resignation_id.date_of_joining),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"), ).send_mail(
                    self.resignation_id.resignation_ids.ids[0],
                    notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Resignation cancellation applied successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class AdminRemarkWizard(models.TransientModel):
    _name = "kw_admin_remark_wizard"
    _description = "kw_admin_remark_wizard"
    _order = 'id'

    resignation_id = fields.Many2one('kw_resignation', string="Ref")
    remark = fields.Text('Remarks')

    def btn_submit(self):
        if self.env.context.get('contract_reject'):
            self.resignation_id.sudo().write({
                'state': 'reject',
                'contract_remark': self.remark,
                'action_to_be_taken_by': False,
            })
            res_log = self.env['kw_resignation_log'].sudo().create({
                'applicant_id': self.env.user.employee_ids.id,
                'date': self.resignation_id.effective_form,
                'state': self.resignation_id.state,
                'remark': f'Rejected By {self.env.user.employee_ids.name}',
                'last_working_date': self.resignation_id.last_working_date,
                'reg_id': self.resignation_id.id,
            })
            template_obj = self.env.ref('kw_eos.contract_reject_mail_template')
            email_cc = self.resignation_id.get_cc(account=True, ra=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                  actionby=self.env.user.name,
                                                                                  email_to=self.resignation_id.applicant_id.work_email,
                                                                                  applicant_name=self.resignation_id.applicant_id.name,
                                                                                  code=self.resignation_id.applicant_id.emp_code,
                                                                                  reason=self.remark,
                                                                                  branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                  contract_start_date=datetime.strptime(
                                                                                      str(self.resignation_id.start_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  contract_end_date=datetime.strptime(
                                                                                      str(self.resignation_id.end_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  department_id=self.resignation_id.department_id.name,
                                                                                  division=self.resignation_id.division.name,
                                                                                  section=self.resignation_id.section.name,
                                                                                  practise=self.resignation_id.practise.name,
                                                                                  job_id=self.resignation_id.job_id.name,
                                                                                  date_of_joining=datetime.strptime(
                                                                                      str(self.resignation_id.date_of_joining),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(
                self.resignation_id.resignation_ids[0].id, notif_layout='kwantify_theme.csm_mail_notification_light',
                force_send=False)
            self.env.user.notify_success("Contract Closure rejected successfully.")
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }
        if self.env.context.get('contract_grant'):
            if self.resignation_id.contract_extend == 'yes':
                self.resignation_id.sudo().write({
                    'contract_remark': self.remark,
                    'state': 'extend'
                })
                template_obj = self.env.ref('kw_eos.contract_extend_grant_mail_template')
                email_cc = self.resignation_id.get_cc(account=True, ra=True)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                      actionby=self.env.user.name).send_mail(
                    self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Contract Closure Extended successfully.")

                employee_rec = self.env['hr.employee'].sudo().search([('id', '=', self.resignation_id.applicant_id.id)])
                employee_rec.write({'end_date': self.resignation_id.new_contract_end_date})

                action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
            if self.resignation_id.contract_extend == 'no':
                self.resignation_id.sudo().write({
                    'state': 'grant',
                    'contract_remark': self.remark,
                    'action_to_be_taken_by': False,
                })
                res_log = self.env['kw_resignation_log'].sudo().create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': self.resignation_id.effective_form,
                    'state': self.resignation_id.state,
                    'remark': f'Granted By {self.env.user.employee_ids.name}',
                    'last_working_date': self.resignation_id.last_working_date,
                    'reg_id': self.resignation_id.id,
                })
                assetdata = self.resignation_id.get_asset_data()
                advances_data = False
                petty_cash_data = False
                advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                if not advance_checklist:
                    advances_data = self.resignation_id.get_advance_details(self.resignation_id.applicant_id)
                    petty_cash_data = self.resignation_id.get_petty_cash_details(self.resignation_id.applicant_id)
                tour_clearance = self.resignation_id.tour_clearance if self.resignation_id.tour_clearance else 'No tour settlement is pending'
                sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
                petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
                asset_clearance = len(assetdata) if assetdata else 'NIL'
                template_obj = self.env.ref('kw_eos.contract_grant_mail_template')
                email_cc = self.resignation_id.get_cc(account=True, ra=True)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                      actionby=self.env.user.name,
                                                                                      email_to=self.resignation_id.applicant_id.work_email,
                                                                                      applicant_name=self.resignation_id.applicant_id.name,
                                                                                      code=self.resignation_id.applicant_id.emp_code,
                                                                                      reason=self.remark,
                                                                                      tour_clearance=tour_clearance,
                                                                                      sal_adv_clearance=sal_adv_clearance,
                                                                                      petty_cash_clearance=petty_cash_clearance,
                                                                                      assetdata=assetdata,
                                                                                      branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                      contract_start_date=datetime.strptime(
                                                                                          str(self.resignation_id.start_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      contract_end_date=datetime.strptime(
                                                                                          str(self.resignation_id.end_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      department_id=self.resignation_id.department_id.name,
                                                                                      division=self.resignation_id.division.name,
                                                                                      section=self.resignation_id.section.name,
                                                                                      practise=self.resignation_id.practise.name,
                                                                                      job_id=self.resignation_id.job_id.name,
                                                                                      date_of_joining=datetime.strptime(
                                                                                          str(self.resignation_id.date_of_joining),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      ).send_mail(
                    self.resignation_id.resignation_ids[0].id,
                    notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Contract Closure granted successfully.")

                action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
        if self.env.context.get('retirement_submit'):
            # self.resignation_id.sudo().write({
            #     'state':'grant',
            #     'retirement_submit_remark': self.remark,
            #     'action_to_be_taken_by':False,
            # })

            template_obj = self.env.ref('kw_eos.retirement_extend_grant_mail_template')
            email_cc = self.resignation_id.get_cc(dept_head=True, ra=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc,
                                                                                  mailt=self.resignation_id.applicant_id.work_email,
                                                                                  code=self.resignation_id.applicant_id.emp_code,
                                                                                  mailtn=self.resignation_id.applicant_id.name,
                                                                                  reason=self.resignation_id.retirement,
                                                                                  branch_alias=self.resignation_id.base_branch_id.alias,
                                                                                  effective_form=datetime.strptime(
                                                                                      str(self.resignation_id.effective_form),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.resignation_id.last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  department_id=self.resignation_id.department_id.name,
                                                                                  division=self.resignation_id.division.name,
                                                                                  section=self.resignation_id.section.name,
                                                                                  practise=self.resignation_id.practise.name,
                                                                                  job_id=self.resignation_id.job_id.name,
                                                                                  date_of_joining=datetime.strptime(
                                                                                      str(self.resignation_id.date_of_joining),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(
                self.resignation_id.resignation_ids[0].id, notif_layout='kwantify_theme.csm_mail_notification_light',
                force_send=False)

            emp_obj = self.env['hr.employee'].sudo()
            emp = emp_obj.search([('id', '=', self.resignation_id.applicant_id.id)])
            if self.resignation_id.retain == 'yes':
                data = {
                    'enable_payroll': 'no',
                    # 'at_join_time_ctc': reg_rec.current_ctc if reg_rec else self.current_ctc,
                    'current_ctc': self.resignation_id.new_current_ctc,
                    'department_id': self.resignation_id.ret_department_id.id if self.resignation_id else emp.ret_department_id.id,
                    'division': self.resignation_id.ret_division.id if self.resignation_id else emp.ret_division.id,
                    'section': self.resignation_id.ret_section.id if self.resignation_id else emp.ret_section.id,
                    'practise': self.resignation_id.ret_practise.id if self.resignation_id else emp.ret_practise.id,
                    'job_id': self.resignation_id.ret_job_id.id if self.resignation_id else emp.job_id.id,
                    'linkedin_url': emp.linkedin_url if emp.linkedin_url else False,
                    'marital_code': emp.marital_code if emp.marital_code else False,
                    'wedding_anniversary': emp.wedding_anniversary if emp.wedding_anniversary else False,
                    'name': emp.name if emp.name else '',
                    'employement_type': self.resignation_id.employement_type.id,
                    'direct_indirect': emp.direct_indirect,
                    'emp_role': self.resignation_id.emp_role.id,
                    'emp_category': self.resignation_id.emp_category.id,
                    # 'emp_project_id': self.resignation_id.emp_project_id.id if self.resignation_id else emp.emp_project_id.id,
                    'start_date': self.resignation_id.ret_contract_start_date,
                    'end_date': self.resignation_id.ret_contract_end_date,
                    'work_email': emp.work_email if emp.work_email else '',
                    'emp_code': emp.emp_code if emp.emp_code else '',
                    'mobile_phone': emp.mobile_phone if emp.mobile_phone else '',
                    'work_phone': emp.work_phone if emp.work_phone else '',
                    'user_id': emp.user_id.id if emp.user_id else '',
                    'parent_id': emp.parent_id.id if emp.parent_id else False,
                    'gender': emp.gender if emp.gender else '',
                    'permanent_addr_street': emp.permanent_addr_street if emp.permanent_addr_street else '',
                    'permanent_addr_street2': emp.permanent_addr_street2 if emp.permanent_addr_street2 else '',
                    'personal_email': emp.personal_email if emp.personal_email else '',
                    'permanent_addr_zip': emp.permanent_addr_zip if emp.permanent_addr_zip else '',
                    'permanent_addr_country_id': emp.permanent_addr_country_id.id if emp.permanent_addr_country_id else '',
                    'permanent_addr_state_id': emp.permanent_addr_state_id.id if emp.permanent_addr_state_id else '',
                    'permanent_addr_city': emp.permanent_addr_city if emp.permanent_addr_city else '',
                    'date_of_joining': emp.date_of_joining if emp.date_of_joining else False,
                    'outlook_pwd': emp.outlook_pwd if emp.outlook_pwd else '',
                    'birthday': emp.birthday if emp.birthday else False,
                    'same_address': emp.same_address if emp.same_address else '',
                    'emp_religion': emp.emp_religion.id if emp.emp_religion else '',
                    'emergency_contact': emp.emergency_contact if emp.emergency_contact else '',
                    'emergency_phone': emp.emergency_phone if emp.emergency_phone else '',
                    'id_card_no': emp.id_card_no.id if emp.id_card_no else '',
                    'country_id': emp.country_id.id if emp.country_id else '',
                    'present_addr_street': emp.present_addr_street if emp.present_addr_street else '',
                    'present_addr_street2': emp.present_addr_street2 if emp.present_addr_street2 else '',
                    'blood_group': emp.blood_group.id if emp.blood_group else '',
                    'present_addr_country_id': emp.present_addr_country_id.id if emp.present_addr_country_id else '',
                    'present_addr_city': emp.present_addr_city if emp.present_addr_city else '',
                    'present_addr_state_id': emp.present_addr_state_id.id if emp.present_addr_state_id else '',
                    'present_addr_zip': emp.present_addr_zip if emp.present_addr_zip else '',
                    'whatsapp_no': emp.whatsapp_no if emp.whatsapp_no else '',
                    'experience_sts': emp.experience_sts if emp.experience_sts else '',
                    'image': emp.image if emp.image else '',
                    'job_title': emp.job_title if emp.job_title else '',
                    'epbx_no': emp.epbx_no if emp.epbx_no else '',
                    'company_id': emp.company_id.id if emp.company_id else '',
                    'identification_ids': [[0, 0, {
                        'name': r.name,
                        'doc_number': r.doc_number,
                        'date_of_issue': r.date_of_issue,
                        'date_of_expiry': r.date_of_expiry,
                        'renewal_sts': r.renewal_sts,
                        'uploaded_doc': r.uploaded_doc,
                        # 'doc_file_name':r.doc_file_name,
                        'emp_document_id': r.id,
                    }] for r in emp.identification_ids] if emp.identification_ids else False,
                    'family_details_ids': [[0, 0, {
                        'relationship_id': r.relationship_id.id,
                        'name': r.name,
                        'gender': r.gender,
                        'date_of_birth': r.date_of_birth,
                        'dependent': r.dependent,
                        'family_id': r.id,
                    }] for r in emp.family_details_ids] if emp.family_details_ids else False,
                    'work_experience_ids': [[0, 0, {
                        'country_id': r.country_id.id,
                        'name': r.name,
                        'designation_name': r.designation_name,
                        'organization_type': r.organization_type.id,
                        'industry_type': r.industry_type.id,
                        'effective_from': r.effective_from,
                        'effective_to': r.effective_to,
                        'uploaded_doc': r.uploaded_doc,
                        'emp_work_id': r.id,
                    }] for r in emp.work_experience_ids] if emp.work_experience_ids else False,
                    'membership_assc_ids': [[0, 0, {
                        'date_of_issue': r.date_of_issue,
                        'name': r.name,
                        'date_of_expiry': r.date_of_expiry,
                        'renewal_sts': r.renewal_sts,
                        'uploaded_doc': r.uploaded_doc,
                        'emp_membership_id': r.id,
                    }] for r in emp.membership_assc_ids],
                    # 'worked_country_ids': [[6, False,country_list]],

                    'technical_skill_ids': [[0, 0, {
                        'category_id': r.category_id.id,
                        'skill_id': r.skill_id.id,
                        'proficiency': r.proficiency,
                        'emp_technical_id': r.id,
                    }] for r in emp.technical_skill_ids] if emp.technical_skill_ids else False,
                    'known_language_ids': [[0, 0, {
                        'language_id': r.language_id.id,
                        'reading_status': r.reading_status,
                        'writing_status': r.writing_status,
                        'speaking_status': r.speaking_status,
                        'understanding_status': r.understanding_status,
                        'emp_language_id': r.id,
                    }] for r in emp.known_language_ids] if emp.known_language_ids else False,
                    'educational_details_ids': [[0, 0, {
                        'course_type': r.course_type,
                        'course_id': r.course_id.id,
                        'stream_id': r.stream_id.id,
                        'university_name': r.university_name.id,
                        'passing_year': str(r.passing_year),
                        'division': r.division,
                        'marks_obtained': r.marks_obtained,
                        'uploaded_doc': r.uploaded_doc,
                        'emp_educational_id': r.id,
                        'passing_details': [(6, 0, r.passing_details.ids)],

                    }] for r in emp.educational_details_ids] if emp.educational_details_ids else False,
                    'cv_info_details_ids': [[0, 0, {
                        'project_of': r.project_of,
                        'project_name': r.project_name,
                        # 'project_id':r.project_id.id,
                        'location': r.location,
                        'start_month_year': r.start_month_year,
                        'end_month_year': r.end_month_year,
                        'project_feature': r.project_feature,
                        'role': r.role,
                        'responsibility_activity': r.responsibility_activity,
                        'client_name': r.client_name,
                        'compute_project': r.compute_project,
                        'organization_id': r.organization_id.id,
                        'activity': r.activity,
                        'other_activity': r.other_activity,
                        'emp_cv_info_id': r.id,
                        'emp_project_id': r.emp_project_id.id,

                    }] for r in emp.cv_info_details_ids] if emp.cv_info_details_ids else False,
                }
                emp.write({'active': False})
                emp_obj.create(data)
                self.resignation_id.state = 'extend'
            else:
                emp.write({'active': False})
                self.resignation_id.state = 'exemployee'

            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

        # if self.env.context.get('retirement_reject'):
        #     self.resignation_id.sudo().write({
        #         'state':'reject',
        #         'retirement_reject_remark': self.remark,
        #         'action_to_be_taken_by':False,
        #     })
        if self.env.context.get('termination_submit'):
            self.resignation_id.sudo().write({
                'state': 'grant',
                'termination_submit_remark': self.remark,
                'action_to_be_taken_by': False,
            })

        # if self.env.context.get('demise_exemployee'):
        #     self.resignation_id.sudo().write({
        #         'state':'exemployee',
        #         'action_to_be_taken_by':False,
        #     })
        #     employee_rec = self.env['hr.employee'].sudo().search([('id','=',self.resignation_id.applicant_id.id)])
        #     employee_rec.write({'active':False})
        #     template_obj = self.env.ref('kw_eos.demise_mail_template')
        #     email_cc = self.resignation_id.get_cc(dept_head=True,resource_head=True,ceo=True)
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #     email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
        #     self.env.user.notify_success("Demise mail sent successfully.")

        # if self.env.context.get('confirm_exemployee'):
        #     self.resignation_id.sudo().write({
        #         'state':'exemployee',
        #         'action_to_be_taken_by':False,
        #     })
        #     employee_rec = self.env['hr.employee'].sudo().search([('id','=',self.resignation_id.applicant_id.id)])
        #     employee_rec.write({'active':False})
        #     template_obj = self.env.ref('kw_eos.termination_mail_template')
        #     email_cc = self.resignation_id.get_cc(dept_head=True,resource_head=True)
        #     mail = self.env['mail.template'].browse(template_obj.id).with_context(
        #     email_cc=email_cc).send_mail(self.resignation_id.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
        #     self.env.user.notify_success("Terminated successfully.")

        return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class KwOffboardingReportWizard(models.TransientModel):
    _name = 'kw_offboarding_report_wizard'
    _description = 'Report Wizard'

    def get_year_data():
        year_list = []
        # start_year = (date.today().year - (date.today().year - 2000))
        for i in range((date.today().year), 1998, -1):
            year_list.append((i, str(i)))
        return year_list

    search_by = fields.Selection([('02', 'Last Working Date'), ('01', 'Effective From')],
                                 string="Search By", default='02')
    applied_by = fields.Selection([('all', 'All'),
                                   ('dt', 'Date wise'),
                                   ('my', 'Month & Year wise'),
                                   ('employee', 'Employee'),
                                   ('exemployee', 'Ex-employee')
                                   ], string="Applied By", default='all')
    report_state = fields.Selection([('apply', 'Applied'),
                              ('forward', 'Forwarded'),
                              ('confirm', 'Approved'),
                              ('grant', 'Granted'),
                              ('reject', 'Rejected')], string='Status', default='apply')
    date_from = fields.Date('Date From', help="Choose a Starting date to get the salary advance at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the salary advance at that date")
    year = fields.Selection(get_year_data(), string='Year', default=date.today().year)
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    employee_ids = fields.Many2many('hr.employee', 'kw_resignation_wiz_hr_employee_rel', 'offboarding_wiz_id',
                                    'employee_id', string="Employee")
    exemployee_ids = fields.Many2many('hr.employee', 'kw_resignation_wiz_exhr_employee_rel', 'offboarding_wiz_id',
                                      'employee_id', string="Ex-employee", domain=[('active', '=', False)])

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        employee_data = False
        dm = False
        employees = self.env['hr.employee'].sudo()
        resignation_employee_obj = self.env['kw_resignation'].sudo().search([]).mapped('applicant_id')
        # print("dataa=================--------------",resignation_employee_obj)
        resignation_employee_list = resignation_employee_obj.ids
        if self.env.user.has_group('kw_employee.group_hr_ra')\
                and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
            # print('1',resignation_employee_list,domain,self.applied_by)
            
            if self.applied_by == 'employee':
                # print("inside employee iffffff===============================")
                domain = ['&', '|','|',('id', '=', self.env.user.employee_ids.id),
                            ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),('active', '=', True)]
                # print("domain=/=======================",domain)
            elif self.applied_by == 'exemployee':
                domain = ['&', '|','|',('id', '=', self.env.user.employee_ids.id),
                            ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in resignation_employee_list).ids
            # print('employeedata===================',employee_data)
        elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
            # print('2')
            if self.applied_by == 'employee':
                domain = ['&', '|','|', ('id', '=', self.env.user.employee_ids.id),('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                            ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                            ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['&', '|', '|', ('id', '=', self.env.user.employee_ids.id),('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in resignation_employee_list).ids
            # print("employee_data 111111111111 ", employee_data)
            employee_data = (employees.with_context(active_test=False).search(domain) & resignation_employee_obj).ids
            # print("employee_data 2222222222222 ", employee_data)
            
        elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
            # print('333333333333333333333333333')
            if self.applied_by == 'employee':
                domain = ['&', '|', '|',('id', '=', self.env.user.employee_ids.id),('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                            ('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                            ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['&', '|', '|', ('id', '=', self.env.user.employee_ids.id),('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in resignation_employee_list).ids
            # print("employee_data 111111111111 ", employee_data)
            employee_data = (employees.with_context(active_test=False).search(domain) & resignation_employee_obj).ids
            # print("employee_data 2222222222222 ", employee_data)
        else:
            # print('3')
            # if self.applied_by == 'employee':
            #     domain = [('active', '=', True)]
            # elif self.applied_by == 'exemployee':
            #     domain = [('active', '=', False)]
            # print("employees.with_context(active_test=False).search(domain) ", employees.with_context(active_test=False).search(domain))
            # print("resignation_employee_list ", resignation_employee_list)
            # print(" common ", (employees.with_context(active_test=False).search(domain) & self.env['kw_resignation'].sudo().search([]).mapped('applicant_id') ))
            # employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in resignation_employee_list)
            employee_data = resignation_employee_list
        if self.applied_by == 'employee':
            dm = {'domain': {'employee_ids': [('id', 'in', employee_data)]}}
        elif self.applied_by == 'exemployee':
            dm = {'domain': {'exemployee_ids': [('id', 'in', employee_data)]}}
        # print("dm >>>>>> ", dm)
        return dm

    def get_offboarding_report_data(self):
        # import pdb
        # pdb.set_trace()
        self.ensure_one()
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            eos_data = self.env['kw_resignation']
            record_data = False
            if self.search_by == '01':
                record_data = eos_data.sudo().search([('effective_form', '>=', dt1), ('effective_form', '<=', dt2)])
            else:
                record_data = eos_data.sudo().search(
                    [('last_working_date', '>=', dt1), ('last_working_date', '<=', dt2)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
                form_view_id = self.env.ref('kw_eos.report_form').id
                action = {
                    'type': 'ir.actions.act_window',
                    'name': 'Offboarding Report',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'kw_resignation',
                    'target': 'main',
                }

                if self.env.user.has_group('kw_employee.group_hr_ra') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    # print("dt1111111111======================================")
                    # if self.search_by == '01':
                        # action['domain'] = ['&', '&',('id', 'in', record_data.ids),('state','=',self.report_state),
                        #                     '|', '|',('applicant_id', '=', self.env.user.employee_ids.id), (
                        #                         'applicant_id.parent_id.user_id', '=',
                        #                         self.env.user.employee_ids.user_id.id),(
                        #                         'applicant_id.sbu_master_id.representative_id.user_id', '=',
                        #                         self.env.user.employee_ids.user_id.id)]
                        # print('action==================',action)
                        # return action
                    # else:
                    action['domain'] = ['&', '&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                            '|', '|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                    return action
                elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                    # print("dt222222222222222222222======================================")
                    
                    # if self.search_by == '01':
                    #     action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                    #                         '|', ('applicant_id', '=', self.env.user.employee_ids.id), (
                    #                             'applicant_id.department_id.manager_id.user_id', '=',
                    #                             self.env.user.employee_ids.user_id.id)]
                    #     return action
                    # else:
                    action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                            '|', '|',('applicant_id', '=', self.env.user.employee_ids.id),(
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id), (
                                                'applicant_id.department_id.manager_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                    return action
                    
                elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                    # print("d33333333333333333333333333333333333333======================================")
                    
                    # if self.search_by == '01':
                    #     action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                    #                         '|', ('applicant_id', '=', self.env.user.employee_ids.id),(
                    #                             'applicant_id.sbu_master_id.representative_id.user_id', '=',
                    #                             self.env.user.employee_ids.user_id.id)]
                    #     return action
                    # else:
                    action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                            '|','|', ('applicant_id', '=', self.env.user.employee_ids.id),(
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                    return action
                else:
                    # print("d444444444444444444444444444444444444444======================================")
                    
                    if self.search_by == '01':
                        action['domain'] = [('effective_form', '>=', dt1),('effective_form', '<=', dt2),('state','=',self.report_state)]
                        return action
                    else:
                        action['domain'] = [('last_working_date', '>=', dt1),('last_working_date', '<=', dt2),('state','=',self.report_state)]
                return action
        elif self.applied_by == 'my':
            cuur_year = self.year
            curr_month = int(self.month)
            num_days = calendar.monthrange(cuur_year, curr_month)
            lst_day = list(num_days)[1]
            first_day = date(cuur_year, curr_month, 1)
            last_day = date(cuur_year, curr_month, lst_day)
            record_data = self.env['kw_resignation'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
                form_view_id = self.env.ref('kw_eos.report_form').id
                action = {
                    'type': 'ir.actions.act_window',
                    'name': 'Offboarding Report',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'kw_resignation',
                    'target': 'main',
                }
                if self.env.user.has_group('kw_employee.group_hr_ra') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    if self.search_by == '01':
                        action['domain'] = ['&', '&','&',('effective_form', '>=', first_day),
                                            ('effective_form', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                    else:
                        action['domain'] = ['&', '&','&',('last_working_date', '>=', first_day),
                                            ('last_working_date', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                    if self.search_by == '01':
                        action['domain'] = ['&','&','&',('effective_form', '>=', first_day),
                                            ('effective_form', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id), (
                                                'applicant_id.department_id.manager_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                    else:
                        action['domain'] = ['&','&','&',('last_working_date', '>=', first_day),
                                            ('last_working_date', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id), (
                                                'applicant_id.department_id.manager_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                    
                elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                    if self.search_by == '01':
                        action['domain'] = ['&', '&','&',('effective_form', '>=', first_day),
                                            ('effective_form', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                    else:
                        action['domain'] = ['&', '&','&',('last_working_date', '>=', first_day),
                                            ('last_working_date', '<=', last_day),('state','=',self.report_state),
                                            '|','|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                                'applicant_id.parent_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id),(
                                                'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                                self.env.user.employee_ids.user_id.id)]
                        return action
                else:
                    if self.search_by == '01':
                        action['domain'] = [('effective_form', '>=', first_day), ('effective_form', '<=', last_day),('state','=',self.report_state)]
                        return action
                    else:
                        action['domain'] = [('last_working_date', '>=', first_day),
                                            ('last_working_date', '<=', last_day),('state','=',self.report_state)]
                        return action

        elif self.applied_by == 'employee' or self.applied_by == 'exemployee':
            # import pdb
            # pdb.set_trace()
            emp_id = self.employee_ids
            record_data = self.env['kw_resignation'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
                form_view_id = self.env.ref('kw_eos.report_form').id
                action_return =  {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'name': 'Offboarding Report',
                    'res_model': 'kw_resignation',
                    'target': 'main',
                }
                if self.applied_by == 'employee':
                    action_return['domain'] = [('applicant_id', 'in', self.employee_ids.ids),('state','=',self.report_state),]
                if self.applied_by == 'exemployee':
                    action_return['domain'] = [('applicant_id', 'in', self.exemployee_ids.ids),('state','=',self.report_state),]
                return action_return

        elif self.applied_by == 'all':
            # emp_id = self.employee_ids
            # record_data = self.env['kw_resignation'].sudo().search([])
            # for rec in record_data:
            tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
            form_view_id = self.env.ref('kw_eos.report_form').id
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'view_type': 'form',
                'name': 'Offboarding Report',
                'res_model': 'kw_resignation',
                'target': 'main',
            }
            domain=[]
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                domain = []
            elif self.env.user.has_group('kw_employee.group_hr_ra') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                domain = [('applicant_id.parent_id.user_id', '=', self.env.user.id)]
            elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                domain = ['|',('applicant_id.parent_id.user_id', '=', self.env.user.id),('applicant_id.department_id.manager_id.user_id', '=', self.env.user.id)]
            elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                domain = ['|',('applicant_id.parent_id.user_id', '=', self.env.user.id),('applicant_id.sbu_master_id.representative_id.user_id', '=', self.env.user.id)]
            # print("action >>>>>>>>> report", domain)
            action['domain'] = domain
            return action
