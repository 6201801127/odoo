# -*- coding: utf-8 -*-
import json
from ast import literal_eval
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import requests
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from _datetime import date
from kw_utility_tools import kw_validations


class kw_resignation(models.Model):
    _name = "kw_resignation"
    _description = "Offboarding"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = "offboarding_type"

    def _compute_manager_groups(self):
        for res in self:
            print("compute manager group called=====================================",res)
            if res.state == 'apply' and self.env.user.employee_ids.id == res.applicant_id.parent_id.id:
                res.show_btn_apply = True
                print("inside first if of compute manager grpiups======================",res.show_btn_apply)
            if res.state == 'apply' and self.env.user.employee_ids.id == res.applicant_id.parent_id.id \
                    and res.cancel_process == True:
                res.show_cancel_apply = True
            if res.state == 'forward' and self.env.user.employee_ids.id == res.forward_to.id:
                res.show_btn_foward = True
            if res.state == 'forward' and self.env.user.employee_ids.id == res.forward_to.id and res.cancel_process == True:
                res.show_cancel_foward = True
            if res.state == 'confirm' and self.env.user.employee_ids.id == res.applicant_id.department_id.manager_id.id:
                res.show_btn_confirm = True
            if res.state == 'confirm' and self.env.user.employee_ids.id == res.applicant_id.department_id.manager_id.id \
                    and res.cancel_process == True:
                res.show_cancel_confirm = True
            if self.env.user.employee_ids.id == res.applicant_id.department_id.manager_id.id:
                res.is_dept_manager = True
            if self.env.user.employee_ids.id == res.applicant_id.parent_id.id:
                res.is_RA = True

    @api.depends('applicant_id')
    def _get_subordinate_count(self):
        for res in self:
            if res.applicant_id:
                records = self.env['hr.employee'].search([('parent_id', '=', res.applicant_id.id)])
                res.subordinate_count += len(records)

    @api.model
    def _domain_get_ids(self):
        hr_id = self.env['kw_user_type_master'].sudo().search([('user_type', '=', 'HR')])
        employee_id = self.env['kw_user_type_master'].sudo().search([('user_type', '=', 'Employee')])
        account_manager = self.env['kw_user_type_master'].sudo().search([('user_type', '=', 'Account Manager')])
        if self.logged_user.has_group('kw_eos.group_kw_eos_manager') or self.logged_user.has_group(
                'kw_eos.group_kw_eos_officer'):
            user_type = self.env['kw_offboarding_type_master'].sudo().search([('user_type_id', 'in', hr_id.id)])

        elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') and self.env.user.has_group(
                'kw_eos.group_kw_eos_user'):
            user_type = self.env['kw_offboarding_type_master'].sudo().search(
                ['|', ('user_type_id', 'in', employee_id.id), ('user_type_id', 'in', account_manager.id)])
        else:
            user_type = self.env['kw_offboarding_type_master'].sudo().search([('user_type_id', 'in', employee_id.id)])
        return [('id', 'in', user_type.ids)]

    @api.model
    def _domain_get_resig_ids(self):
        mang_resig_id = self.env['kw_resignation_master'].sudo().search([('active', '=', True)])
        employee_resig_id = self.env['kw_resignation_master'].sudo().search([('active', '=', True),('is_visible_emp', '=', True)])
        if self.logged_user.has_group('kw_eos.group_kw_eos_manager') :
            user_type = mang_resig_id
        else:
            user_type = employee_resig_id
        return [('id', 'in', user_type.ids)]

    offboarding_type = fields.Many2one('kw_offboarding_type_master', required=True, domain=_domain_get_ids)
    offboard_type_reg = fields.Boolean(string='Offboarding Type Name')
    contract_closure = fields.Text(string="Contract Closure")
    contract_extend = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no', string='Extend')
    contract_closure_check = fields.Boolean(string='Contract Closure Check')
    contract_remark = fields.Text(string='Remark')
    start_date = fields.Date(string="Contract Start Date", related='applicant_id.start_date')
    end_date = fields.Date(string="Contract End Date", related='applicant_id.end_date')
    new_contract_end_date = fields.Date(string='New Contract End Date')
    retain = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no', string='Retain')
    ret_job_id = fields.Many2one('hr.job', string="New Job Position", track_visibility='onchange')
    ret_department_id = fields.Many2one('hr.department', string='New Department', track_visibility='onchange',
                                        domain=[('dept_type.code', '=', 'department')])
    ret_division = fields.Many2one('hr.department', string="New Division", track_visibility='onchange',
                                   domain=[('dept_type.code', '=', 'division')])
    ret_section = fields.Many2one('hr.department', string="New Practice", track_visibility='onchange',
                                  domain=[('dept_type.code', '=', 'section')])
    ret_practise = fields.Many2one('hr.department', string="New Section", domain=[('dept_type.code', '=', 'practice')])
    ret_employeement_type = fields.Many2one('kwemp_employment_type', string="Employment Type",
                                            default=lambda self: self.env['kwemp_employment_type'].sudo().search(
                                                [('code', '=', 'O')]))
    ret_contract_start_date = fields.Date(string='Contract Start Date', track_visibility='onchange')
    ret_contract_end_date = fields.Date(string='Contract End Date', track_visibility='onchange')
    new_current_ctc = fields.Integer(string="New Consolidated Amount")
    hra = fields.Integer(string="HRA(%)")
    conveyance = fields.Integer(string="Conveyance")
    current_basic = fields.Integer(string="Current Basic")
    retirement = fields.Text(string="Remark")
    retirement_check = fields.Boolean(string='Retirement Check')
    major_activity = fields.Text(string="Major Activity")
    termination = fields.Text(string="Termination")
    termination_check = fields.Boolean(string='Termination Check')
    apply_for = fields.Selection([('self', 'Self'), ('others', 'Others')], default='self', string="Apply For")
    termination_reason = fields.Many2one('kw_termination_reason_master', ondelete="restrict", string="Reasons")
    termination_remark = fields.Text(string="Remarks")
    upload_related_document = fields.Binary(string="Upload Related Document")
    document_name = fields.Char(string="Document Name")
    termination_submit_remark = fields.Text(string="Remarks")
    demise = fields.Text(string="Demise")
    demise_check = fields.Boolean(string='Demise Check')
    demise_reason = fields.Text(string="Reasons")
    name = fields.Char(string='Resignation Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    reg_type = fields.Many2one('kw_resignation_master', string="Resignation Type", ondelete="restrict",
                               track_visibility='onchange', domain=_domain_get_resig_ids)
    reason = fields.Text(string="Reason For Resignation", track_visibility='onchange')
    effective_form = fields.Date(string="Effective From", default=fields.Date.today(), track_visibility='onchange')
    last_working_date = fields.Date(string='Last Working Date', track_visibility='onchange', store=True)
    state = fields.Selection([('apply', 'Applied'),
                              ('forward', 'Forwarded'),
                              ('confirm', 'Approved'),
                              ('grant', 'Granted'),
                              ('hold', 'Hold'),
                              ('reject', 'Rejected'),
                              ('close','Closed')], string='Status', default='apply')
    sort = fields.Integer(compute='_compute_sort', store=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    logged_user = fields.Many2one('res.users', compute='_get_current_user')
    check_applicant_user_id = fields.Boolean(string="Check Applicant User Id", compute='_get_current_user')
    prev_state = fields.Char('Prev State')
    is_manager = fields.Boolean(string="Is Manager?", default=False, compute='_check_manager')
    is_finance_user = fields.Boolean(string="Is Finance User?", default=False, compute='_check_manager')

    applicant_id = fields.Many2one('hr.employee', string="Employee")
    applicant_name = fields.Char(related='applicant_id.name', string="Applicant")
    applicant_code = fields.Char(related='applicant_id.emp_code', string="Applicant Code")
    image = fields.Binary(related='applicant_id.image', string="Photo", attachment=True, store=True,
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    dept_manager_id = fields.Many2one('hr.employee')
    approval_date_dept_manager = fields.Date(string="Approved Date(Department Manager)")
    # Manager Groups
    is_dept_manager = fields.Boolean(compute='_compute_manager_groups', default=False)
    is_RA = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_btn_foward = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_btn_confirm = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_btn_apply = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_btn_hold = fields.Boolean(compute='_compute_manager_groups', default=False)
    hide_btn_cancel = fields.Boolean(default=False)
    cancel_process = fields.Boolean(default=False)
    show_cancel_foward = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_cancel_confirm = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_cancel_apply = fields.Boolean(compute='_compute_manager_groups', default=False)
    show_cancel_hold = fields.Boolean(compute='_compute_manager_groups', default=False)
    forward_by = fields.Many2one('hr.employee', string="Forwarded By", track_visibility='onchange')
    kt_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string='Schedule KT Plan')
    replacement_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Replacement Required',default='no')
    remark = fields.Text('Remarks', track_visibility=True)
    action_to_be_taken_by = fields.Char(string="Action To Be Taken By", compute='_compute_action_to_be_taken_by')
    forward_to = fields.Many2one('hr.employee', string='Forward To')
    cancel_reason = fields.Text(string="Reason for Cancellation")
    # Employee Details
    date_of_joining = fields.Date('Date of Joining', related='applicant_id.date_of_joining')
    project_list_ids = fields.Many2many('project.project', string="Projects", )
    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange',
                                    compute="_compute_details", search="_search_applicant_department")
    job_id = fields.Many2one('hr.job', string="Job Position", track_visibility='onchange', compute="_compute_details")
    division = fields.Many2one('hr.department', string="Division", compute="_compute_details",
                               track_visibility='onchange')
    section = fields.Many2one('hr.department', string=" Practice", compute="_compute_details",
                              track_visibility='onchange')
    practise = fields.Many2one('hr.department', string="Section", compute="_compute_details")
    check_kt_record = fields.Boolean(string="Check KT", compute="_compute_details")

    subordinate_count = fields.Integer(compute='_get_subordinate_count', string='Subordinates')
    total_experience_display = fields.Char('Total Experience', related='applicant_id.total_experience_display')
    kw_id = fields.Integer('KW ID', default=0)
    aprv_rl_cancel_remark = fields.Text('Remarks')
    rl_cancel_reject_remark = fields.Text('Remarks')

    retirement_document = fields.Binary(string="Upload Related Document")
    retirement_document_name = fields.Char(string="Retirement Document Name")
    retirement_submit_remark = fields.Text(string='Remark')
    retirement_reject_remark = fields.Text(string='Remark')
    done_by_finance = fields.Boolean(string='Done By Finance', default=False, compute="_check_done_by_finance")

    ra_cancel_aprv_btn_check = fields.Boolean(string='RL Cancellation Approve Check', compute='_ra_cancel_aprv_btn')
    applicant_user_id_check = fields.Boolean(string='Applicant User Id Check', compute='_ra_cancel_aprv_btn')
    dept_head_check = fields.Boolean(string="Department Head Check", compute='_ra_cancel_aprv_btn')
    check_apply_for_self = fields.Boolean(string="Check Apply For Self")
    contract_check = fields.Boolean(string="Contract Closure Check", compute='_ra_cancel_aprv_btn')
    hide_apply_for = fields.Boolean(string="Check Offboard Type")
    report_check = fields.Boolean(string='Report Check', compute='_compute_report_check')
    eos_status = fields.Char(string="EOS Status", compute="_compute_eos_status")
    check_contract_create_user = fields.Boolean(string='Contract Create user Check',
                                                compute='_compute_check_contract_create_user')
    month_last_working_date = fields.Char(string='Month', compute='_compute_month_last_working_date', store=True)
    year_last_working_date = fields.Char(string='Year', compute='_compute_year_last_working_date', store=True)
    report_employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type',
                                              track_visibility='onchange', compute="_compute_details",
                                              search="_search_emp_type")
    base_branch_id = fields.Many2one('kw_res_branch', 'Location', track_visibility='onchange',
                                     compute="_compute_details", search='_search_emp_location')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], 'Gender',
                              track_visibility='onchange', compute="_compute_details", store=True)
    ra = fields.Char('RA', track_visibility='onchange', compute="_compute_details")
    emp_role = fields.Many2one('kwmaster_role_name', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Employee Category")
    employement_type = fields.Many2one('kwemp_employment_type', string="Employment Type",
                                       default=lambda self: self.env['kwemp_employment_type'].sudo().search(
                                           [('code', '=', 'O')]))
    offboarding_process_status = fields.Char(string='Progress Status', compute='_comp_offboarding_process_status')
    read_only_for_finance = fields.Boolean(string='Read only for finance user', compute='_compute_readonly_for_finance')
    budget_submit = fields.Boolean(string='Budget Submit', default=False)
    required_effective_from = fields.Boolean(string='Required Effective From', default=True)

    """ Clearance"""
    tour_clearance = fields.Char(string='Tour Settlement Details', compute='_comp_clearance_details')
    sal_adv_clearance = fields.Char(string='Salary Advance Details', compute='_comp_clearance_details')
    petty_cash_clearance = fields.Char(string='Petty Cash Details', compute='_comp_clearance_details')
    asset_clearance = fields.Char(string='Asset Details', compute='_comp_clearance_details')
    resignation_ids = fields.One2many('kw_resignation_log', 'reg_id', string='Approval Details')
    """ hide last working days for RA """
    ra_check = fields.Boolean(string='RA check', compute='_comp_ra_check')
    current_project = fields.Char(string="Project Name", compute="compute_project")
    """ fiscal year filter """
    fiscal_yr = fields.Char(string='Fiscal Year', compute="_compute_sort", store=True)
    tax_given = fields.Boolean(string='Tax Given')
    attrition_type = fields.Selection([('vountary', 'Voluntary'), ('involuntary', 'Involuntary')], 'Attrition Type',
                              track_visibility='onchange',)
    tenure_at_csm = fields.Char(compute='_compute_tenure_at_csm', string="Tenure at CSM")
    manual_closing =fields.Boolean("Manual Closing",default=False)

    @api.depends('date_of_joining', 'last_working_date')
    def _compute_tenure_at_csm(self):
        for employee in self:
            if employee.date_of_joining and employee.last_working_date:
                joining_date = fields.Date.from_string(employee.date_of_joining)
                last_working_date = fields.Date.from_string(employee.last_working_date)
                delta = relativedelta(last_working_date, joining_date)
                tenure = ''
                if delta.years:
                    tenure += f"{delta.years}yrs "
                if delta.months:
                    tenure += f"{delta.months}months "
                if delta.days:
                    tenure += f"{delta.days}days"
                
                employee.tenure_at_csm = tenure.strip()
            else:
                employee.tenure_at_csm = '0 days'


    @api.multi
    def offboarding_report_render(self):
        tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
        form_view_id = self.env.ref('kw_eos.report_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name' : 'Offboarding Report',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'views': [(tree_view_id, 'tree'), (form_view_id,'form')],
            'res_model': 'kw_resignation',
        }
        if self.env.user.has_group('kw_eos.group_kw_eos_user') and \
                                not self.env.user.has_group('kw_eos.group_kw_eos_manager') and \
                                not self.env.user.has_group('kw_employee.group_hr_ra') and \
                                not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') and \
                                not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') and \
                                not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') and \
                                not self.env.user.has_group('kw_eos.group_kw_eos_officer') and \
                                not self.env.user.has_group('kw_eos.group_kw_eos_resource_head') and \
                                not self.env.user.has_group('kw_wfh.group_hr_hod') and \
                                not self.env.user.has_group('kw_resource_management.group_sbu_representative') and \
                                not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') and \
                                not self.env.user.has_group('kw_eos.group_kw_offboarding_report'):
            print("inside first if only user======================")

            action['domain'] = [('applicant_id.user_id', '=', self.env.uid)]

        if self.env.user.has_group('kw_employee.group_hr_ra') \
                            and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                            and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                            and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                            and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head') and \
                            not self.env.user.has_group('kw_eos.group_kw_offboarding_report'):
            print("inside second ra condition============================")
            action['domain'] = ['|', '|',('applicant_id', '=', self.env.user.employee_ids.id), (
                                        'applicant_id.parent_id.user_id', '=',
                                        self.env.user.employee_ids.user_id.id),(
                                        'applicant_id.sbu_master_id.representative_id.user_id', '=',
                                        self.env.user.employee_ids.user_id.id)]
        
        if self.env.user.has_group('kw_wfh.group_hr_hod') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                            and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') and \
                            not self.env.user.has_group('kw_eos.group_kw_offboarding_report'):
                print("inside hod wala if condition=============================")
                action['domain'] = [ '|', '|',('applicant_id', '=', self.env.user.employee_ids.id),(
                                            'applicant_id.parent_id.user_id', '=',
                                            self.env.user.employee_ids.user_id.id), (
                                            'applicant_id.department_id.manager_id.user_id', '=',
                                            self.env.user.employee_ids.user_id.id)]
                    
        if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                print("inside the manager group===============================")
                action['domain'] = []
        if self.env.user.has_group('kw_eos.group_kw_offboarding_report'):
                # print("isude offboarding report group=========================")
                action['domain'] = []
        return action
                

    @api.onchange('apply_for')
    def onchange_apply_for(self):
        if self.apply_for == 'others':
            empls = self.env['hr.employee'].search([('employement_type.code','not in',['O','CE'])])
            return {'domain': {'applicant_id': [('id', 'in', empls.ids)]}}

    @api.multi
    def _comp_ra_check(self):
        for rec in self:
            if self.env.user.has_group('kw_employee.group_hr_ra') or self.env.user.id == rec.applicant_id.parent_id.user_id.id  and self.env.user.id != rec.applicant_id.user_id.id:
                rec.ra_check = True
    """ 
        1) State changes to grant if submitted by HR when retain is NO and mail is fired to respective authorities 
        2) State changes to Pending at finance if retain is YES and mail is fired to respective authorities 
    """

    @api.multi
    def action_manager_submit(self):
        if (self.env.user.has_group('kw_eos.group_kw_eos_manager')
                or self.env.user.has_group('kw_eos.group_kw_eos_officer')):
            if self.retain == 'yes' and self.offboarding_type.code == 'ret':
                self.write({
                    'state': 'pending_at_finance'
                })
                """ mail fired to finance group """
                account_list = []
                accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
                account_list += accaunt.filtered(lambda r: r.work_email != False).mapped('work_email')
                account_lists = account_list and ",".join(account_list) or ''
                template_obj = self.env.ref('kw_eos.retirnment_details_account_mail_template')
                mail_cc = self.get_cc(dept_head=True, hrd=True, ra=True, deg_group=True, reg_record=self)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=account_lists,
                                                                                      mailt=self.applicant_id.work_email,
                                                                                      mail_cc=mail_cc,
                                                                                      code=self.applicant_id.emp_code,
                                                                                      mailtn=self.applicant_id.name,
                                                                                      reason=self.retirement,
                                                                                      branch_alias=self.base_branch_id.alias,
                                                                                      effective_form=datetime.strptime(
                                                                                          str(self.effective_form),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(self.last_working_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      department_id=self.department_id.name,
                                                                                      division=self.division.name,
                                                                                      section=self.section.name,
                                                                                      practise=self.practise.name,
                                                                                      job_id=self.job_id.name,
                                                                                      date_of_joining=datetime.strptime(
                                                                                          str(self.date_of_joining),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      retain='Yes' if self.retain == 'yes' else 'NO',
                                                                                      new_department_id=self.ret_department_id.name,
                                                                                      new_division=self.ret_division.name,
                                                                                      new_section=self.ret_section.name,
                                                                                      new_practise=self.ret_practise.name,
                                                                                      new_job_id=self.ret_job_id.name,
                                                                                      emp_type=self.ret_employeement_type.name,
                                                                                      con_amt=self.new_current_ctc,
                                                                                      start_date=self.ret_contract_start_date,
                                                                                      end_date=self.ret_contract_end_date,
                                                                                      ).send_mail(
                    self.resignation_ids[0].id, notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)
            if self.retain == 'no' and self.offboarding_type.code == 'ret':
                self.write({
                    'state': 'grant',
                })
                """ mail fired to applicant """
                assetdata = self.get_asset_data()
                advances_data = False
                petty_cash_data = False
                advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                if not advance_checklist:
                    advances_data = self.get_advance_details(self.applicant_id)
                    petty_cash_data = self.get_petty_cash_details(self.applicant_id)
                tour_clearance = self.tour_clearance if self.tour_clearance else 'No tour settlement is pending'
                sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
                petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
                asset_clearance = len(assetdata) if assetdata else 'NIL'
                template_obj = self.env.ref('kw_eos.retirnment_details_applicant_mail_template')
                rec = self
                mail_cc = self.get_cc(dept_head=True, hrd=True, ra=True, deg_group=True, reg_record=rec)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(to=self.applicant_id.work_email,
                                                                                      mail_cc=mail_cc,
                                                                                      code=self.applicant_id.emp_code,
                                                                                      mailtn=self.applicant_id.name,
                                                                                      reason=self.retirement,
                                                                                      branch_alias=self.base_branch_id.alias,
                                                                                      effective_form=datetime.strptime(
                                                                                          str(self.effective_form),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(self.last_working_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      department_id=self.department_id.name,
                                                                                      division=self.division.name,
                                                                                      section=self.section.name,
                                                                                      practise=self.practise.name,
                                                                                      job_id=self.job_id.name,
                                                                                      assetdata=assetdata,
                                                                                      tour_clearance=tour_clearance,
                                                                                      sal_adv_clearance=sal_adv_clearance,
                                                                                      petty_cash_clearance=petty_cash_clearance,
                                                                                      date_of_joining=datetime.strptime(
                                                                                          str(self.date_of_joining),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      retain='Yes' if self.retain == 'yes' else 'NO',
                                                                                      ).send_mail(
                    self.resignation_ids[0].id, notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)
            """ Url redirected to take action page """
            action_id = self.env.ref('kw_eos.approved_resignation_requests_action_new_views_one').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                'target': 'self',
            }

    @api.multi
    @api.depends('state')
    def _compute_sort(self):
        sort_order = {
            'apply': 1,
            'confirm': 2,
            'forward': 3,
            'grant': 4,
            'pending_at_finance': 5,
            'submit_by_finance': 6,
            'waiting_for_rl_cancellation': 7,
            'extend': 8,
            'exemployee': 9,
            'reject': 10,
            'cancel': 11,
            'cancelreject': 12,
        }
        for record in self:
            today = date.today()
            april = date.today().replace(day=1, month=4)
            year = int(date.today().strftime("%Y"))
            if today >= april:
                record.fiscal_yr = f"{str(year)}-{str(year + 1)}"
            else:
                record.fiscal_yr = f"{str(year - 1)}-{str(year)}"
            record.sort = sort_order.get(record.state)

    @api.multi
    def _comp_clearance_details(self):
        for rec in self:
            employee = rec.applicant_id
            """ Tour details"""
            tour_rec = self.env['kw_tour'].sudo().search([('employee_id', '=', employee.id), (
                'state', 'in', ['Applied', 'Approved', 'Forwarded', 'Traveldesk Approved', 'Finance Approved'])])
            un_settle_tours = tour_rec.filtered(lambda r: not set(r.settlement_ids.mapped('state')) & {'Payment Done'})
            if un_settle_tours:
                rec.tour_clearance = "Tour settlement is pending"
            else:
                rec.tour_clearance = 'No tour settlement is pending'
            """ salary  advance, Asset, petty cash details through api """
            demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'kw_eos.module_offboarding_mode_status')
            """ Demo mode mandatory check"""
            if demo_mode_enabled:
                pass
            else:
                parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
                EOSurl = parameterurl + 'ManageEOSDetails'
                header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                user_id = rec.applicant_id.kw_id
                if not user_id:
                    user_id = self.env.user.employee_ids.kw_id
                EOSDict = {
                    "userId": user_id
                }
                try:
                    resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)
                except Exception:
                    raise ValidationError("Some error occurred.Please try again later")
                if json_record.get('Userstatus') == '1':
                    if json_record.get('retEOSActDa'):
                        eos_checklist = json_record.get('retEOSActDa')
                        for eos in eos_checklist:
                            if eos['Activity_Name'] == "Assets":
                                rec.asset_clearance = 'Nill' if int(eos['Applied']) == 0 else 'Pending'
                                assets_pendings = int(eos['Pendings'])
                            if eos['Activity_Name'] == "Salary Advance":
                                rec.sal_adv_clearance = 'Nill' if int(eos['Applied']) == 0 else 'Pending'
                    self.env['kw_eos_log'].sudo().create(
                        {'req_data': EOSDict, 'response_res': json_record, 'type': 'ManageEOSDetails'})

    @api.depends('applicant_id')
    def _compute_readonly_for_finance(self):
        for rec in self:
            if self._context.get('finance_user'):
                rec.read_only_for_finance = True
    # ==== Action For Budget Submit ======
    @api.multi
    def action_budget_submit(self):
        for rec in self:
            rec.write({'budget_submit': True, 'state': 'submit_by_finance'})
            resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', rec.id)], limit=1)
            if resignation_log:
                self.env['kw_resignation_log'].create({
                    'applicant_id': self.env.user.employee_ids.id,
                    'date': rec.effective_form,
                    'state': 'submit_by_finance',
                    'remark': 'Submitted by Finance',
                    'last_working_date': rec.last_working_date,
                    'reg_id': rec.id,
                })
        self.env.user.notify_success("Budget submitted successfully.")

    @api.depends('applicant_id')
    def _comp_offboarding_process_status(self):
        for rec in self:
            # print("=========================re c=========================")
            
            if rec.state == 'cancel':
                resignation_log = self.env['kw_resignation_log'].sudo().search(
                    [('reg_id', '=', rec.id), ('state', '=', 'cancel')], limit=1)
                rec.offboarding_process_status = f'Cancelled by {resignation_log.applicant_id.name}'
            elif rec.state == 'apply':
                rec.offboarding_process_status = f'Pending at {rec.applicant_id.parent_id.name}'
            elif rec.state == 'confirm':
                rec.offboarding_process_status = f'Pending at {rec.applicant_id.sbu_master_id.representative_id.name if rec.applicant_id.sbu_master_id.representative_id else rec.applicant_id.department_id.manager_id.name}'
            elif rec.state == 'forward':
                rec.offboarding_process_status = f'Forwarded to {rec.forward_to.name}'
            elif rec.state == 'reject':
                resignation_log = self.env['kw_resignation_log'].sudo().search(
                    [('reg_id', '=', rec.id), ('state', '=', 'reject')], limit=1)
                rec.offboarding_process_status = f'Rejected by {resignation_log.applicant_id.name}'
            elif rec.state == 'grant':
                if rec.kt_required == 'yes':
                    kt_record = self.env['kw_kt_view'].sudo().search(
                        [('applicant_id', '=', rec.applicant_id.id), ('resignation_id', '=', rec.id),
                         ('kt_type_id.code', '=', 'reg')])
                    if kt_record:
                        if kt_record.state == 'Completed':
                            rec.offboarding_process_status = 'KT Plan completed'
                        elif kt_record.state == 'Draft':
                            rec.offboarding_process_status = 'KT Plan to start'
                        else:
                            rec.offboarding_process_status = 'KT Plan in progress'
                else:
                    rec.offboarding_process_status = 'KT Plan Not Applicable'

            eos_record = self.env['kw_eos_checklist'].sudo().search([('applicant_id', '=', rec.applicant_id.id)])
            if eos_record:
                if eos_record.state == 'Applied' or eos_record.state == 'Approved':
                    rec.offboarding_process_status = 'EOS in progress'
                elif eos_record.state == 'Draft':
                    rec.offboarding_process_status = 'EOS not applied'
            clearance_record = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', rec.applicant_id.id)])
            for cl_rec in clearance_record:
                if cl_rec.done_by_hr:
                    rec.offboarding_process_status = 'Ex-Employee'
            if rec.manual_closing:
                rec.offboarding_process_status = 'Ex-Employee'

    @api.multi
    def _search_applicant_department(self, operator, value):
        return [('applicant_id.department_id', 'ilike', value)]

    @api.multi
    def _search_emp_location(self, operator, value):
        return [('applicant_id.base_branch_id', 'ilike', value)]

    @api.multi
    def _search_emp_type(self, operator, value):
        return [('applicant_id.report_employement_type', 'ilike', value)]

    @api.onchange('retain')
    def onchange_retain(self):
        if self.retain == 'yes':
            self.kt_required = 'no'

    @api.depends('applicant_id')
    def _check_done_by_finance(self):
        for rec in self:
            if rec.emp_role and rec.emp_category and rec.employement_type:
                rec.done_by_finance = True
            else:
                rec.done_by_finance = False

    @api.depends('last_working_date')
    def _compute_month_last_working_date(self):
        for rec in self:
            rec.month_last_working_date = rec.last_working_date.strftime("%B")

    @api.depends('last_working_date')
    def _compute_year_last_working_date(self):
        for rec in self:
            exit_date = rec.last_working_date
            rec.year_last_working_date = exit_date.year

    @api.depends('applicant_id')
    def _compute_check_contract_create_user(self):
        for rec in self:
            if rec.create_uid.id == self._uid:
                rec.check_contract_create_user = True

    @api.depends('applicant_id')
    def _compute_eos_status(self):
        for rec in self:
            eos_rec = self.env['kw_eos_checklist'].sudo().search(
                [('applicant_id', '=', rec.applicant_id.id), ('state', '!=', 'Rejected')])
            rec.eos_status = eos_rec.state

    @api.constrains('upload_related_document', 'retirement_document')
    def validate_upload_related_document(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.upload_related_document, allowed_file_list)
            kw_validations.validate_file_size(record.upload_related_document, 4)

    @api.depends('applicant_id')
    def _get_current_user(self):
        for res in self:
            res.logged_user = self.env.user.id
            if res.applicant_id.user_id.id == self.env.user.id:
                res.check_applicant_user_id = True

    # button hide for report form view
    @api.depends('applicant_id')
    def _compute_report_check(self):
        for rec in self:
            if self._context.get('report'):
                rec.report_check = True

    @api.multi
    def action_cancel_resignation(self):
        wizard_form = self.env.ref('kw_eos.cancel_resignation_view', False)
        action = {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw_resignation_cancellation_wizard',
            'target': 'new',
            'context': {'default_resignation_id': self.id, }
        }
        return action

    @api.depends('applicant_id')
    def _compute_action_to_be_taken_by(self):
        for rec in self:
            if rec.offboarding_type.name == 'Retirement':
                if rec.state == 'apply':
                    rec.action_to_be_taken_by = rec.applicant_id.parent_id.name
                if rec.state == 'forward':
                    rec.action_to_be_taken_by = rec.forward_to.name
                if rec.state in ['confirm', 'cancelreject']:
                    rec.action_to_be_taken_by = rec.applicant_id.sbu_master_id.representative_id.name if rec.applicant_id.sbu_master_id.representative_id else rec.applicant_id.department_id.manager_id.name
            else:
                if rec.state == 'apply' and (
                        not rec.offboarding_type.name == 'Termination' or not rec.offboarding_type.name == 'Retirement'):
                    rec.action_to_be_taken_by = rec.applicant_id.parent_id.name
                if rec.state == 'apply' and rec.offboarding_type.name == 'Contract Closure':
                    if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                            or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                            or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                        rec.action_to_be_taken_by = 'HR Manager'
                if rec.state == 'apply' and rec.offboarding_type.name == 'Termination':
                    rec.action_to_be_taken_by = '--'
                if rec.state == 'waiting_for_rl_cancellation':
                    rec.action_to_be_taken_by = rec.applicant_id.parent_id.name
                if rec.state in ['confirm', 'cancelreject']:
                    rec.action_to_be_taken_by = rec.applicant_id.sbu_master_id.representative_id.name if rec.applicant_id.sbu_master_id.representative_id else rec.applicant_id.department_id.manager_id.name
                    print("===============rec.action_to_be_taken_by===========",rec.action_to_be_taken_by)
                if rec.state == 'forward':
                    rec.action_to_be_taken_by = rec.forward_to.name
            if rec.state == 'grant' or rec.state == 'cancel':
                rec.action_to_be_taken_by = '--'

    @api.depends('applicant_id')
    def _compute_details(self):
        for rec in self:
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') or self.env.user.has_group(
                    'kw_eos.group_kw_eos_officer'):
                if rec.apply_for == 'self' and not self._context.get('report'):
                    employee = rec.applicant_id if rec.applicant_id else self.env.user.employee_ids
                else:
                    employee = rec.applicant_id
            else:
                employee = rec.applicant_id if rec.applicant_id else self.env.user.employee_ids
            rec.job_id = employee.job_id.id
            rec.division = employee.division.id
            rec.section = employee.section.id
            rec.practise = employee.practise.id
            rec.department_id = employee.department_id.id
            rec.report_employement_type = employee.employement_type.id
            rec.base_branch_id = employee.base_branch_id.id
            rec.gender = employee.gender
            rec.ra = employee.parent_id.name
            # if rec.applicant_id:
            #     kt_type_rec = self.env['kw_kt_type_master'].sudo().search([('name', '=', 'Resignation')])
            #     record = self.env['kw_kt_view'].sudo().search([('applicant_id','=',rec.applicant_id.id),('resignation_id','=',rec.id),('kt_type_id','=',kt_type_rec.id)])
            #     if not record and rec.kt_required == 'yes' and rec.state == 'grant':
            #         rec.check_kt_record = True
            #     else:
            #         rec.check_kt_record = False

    @api.depends('applicant_id')
    def compute_project(self):
        for rec in self:
            if rec.report_employement_type.code == 'C' or rec.report_employement_type.code == 'S':
                project_rec = self.env['kw_project_resource_tagging'].sudo().search(
                    [('emp_id', '=', rec.applicant_id.id), ('start_date', '<=', datetime.today().date()),
                     ('end_date', '>=', datetime.today().date())], limit=1)
                if project_rec:
                    rec.current_project = project_rec.project_id.name
                else:
                    rec.current_project = 'Not Applicable'
            else:
                rec.current_project = 'Not Applicable'

    @api.onchange('apply_for', 'offboarding_type')
    def _onchange_apply_for(self):
        emp_id = []
        if self.apply_for == 'self':
            self.applicant_id = False
            self.check_apply_for_self = True
            self.applicant_id = self.env.user.employee_ids.id
            if not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                if self.offboarding_type.code == 'ret':
                    if not self.env.user.has_group('kw_eos.group_kw_eos_senior_citizen'):
                        raise ValidationError(_('You can not apply for retirement.'))

        elif self.apply_for == 'others':
            self.applicant_id = False
            if self.offboarding_type.code == 'con':
                contract_employee = self.env['hr.employee'].sudo().search(
                    [('employement_type.code', 'in', ['S', 'C'])]) - self.env.user.employee_ids
                for rec in contract_employee:
                    emp_id.append(rec.id)
            elif self.offboarding_type.code == 'ret':
                retirement_emp = self.env.ref('kw_eos.group_kw_eos_senior_citizen').users - self.env.user
                for record in retirement_emp:
                    emp_id.append(record.employee_ids.id)
            else:
                self.applicant_id = False
                current_login_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
                emp_records = self.env['hr.employee'].sudo().search([('employement_type.code', 'not in', ['O', 'CE'])]) - current_login_id
                self.check_apply_for_self = False
                for rec in emp_records:
                    emp_id.append(rec.id)
        return {'domain': {'applicant_id': [('id', 'in', emp_id)]}}

    @api.depends('applicant_id')
    def _check_manager(self):
        for record in self:
            if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                record.is_manager = True
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
                if record.applicant_id.user_id.id != self.env.user.id:
                    record.is_finance_user = True

    @api.onchange('ret_department_id')
    def onchange_department(self):
        for rec in self:
            return {'domain': {
                'division': [('parent_id', '=', rec.ret_department_id.id), ('dept_type.code', '=', 'division')]}}

    @api.multi
    def _ra_cancel_aprv_btn(self):
        for rec in self:
            if rec.applicant_id.user_id.id == self.env.user.id:
                rec.applicant_user_id_check = True
            else:
                rec.applicant_user_id_check = False
            if rec.applicant_id.parent_id.user_id.id == self.env.user.id:
                rec.ra_cancel_aprv_btn_check = True
            else:
                rec.ra_cancel_aprv_btn_check = False

            # if self.env.user.id == rec.applicant_id.department_id.manager_id.user_id.id or self.env.user.id == rec.applicant_id.division.manager_id.user_id.id or self.env.user.id == rec.applicant_id.sbu_master_id.representative_id.user_id.id or self.env.user.id == rec.applicant_id.parent_id.user_id.id:
            if self.env.user.id == rec.applicant_id.department_id.manager_id.user_id.id \
                    or self.env.user.id == rec.applicant_id.sbu_master_id.representative_id.user_id.id \
                    or self.env.user.id == rec.applicant_id.parent_id.user_id.id:
                if self.env.user.id == rec.applicant_id.user_id.id:
                    rec.dept_head_check = False
                elif self.env.user.employee_ids.id == rec.applicant_id.parent_id.id \
                        and self.env.user.employee_ids.id == rec.applicant_id.department_id.manager_id.id:
                    rec.dept_head_check = True   
                else:
                    rec.dept_head_check = True
            # if rec.offboarding_type.name == 'Demise':
            #     rec.demise_check = True
            if rec.offboarding_type.name == 'Contract Closure':
                rec.contract_check = True
            # if rec.offboarding_type.name == 'Retirement':
            #     rec.retirement_check = True

    @api.multi
    def take_action_rl_cancellation_button(self):
        aprv_rl_cancel_form = self.env.ref('kw_eos.apply_rl_cancellation_view_form')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': aprv_rl_cancel_form.id,
            'res_model': 'kw_resignation',
            'res_id': self.id,
            'target': 'self',
        }

    @api.multi
    def btn_aprv_rl_cancel(self):
        self.sudo().write({'aprv_rl_cancel_remark': self.aprv_rl_cancel_remark,
                           'state': 'cancel',
                           'action_to_be_taken_by': False})
        self.applicant_id.sudo().write({'in_noticeperiod': False,
                                        'resignation_reason': False
                                        })

        """ Updating log details """
        resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.id)], limit=1)
        if resignation_log:
            self.env['kw_resignation_log'].sudo().create({
                'applicant_id': self.env.user.employee_ids.id,
                'date': self.sudo().effective_form,
                'state': 'rlcancel_approve',
                'remark': self.sudo().aprv_rl_cancel_remark,
                'last_working_date': self.sudo().last_working_date,
                'reg_id': self.id,
            })
        kt_record = self.env['kw_kt_view'].sudo().search(
            [('applicant_id', '=', self.sudo().applicant_id.id), ('kt_type_id', '=', self.sudo().offboarding_type.id)])
        if kt_record:
            for kt in kt_record:
                kt.active = False

        template_obj = self.env.ref('kw_eos.rl_cancel_approve_mail_template')
        # mail_cc = self.get_cc(hrd=True, dept_head=True)
        mail = self.env['mail.template'].browse(template_obj.id).with_context(
            ra_email=self.sudo().applicant_id.parent_id.work_email,
            applicant_email=self.sudo().applicant_id.work_email,
            mailfn=self.env.user.employee_ids.name,
            cancel_reason=self.sudo().aprv_rl_cancel_remark,
            applicant_name=self.sudo().applicant_id.name,
            ra_name=self.sudo().applicant_id.parent_id.name,
            applicant_emp_code=self.sudo().applicant_id.emp_code,
        ).send_mail(self.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light',
                    force_send=False)
        temp_obj = self.sudo().env.ref('kw_eos.rl_cancel_approve_hrd_mail_template')
        mail_cc = self.sudo().get_cc(deg_group=True, dept_head=True,sbu=True)
        mail = self.sudo().env['mail.template'].browse(temp_obj.id).with_context(
            mailfn=self.env.user.employee_ids.name,
            mail_cc=mail_cc,
            cancel_reason=self.sudo().aprv_rl_cancel_remark,
            ra_email=self.sudo().applicant_id.parent_id.work_email,
            applicant_name=self.sudo().applicant_id.name,
            ra_name=self.sudo().applicant_id.parent_id.name,
            applicant_emp_code=self.sudo().applicant_id.emp_code,
            create_date=datetime.strptime(str(self.sudo().create_date), "%Y-%m-%d %H:%M:%S.%f").date().strftime("%d-%b-%Y"),
            reason=self.sudo().reason,
            reg_type=self.sudo().reg_type.name,
            branch_alias=self.sudo().base_branch_id.alias,
            effective_form=datetime.strptime(str(self.sudo().effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
            last_working_date=datetime.strptime(str(self.sudo().last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
            department_id=self.sudo().department_id.name,
            division=self.sudo().division.name,
            section=self.sudo().section.name,
            practise=self.sudo().practise.name,
            job_id=self.sudo().job_id.name,
            date_of_joining=datetime.strptime(str(self.sudo().date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"), ).send_mail(
            self.sudo().resignation_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
        self.env.user.notify_success("Resignation cancellation request approved successfully.")
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def btn_reject_rl_cancel(self):
        if self.prev_state == 'grant':
            self.write({'rl_cancel_reject_remark': self.rl_cancel_reject_remark,
                        'state': 'grant', 'resignation_reject': True})
        else:
            self.write({'rl_cancel_reject_remark': self.rl_cancel_reject_remark,
                        'state': 'cancelreject'})
        resignation_log = self.env['kw_resignation_log'].sudo().search([('reg_id', '=', self.id)], limit=1)
        if resignation_log:
            self.env['kw_resignation_log'].create({
                'applicant_id': self.env.user.employee_ids.id,
                'date': self.effective_form,
                'state': 'cancelreject',
                'remark': self.rl_cancel_reject_remark,
                'last_working_date': self.last_working_date,
                'reg_id': self.id,
            })

        template_obj = self.env.ref('kw_eos.rl_cancel_reject_mail_template')
        mail_cc = self.get_cc(deg_group=True, dept_head=True,sbu=True)
        mail = self.env['mail.template'].browse(template_obj.id).with_context(
            mailfn=self.env.user.employee_ids.name,
            cancel_reason=self.rl_cancel_reject_remark,
            ra_email=self.applicant_id.parent_id.work_email,
            applicant_email=self.applicant_id.work_email,
            applicant_name=self.applicant_id.name,
            applicant_emp_code=self.applicant_id.emp_code,
            ra_name=self.applicant_id.parent_id.name,
            mail_cc=mail_cc).send_mail(self.resignation_ids.ids[0],
                                       notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
        self.env.user.notify_success("Resignation cancellation request rejected successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def btn_apply_kt(self):
        if self.state == 'grant':
            kt_type_rec = self.env['kw_kt_type_master'].sudo().search([('name', '=', self.offboarding_type.name)])
            self.env.cr.execute(f"""insert into kw_kt_view (resignation_id,applicant_id,effective_form,last_working_date,kt_type_id,manual,applied_for,company_id,create_uid,write_uid,create_date,write_date,state,active) values({self.id},{self.applicant_id.id},'{self.effective_form}','{self.last_working_date}',{kt_type_rec.id},False,'self',{self.env.user.company_id.id},{self.env.user.id},{self.env.user.id},'{datetime.today().now()}','{datetime.today().now()}','Draft',True)""")
            action_id = self.env.ref('kw_kt.kt_view_action').id
            # print("action_idaction_idaction_idaction_id===",action_id)
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
                    'target': 'self',
                }
            # view_id = self.env.ref('kw_kt.kw_kt_view_tree').id
            # action = {
            #     'name': 'KT Application',
            #     'type': 'ir.actions.act_window',
            #     'res_model': 'kw_kt_view',
            #     'view_type': 'form',
            #     'view_mode': 'tree,form',
            #     'views': [(view_id, 'form')],
            #     'target': 'self',
            #     'view_id': view_id,
            # }
            #     # 'res_id': self.id,
            # return action
        # print("apply KT called-------")

    @api.onchange('ret_division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.department_id:
                domain['ret_section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('ret_section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.section:
                domain['ret_practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}

    @api.onchange('offboarding_type')
    def on_change_offboard(self):
        for record in self:
            record.kt_required = 'no'
            record.offboard_type_reg = False
            record.reg_type = False
            record.reason = False
            record.hide_apply_for = False
            record.apply_for = 'self'
            record.contract_closure_check = False
            record.contract_closure = False
            record.retirement_check = False
            record.retirement = False
            record.major_activity = False
            record.effective_form = fields.Date.today()
            record.termination_check = False
            record.termination = False
            record.termination_reason = False
            record.termination_remark = False
            record.upload_related_document = False
            record.required_effective_from = True
            record.demise_check = False
            record.demise = False
            record.demise_reason = False

            if not record.offboarding_type:
                record.hide_apply_for = True

            if record.offboarding_type.code == 'reg':
                record.offboard_type_reg = True
                record.hide_apply_for = False
                record.kt_required = 'yes'

            elif record.offboarding_type.code == 'con':
                record.contract_closure_check = True
                record.hide_apply_for = True
                record.apply_for = 'others'
                # self._onchange_apply_for()
            elif record.offboarding_type.code == 'ret':
                if not self.env.user.has_group('kw_eos.group_kw_eos_manager') and not self.env.user.has_group(
                        'kw_eos.group_kw_eos_officer'):
                    if self.env.user.has_group('kw_eos.group_kw_eos_senior_citizen'):
                        record.hide_apply_for = False
                    else:
                        raise ValidationError(_('You can not apply for retirement.'))

                elif self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                    record.hide_apply_for = False
                    record.apply_for = 'others'
                # else:
                #     record.hide_apply_for = True
                #     record.apply_for = 'others'
                record.retirement_check = True
                record.kt_required = 'yes'

            elif record.offboarding_type.code == 'ter':
                record.termination_check = True
                record.hide_apply_for = True
                record.apply_for = 'others'
                record.effective_form = False
                record.last_working_date = False

            elif record.offboarding_type.code == 'dem':
                record.required_effective_from = False
                record.demise_check = True
                record.hide_apply_for = True
                record.apply_for = 'others'
                record.effective_form = False
                record.last_working_date = fields.Date.today()

    # @api.model
    # def default_get(self, fields):
    #     res = super(kw_resignation, self).default_get(fields)
    #     if not self.env.user.has_group('kw_eos.group_kw_eos_manager') and not self.env.user.has_group(
    #             'kw_eos.group_kw_eos_officer'):
    #         record = self.search(
    #             [('applicant_id', '=', self.env.user.employee_ids.id), ('state', 'not in', ['reject', 'cancel'])])
    #         # if record:
    #         #     raise ValidationError(f"You have already applied for {record.offboarding_type.name}.")
    #         """ Restricting Employees if he/she is in WFH,Tour,Leave """
    #         """ WFH """

    @api.constrains('applicant_id', 'state')
    def _check_already_applied(self):
        for record in self:
            existing_resignations = self.search(
                [('applicant_id', '=', record.applicant_id.id),
                 ('state', 'not in', ['reject', 'cancel'])]
            )
            if len(existing_resignations) > 1:
                raise ValidationError(
                    f"You have already applied for {existing_resignations[0].offboarding_type.name}."
                )
          
    def validate_dates(self):
        for record in self:
            if not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                if record.effective_form and record.effective_form < date.today():
                    raise ValidationError("You cannot add a previous Date.")
            if record.effective_form and record.last_working_date and record.effective_form > record.last_working_date:
                raise ValidationError("Last working date should be greater than effective from date.")

    @api.multi
    def get_cc(self, grant=False, deg_group=False, hrd=False, dept_head=False, reg_record=None, forward_emp=False,
               resource_head=False, ceo=False, emp_id=False, account=False, ra=False, f_auth=False, it=False,
               admin=False, upper_ra=False, sbu=False):
        param = self.env['ir.config_parameter'].sudo()

        email_list = []
        employee = self.applicant_id if self.applicant_id else self.env.user.employee_ids

        if ra:
            if reg_record:
                ra_id = reg_record.mapped('applicant_id.parent_id')
                email_list += ra_id and ra_id.work_email and ra_id.active == True and [ra_id.work_email] or []
            else:
                email_list.append(employee.parent_id.work_email)

        if f_auth:
            if reg_record and reg_record.applicant_id.coach_id != reg_record.applicant_id.parent_id:
                f_auth_id = reg_record.mapped('applicant_id.coach_id')
                if f_auth_id:
                    email_list += f_auth_id and f_auth_id.work_email and f_auth_id.active == True and [f_auth_id.work_email] or []

        if account:
            account_emp = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
            email_list += account_emp.filtered(lambda r: r.work_email).mapped('work_email')

        if it:
            it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
            email_list += it.filtered(lambda r: r.work_email).mapped('work_email')

        if admin:
            admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
            email_list += admin.filtered(lambda r: r.work_email).mapped('work_email')

        if upper_ra:
            # Restrict CEO mail
            upper_upper_ra = employee.parent_id.parent_id.mapped('parent_id') if employee.active==True else False
            if upper_upper_ra:
                email_list.append(employee.parent_id.parent_id.work_email)
        
        """ fetch SBU representative email """
        if sbu:
            sbu_emp = employee.sbu_master_id.representative_id if employee.active == True else False
            if sbu_emp:
                email_list.append(employee.sbu_master_id.representative_id.work_email)
        
        if ceo:
            ceo = self.env['hr.employee'].search([('job_id.name', '=', 'Chief Executive Officer'),('active', '=', True)])
            email_list += ceo.filtered(lambda r: r.work_email).mapped('work_email')

        if resource_head:
            employees = self.env.ref('kw_eos.group_kw_eos_resource_head').mapped('users.employee_ids')
            email_list += employees.filtered(lambda r: r.work_email).mapped('work_email')

        if emp_id:
            if emp_id.parent_id and emp_id.parent_id.active == True and emp_id.parent_id.work_email:
                email_list.append(emp_id.parent_id.work_email)

        """HRD users"""
        if hrd:
            hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
            if hrd_group:
                empls = self.env['hr.employee'].search([('id', 'in', hrd_group)])
                email_list += empls.filtered(lambda r: r.work_email).mapped('work_email')

        """Notify CC users"""
        if deg_group:
            cc_group = literal_eval(param.get_param('kw_eos.notify_cc'))
            if cc_group:
                # all_jobs = self.env['hr.job'].browse(cc_group)
                # empls = self.env['hr.employee'].search([('jemail_listob_id', 'in', all_jobs.ids)])
                empls = self.env['hr.employee'].search([('id', 'in', cc_group)])
                if empls:
                    email_list += [emp.work_email for emp in empls if emp.work_email]

            hrd_cc_group = self.env.ref('kw_eos.group_kw_resignation_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list += [user.email for user in hrd_cc_group if user.email]

        """department head users"""
        if dept_head:
            if reg_record:
                manager_id = reg_record.mapped('applicant_id.department_id.manager_id')
                email_list += manager_id and manager_id.work_email and manager_id.active==True and [manager_id.work_email] or []
            else:
                email_list.append(employee.department_id.manager_id.work_email)
                if forward_emp:
                    email_list.append(employee.work_email)
                if self.state == 'forward':
                    email_list.append(employee.parent_id.work_email)
        if grant:
            admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
            email_list += admin.filtered(lambda r: r.work_email).mapped('work_email')

            it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
            email_list += it.filtered(lambda r: r.work_email).mapped('work_email')

            accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
            email_list += accaunt.filtered(lambda r: r.work_email).mapped('work_email')

            manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
            email_list += manager.filtered(lambda r: r.work_email).mapped('work_email')

            email_list.append(self.applicant_id.parent_id.work_email)
        # print("Email Join Return============>",email_list)
        email_list = list(filter(None, email_list))
        email = set(email_list)
        return email and ",".join(email) or ''

    @api.onchange('effective_form')
    def _onchange_effective_form(self):
        for res in self:
            np_days = 0
            employee = res.applicant_id if res.applicant_id else self.env.user.employee_ids
            if employee.grade:
                np_days = res.get_notice_period(employee)
            else:
                param = self.env['ir.config_parameter'].sudo()
                if param.get_param('kw_eos.notice_period') != 'False':
                    np_days = int(param.get_param('kw_eos.notice_period'))
                    #if param.get_param('kw_eos.notice_period') else '0'
                else:
                    np_days = 0
            if res.effective_form and res.offboarding_type.name != 'Termination':
                res.last_working_date = res.effective_form + timedelta(days=np_days)

    @api.onchange('user_id', 'applicant_id')
    def _get_data(self):
        for res in self:
            if res.apply_for == 'self':
                employee = self.env.user.employee_ids
            else:
                employee = res.applicant_id
            res.job_id = employee.job_id
            res.department_id = employee.department_id
            np_days = 0
            np_days = res.get_notice_period(employee)
            if res.effective_form and res.offboarding_type.name != 'Termination':
                res.last_working_date = res.effective_form + timedelta(days=np_days)

    @api.model
    def create(self, values):
        employee = self.env.user.employee_ids
        empl = self.env['hr.employee'].sudo().search([('id', '=', values.get('applicant_id'))])
        record = self.env['kw_resignation'].search(
            [('applicant_id', '=', empl.id), ('state', 'not in', ['reject', 'cancel'])])
        """ Tour """
        tour_rec = self.env['kw_tour']
        pending_tours = tour_rec.sudo().search_count([('employee_id', '=', employee.id), (
            'state', 'in', ['Applied', 'Approved', 'Forwarded', 'Traveldesk Approved'])])
        journey_incomplete_tours = tour_rec.search_count(
            [('employee_id', '=', employee.id), ('state', '=', 'Finance Approved'),
             ('date_return', '>=', date.today())])
        if pending_tours or journey_incomplete_tours:
            raise ValidationError("You cannot apply for resignation on Tour.")
        """ leave """
        leave_applied = self.env['hr.leave'].sudo().search(
            [('employee_id', '=', employee.id), ('state', 'in', ['confirm', 'hold', 'forward'])])
        if leave_applied:
            for leave in leave_applied:
                if leave.request_date_from and date.today():
                    if leave.request_date_from <= date.today() and leave.request_date_to >= date.today():
                        raise ValidationError("You cannot apply for resignation on Leave.")
        # if RA on leave forward to upper RA  
        attendance = self.env['kw_daily_employee_attendance'].search(
            [('employee_id', '=', employee.parent_id.id), ('attendance_recorded_date', '=', datetime.today().date())])
        if attendance and attendance.status == 'On Leave':
            values['forward_to'] = employee.parent_id.parent_id.id
        # if record:
        #     if not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
        #             or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                # print("users validations==========================")
                # raise ValidationError(f"You cannot apply for {record.offboarding_type.name} as you have already applied.")
            #f"You cannot apply for {record.offboarding_type.name} as you have already applied."

            # else:
                # print("manager validation===========================")
                # raise ValidationError(f"{record.offboarding_type.name} already applied for {record.applicant_id.name}.")

        values['name'] = self.env['ir.sequence'].next_by_code('kw_resignation') or _('New')
        res = super(kw_resignation, self).create(values)
        # self.env.user.employee_ids.resignation_aplied = True

        res.applicant_id.sudo().write({
                'in_noticeperiod':True,
                'resignation_reason': res.reg_type.id
            })

        eos_rec = self.env['kw_eos_checklist']
        if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                or self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
            if res.apply_for == 'self':
                res.applicant_id = self.env.user.employee_ids.id
            else:
                res.applicant_id = res.applicant_id.id
        # else:
        #     print("inside second else============================")
        #     res.applicant_id = self.env.user.employee_ids.id

        resignation_rec = self.env['kw_resignation_log']
        res_log = {
            'applicant_id': self.env.user.employee_ids.id,
            'date': res.effective_form,
            'state': res.state,
            'remark': f'Applied By {self.env.user.employee_ids.name}',
            'last_working_date': res.last_working_date,
            'reg_id': res.id,
        }
        log = resignation_rec.sudo().create(res_log)

        """send resignation email"""
        template_obj = self.env.ref('kw_eos.resignation_request_mail_template')
        template = self.env['mail.template'].browse(template_obj.id)
        parent_mail = res.forward_to.work_email if res.forward_to.work_email else res.applicant_id.parent_id.work_email
        if res.offboarding_type.name == 'Resignation':
            mail_cc = self.get_cc(deg_group=True, dept_head=True, hrd=True, f_auth=True, upper_ra=True, reg_record=res,sbu=True)
            mail = template.with_context(mailf=self.env.user.employee_ids.work_email,
                                         parent_mail=res.applicant_id.parent_id.work_email,
                                         applicant_name=res.applicant_id.name,
                                         code=res.applicant_id.emp_code,
                                         mailtn=res.applicant_id.parent_id.name,
                                         mail_cc=mail_cc,
                                         sbu_type=res.applicant_id.sbu_master_id.type if res.applicant_id.sbu_master_id.type else '',
                                         sbu=res.applicant_id.sbu_master_id.name if res.applicant_id.sbu_master_id else '',
                                         create_date=datetime.strptime(str(res.create_date), "%Y-%m-%d %H:%M:%S.%f").date().strftime("%d-%b-%Y"),
                                         reason=res.reason,
                                         reg_type=res.reg_type.name,
                                         branch_alias=res.base_branch_id.alias,
                                         effective_form=datetime.strptime(str(res.effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                         last_working_date=datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                         department_id=res.department_id.name,
                                         division=res.division.name,
                                         section=res.section.name,
                                         practise=res.practise.name,
                                         job_id=res.job_id.name,
                                         date_of_joining=datetime.strptime(str(res.date_of_joining),
                                                                           "%Y-%m-%d").strftime("%d-%b-%Y") if res.date_of_joining else False,
                                         ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)

            # date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),
            # ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

            self.env.user.notify_success("Resignation applied successfully.")
            self.env.user.notify_info("Mail sent successfully.")

        if res.offboarding_type.name == 'Retirement':
            if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                template_obj = self.env.ref('kw_eos.retirement_request_mail_template')
                template = self.env['mail.template'].browse(template_obj.id)

                manager_list = []
                manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
                manager_list += manager.filtered(lambda r: r.work_email).mapped('work_email')
                manager_lists = manager_list and ",".join(manager_list) or ''
                mail_cc = self.get_cc(deg_group=True, dept_head=True, hrd=True, ra=True, f_auth=True, reg_record=res)
                mail = template.with_context(mailf=self.env.user.employee_ids.work_email,
                                             code=res.applicant_id.emp_code,
                                             mailtn=res.applicant_id.name,
                                             mail_cc=mail_cc,
                                             manager_lists=manager_lists,
                                             employee_ra = res.applicant_id.parent_id.name,
                                             reason=res.retirement,
                                             branch_alias=res.base_branch_id.alias,
                                             effective_form=datetime.strptime(str(res.effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             last_working_date=datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             department_id=res.department_id.name,
                                             division=res.division.name,
                                             section=res.section.name,
                                             practise=res.practise.name,
                                             job_id=res.job_id.name,
                                             date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Mail sent successfully.")
                # if res.retain == 'no':
                #     res.state = 'grant'
                #     assetdata = self.get_asset_data()
                #     advances_data = False
                #     petty_cash_data = False
                #     advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                #     if not advance_checklist:
                #         advances_data = self.get_advance_details(res.applicant_id)
                #         petty_cash_data = self.get_petty_cash_details(res.applicant_id)
                #     tour_clearance = self.tour_clearance if self.tour_clearance else 'No tour settlement is pending'
                #     sal_adv_clearance =  advances_data.adv_amnt if advances_data else 'NIL'
                #     petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
                #     asset_clearance =len(assetdata) if assetdata else 'NIL'
                #     template_obj = self.env.ref('kw_eos.retirement_retain_request_mail_template')
                #     template = self.env['mail.template'].browse(template_obj.id)
                #     mail_cc = self.get_cc(dept_head=True, ra=True, f_auth=True, reg_record=res)
                #     mail = template.with_context(mailf=self.env.user.employee_ids.work_email,
                #                                 mailt=res.applicant_id.work_email,
                #                                 code=res.applicant_id.emp_code,
                #                                 mailtn=res.applicant_id.name, 
                #                                 mail_cc=mail_cc,
                #                                 reason=res.retirement,
                #                                 branch_alias=res.base_branch_id.alias,
                #                                 effective_form=datetime.strptime(str(res.effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
                #                                 last_working_date = datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                #                                 department_id = res.department_id.name,
                #                                 division = res.division.name,
                #                                 section = res.section.name,
                #                                 practise = res.practise.name,
                #                                 job_id = res.job_id.name,
                #                                 assetdata=assetdata,
                #                                 tour_clearance=tour_clearance,
                #                                 sal_adv_clearance=sal_adv_clearance,
                #                                 petty_cash_clearance=petty_cash_clearance,
                #                                 date_of_joining = datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),).send_mail(
                #         log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                #     self.env.user.notify_info("Mail sent successfully.")
                # if res.retain == 'yes':
                #     res.state = 'pending_at_finance'
                #     template_obj = self.env.ref('kw_eos.retirement_retain_yes_request_mail_template')
                #     template = self.env['mail.template'].browse(template_obj.id)

                #     account_list = []
                #     accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
                #     account_list += accaunt.filtered(lambda r: r.work_email).mapped('work_email')
                #     account_lists = account_list and ",".join(account_list) or ''
                #     mail_cc = self.get_cc(dept_head=True, ra=True, f_auth=True, reg_record=res)
                #     mail = template.with_context(mailf=self.env.user.employee_ids.work_email,
                #                                  mailt=res.applicant_id.parent_id.work_email,
                #                                  mailfn=res.applicant_id.name, code=res.applicant_id.emp_code,
                #                                  mailtn=res.applicant_id.parent_id.name, mail_cc=mail_cc,
                #                                  account_lists=account_lists,
                #                                  applicant = res.applicant_id.name,
                #                                  emp_code = res.applicant_id.emp_code,
                #                                  effective_form=datetime.strptime(str(res.effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
                #                                  last_working_date = datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                #                                  retirement = res.retirement,
                #                                  department_id = res.department_id.name,
                #                                  division = res.division.name,
                #                                  section = res.section.name,
                #                                  practise = res.practise.name,
                #                                  job_id = res.job_id.name,
                #                                  date_of_joining = datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),).send_mail(log.id,notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
                #     self.env.user.notify_success("Mail sent successfully.")
            else:
                """ for employee self apply Retirement """
                template_obj = self.env.ref('kw_eos.retirement_request_mail_template')
                template = self.env['mail.template'].browse(template_obj.id)

                manager_list = []
                manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
                manager_list += manager.filtered(lambda r: r.work_email).mapped('work_email')
                manager_lists = manager_list and ",".join(manager_list) or ''
                mail_cc = self.get_cc(deg_group=True, dept_head=True, hrd=True, ra=True, f_auth=True, reg_record=res)
                mail = template.with_context(mailf=self.env.user.employee_ids.work_email,
                                             code=res.applicant_id.emp_code,
                                             mailtn=res.applicant_id.name,
                                             mail_cc=mail_cc,
                                             manager_lists=manager_lists,
                                             employee_ra = res.applicant_id.parent_id.name,
                                             reason=res.retirement,
                                             branch_alias=res.base_branch_id.alias,
                                             effective_form=datetime.strptime(str(res.effective_form), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             last_working_date=datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             department_id=res.department_id.name,
                                             division=res.division.name,
                                             section=res.section.name,
                                             practise=res.practise.name,
                                             job_id=res.job_id.name,
                                             date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                             ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Mail sent successfully.")

        # ====== Termination Create =====
        if res.offboarding_type.name == 'Termination':
            res.state = 'grant'
            assetdata = self.get_asset_data()
            advances_data = False
            petty_cash_data = False
            advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
            if not advance_checklist:
                advances_data = self.get_advance_details(res.applicant_id)
                petty_cash_data = self.get_petty_cash_details(res.applicant_id)
            template_obj = self.env.ref('kw_eos.termination_mail_template')
            tour_clearance = self.tour_clearance if self.tour_clearance else 'No tour settlement is pending'
            sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
            petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
            asset_clearance = len(assetdata) if assetdata else 'NIL'
            email_cc = self.get_cc(deg_group=True, dept_head=True, hrd=True, resource_head=True, reg_record=res)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                email_cc=email_cc,
                applicant=res.applicant_id.name,
                emp_code=res.applicant_id.emp_code,
                parent=res.applicant_id.parent_id.name,
                last_working_date=datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                termination_reason=res.termination_reason.name,
                termination_remark=res.termination_remark,
                department_id=res.department_id.name,
                division=res.division.name,
                section=res.section.name,
                practise=res.practise.name,
                job_id=res.job_id.name,
                assetdata=assetdata,
                tour_clearance=tour_clearance,
                sal_adv_clearance=sal_adv_clearance,
                petty_cash_clearance=petty_cash_clearance,
                date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y")
            ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            self.env.user.notify_success("Terminated successfully.")
            # ==== Eos creation ======
            eos_rec.sudo().create({'application_id': res.id,
                                   'applicant_id': res.applicant_id.id,
                                   'state': 'Draft',
                                   'termination_create': True,
                                   'eos_apply_for': 'sub'})
            self.env.user.notify_success("End of Service applied successfully.")

        # ====== Demise Create =====

        if res.offboarding_type.name == 'Demise':
            res.state = 'grant'
            assetdata = self.get_asset_data()
            advances_data = False
            petty_cash_data = False
            advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
            if not advance_checklist:
                advances_data = self.get_advance_details(res.applicant_id)
                petty_cash_data = self.get_petty_cash_details(res.applicant_id)
            tour_clearance = self.tour_clearance if self.tour_clearance else 'No tour settlement is pending'
            sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
            petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
            asset_clearance = len(assetdata) if assetdata else 'NIL'
            template_obj = self.env.ref('kw_eos.demise_mail_template')
            email_cc = self.get_cc(deg_group=True, dept_head=True, resource_head=True, ceo=True, reg_record=res,
                                   hrd=True)
            mail = self.env['mail.template'].browse(template_obj.id).with_context(applicant_name=res.applicant_id.name,
                                                                                  email_to=res.applicant_id.parent_id.work_email,
                                                                                  email_tn=res.applicant_id.parent_id.name,
                                                                                  email_cc=email_cc,
                                                                                  code=res.applicant_id.emp_code,
                                                                                  reason=res.demise_reason,
                                                                                  branch_alias=res.base_branch_id.alias,
                                                                                  last_working_date=datetime.strptime(str(res.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  department_id=res.department_id.name,
                                                                                  division=res.division.name,
                                                                                  section=res.section.name,
                                                                                  practise=res.practise.name,
                                                                                  job_id=res.job_id.name,
                                                                                  assetdata=assetdata,
                                                                                  tour_clearance=tour_clearance,
                                                                                  sal_adv_clearance=sal_adv_clearance,
                                                                                  petty_cash_clearance=petty_cash_clearance,
                                                                                  date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y")
                                                                                  ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
            self.env.user.notify_success("Demise request created successfully.")
            self.env.user.notify_info("Mail sent successfully.")

            # ==== Eos creation ======
            eos_rec.sudo().create({'application_id': res.id,
                                   'applicant_id': res.applicant_id.id,
                                   'state': 'Draft',
                                   'demise_create': True,
                                   'eos_apply_for': 'sub'})
            self.env.user.notify_success("End of Service applied successfully.")

        #  ===== Contract closure create ======
        if res.offboarding_type.name == 'Contract Closure':
            if res.contract_extend == 'yes':
                template_obj = self.env.ref('kw_eos.contract_extend_yes_mail_template')
                email_cc = self.get_cc(deg_group=True, dept_head=True, ra=True, f_auth=True, reg_record=res)
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    email_cc=email_cc).send_mail(res.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                self.env.user.notify_success("Terminated successfully.")

                employee_rec = self.env['hr.employee'].sudo().search([('id', '=', values.get('applicant_id'))])
                employee_rec.write({'end_date': res.new_contract_end_date})
                res.sudo().write({'state': 'extend'})
            elif res.contract_extend == 'no':
                if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
                    template_obj = self.env.ref('kw_eos.contract_apply_mail_template')
                    email_to = self.get_cc(deg_group=True, dept_head=True, hrd=True, f_auth=True)
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(actionby=self.env.user.name,
                                                                                          email_to=email_to,
                                                                                          applicant_name=res.applicant_id.name,
                                                                                          code=res.applicant_id.emp_code,
                                                                                          reason=res.contract_closure,
                                                                                          branch_alias=res.base_branch_id.alias,
                                                                                          contract_start_date=datetime.strptime(str(res.start_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                          contract_end_date=datetime.strptime(str(res.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                          department_id=res.department_id.name,
                                                                                          division=res.division.name,
                                                                                          section=res.section.name,
                                                                                          practise=res.practise.name,
                                                                                          job_id=res.job_id.name,
                                                                                          date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                          ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

                    res.sudo().write({'state': 'apply'})
                    self.env.user.notify_success("Contract Closure applied successfully.")
                else:
                    res.sudo().write({'state': 'grant'})
                    assetdata = self.get_asset_data()
                    advances_data = False
                    petty_cash_data = False
                    advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                    if not advance_checklist:
                        advances_data = self.get_advance_details(res.applicant_id)
                        petty_cash_data = self.get_petty_cash_details(res.applicant_id)
                    tour_clearance = self.tour_clearance if self.tour_clearance else 'No tour settlement is pending'
                    sal_adv_clearance = advances_data.adv_amnt if advances_data else 'NIL'
                    petty_cash_clearance = petty_cash_data.advance_amt if petty_cash_data else 'NIL'
                    asset_clearance = len(assetdata) if assetdata else 'NIL'
                    template_obj = self.env.ref('kw_eos.contract_extend_no_mail_template')
                    email_cc = self.get_cc(deg_group=True, dept_head=True, ra=True, reg_record=res)
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                        email_cc=email_cc,
                        applicant_name=res.applicant_id.name,
                        code=res.applicant_id.emp_code,
                        reason=res.contract_closure,
                        branch_alias=res.base_branch_id.alias,
                        contract_start_date=datetime.strptime(str(res.start_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                        contract_end_date=datetime.strptime(str(res.end_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                        department_id=res.department_id.name,
                        division=res.division.name,
                        section=res.section.name,
                        practise=res.practise.name,
                        job_id=res.job_id.name,
                        assetdata=assetdata,
                        tour_clearance=tour_clearance,
                        sal_adv_clearance=sal_adv_clearance,
                        petty_cash_clearance=petty_cash_clearance,
                        date_of_joining=datetime.strptime(str(res.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y"),
                        email_to=res.applicant_id.work_email,
                    ).send_mail(log.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                    self.env.user.notify_success("Contract Closure granted successfully.")
        return res

    def get_advance_details(self, applicant=False):
        advances_data = self.env['kw_advance_apply_salary_advance'].sudo().search(
            [('employee_id', '=', applicant.id), ('state', 'not in', ['paid', 'cancel', 'reject'])])
        return advances_data

    def get_petty_cash_details(self, applicant=False):
        petty_cash_data = self.env['kw_advance_apply_petty_cash'].sudo().search(
            [('user_emp_id', '=', applicant.id), ('state', 'not in', ['paid', 'cancel', 'reject'])])
        return petty_cash_data

    def get_asset_data(self):
        demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_eos.module_offboarding_mode_status')
        """ Demo mode mandatory check"""
        if demo_mode_enabled:
            return False

        """ eos api called to fetch asset data """
        assetdata = False
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
        EOSurl = parameterurl + 'ManageEOSDetails'
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        user_id = self.applicant_id.kw_id
        if not user_id:
            user_id = self.env.user.employee_ids.kw_id
        EOSDict = {
            "userId": user_id
        }
        json_record = False
        try:
            resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)

        except Exception as e:
            # print(e)
            raise ValidationError("Some error occurred.Please try again later")
        if json_record.get('Userstatus') == '1':
            if json_record.get('retEOSAsstDa'):
                assetdata = json_record.get('retEOSAsstDa')
        return assetdata

    """Reminder to RA : after 2 working days of applying RL"""

    def after_two_working_days_applying(self):
        for rec in self:
            if datetime.now().date().day - rec.effective_form.day == 2:
                template_obj = self.env.ref('kw_eos.reminder_mail_after_two_days_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                    rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """Reminder to RA : after 4 working days of applying RL"""

    def after_four_working_days_applying(self):
        for rec in self:
            if datetime.now().date().day - rec.effective_form.day == 4:
                template_obj = self.env.ref('kw_eos.reminder_mail_after_four_days_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                    rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """Reminder to upper RA : after 6 working days of applying RL"""

    def after_six_working_days_applying(self):
        for rec in self:
            if datetime.now().date().day - rec.effective_form.day == 6:
                if self.applicant_id.parent_id.parent_id.parent_id:
                    template_obj = self.env.ref('kw_eos.reminder_mail_after_six_days_template')
                    mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                    rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                else:
                    pass
               

    """Reminder to upper RA : after 8 working days of applying RL"""

    def after_eight_working_days_applying(self):
        for rec in self:
            if datetime.now().date().day - rec.effective_form.day == 8:
                template_obj = self.env.ref('kw_eos.reminder_mail_after_eight_days_template')
                if self.applicant_id.parent_id.parent_id.parent_id:
                    mail = self.env['mail.template'].browse(template_obj.id).with_context().send_mail(
                        rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                    # print("inside if=======================================resignation")
                else:
                    pass
                    # print("inside else========================resignation")

    """remainder mail scheduler"""

    @api.model
    def run_remainder_mail_eos(self):
        resignation_rec = self.env['kw_resignation'].sudo().search(
            [('effective_form', '<=', datetime.now().date()), ('state', '=', 'apply')])
        if resignation_rec:
            for rec in resignation_rec:
                rec.after_two_working_days_applying()
                rec.after_four_working_days_applying()
                rec.after_six_working_days_applying()
                rec.after_eight_working_days_applying()
    
    @api.model
    def action_update_offboarding_id(self):
        eos_rec = self.env['kw_eos_checklist'].sudo().search(
            [('offboarding_type', '=', False), ('state', '=', 'Draft')])
        for record in eos_rec:
            resignation_rec = self.env['kw_resignation'].sudo().search([('applicant_id', '=', record.applicant_id.id), ('state', '=', 'grant')],order='id desc',limit=1)
            interview_rec = self.env['employee.exit.interview'].sudo().search([('employee_id', '=', record.applicant_id.id)],order='id desc',limit=1)
            clearance_rec = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', record.applicant_id.id)],order='id desc',limit=1)
            if resignation_rec:
                update_query = f"""update kw_eos_checklist set offboarding_type = {resignation_rec.id} WHERE id={record.id};"""
                self._cr.execute(update_query)
                if interview_rec:
                    interview_query = f"""update employee_exit_interview set resignation_id = {resignation_rec.id} WHERE id={interview_rec.id};"""
                    self._cr.execute(interview_query)
                if clearance_rec:
                    clearance_query = f"""update hr_employee_clearance set resignation_id = {resignation_rec.id} WHERE id={clearance_rec.id};"""
                    self._cr.execute(clearance_query)

    @api.model
    def action_update_offboarding_reason(self):
        resign_apply = self.env['kw_resignation'].sudo().search([]) # ('state', '=', 'grant')
        for rec in resign_apply:
            emp_rec = self.env['hr.employee'].sudo().search([('id', '=', rec.applicant_id.id), ('active', '=', False)])
            for record in emp_rec:
                if not record.resignation_reason:
                    # record.write({'resignation_reason': rec.reg_type.id})
                    emp_query = f"UPDATE hr_employee SET resignation_reason={rec.reg_type.id} WHERE id={record.id};"
                    self._cr.execute(emp_query)

    @api.model
    def action_update_offboarding_record(self):
        emp_data = self.env['hr.employee'].sudo().search(
            [('active', '=', False), ('resignation_reason', '!=', False), ('last_working_day', '!=', False)])
        user_type = self.env['kw_offboarding_type_master'].sudo().search([('code', 'ilike', 'reg')])
        # print('emp_data >> ', emp_data, user_type)
        for emp in emp_data:
            if emp.resignation_reason and emp.last_working_day:
                resign_rec = self.env['kw_resignation'].sudo().search([('applicant_id', '=', emp.id)], limit=1, order="id desc")
                # , ('state', 'not in', ['reject', 'cancel'])
                # print('resign_rec >> ', resign_rec)
                if not resign_rec.exists():
                    ref_name = self.env['ir.sequence'].next_by_code('kw_resignation') or _('New')
                    insert_qry = f"INSERT INTO kw_resignation (name,applicant_id,offboarding_type, reg_type, reason, state, last_working_date,effective_form,apply_for,termination_check,retirement_check, contract_closure_check,demise_check,kt_required,hide_btn_cancel,cancel_process,check_apply_for_self, retain, hide_apply_for, contract_extend, gender, budget_submit, required_effective_from, offboard_type_reg) VALUES ('{ref_name}',{emp.id}, {user_type.id}, {emp.resignation_reason.id}, 'System Generated Resignation', 'grant', '{emp.last_working_day}','{emp.last_working_day}','self', {False}, {False}, {False}, {False},'no',{False},{False},{False},'no',{False},'no','{emp.gender}',{False},{True},{True});"
                    self._cr.execute(insert_qry)
                    # print('insert_qry >> ', insert_qry)

                    offboard_rec = self.env['kw_resignation'].sudo().search([('applicant_id', '=', emp.id)], limit=1, order="id desc")
                    # , ('state', '=', 'grant')
                else:
                    offboard_rec = resign_rec
                # print('offboard_rec >> ', offboard_rec)

                eos_checklist = self.env['kw_eos_checklist'].sudo().search(
                    ['|', ('offboarding_type', '=', offboard_rec.id), ('applicant_id', '=', emp.id)], limit=1, order="id desc")
                # print('eos_checklist > ', eos_checklist)
                # eos_check_rec = False
                if not eos_checklist.exists():
                    eos_check_rec = eos_checklist.sudo().create({'applicant_id': emp.id,
                                                                 'offboarding_type': offboard_rec.id,
                                                                 'state': 'Granted',
                                                                 })
                else:
                    eos_check_rec = eos_checklist

                clearance = self.env['hr.employee.clearance'].sudo().search(
                    ['|', ('resignation_id', '=', offboard_rec.id), ('employee_id', '=', emp.id)])
                # print('clearance > ', clearance)
                if not clearance.exists():
                    clearance.sudo().create({
                        'employee_id': emp.id,
                        'eos_id': eos_check_rec.id if eos_check_rec else False,
                        'resignation_id': offboard_rec.id,
                        'last_day_of_service': offboard_rec.last_working_date,
                        'hr_unit_date': offboard_rec.last_working_date,
                        'done_by_ra': True,
                        'done_by_it': True,
                        'done_by_admin': True,
                        'done_by_account': True})

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('ra_action'):

    #         if self.env.user.has_group('kw_eos.group_kw_eos_user'):
    #             if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
    #                 # args += [('offboarding_type.name','=','Retirement'),('state','in',['apply','pending_at_finance'])]

    #                 args += ['|', '|', '|',
    #                          '&', ('applicant_id.parent_id.user_id', '=', self.env.uid),
    #                          '&', ('state', '=', 'apply'), ('offboarding_type.name', 'not in', ['Retirement', 'Termination', 'Demise', 'Contract Closure']),
    #                          '&', ('applicant_id.department_id.manager_id.user_id', '=', self.env.uid),
    #                          ('state', 'in', ['confirm', 'cancelreject']),
    #                          '&', ('forward_to.user_id', '=', self.env.uid), ('state', '=', 'forward'),
    #                          '&', ('offboarding_type.name', '=', 'Retirement'), ('state', 'in', ['pending_at_finance'])]
    #             else:
    #                 args += ['|', '|',
    #                          '&', ('applicant_id.parent_id.user_id', '=', self.env.uid),
    #                          '&', ('state', '=', 'apply'), ('offboarding_type.name', 'not in', ['Retirement', 'Termination', 'Demise', 'Contract Closure']),
    #                          '&', ('applicant_id.department_id.manager_id.user_id', '=', self.env.uid),
    #                          ('state', 'in', ['confirm', 'cancelreject']),
    #                          '&', ('forward_to.user_id', '=', self.env.uid), ('state', '=', 'forward')]

    #         elif self.env.user.has_group('kw_eos.group_kw_eos_officer') or self.env.user.has_group(
    #                 'kw_eos.group_kw_eos_manager'):
    #             args += ['&', '|', '|',
    #                      '&', ('applicant_id.parent_id.user_id', '=', self.env.uid), ('state', '=', 'apply'),
    #                      '&', ('offboarding_type.name', '=', 'Retirement'),
    #                      ('state', 'in', ['apply', 'submit_by_finance']),
    #                      '&', ('offboarding_type.name', '=', 'Contract Closure'), ('state', '=', 'apply'),
    #                      ('create_uid', '!=', self.env.uid)]

    #     if self._context.get('applicant_action'):
    #         if self.env.user.has_group('kw_eos.group_kw_eos_user'):
    #             args += ['|', ('create_uid', '=', self.env.uid), ('applicant_id.user_id', '=', self.env.uid)]

    #     if self._context.get('report'):
    #         if self.env.user.has_group('kw_eos.group_kw_eos_manager') or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
    #             args += []
    #         else:
    #             args += ['|', '|', ('applicant_id.user_id', '=', self.env.uid),
    #                      ('applicant_id.parent_id.user_id', '=', self.env.uid),
    #                      ('applicant_id.department_id.manager_id.user_id', '=', self.env.uid)]
    #     # print('args===>',args)
    #     return super(kw_resignation, self)._search(args, offset=offset, limit=limit, order=order, count=count,
    #                                                access_rights_uid=access_rights_uid)
    @api.model
    def action_notice_period_correction(self):
        active_employees_in_notice_period = self.env['hr.employee'].sudo().search(
            [('active', '=', True), ('in_noticeperiod', '=', True)])
        for rec in active_employees_in_notice_period:
            applicant = self.env['kw_resignation'].sudo().search([('applicant_id','=',rec.id)])
            mapped_state = applicant.mapped('state')
            if mapped_state and ('apply' or 'confirm' or 'forward' or 'grant') in mapped_state:
                pass
            else:
                query = f''' update hr_employee set in_noticeperiod=False, resignation_reason=null where id = {rec.id}; '''
                self._cr.execute(query)

    @api.model
    def action_retirement_reminder_mail(self):
        sixty_years_back_date = date.today() - relativedelta(years=60)
        thirty_days_back_bday = (date.today() - relativedelta(years=60))-relativedelta(days=30)
        emp_records = self.env['hr.employee'].search(
            ['&', ('birthday', '<=', sixty_years_back_date), ('birthday', '>=', thirty_days_back_bday)])
        template_obj = self.env.ref('kw_eos.retirement_reminder_mail_template')
        today_date = date.today()
        template_obj_for_manager = self.env.ref('kw_eos.retirement_reminder_to_manager_mail_template')

        for emp in emp_records:
            if emp.birthday and emp.id:
                reminder_date = emp.birthday + relativedelta(years=60) - relativedelta(months=1)
                reminder_date_before_half_month = emp.birthday + relativedelta(years=60) - relativedelta(days=15)
                reminder_date_before_week = emp.birthday + relativedelta(years=60) - relativedelta(days=7)
                if reminder_date == today_date \
                        or reminder_date_before_half_month == today_date \
                        or reminder_date_before_week == today_date:
                    if reminder_date == today_date:
                        timeline = '1 month'
                    elif reminder_date_before_half_month == today_date:
                        timeline = '15 days'
                    elif reminder_date_before_week == today_date:
                        timeline = '7 days'
                    email_cc = self.get_cc(hrd=True, emp_id=emp, resource_head=True)
                    mail = self.env['mail.template'].browse(template_obj_for_manager.id).with_context(timeline=timeline,
                                                                                                      email_cc=email_cc).send_mail(emp.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                    self.env.user.notify_info("Mail Sent Successfully.")

                target_date = emp.birthday + relativedelta(years=60) + relativedelta(days=1)
                # target_date = emp.birthday + relativedelta(years=60)
                if target_date <= today_date and not emp.user_id.has_group('kw_eos.group_kw_eos_senior_citizen'):
                    email_cc = self.get_cc(hrd=True, emp_id=emp, resource_head=True)
                    senior_citizen_group = self.env.ref('kw_eos.group_kw_eos_senior_citizen')
                    # filter criteria here:
                    users = self.env['res.users'].search([('id', '=', emp.user_id.id)])
                    for user in users:
                        senior_citizen_group.write({'users': [(4, user.id)]})

                    mail = self.env['mail.template'].browse(template_obj.id).with_context(email_cc=email_cc).send_mail(emp.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)
                    self.env.user.notify_info("Mail sent successfully.")

    # To Do
    @api.multi
    def get_notice_period(self, employee):
        for res in self:
            np_days = [0]
            if employee.grade:
                np_datas = self.env['kw_notice_period_master'].search([('grade_ids', '=', employee.grade.id)])
                if np_datas:
                    if employee.emp_band:
                        np_days = [int(data.notice_period) for data in np_datas for bands in data.band_ids if bands.id == employee.emp_band.id]
                    else:
                        np_days = [int(data.notice_period) for data in np_datas]
                else:
                    param = self.env['ir.config_parameter'].sudo()
                    if param.get_param('kw_eos.notice_period') != 'False':
                        # print(type(param.get_param('kw_eos.notice_period')))
                        np_days = [int(param.get_param('kw_eos.notice_period'))]
                    else:
                        np_days = [0]
            else:
                param = self.env['ir.config_parameter'].sudo()
                if param.get_param('kw_eos.notice_period') != 'False':#To Do
                    np_days = [int(param.get_param('kw_eos.notice_period'))]
                else:
                    np_days = [0]
            return np_days[0]

    @api.multi
    def take_action_button(self):
        if self.env.user.id == self.applicant_id.department_id.manager_id.user_id.id  \
                or self.env.user.id == self.applicant_id.sbu_master_id.representative_id.user_id.id \
                or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
            dept_head_view_id = self.env.ref('kw_eos.resignation_view_form_action_dept').id
            finance_user_view = self.env.ref('kw_eos.resignation_view_form').id
            action = {
                'name': 'Resignation',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_resignation',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'self',
            }
            if self.env.user.id == self.applicant_id.department_id.manager_id.user_id.id \
                    or self.env.user.id == self.applicant_id.sbu_master_id.representative_id.user_id.id \
                    and self.state in ['confirm', 'cancelreject']:
                action['views'] = [(dept_head_view_id, 'form')]
                action['view_id'] = dept_head_view_id
                action['context'] = {'form_view_initial_mode': 'edit'}
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and self.state == 'pending_at_finance':
                action['views'] = [(finance_user_view, 'form')]
                action['view_id'] = finance_user_view
                action['context'] = {'form_view_initial_mode': 'edit', 'finance_user': True}
            if self.env.user.has_group('kw_employee.group_hr_ra') \
                    or self.env.user.id == self.applicant_id.parent_id.user_id.id \
                    and self.state == 'apply':
                # print("inside take action of RA==============================")
                view_id = self.env.ref('kw_eos.resignation_view_form_action_ra').id
                action['views'] = [(view_id, 'form')]
                action['view_id'] = view_id
                action['context'] = {'form_view_initial_mode': 'edit', 'default_kt_required': 'yes'}

            return action

        elif self.env.user.has_group('kw_employee.group_hr_ra') \
                or self.env.user.id == self.applicant_id.parent_id.user_id.id \
                or self.env.user.id == self.forward_to.user_id.id:
            # print("print inside elif of take action=============================")
            view_id = self.env.ref('kw_eos.resignation_view_form_action_ra').id
            action = {
                'name': 'Resignation',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_resignation',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(view_id, 'form')],
                'target': 'self',
                'view_id': view_id,
                'context': {'form_view_initial_mode': 'edit', 'default_kt_required': 'yes'},
            }
            return action
        elif self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
            view_id = self.env.ref('kw_eos.resignation_view_form_action_ra').id
            action = {
                'name': 'Retirement',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_resignation',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(view_id, 'form')],
                'target': 'self',
                'view_id': view_id,
                'context': {'form_view_initial_mode': 'edit'},
            }
            return action

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         record_name = str(record.applicant_name)+"("+str(record.name)+")"
    #         result.append((record.id, record_name))
    #     return result

    """ View redirection
    1) if login user normal Employee with no offboarding record------ forms view opens directly
    2) if login user normal employee with offboarding records -- tree view opens directly
    3) if login user is RA,HOD,HR --- tree view will be opened """

    def offboarding_menu_render(self):
        if self.env.user.has_group('kw_eos.group_kw_eos_user') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_employee.group_hr_ra') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head') \
                and not self.env.user.has_group('kw_wfh.group_hr_hod'):
            offboarding_records = self.env['kw_resignation'].sudo().search(
                [('applicant_id', '=', self.env.user.employee_ids.id)])
            if not offboarding_records:
                view_id = self.env.ref('kw_eos.resignation_view_form').id
                action = {
                    'name': 'Apply Offboarding',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_resignation',
                    'res_id': self.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'target': 'self',
                    'view_id': view_id,
                    'context': {'form_view_initial_mode': 'edit'},
                }
                return action
            else:
                action_id = self.env.ref('kw_eos.resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
        else:
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                manager_action_id = self.env.ref('kw_eos.manager_resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={manager_action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
            else:
                action_id = self.env.ref('kw_eos.resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }

    def offboarding_menu_render2(self):
        offboarding_records = self.env['kw_resignation'].sudo().search(
            ['|', ('applicant_id', '=', self.env.user.employee_ids.id), ('create_uid', '=', self.env.user.id)])
        if not offboarding_records:
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                manager_action_id = self.env.ref('kw_eos.manager_resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={manager_action_id}&model=kw_resignation&view_type=form',
                    'target': 'self',
                }
            else:
                view_id = self.env.ref('kw_eos.resignation_view_form').id
                action = {
                    'name': 'Apply Offboarding',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_resignation',
                    'res_id': self.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'target': 'self',
                    'view_id': view_id,
                    'context': {'form_view_initial_mode': 'edit'},
                }
                return action
        else:
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                manager_action_id = self.env.ref('kw_eos.manager_resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={manager_action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }
            else:
                action_id = self.env.ref('kw_eos.resignation_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
                    'target': 'self',
                }

    """ ==== View Clearance Details button method ==== """
    @api.multi
    def view_clearance_details(self):
        view_id = self.env.ref('kw_eos.view_hr_employee_clearance_form').id
        rec = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', self.applicant_id.id)])
        if rec:
            action = {
                'name': 'Employee Clearance',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee.clearance',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'res_id': rec.id,
                'context': {'create': False, 'edit': False, 'delete': False}
            }
            return action
        else:
            raise ValidationError("EOS/Clearance has not been created for the Applicant.")

    def action_correct_fy_year(self):
        rec = self.sudo().search([])  #('fiscal_yr', '=', False)
        sort_order = {
            'apply': 1, 'confirm': 2, 'forward': 3, 'grant': 4,
            'pending_at_finance': 5, 'submit_by_finance': 6, 'waiting_for_rl_cancellation': 7,
            'extend': 8, 'exemployee': 9, 'reject': 10, 'cancel': 11, 'cancelreject': 12,
        }
        for record in rec:
            today = record.effective_form
            april = today.replace(day=1, month=4)
            year = int(today.strftime("%Y"))
            # print('year >>>> ', year, today, april)
            if today >= april:
                record.fiscal_yr = f"{str(year)}-{str(year + 1)}"
            else:
                record.fiscal_yr = f"{str(year - 1)}-{str(year)}"
            record.sort = sort_order.get(record.state)


class kw_eos_log(models.Model):
    _name = "kw_eos_log"
    _description = "Service Log"
    _order = 'id desc'

    ref_id = fields.Many2one('kw_resignation')
    status = fields.Integer('Status')
    mesg = fields.Char('Message')
    req_data = fields.Char('Json Data')
    response_res = fields.Char('Response Result')
    type = fields.Char('Type')
