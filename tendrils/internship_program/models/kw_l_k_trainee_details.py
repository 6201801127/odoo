# -*- coding: utf-8 -*-
"""
Module: Text Utility Functions

Summary:
    This module provides utility functions for text manipulation and processing.

Description:
    The module includes functions for handling various text-related tasks such as encoding, decoding, normalization,
    and validation. These functions can be used for processing text data within the Odoo platform.

"""
import base64
import math
from datetime import date, datetime
import unicodedata
from odoo.exceptions import ValidationError
from odoo import models, fields, api
import re
from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell


class AccountFiscalPeriod(models.Model):
    _inherit = "account.fiscalyear"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context
        if 'order_display' in ctx:
            order = ctx['order_display']
        res = super(AccountFiscalPeriod, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res


class LearningAndKnowledge(models.Model):
    """
    Model representing learning and knowledge entities.

    This class defines a model for managing learning and knowledge entities within the system.
    It provides functionalities for storing and manipulating data related to learning materials,
    courses, certifications, and other knowledge-related entities.

    """
    _name = "lk_batch"
    _description = "Internship Program"
    _rec_name = "name"
    _order = "name"

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    name = fields.Char(string="Batch Name", required=True)
    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', default=_default_financial_yr,
                                        required=True)
    date_of_joining = fields.Date(string="Date of Joining")
    training_completion_details_ids = fields.One2many('lk_batch_details', 'batch_id', string="Training details")
    internship_completion_details_ids = fields.One2many('lk_batch_details', 'internship_id',
                                                        string="Internship details")
    training_completion_payroll_details_ids = fields.One2many('lk_batch_details', 'lk_payroll', string="Payroll Revise")
    internship_completion_payroll_details_ids = fields.One2many('lk_batch_details', 'lk_payroll_internship',
                                                                string="Payroll Revise")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Applied'), ('approve', 'Approved')], default="draft",
                             string='Status')
    rh_check_bool = fields.Boolean(compute="check_enable_editing")

    current_ctc_traineeship = fields.Integer(string="CTC After Traineeship Completion")
    current_ctc_internship = fields.Integer(string="CTC After Internship Completion")
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='MRF', required=True,
                             domain="[('dept_name.code','=','LAK'), ('categ_id.code', '=','INN'), ('state', 'in', ['approve'])]")
    locked_bool = fields.Boolean(string="Locked", default=False)
    pay_revies_all_bool = fields.Boolean(string="All Pay Revise", compute="_get_payrevies_all_traineeship")

    @api.constrains('mrf_id', 'internship_completion_details_ids')
    def check_mrf_id(self):
        exists_title = self.env['lk_batch'].search([('mrf_id', '=', self.mrf_id.id), ('id', '!=', self.id)])
        if exists_title:
            raise ValueError('Exists! Batch with this MRF already exists.')
        for rec in self.internship_completion_details_ids:
            if not rec.new_dept_id:
                raise ValidationError("New Department is required for Internship Completion Details.")

    def update_employee_list(self):
        if self.financial_year_id:
            employee_data = self.env['hr.employee'].sudo().search([('mrf_id', '=', self.mrf_id.id)])
            # print('employee_data >> ', employee_data)
            # [('date_of_joining', '=', self.date_of_joining), ('grade', '=', 'M1'), ('emp_band', '=', 'Band 1')])
            for rec in employee_data:
                if self.env['lk_batch_details'].sudo().search([('employee_id', '=', rec.id)]).exists():
                    # raise ValidationError("Record already exist.")
                    pass
                else:
                    self.env['lk_batch_details'].sudo().create({'batch_id': self.id,
                                                                'employee_id': rec.id,
                                                                })
                    # 'employee_code': rec.emp_code,
                    # 'deg_id': rec.job_id.id,
                    # 'doj': rec.date_of_joining

    def action_apply_all_managers(self):
        if self._context.get('button') == 'foundation_approve_all':
            if any(status.traineeship_status in ['In Progress'] for status in self.training_completion_details_ids):
                view_id = self.env.ref("internship_program.employee_take_action_view_form").id
                action = {
                    'name': 'Take Action',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee_take_action_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': {'current_ids': [rec.id for rec in self.training_completion_details_ids if rec.traineeship_status == 'In Progress']}
                }
                return action
            else:
                raise ValidationError("There will be no any Employee in In progress Stage.")

    def action_internship_apply_all_managers(self):
        if self._context.get('button') == 'internship_apply_all':
            # print("internship_apply_all=============")
            view_id = self.env.ref("internship_program.internship_program_take_action_view_form").id
            # filtered_inprogress_data = self.internship_completion_details_ids.filtered(lambda x : x.internship_status == 'In Progress')
            # print(filtered_inprogress_data,"filtered_inprogress_data===============")
            
            # if filtered_inprogress_data:
            action = {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'employee_take_action_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'current_ids': [rec.id for rec in self.internship_completion_details_ids if rec.internship_status == 'In Progress']}
            }
            return action

    def action_internship_approve_all_managers(self):
        if self._context.get('button') == 'internship_approve_all':
            # print("internship_approve_all=============")
            view_id = self.env.ref("internship_program.internship_program_take_action_view_form").id
            filtered_inprogress_data = self.internship_completion_details_ids.filtered(lambda x: x.internship_status == 'Applied')
            # print(filtered_inprogress_data,"filtered_inprogress_data===============")
            
            if filtered_inprogress_data:
                action = {
                    'name': 'Take Action',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee_take_action_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': {'current_ids': [record.id for record in filtered_inprogress_data]}
                }
                # print(action, "------------------->>>>>>>>>>>>>>>>>>>....")
                return action

    def batches_take_action(self):
        view_id = self.env.ref("internship_program.employee_take_action_view_form").id
        filtered_applied_data = self.env['lk_batch_details'].sudo().search([('traineeship_status', '=', 'Applied')])
        # print(filtered_applied_data,"filtered_applied_data====================")
        if filtered_applied_data:
            action = {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'employee_take_action_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'current_ids': [record.id for record in filtered_applied_data]}
            }
            return action

    def check_enable_editing(self):
        if self.env.user.has_group('internship_program.group_rh_internship_program'):
            self.rh_check_bool = True
        else:
            self.rh_check_bool = False

    def action_apply_all_manager(self):
        form_view_id = self.env.ref("internship_program.remarks_manager_view_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'traineeship_submit_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def action_notify_to_rh_traineeship_approve(self):
        template = self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied=[]
            for recc in self.training_completion_details_ids:
                if recc.traineeship_status == 'Applied':
                    records_applied.append({'name': recc.employee_id.name,
                                            'employee_code':recc.employee_id.emp_code,
                                            'designation': recc.deg_id.name,
                                            'date_of_joining': recc.doj.strftime("%d-%b-%Y"),
                                            'status': recc.traineeship_status,
                                            'score': recc.traineeship_score,
                                            'comments': recc.traineeship_comments_applied})

            rh_users = self.env.ref('internship_program.group_rh_internship_program').users
            name = ','.join(rh_users.mapped("name")) if rh_users else ''
            email_to = ','.join(rh_users.mapped("email")) if rh_users else ''

            # users = self.env['res.users'].sudo().search([])
            # rh_emp = users.filtered(lambda user: user.has_group('internship_program.group_rh_internship_program') == True)
            # name = ",".join(rh_emp.mapped('name')) or ''
            # email_to = ",".join(rh_emp.mapped('email')) or ''

            email_from = self.env.user.employee_ids.work_email
            subject = "Applied traineeship Program"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='applied',
                                                                              subject=subject,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to RH successfully.")

    def action_notify_to_manager_traineeship_approve(self):
        template = self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied = []
            for recc in self.training_completion_details_ids:
                if recc.traineeship_status == 'Approved':
                    records_applied.append({'name': recc.employee_id.name,
                                            'employee_code': recc.employee_id.emp_code,
                                            'designation': recc.deg_id.name,
                                            'date_of_joining': recc.doj.strftime("%d-%b-%Y"),
                                            'status': recc.traineeship_status,
                                            'score': recc.traineeship_score,
                                            'comments': recc.traineeship_comments_applied})

            manager_users = self.env.ref('internship_program.group_manager_internship_program').users
            name = ','.join(manager_users.mapped("name")) if manager_users else ''
            email_to = ','.join(manager_users.mapped("email")) if manager_users else ''

            payroll_users = self.env.ref('hr_payroll.group_hr_payroll_manager').users
            email_cc = ','.join(payroll_users.mapped("email")) if payroll_users else ''

            # users = self.env['res.users'].sudo().search([])
            # rh_emp = users.filtered(lambda user: user.has_group('internship_program.group_manager_internship_program') == True)
            # payroll_manager = users.filtered(lambda user: user.has_group('hr_payroll.group_hr_payroll_manager') == True)
            # email_cc = ",".join(payroll_manager.mapped('email')) or ''
            # name = ",".join(rh_emp.mapped('name')) or ''
            # email_to = ",".join(rh_emp.mapped('email')) or ''

            email_from = self.env.user.employee_ids.work_email
            email_content = "The Internship program (upon completion of 3 months training) has been approved for the members listed below. Please check and update their pay structure."
            subject = "Internship Program (Upon completion of 3 months training) | Approved"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='approved',
                                                                              email_cc=email_cc,
                                                                              subject=subject,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name,
                                                                              email_content=email_content).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to manager successfully.")

    def action_notify_to_rh_internship_approve(self):
        template = self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied = []
            for recc in self.internship_completion_details_ids:
                if recc.internship_status == 'Applied':
                    records_applied.append({'name': recc.employee_id.name,
                                            'designation': recc.deg_id.name,
                                            'date_of_joining': recc.doj.strftime("%d-%b-%Y"),
                                            'status': recc.internship_status,
                                            'score': recc.internship_score,
                                            'comments': recc.internship_comments_applied})

            rh_users = self.env.ref('internship_program.group_rh_internship_program').users
            name = ','.join(rh_users.mapped("name")) if rh_users else ''
            email_to = ','.join(rh_users.mapped("email")) if rh_users else ''

            # users = self.env['res.users'].sudo().search([])
            # rh_emp = users.filtered(lambda user: user.has_group('internship_program.group_rh_internship_program') == True)
            # name = ",".join(rh_emp.mapped('name')) or ''
            # email_to = ",".join(rh_emp.mapped('email')) or ''

            email_from = self.env.user.employee_ids.work_email
            subject = "Applied internship batch Program"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='internship_applied',
                                                                              subject=subject,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to RH successfully.")
            
    def action_notify_to_manager_internship_approve(self):
        template=self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied = []
            for recc in self.internship_completion_details_ids:
                if recc.internship_status == 'Approved':
                    records_applied.append({'name': recc.employee_id.name,
                                            'employee_code':recc.employee_id.emp_code,
                                            'designation': recc.deg_id.name,
                                            'date_of_joining': recc.doj.strftime("%d-%b-%Y"),
                                            'status': recc.internship_status,
                                            'score': recc.internship_score,
                                            'comments': recc.internship_comments_applied})

            manager_users = self.env.ref('internship_program.group_manager_internship_program').users
            name = ','.join(manager_users.mapped("name")) if manager_users else ''
            email_to = ','.join(manager_users.mapped("email")) if manager_users else ''

            payroll_users = self.env.ref('hr_payroll.group_hr_payroll_manager').users
            email_cc = ','.join(payroll_users.mapped("email")) if payroll_users else ''

            # users = self.env['res.users'].sudo().search([])
            # payroll_manager = users.filtered(lambda user: user.has_group('hr_payroll.group_hr_payroll_manager') == True)
            # email_cc = ",".join(payroll_manager.mapped('email')) or ''
            # manager_emp = users.filtered(lambda user: user.has_group('internship_program.group_manager_internship_program') == True)
            # name = ",".join(manager_emp.mapped('name')) or ''
            # email_to = ",".join(manager_emp.mapped('email')) or ''

            email_from = self.env.user.employee_ids.work_email
            email_content = "The Internship program (upon completion of 12 months) has been approved for the members listed below. Please check and update their pay structure."
            subject = "Internship Program (Upon completion of 12 months) | Approved"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='internship_approved',
                                                                              subject=subject,
                                                                              email_cc=email_cc,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name,
                                                                              email_content=email_content).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to manager successfully.")

    def action_apply_internship_all_manager(self):
        form_view_id = self.env.ref("internship_program.remarks_manager_view_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'traineeship_submit_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def action_approve_all(self):
        form_view_id = self.env.ref("internship_program.remarks_rh_view_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'traineeship_submit_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def get_approve_all_internship(self):
        form_view_id = self.env.ref("internship_program.remarks_rh_view_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'traineeship_submit_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def compute_ctc_revise_payroll_traineeship(self):
        if self._context.get('button') == 'ctc_traineeship':
            lk_batch_data = self.env['lk_batch_details'].sudo().search([])
            for data in lk_batch_data:
                training_complete_data = data.effective_from_date
                emp_id = data.employee_id
                applicant_ctc = self.env['hr.applicant.offer'].search(
                    [('applicant_id', '=', emp_id.onboarding_id.applicant_id.id)])
                contract_data = self.env['hr.contract'].sudo().search([('employee_id', '=', emp_id.id)])

                if applicant_ctc:
                    # if training_complete_data and training_complete_data != 'False':
                    #     emp_query = f"UPDATE hr_employee SET training_completion_date = '{training_complete_data}' WHERE id = {data.employee_id.id}"
                    #     self._cr.execute(emp_query)
                    
                    data.traineeship_current_ctc = applicant_ctc.revised_amount
                    data.gratuity_enable = applicant_ctc.gratuity_applicable
                    data.pf_enable = applicant_ctc.avail_pf_benefit
                    data.pf_deduction = applicant_ctc.pf_deduction
                if contract_data:
                    for rec in contract_data:
                        data.enable_epf = rec.enable_epf
                        data.pf_deduction = rec.pf_deduction 
                        data.eps_enable = rec.eps_enable
                        data.enable_gratuity = rec.enable_gratuity
                        data.esi_applicable = rec.esi_applicable

                for record in applicant_ctc:
                    offer_details = self.env['offer.details'].sudo().search([("offer_id", '=', record.id)])
                    for offer in offer_details:
                        if offer.code == 'basic':
                            data.traineeship_emp_basic = offer.per_month
                        elif offer.code == 'hra':
                            data.traineeship_emp_hra = offer.per_month
                        elif offer.code == 'conv':
                            data.traineeship_emp_conv = offer.per_month
                        elif offer.code == 'pb':
                            data.traineeship_emp_pb = offer.per_month
                        elif offer.code == 'cb':
                            data.traineeship_emp_cb = offer.per_month
                        else:
                            pass

    def compute_ctc_revise_payroll_internship(self):
        for rec in self:
            ctc = rec.current_ctc_internship
            if ctc < 1:
                raise ValidationError("Please enter CTC more than zero(0).")
            # print('ctc >>> ', ctc)
            for emp in rec.internship_completion_payroll_details_ids:
                offer_letter = self.env['hr.applicant.offer'].search(
                    [('applicant_id', '=', emp.employee_id.onboarding_id.applicant_id.id)])
                if offer_letter.exists():
                    ctc = offer_letter.annual_amount / 12
                    rec.current_ctc_internship = ctc
                    rec.internship_emp_basic_percentage = offer_letter.update_basic
                # print('ctc 2 >>> ', ctc)
                emp.internship_current_ctc = ctc
        # lk_batch_data = self.env['lk_batch_details'].sudo().search([])
        # for data in lk_batch_data:
        #     data
            # emp_id = data.employee_id

            # applicant_ctc = self.env['hr.applicant.offer'].search(
            #     [('applicant_id', '=', emp_id.onboarding_id.applicant_id.id)])
            #
            # if applicant_ctc:
            #     data.internship_current_ctc = applicant_ctc.annual_amount / 12
                # print(data.internship_current_ctc,"data.traineeship_current_ctc==============")
            
            # for rec in self.training_completion_payroll_details_ids:
            # traineeship_ctc = 
            # print("applicant offer 1 >> ", rec.employee_id, rec.employee_id.onboarding_id, rec.employee_id.onboarding_id.applicant_id)
            # print("applicant offer 2 >> ", rec.employee_id.onboarding_id.applicant_id.offer_id)
            # print("applicant offer 3 >> ", rec.employee_id.onboarding_id.applicant_id.offer_id.exists())
            # rec.traineeship_current_ctc = self.current_ctc_traineeship
    def compute_revise_payroll_internship(self):
        for rec in self:
            training_data = rec.training_completion_payroll_details_ids
            # print("training_data >>>> ", training_data)
            for emp in rec.internship_completion_payroll_details_ids:
                monthly_ctc = emp.internship_current_ctc
                basic_percentage = emp.internship_emp_basic_percentage if emp.internship_emp_basic_percentage > 0 else 35
                basic = (monthly_ctc * basic_percentage) / 100
                emp.internship_emp_basic = basic
                emp.internship_emp_hra = (basic * 40) / 100
                emp.internship_emp_conv = (basic * 10) / 100
                sum_month = emp.internship_emp_basic + emp.internship_emp_hra + emp.internship_emp_conv
                emp.internship_emp_pb = math.ceil((monthly_ctc - sum_month) / 2)
                emp.internship_emp_cb = math.floor((monthly_ctc - sum_month) / 2)

                training_rec = training_data.filtered(lambda x: x.employee_id==emp.employee_id)
                # print("training_rec >> ", training_rec)
                emp.internship_gratuity_enable = training_rec.gratuity_enable
                emp.internship_pf_enable = training_rec.pf_enable
                emp.internship_enable_epf = training_rec.enable_epf
                emp.internship_pf_deduction = training_rec.pf_deduction
                emp.internship_eps_enable = training_rec.eps_enable
                emp.internship_enable_gratuity = training_rec.enable_gratuity
                emp.internship_esi_applicable = training_rec.esi_applicable


    def compute_revise_payroll_traineeship(self):
        form_view_id = self.env.ref("internship_program.traineeship_program_payrevies_view_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pay Revise',
            'res_model': 'employee_take_action_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'current_ids': [rec.id for rec in self.training_completion_payroll_details_ids if rec.traineeship_status == 'Approved']}
        }
        # for rec in self.training_completion_details_ids:
        #     if rec.traineeship_current_ctc:
        #         emp_basic = (rec.traineeship_current_ctc * 35) / 100
        #         emp_hra = (emp_basic * 40) / 100
        #         emp_conv = (emp_basic * 10) / 100
        #         sum_month = emp_basic + emp_hra + emp_conv
        #         rec.traineeship_emp_basic = emp_basic
        #         rec.traineeship_emp_hra = emp_hra
        #         rec.traineeship_emp_conv = emp_conv
        #         rec.traineeship_emp_pb = math.ceil((rec.traineeship_current_ctc - sum_month) / 2)
        #         rec.traineeship_emp_cb = math.floor((rec.traineeship_current_ctc - sum_month) / 2)

    def _get_payrevies_all_traineeship(self):
        if all(status.traineeship_status in ['Pay Revised'] for status in self.training_completion_payroll_details_ids):
            self.pay_revies_all_bool = True
        else:
            self.pay_revies_all_bool = False
            
    def traineeship_department_change_btn(self):
        form_view_id = self.env.ref("internship_program.employee_dept_change_view_form").id
        if self.env.context.get('current_id'):
            filtered_pay_revies_data = self.env['lk_batch_details'].sudo().search(
                [('batch_id', '=', self.env.context.get('current_id')),
                 ('traineeship_status', 'in', ['Approved', 'Pay Revised']),
                 ('change_dept_bool', '=', False)])
            if not all(rec.change_dept_bool in [True] for rec in self.training_completion_payroll_details_ids):
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Change Department',
                    'res_model': 'employee_take_action_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                    'context': {'current_ids': [record.id for record in filtered_pay_revies_data]}
                }
            else:
                self.env.user.notify_success(message='No records found to update!')
                
    # def traineeship_complete_change_btn(self):
    #     form_view_id = self.env.ref("internship_program.employee_traineeship_date_change_view_form").id
    #     if self.env.context.get('current_id'):
    #         filtered_trainee_data = self.env['lk_batch_details'].sudo().search(
    #             [('batch_id', '=', self.env.context.get('current_id')),
    #              ('traineeship_status', 'in', ['Approved', 'Pay Revised']),
    #              ('change_dept_bool', '=', True),
    #              ('employee_id.training_completion_date', '=', False)])
    #         if filtered_trainee_data:
    #             return {
    #                 'type': 'ir.actions.act_window',
    #                 'name': 'Update Date',
    #                 'res_model': 'employee_take_action_wizard',
    #                 'view_mode': 'form',
    #                 'view_type': 'form',
    #                 'view_id': form_view_id,
    #                 'target': 'new',
    #                 'context': {'current_ids': [record.id for record in filtered_trainee_data]}
    #             }
    #         else:
    #             self.env.user.notify_success(message='No records found to update!')

    def locked_for_no_edit(self):
        for rec in self:
            rec.locked_bool = True

    def unlocked_for_edit(self):
        for rec in self:
            rec.locked_bool = False


class LearningAndKnowledgeData(models.Model):
    """
    Model representing learning and knowledge data.

    This class defines a model for managing training and internship employee data within the system.
    It provides functionalities for storing and manipulating data related to training batches,
    internship details, and employee records associated with learning and knowledge initiatives.
    """
    _name = "lk_batch_details"
    _description = "Training and Internship employee"

    batch_id = fields.Many2one("lk_batch", string="Details")
    internship_id = fields.Many2one('lk_batch', string="Details")
    lk_payroll = fields.Many2one('lk_batch')
    lk_payroll_internship = fields.Many2one('lk_batch')

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    employee_name = fields.Char(string="Name", related="employee_id.name")
    employee_code = fields.Char(string="Emp Code", related="employee_id.emp_code")
    employee_current_ctc = fields.Float(string="Current CTC", related="employee_id.current_ctc")
    deg_id = fields.Many2one('hr.job', string='Designation', related="employee_id.job_id")
    doj = fields.Date(string="Date of Joining", related="employee_id.date_of_joining")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',
                                    string='Department', store=True)
    new_dept_id = fields.Many2one('hr.department', string='New Department',
                                  domain=[('dept_type.code', '=', 'department')])
    new_division_id = fields.Many2one('hr.department', string="New Division", domain="[('parent_id','=',new_dept_id)]")
    effective_from_date = fields.Date('Effective From')
    gratuity_enable = fields.Boolean('Gratuity Enable')
    pf_enable = fields.Boolean('PF Enable')
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")
    pf_deduction = fields.Selection([('basicper', "12% of basic"), ('avail1800', 'Flat 1,800/-')],
                                    string='PF Deduction')
    eps_enable = fields.Boolean("Enable EPS", track_visibility='always')
    enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity")
    esi_applicable = fields.Boolean(string='ESI APPLICABLE')

    increment_pattern = fields.Selection(string="Increment Pattern",
                                         selection=[('Phase Wise', 'Phase Wise'), ('Yearly', 'Yearly')])

    traineeship_applied_date = fields.Date(string="Training Applied Date")
    traineeship_completion_date = fields.Date(string="Training Completion Date")
    traineeship_score = fields.Float(string="Score")
    traineeship_comments_applied = fields.Char(string="L&K Feedback")
    traineeship_comments_approved = fields.Char(string="RH Feedback")
    traineeship_status = fields.Selection(string="Status", default="In Progress",
                                          selection=[('In Progress', 'In Progress'),
                                                     ('Applied', 'Applied'),
                                                     ('Approved', 'Approved'),
                                                     ('Rejected', 'Rejected'),
                                                     ('Pay Revised', 'Pay Revised')])
    traineeship_complete_check = fields.Boolean(string="traineeship_complete_check", default=False)
    traineeship_current_ctc = fields.Float(string="CTC")
    traineeship_emp_basic = fields.Float(string='Basic')
    traineeship_emp_hra = fields.Float(string="HRA")
    traineeship_emp_conv = fields.Float(string="Conveyance")
    traineeship_emp_pb = fields.Float(string="PB")
    traineeship_emp_cb = fields.Float(string="CB")
    traineeship_emp_esi = fields.Float(string="ESI")
    traineeship_emp_tax = fields.Float(string="Professional Tax")

    internship_applied_date = fields.Date(string="Internship Applied Date")
    internship_completion_date = fields.Date(string="Internship Completion Date")
    internship_score = fields.Float(string="Score")
    internship_comments_applied = fields.Char(string="L&K Feedback")
    internship_comments_approved = fields.Char(string="RH Feedback")
    internship_status = fields.Selection(string="Status", default="In Progress",
                                         selection=[('In Progress', 'In Progress'), ('Applied', 'Applied'),
                                                    ('Approved', 'Approved'),
                                                    ('Rejected', 'Rejected'),
                                                    ('Pay Revised', 'Payroll Revised')])
    internship_complete_check = fields.Boolean(string="internship_complete_check", default=False)
    internship_current_ctc = fields.Float(string="CTC")
    internship_emp_basic_percentage = fields.Float(string='Basic %')
    internship_emp_basic = fields.Float(string='Basic')
    internship_emp_hra = fields.Float(string="HRA")
    internship_emp_conv = fields.Float(string="Conveyance")
    internship_emp_pb = fields.Float(string="PB")
    internship_emp_cb = fields.Float(string="PB")
    internship_emp_esi = fields.Float(string="ESI")
    internship_emp_tax = fields.Float(string="Tax")

    internship_gratuity_enable = fields.Boolean('Gratuity Enable')
    internship_pf_enable = fields.Boolean('PF Enable')
    internship_enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")
    internship_pf_deduction = fields.Selection([('basicper', "12% of basic"), ('avail1800', 'Flat 1,800/-')],
                                               string='PF Deduction')
    internship_eps_enable = fields.Boolean("Enable EPS", track_visibility='always')
    internship_enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity")
    internship_esi_applicable = fields.Boolean(string='ESI APPLICABLE')
    internship_pay_revise_success_bool = fields.Boolean(string="Pay Revise Successfully", default=False)

    rh_check = fields.Boolean(compute="check_boolean_field", store=False)
    hide_button_applied = fields.Boolean(string="hide_button_applied", default=False)
    hide_button_intern_compl = fields.Boolean(string="hide_button_intern_compl", default=False)
    pay_revise_success_bool = fields.Boolean(string="Pay Revise Successfully", default=False)
    change_dept_bool = fields.Boolean(string="Change dept", default=False)

    @api.onchange('new_dept_id')
    def _onchange_new_dept_id(self):
        for rec in self:
            if rec.new_dept_id:
                rec.new_division_id = False

    def check_boolean_field(self):
        for rec in self:
            if self.env.user.has_group('internship_program.group_rh_internship_program'):
                rec.rh_check = True
            else:
                rec.rh_check = False

    def training_completion_check(self):
        if self.traineeship_comments_applied is False or self.traineeship_score <= 0:
            raise ValidationError("Please give score and comment to apply for traineeship completion.")

        self.write({'traineeship_status': 'Applied',
                    'traineeship_applied_date': date.today(),
                    'hide_button_applied': True})
        # self.batch_id = self.batch_id.id 

    def traineeship_approved_by_rh(self):
        if self._context.get('button') == 'approve':
            form_view_id = self.env.ref("internship_program.remarks_rh_view_form").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm',
                'res_model': 'traineeship_submit_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
            }
        elif self._context.get('button') == 'reject':
            form_view_id = self.env.ref("internship_program.remarks_rh_reject_view_form").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reject',
                'res_model': 'traineeship_submit_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
            }

    def internship_completion_check(self):
        if self.internship_score <= 0.0 or self.internship_comments_applied == False:
            raise ValidationError("You can't complete internship program  without score and comments.")
        else:
            self.write({'internship_status': 'Applied',
                        'internship_applied_date': date.today(),
                        'hide_button_intern_compl': True,
                        'internship_id': self.internship_id.id
                        })
        # self.internship_id = self.internship_id.id

    def internship_approved_by_rh(self):
        if self._context.get('button') == 'approve_rh_internship':
            if self.internship_status == 'In Progress' and self.internship_score == 0.0:
                raise ValidationError("You cannot complete this internship program.")
            form_view_id = self.env.ref("internship_program.remarks_rh_view_form").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm',
                'res_model': 'traineeship_submit_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
            }
        elif self._context.get('button') == 'reject_rh_internship':
            if self.internship_status == 'In Progress' and self.internship_score == 0.0:
                raise ValidationError("You cannot complete this internship program.")
            form_view_id = self.env.ref("internship_program.remarks_rh_reject_view_form").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reject',
                'res_model': 'traineeship_submit_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
            }

    @api.onchange('traineeship_score')
    def onchange_traineeship_score(self):
        for rec in self:
            if rec.traineeship_score >= 60:
                rec.traineeship_comments_applied = 'Completed'
            elif 50 <= rec.traineeship_score < 60:
                rec.traineeship_comments_applied = 'Hold'
            elif rec.traineeship_score < 50:
                rec.traineeship_comments_applied = 'Close'

    @api.onchange('internship_score')
    def onchange_internship_score(self):
        for rec in self:
            if rec.internship_score >= 60:
                rec.internship_comments_applied = 'Completed'
            elif 50 <= rec.internship_score < 60:
                rec.internship_comments_applied = 'Hold'
            elif rec.internship_score < 50:
                rec.internship_comments_applied = 'Close'
                
    def trainee_department_change_btn(self):
        form_view_id = self.env.ref("internship_program.employee_dept_change_view_form").id
        if self.env.context.get('current_id'):
            filtered_pay_revies_data = self.env['lk_batch_details'].sudo().search(
                [('id', '=', self.env.context.get('current_id')),
                 ('traineeship_status', 'in', ['Approved', 'Pay Revised']),
                 ('change_dept_bool', '=', False)])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Change Department',
                'res_model': 'employee_take_action_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
                'context': {'current_ids': [record.id for record in filtered_pay_revies_data]}
            }
            
    def payroll_revise_check(self):
        for rec in self:
            emp_record = rec.employee_id
            employee_id = emp_record.id
            emp_data = {
                'current_ctc': rec.traineeship_current_ctc,
                'current_basic': rec.traineeship_emp_basic,
                'hra': 40 if not emp_record.hra > 0 else emp_record.hra,  # rec.traineeship_emp_hra,
                'conveyance': 10 if not emp_record.conveyance > 0 else emp_record.conveyance,  # rec.traineeship_emp_conv,
                'productivity': rec.traineeship_emp_pb,
                'commitment': rec.traineeship_emp_cb,
                # 'department_id': rec.new_dept_id.id if rec.new_dept_id else '',
                # 'division': rec.new_division_id.id if rec.new_division_id else ''
            }
            # if not emp_record.hra > 0:
            #     emp_data['hra'] = 40
            # if not emp_record.conveyance > 0:
            #     emp_data['conveyance'] = 10
            # emp_record.write(emp_data)
            query = f"UPDATE hr_employee SET current_ctc={emp_data['current_ctc']}, current_basic={emp_data['current_basic']}, productivity={emp_data['productivity']}, commitment={emp_data['commitment']}, hra={emp_data['hra']}, conveyance={emp_data['conveyance']} WHERE id={employee_id};"
            self._cr.execute(query)

            contract_record = self.env['hr.contract'].search([('employee_id', '=', employee_id)])
            if contract_record.exists():
                contract_data = {
                    'wage': rec.traineeship_current_ctc,
                    'current_basic': rec.traineeship_emp_basic,
                    'productivity': rec.traineeship_emp_pb,
                    'commitment': rec.traineeship_emp_cb,
                }
                # 'house_rent_allowance_metro_nonmetro': rec.traineeship_emp_hra,
                # 'conveyance': rec.traineeship_emp_conv,
                if not contract_record.house_rent_allowance_metro_nonmetro > 0:
                    contract_data['house_rent_allowance_metro_nonmetro'] = 40
                if not contract_record.conveyance > 0:
                    contract_data['conveyance'] = 10
                contract_record.write(contract_data)

            # rec.batch_id.write({'internship_completion_details_ids':[[0,0,
            # {'employee_id': rec.employee_id.id,
            # 'new_dept_id':rec.new_dept_id.id,
            # 'new_division_id':rec.new_division_id.id}]],
            # 'internship_id':rec.batch_id.id})
            rec.write({'pay_revise_success_bool': True,
                       'change_dept_bool': True,
                       'traineeship_status': 'Pay Revised',
                       'internship_id': rec.batch_id.id})

        self.env.user.notify_success(message='Salary Updated successfully!')
    def internship_payroll_revise_check(self):
        for rec in self:
            emp_record = rec.employee_id
            employee_id = emp_record.id
            emp_data = {
                'current_ctc': rec.internship_current_ctc,
                'current_basic': rec.internship_emp_basic,
                'hra': 40 if not emp_record.hra > 0 else emp_record.hra,  # rec.traineeship_emp_hra,
                'conveyance': 10 if not emp_record.conveyance > 0 else emp_record.conveyance,  # rec.traineeship_emp_conv,
                'productivity': rec.internship_emp_pb,
                'commitment': rec.internship_emp_cb,
            }

            query = f"UPDATE hr_employee SET current_ctc={emp_data['current_ctc']}, current_basic={emp_data['current_basic']}, productivity={emp_data['productivity']}, commitment={emp_data['commitment']}, hra={emp_data['hra']}, conveyance={emp_data['conveyance']} WHERE id={employee_id};"
            self._cr.execute(query)

            contract_record = self.env['hr.contract'].search([('employee_id', '=', employee_id)])
            if contract_record.exists():
                contract_data = {
                    'is_consolidated': False,
                    'wage': rec.internship_current_ctc,
                    'current_basic': rec.internship_emp_basic,
                    'productivity': rec.internship_emp_pb,
                    'commitment': rec.internship_emp_cb,
                }
                if not contract_record.house_rent_allowance_metro_nonmetro > 0:
                    contract_data['house_rent_allowance_metro_nonmetro'] = 40
                if not contract_record.conveyance > 0:
                    contract_data['conveyance'] = 10
                contract_record.write(contract_data)

            rec.write({'internship_pay_revise_success_bool': True,
                       'internship_status': 'Pay Revised'})

        self.env.user.notify_success(message='Salary Updated successfully!')

    def payroll_revise_traineeship_notify_emp(self):
        template = self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied = []
            records_applied.append({'name': self.employee_name,
                                    'designation': self.deg_id.name,
                                    'date_of_joining': self.doj.strftime("%d-%b-%Y"),
                                    'CTC': self.traineeship_current_ctc,
                                    'basic': self.traineeship_emp_basic,
                                    'emp_hra': self.traineeship_emp_hra,
                                    'emp_conv': self.traineeship_emp_conv,
                                    'emp_pb': self.traineeship_emp_pb,
                                    'emp_cb': self.traineeship_emp_cb,
                                    })
          
            email_to = self.employee_id.work_email
            name = self.employee_name
            # email_cc = ",".join(rh_emp.mapped('email')) + ",".join(payroll_manager.mapped('email')) or ''
            email_from = self.env.user.employee_ids.work_email
            subject = "Pay Revise Foundation Program"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='pay_revise_traineeship',
                                                                              subject=subject,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name).send_mail(self.batch_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to employee successfully.")

    def payroll_revise_internship_notify_emp(self):
        template = self.env.ref("internship_program.mail_to_rh_manager_template")
        if template:
            records_applied = []
            records_applied.append({'name': self.employee_name,
                                    'designation': self.deg_id.name,
                                    'date_of_joining': self.doj.strftime("%d-%b-%Y"),
                                    'CTC': self.internship_current_ctc,
                                    'basic': self.internship_emp_basic,
                                    'emp_hra': self.internship_emp_hra,
                                    'emp_conv': self.internship_emp_conv,
                                    'emp_pb': self.internship_emp_pb,
                                    'emp_cb': self.internship_emp_cb
                                    })
          
            email_to = self.employee_id.work_email
            name = self.employee_name
            # email_cc = ",".join(rh_emp.mapped('email')) + ",".join(payroll_manager.mapped('email')) or ''
            email_from = self.env.user.employee_ids.work_email
            subject = "Pay Revise Internship Program"
            mail = self.env['mail.template'].browse(template.id).with_context(mail_for='pay_revise_internship',
                                                                              subject=subject,
                                                                              email_to=email_to,
                                                                              email_from=email_from,
                                                                              records=records_applied,
                                                                              name=name).send_mail(self.internship_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Notified to employee successfully.")
            
    def update_employee_joined_as(self):
        emp_details_rec = self.env['lk_batch_details'].search([('employee_id.joining_type', '!=', 'Intern')]).mapped('employee_id')
        # print('emp_details_rec >>>> ', emp_details_rec)

        # for emp_data in emp_details_rec:
        #     print('emp_data >>>> ', emp_data.name)
        #     if emp_data.joining_type != 'Intern':
        #         emp_data.write({'joining_type': 'Intern'})
        if emp_details_rec.exists():
            employee_ids = ','.join(str(i) for i in emp_details_rec.ids)
            query = f"UPDATE hr_employee SET joining_type='Intern' WHERE id in ({employee_ids});"
            # print("employee_ids >>> ", employee_ids, query)
            self.env.cr.execute(query)
        return True


class DownloadEmployeePayreviseReport(models.TransientModel):
    """
    Wizard for downloading employee pay revision details report.

    This class represents a transient model used for generating and downloading reports
    containing details of employee pay revisions.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): Description of the model.
    """
    _name = "employee_pay_revies_details_report_download"
    _description = "Employee Details Download Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadEmployeePayreviseReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'payrevies_emp_details_ids': active_ids,
        })

        return res

    payrevies_emp_details_ids = fields.Many2many(string='Details',
                                                 comodel_name='lk_batch',
                                                 relation='emp_payrevies_download_rel',
                                                 column1='payrevise_id',
                                                 column2='download_id',
                                                 )
    download_file = fields.Binary(string="Download Xls")

    @api.multi
    def download_emp_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        date_default_col1_style = workbook.add_format({'font_size': 12, 'align': 'center', 'num_format': 'yyyy-mm-dd'})
        date_default_col1_style.set_border()

        cell_text_format_n = workbook.add_format({'align': 'left', 'bold': False, 'size': 9})
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': True, 'size': 11})
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': False, 'size': 12})
        cell_text_format.set_border()

        cell_text_amount_format = workbook.add_format({'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_text_amount_format.set_border()

        cell_total_amount_format = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_total_amount_format.set_border()

        cell_number_total_format = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, 'num_format': '########'})
        cell_number_total_format.set_border()

        worksheet = workbook.add_worksheet(f'Employee Role and Category wise report')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_column('K:K', 30)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 30)
        worksheet.set_column('N:N', 30)

        row = 0
        worksheet.write(row, 0, 'Financial Year', cell_number_total_format)
        worksheet.write(row, 1, 'Batch Name', cell_text_center_normal)
        worksheet.write(row, 2, 'MRF', cell_text_center_normal)
        worksheet.write(row, 3, 'Employee Name', cell_text_center_normal)
        worksheet.write(row, 4, 'Employee Code', cell_text_center_normal)
        worksheet.write(row, 5, 'Department', cell_text_center_normal)
        worksheet.write(row, 6, 'Designation', cell_text_center_normal)
        worksheet.write(row, 7, 'Date of Joining', cell_text_center_normal)
        worksheet.write(row, 8, 'CTC', cell_total_amount_format)
        worksheet.write(row, 9, 'Basic', cell_total_amount_format)
        worksheet.write(row, 10, 'HRA', cell_total_amount_format)
        worksheet.write(row, 11, 'Conveyance', cell_total_amount_format)
        worksheet.write(row, 12, 'PB(Productivity Allowance)', cell_total_amount_format)
        worksheet.write(row, 13, 'CB(Commitment Allowance)', cell_total_amount_format)
        worksheet.write(row, 14, 'PF Deduction', cell_text_center_normal)
        
        prev_group_key = None  # Track the previous group
        row += 1
        col = 0

        for formb in self.payrevies_emp_details_ids:
            for data in formb.training_completion_payroll_details_ids:
                group_key = (formb.financial_year_id.name, formb.name, formb.mrf_id.code)
                if group_key != prev_group_key:
                    # Print group information
                    worksheet.write(row, col, formb.financial_year_id.name, cell_number_total_format)
                    worksheet.write(row, col + 1, formb.name, cell_text_format)
                    worksheet.write(row, col + 2, formb.mrf_id.code, cell_text_format)
                    prev_group_key = group_key
                else:
                    # Leave empty for the grouped cells
                    worksheet.write(row, col, '', cell_number_total_format)
                    worksheet.write(row, col + 1, '', cell_text_format)
                    worksheet.write(row, col + 2, '', cell_text_format)

                # Print employee details
                worksheet.write(row, col + 3, data.employee_name, cell_text_format)
                worksheet.write(row, col + 4, data.employee_code, cell_text_format)
                
                worksheet.write(row, col + 5, data.new_dept_id.name, cell_text_format)
                worksheet.write(row, col + 6, data.deg_id.name, cell_text_format)
                worksheet.write(row, col + 7, data.doj, date_default_col1_style)
                worksheet.write(row, col + 8, data.traineeship_current_ctc, cell_total_amount_format)
                worksheet.write(row, col + 9, data.traineeship_emp_basic, cell_total_amount_format)
                worksheet.write(row, col + 10, data.traineeship_emp_hra, cell_total_amount_format)
                worksheet.write(row, col + 11, data.traineeship_emp_conv, cell_total_amount_format)
                worksheet.write(row, col + 12, data.traineeship_emp_pb, cell_total_amount_format)
                worksheet.write(row, col + 13, data.traineeship_emp_cb, cell_total_amount_format)
                worksheet.write(row, col + 14, data.pf_deduction, cell_text_format)
                
                row += 1

        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/employee_pay_revies_details_report_download/%s/download_file/Employee_Pay_Revise_Details.xls?download=true' % (self.id)
        }

    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
