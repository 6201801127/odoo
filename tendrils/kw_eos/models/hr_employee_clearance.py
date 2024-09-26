# -*- coding: utf-8 -*-
import json
import requests
import collections
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
from datetime import datetime, timedelta, date
from ast import literal_eval
from odoo.exceptions import ValidationError


class HrEmployeeClearance(models.Model):
    _name = 'hr.employee.clearance'
    _description = "EOS Clearance"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _order = 'id desc'

    @api.model
    def _get_employee_list(self):
        emp_list = []
        emp_list2 = []
       
        records = self.env['kw_resignation'].search([('state','=','grant')])
        for record in records:
            if record.applicant_id.id not in emp_list:
                emp_list.append(record.applicant_id.id)

        clearance_records = self.env['hr.employee.clearance'].search([])
        for clearance in clearance_records:
            emp_list2.append(clearance.employee_id.id) if clearance.employee_id.id not in emp_list2 else False

        return [('id','in',emp_list),('id','not in',emp_list2)]

    job_id = fields.Many2one('hr.job', string="Job Position", compute="_compute_employee_details")
    # job_id = fields.Many2one(related="employee_id.job_id", string='Job Position', store=True, )
    department_id = fields.Many2one('hr.department', string='Department', compute="_compute_employee_details")
    # department_id = fields.Many2one(related="employee_id.department_id", string='Department')
    division = fields.Many2one('hr.department', string="Division", compute="_compute_employee_details")
    section = fields.Many2one('hr.department', string="Practice", compute="_compute_employee_details")
    practise = fields.Many2one('hr.department', string="Section", compute="_compute_employee_details")
    offboarding_type = fields.Many2one('kw_resignation', string='Offboarding Type', compute="_compute_employee_details")

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    resignation_id = fields.Many2one('kw_resignation', ondelete='restrict', string='Offboarding Type')
    employee_id = fields.Many2one('hr.employee', track_visibility='onchange', ondelete='restrict', string='Employee',domain=_get_employee_list)
    work_location = fields.Many2one('kw_res_branch', related='employee_id.job_branch_id', readonly=True, store=True)
    date_of_joining = fields.Date('Date of Joining', related='employee_id.date_of_joining')
    # job_grade_id = fields.Many2one(related="employee_id.job_grade_id", string='Job Grade', store=True, readonly=True)
    line_manager = fields.Many2one(related="employee_id.parent_id", string='Reporting Authority', store=True, )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 required=True, ondelete='restrict')
    last_day_of_service = fields.Date('Last Day of Service', copy=False)
    handover_all_reports = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                            'I have handed over all reports/assignments carried out while holding this position to my RA.')
    surrender_items = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       'I have surrendered all items which were entrusted to me during my employment')
    comments = fields.Text(string='Comment by Employee')
    others = fields.Text(string='Others')
    cleared_all_matters = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                           'I have cleared all matters pertaining to advances and expenditures with the Finance department. I understand that any outstanding amounts will be deducted from my final dues. ')
    ps_all_matters = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Performance Assessment All Matters')
    employee_clearance_date = fields.Date("Date", copy=False, default=fields.Date.today())
    all_work_documents_handover_report = fields.Boolean('All work-related documents and handed over report ')
    all_ps_handover_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                              'Performance assessment form completed and submitted')
    cleared_by_line_manager_unit = fields.Boolean('Clearance by RA')
    comments_by_line_manager = fields.Text(string='Comment by RA')
    completed_date_by_line_manager = fields.Date('Completed Date by Reporting Authority', copy=False,
                                                 default=fields.Date.today())
    laptop = fields.Boolean('Computer')
    laptop_accessories = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Laptop Accessories')
    ict_unit_date = fields.Date('IT Dept Date', copy=False, default=fields.Date.today())
    systems_disabled = fields.Boolean('2. Access to CSM systems disabled (Email,MIS, Biometric system etc.)')
    comments_by_ict_manager = fields.Text('Comment by IT Manager')
    ict_manager_date = fields.Date('IT Manager Date', copy=False)
    business_cards = fields.Boolean('Business Cards')
    access_cards = fields.Boolean('Access card /ID card')
    drawer_cabinet_keys = fields.Boolean('Drawer/Cabinet keys')
    cell_phone_accessories = fields.Boolean('Cell phone and accessories')
    cleared_by_administration_unit = fields.Boolean('Cleared by Admin')
    comments_by_administration_unit = fields.Text('Comment by Admin')
    cleared_by_account_unit = fields.Boolean('Cleared by Account')
    comments_by_account_unit = fields.Text('Comment by Finance')
    ict_administration_date = fields.Date('Administration Unit Date', copy=False, default=fields.Date.today())
    cleared_by_it_unit = fields.Boolean('Cleared by IT')
    email_forward_to = fields.Many2one('hr.employee', string='3. Email Forward To')
    email_forward_to_comment = fields.Text('Forward Comments')
    exit_official_whatsapp_group = fields.Boolean(string="Exit From CSM Whatsapp Group")
    comments_by_it_unit = fields.Text('Comment by IT')
    ict_account_date = fields.Date('Account Unit Date', copy=False, default=fields.Date.today())
    comments_by_finance_unit = fields.Text('Comment by Finance')
    finance_unit_date = fields.Date('Accounts Date', copy=False, default=fields.Date.today())
    number_of_leaves_earned = fields.Float('Number of leave days earned:')
    number_of_leaves_taken = fields.Float('Number of leave days taken:')
    number_of_leaves_for_payment = fields.Integer('Number of leave days for payment:')
    number_of_toil_earned = fields.Float('Number of TOIL days earned:')
    number_of_toil_taken = fields.Float('Number of TOIL days taken:')
    number_of_toil_for_payment = fields.Integer('Number of TOIL days for payment:')
    other_payments = fields.Selection([('gratuity', 'Gratuity (15% of total basic salary earned to date)'),
                                       ('other', 'Other')], 'Other Payments')
    description = fields.Text('Description')
    deductions = fields.Selection([('salary_advance', 'Salary Advance'), ('other', 'Other')], 'Deductions')
    deductions_description = fields.Text('Description of Deductions')
    medical_cards_returned = fields.Boolean('Medical Cards Returned')
    medical_cards_returned_comment = fields.Text('Medical Cards Returned Comment')
    ps_form = fields.Boolean('Performance assessment form')
    ps_form_comment = fields.Text('Performance assessment form Comment')
    hr_cleared = fields.Selection([('cleared', 'Cleared'), ('not_cleared', 'Not cleared')], 'HR Cleared')
    eos_granted = fields.Char(string='EOS Clearance')
    ra_clearance = fields.Char(string='RA Clearance')
    admin_clearance = fields.Char(string='Admin Clearance')
    it_clearance = fields.Char(string='IT Clearance')
    comments_by_hr_unit = fields.Text('Comments by HR')
    hr_unit_date = fields.Date(string='Last Working Date', copy=False, default=fields.Date.today())
    # responsibility_center_id = fields.Many2one(related='employee_id.working_country_id', string='Responsibility Center',store=True, readonly=True)
    handover_all_reports_comment = fields.Text('Handover All Reports Comments')
    want_laptop_accessories_details = fields.Boolean('Want laptop accessories details?')
    laptop_accessories_details = fields.Text('Laptop Accessories Details')
    # em_signature = fields.Binary(related="employee_id.digital_signature",string='Employee Signature', store=True, readonly=True)
    lm_signature = fields.Binary(string='RA Signature')
    ict_administration_signature = fields.Binary(string='Admin Dept Signature')
    finance_unit_signature = fields.Binary(string='Accounts Dept Signature')
    laptop_comment = fields.Text('Laptop Comment')
    laptop_accessories_comment = fields.Text('Laptop Accessories Comment')
    ict_unit_signature = fields.Binary(string='IT Dept Signature')
    ict_signature = fields.Binary(string='IT Dept Signature')
    ict_manager_signature = fields.Binary(string='IT Manager Signature')
    hr_unit_signature = fields.Binary(string='HR Dept Signature')
    fu_gratuity = fields.Char(string='Gratuity')
    fu_other = fields.Char(string='Other')
    oa_travel_advance_label = fields.Char(string='Tour advance Comment')
    oa_travel_advance = fields.Boolean(string='Tour advance')
    oa_other_staff_advance_label = fields.Char(string='Other staff advance Comment')
    oa_other_staff_advance = fields.Boolean(string='Other staff advance')
    oa_salary_advance_label = fields.Char(string='Salary advance Comment')
    oa_salary_advance = fields.Boolean(string='Salary advance')
    comment_salary_advance = fields.Text(string='Comments')
    comment_travel_advance = fields.Text(string='Comments')
    comment_petty_cash = fields.Text(string='Comments')
    comment_account = fields.Text(string='Comments')
    comments_income_tax_declaration = fields.Text(string='Income Tax Decalaration Comments')
    comments_income_tax_recovery = fields.Text(string='Income Tax Recovery Comments')
    cleared_income_tax_declaration = fields.Boolean(string='Income Tax Declaration')
    cleared_income_tax_recovery = fields.Boolean(string='Income Tax Recovery')
    done_by_account_first_level = fields.Boolean(string='First Level Account')
    emp_tax_given = fields.Boolean(string='Tax Given',compute='_compute_check_user' )


    petty_cash = fields.Boolean(string='Petty cash')
    oa_ld_label = fields.Char(string='Learning and development advance Comment')
    oa_ld = fields.Boolean(string='Learning and development advance advance')
    oa_other_label = fields.Char(string='Other Label')

    comment_business_cards = fields.Text(string='Comments')
    comment_access_cards = fields.Text(string='Comments')
    comment_drawer_cabinet_keys = fields.Text(string='Comments')
    comment_cell_phone_accessories = fields.Text(string='Comments')
    comment_cleared_by_administration_unit = fields.Text(string='Comments')

    eos_id = fields.Many2one('kw_eos_checklist', string="EOS ID")
    # == button action flag field ==
    done_by_emp = fields.Boolean(string='Done by Employee', default=False)
    done_by_ra = fields.Boolean(string='Done by RA', default=False)
    done_by_it = fields.Boolean(string='Done by IT', default=False)
    done_by_admin = fields.Boolean(string='Done by Admin', default=False)
    done_by_account = fields.Boolean(string='Done by Finance', default=False)
    done_by_hr = fields.Boolean(string='Done by HR', default=False)
    re_hire_eligibility = fields.Boolean(string='Eligibility for Re-hire?', default=False)
    reason_for_re_hire = fields.Text(string='Reason For Re-hire')
    is_exit_settlement_complete = fields.Boolean(
        string='Are the Exit formalities and Full & Final Settlement is Complete?', default=False)
    reason_exit_settlement = fields.Text(string='Reason')
    # reason_for_leaving = fields.Text(string="Reason For Leaving")
    feedback = fields.Text(string="Feedback on account of Disciplinary/Ethical/Integrity conduct on the job")
    check_eos_grant = fields.Boolean(string="Check EOS Grant", default=False, compute="_check_all_done")
    check_all_done = fields.Boolean(string="All Done", default=False, compute="_check_all_done")
    check_eos_status = fields.Char(string="EOS Status", compute="_check_all_done")
    check_eos_pending_status = fields.Many2one('hr.employee', string="EOS Pending at", compute="_check_all_done")
    compute_eos_status = fields.Char(string="EOS Status", compute="_check_all_done")
    check_ex_employee = fields.Boolean(string="Ex Employee", default=False, compute="_check_ex_employee")
    exemployee = fields.Boolean(string="Converted to Ex-Employee", default=False, )

    current_user = fields.Boolean(string="Current User", default="False", compute="_compute_current_user")
    check_parent = fields.Boolean(string="Check Parent", default="False", compute="_compute_current_user")
    check_manager = fields.Boolean(string="Check Manager", default="False", compute="_compute_current_user")
    emp_rec_readonly = fields.Boolean(string="Employee Field Readonly", default="False",
                                      compute="_compute_current_user")

    check_admin_user = fields.Boolean(string="Check Admin User", default=False, compute="_compute_check_user")
    check_account_user = fields.Boolean(string="Check Account User", default=False, compute="_compute_check_user")
    check_it_user = fields.Boolean(string="Check IT User", default=False, compute="_compute_check_user")
    check_hr_user = fields.Boolean(string="Check HR User", default=False, compute="_compute_check_user")
    check_account_final_user = fields.Boolean(string='Is Finance Final User',default=False, compute="_compute_check_user")

    effective_from = fields.Date(related='offboarding_type.effective_form', string='Effective from')
    active = fields.Boolean(string="Active", default=True)
    """ clearance comments """
    ra_daocumnt_clearance = fields.Text(string='Comments')
    business_card_clearance_cmmt = fields.Text(string='Comments')
    id_card_clearance_cmmt = fields.Text(string='Comments')
    drawerkeys_clearance_cmmt = fields.Text(string='Comments')
    computer_clearance_cmnt = fields.Text(string='Comments')
    email_clearance_cmnt = fields.Text(string='Comments')
    whatapp_clearance_cmnt = fields.Text(string='Comments')
    hr_eos_clearance = fields.Text(string='Comments')
    hr_ra_clearance = fields.Text(string='Comments')
    hr_it_clearance = fields.Text(string='Comments')
    hr_admin_clearance = fields.Text(string='Comments')
    hr_finance_clearance = fields.Text(string='Comments')
    """ Additional IT details """
    mouse = fields.Boolean(string='Mouse')
    mouse_comment = fields.Text('Comment')
    key_board = fields.Boolean(string='Keyboard')
    key_board_comment = fields.Text('Comment')
    pendrive = fields.Boolean(string='Pendrive')
    pendrive_comment = fields.Text('Comment')
    data_card = fields.Boolean(string='Datacard')
    data_card_comment = fields.Text('Comment')
    mobile = fields.Boolean(string='Mobile')
    mobile_comment = fields.Text('Comment')
    laptop_bag = fields.Boolean(string='Laptop Bag')
    laptop_bag_comment = fields.Text('Comment')
    closed_server_access = fields.Boolean(string='Closed Server Access')
    closed_server_access_comment = fields.Text('Comment')
    shared_folder = fields.Boolean(string='Shared Folder')
    shared_folder_comment = fields.Text('Comment')
    database = fields.Boolean(string='Database')
    database_comment = fields.Text('Comment')
    server_instance = fields.Boolean(string='Server Instance')
    server_instance_comment = fields.Text('Comment')
    ip_phone = fields.Boolean(string='IP Phone')
    ip_phone_comment = fields.Text('Comment')
    ext_no = fields.Boolean(string='Ext. No')
    ext_no_comment = fields.Text('Comment')
    abbr_dialling = fields.Boolean(string='Abbr. Dialling')
    abbr_dialling_comment = fields.Text('Comment')
    call_forwarding = fields.Boolean(string='Call Forwarding')
    call_forwarding_comment = fields.Text('Comment')
    vpn_access = fields.Boolean(string='VPN Access')
    vpn_access_comment = fields.Text('Comment')
    wifi_access_to_mobile = fields.Boolean(string='Wifi Access to Mobile')
    wifi_access_to_mobile_comment = fields.Text('Comment')
    cug_connection = fields.Boolean(string='CUG Connection')
    cug_connection_comment = fields.Text('Comment')
    project_backup = fields.Boolean(string='Project Backup')
    project_backup_comment = fields.Text('Comment')
    other_backup = fields.Boolean(string='Other Backup')
    other_backup_comment = fields.Text('Comment')
    other = fields.Boolean(string='Other')
    other_comment = fields.Text('Comment')
    attrition_type = fields.Selection([('vountary', 'Voluntary'), ('involuntary', 'Involuntary')], 'Attrition Type',
                              track_visibility='onchange',)
    involuntary_reason = fields.Selection([('contract_closure', 'Contract Closure'),('demise','Demise'),('performance_issue', 'Performance Issue'),('retirement','Retirement'),('termination', 'Termination')], 'Involuntary Attrition Reason',
                              track_visibility='onchange',)
    # === Compute Group User =======
    @api.depends('employee_id')
    def _compute_check_user(self):
        finance_user_check =self.env['ir.config_parameter'].sudo().get_param('finance_approval')
        for rec in self:
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin'):
                rec.check_admin_user = True
            if (self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance')
                    and self.env.user.employee_ids.emp_code ==  str(finance_user_check)):
                rec.check_account_final_user = True
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
                rec.check_account_user = True
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                rec.check_it_user = True
            if (self.env.user.has_group('kw_eos.group_kw_eos_manager') or self.env.user.has_group(
                    'kw_eos.group_kw_eos_officer')) and rec.done_by_ra == True:
                rec.check_hr_user = True
            if self.resignation_id.tax_given == True:
                self.emp_tax_given=True
            else:
                self.emp_tax_given=False


    # ===== Compute Employee Details =====
    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            employee = rec.employee_id
            offboard_id = self.env['kw_resignation'].sudo().search(
                [('applicant_id', '=', employee.id), ('state', '=', 'grant')])
            rec.job_id = employee.job_id.id
            rec.division = employee.division.id
            rec.section = employee.section.id
            rec.practise = employee.practise.id
            rec.department_id = employee.department_id.id
            rec.offboarding_type = offboard_id.id

    @api.multi
    def _compute_current_user(self):
        for rec in self:
            if rec.employee_id.user_id.id == self.env.user.id or self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                rec.current_user = True
            if rec.employee_id.parent_id.user_id.id == self.env.user.id or self.env.user.has_group(
                    'kw_eos.group_kw_eos_manager'):
                if rec.employee_id.parent_id.user_id.id == self.env.user.id:
                    rec.check_parent = True
                # if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                #     rec.check_parent = True
                if rec.employee_id.parent_id.user_id.id == self.env.user.id and not self.env.user.has_group(
                        'kw_eos.group_kw_eos_manager'):
                    rec.check_parent = True
                elif self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                    rec.check_manager = True

            if self.env.user.has_group('kw_eos.group_kw_eos_manager') or rec.employee_id.user_id.id == self.env.user.id:
                rec.check_manager = True
                if rec.employee_id.user_id.id == self.env.user.id:
                    rec.emp_rec_readonly = True
            if self.env.user.has_group('kw_eos.group_kw_eos_officer'):
                rec.check_manager = True

    @api.multi
    def action_done_emp(self):
        self.done_by_emp = True

    @api.multi
    def action_done_ra(self):
        # if not self.all_work_documents_handover_report:
        #     raise ValidationError("All work-related documents and handover report done?")
        self.sudo().write({
            'done_by_ra': True,
            'hr_ra_clearance': self.comments_by_line_manager,
        })
        email_to = self.sudo().grt_clearance_cc(hrd=True, manager_group=True)
        template_obj = self.env.ref('kw_eos.mail_clearance_response')
        clearance = self.sudo().create_clearance_log("Clearance By RA", False, False, False, True)
        mail = self.env['mail.template'].browse(template_obj.id).with_context(action=self.env.user.employee_ids.name,
                                                                              email_to=email_to,
                                                                              applicant_name=self.employee_id.name,
                                                                              applicant_code=self.employee_id.emp_code,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.completed_date_by_line_manager),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ).send_mail(
            clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light',
            force_send=False)

    @api.multi
    def action_done_it(self):
        self.sudo().write({
            'done_by_it': True,
            'hr_it_clearance': self.comments_by_it_unit,
        })

        # cc = self.sudo().grt_clearance_cc(ra=True, hod=True, manager_group=True)
        cc = ''
        email_to = self.sudo().grt_clearance_cc(hrd=True, manager_group=True)
        template_obj = self.env.ref('kw_eos.mail_clearance_response')
        clearance = self.sudo().create_clearance_log("Clearance By IT", True, False, False, False)
        mail = self.env['mail.template'].browse(template_obj.id).with_context(action='IT Team',
                                                                              cc=cc,
                                                                              email_to=email_to,
                                                                              applicant_name=self.employee_id.name,
                                                                              applicant_code=self.employee_id.emp_code,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.completed_date_by_line_manager),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ).send_mail(
            clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light',
            force_send=False)

    @api.multi
    def action_done_admin(self):
        self.sudo().write({
            'done_by_admin': True,
            'hr_admin_clearance': self.comments_by_administration_unit,
        })
        self.done_by_admin = True
        # cc = self.sudo().grt_clearance_cc(ra=True, hod=True, manager_group=True)
        cc = ''
        email_to = self.sudo().grt_clearance_cc(hrd=True, manager_group=True)
        clearance = self.sudo().create_clearance_log("Clearance By Admin", False, True, False, False)
        template_obj = self.env.ref('kw_eos.mail_clearance_response')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(action='Admin Team',
                                                                              cc=cc,
                                                                              email_to=email_to,
                                                                              applicant_name=self.employee_id.name,
                                                                              applicant_code=self.employee_id.emp_code,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.completed_date_by_line_manager),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ).send_mail(
            clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light',
            force_send=False)

    @api.multi
    def action_done_account(self):
        self.sudo().write({
            'done_by_account_first_level': True,
        })

    @api.multi
    def action_done_account_final(self):
        self.sudo().write({
            'done_by_account': True,
            'hr_finance_clearance': self.comments_by_account_unit,
        })
        clearance = self.sudo().create_clearance_log("Clearance By Finance", False, False, True, False)
        # cc = self.sudo().grt_clearance_cc(ra=True, hod=True, manager_group=True)
        cc = ''
        email_to = self.sudo().grt_clearance_cc(hrd=True, manager_group=True)
        template_obj = self.env.ref('kw_eos.mail_clearance_response')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(action='Finance Team',
                                                                              cc=cc,
                                                                              email_to=email_to,
                                                                              applicant_name=self.employee_id.name,
                                                                              applicant_code=self.employee_id.emp_code,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.completed_date_by_line_manager),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ).send_mail(
            clearance.id, notif_layout='kwantify_theme.csm_mail_notification_light',
            force_send=False)

    # @api.multi
    # def action_done_hr(self):
    #     self.done_by_hr = True

    def create_clearance_log(self, remark, it=False, admin=False, finance=False, ra=False):
        obj = self.sudo()
        record = self.env['kw_clearance_log'].sudo().create({
            'applicant_id': obj.employee_id.id,
            'remark': remark,
            'ra': True if it else False,
            'it': True if it else False,
            'admin': True if admin else False,
            'finance': True if finance else False,
            'eos_id': obj.eos_id.id,
            'offboarding_id': obj.offboarding_type.id,
        })
        return record

    @api.multi
    def write(self, values):
        if "comments_by_hr_unit" in values:
            values['done_by_hr'] = True
        if "hr_unit_date" in values:
            if self.eos_id:
                hr_unit_date = values.get('hr_unit_date') if "hr_unit_date" in values else self.hr_unit_date
                self.eos_id.last_working_date = hr_unit_date
                self.eos_id.offboarding_type.last_working_date = hr_unit_date

        # Check for attrition_type and involuntary_reason in values and update the related hr.employee record
        if "attrition_type" in values or "involuntary_reason" in values:
            for record in self:
                employee = record.employee_id
                if "attrition_type" in values:
                    employee.attrition_type = values.get('attrition_type')
                if "involuntary_reason" in values:
                    employee.involuntary_reason = values.get('involuntary_reason')

        res = super(HrEmployeeClearance, self).write(values)
        return res

    def grt_clearance_cc(self, hrd=False, hod=False, ra=False, manager_group=False):
        email_list = []
        param = self.env['ir.config_parameter'].sudo()
        if hrd:
            hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
            empls = self.env['hr.employee'].sudo().search([('id', 'in', hrd_group)])
            email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')

            hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

        if hod:
            if self.employee_id.department_id.manager_id:
                email_list.append(self.employee_id.department_id.manager_id.work_email)

        if ra:
            if self.employee_id.parent_id.work_email:
                email_list.append(self.employee_id.parent_id.work_email)

        if manager_group:
            manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
            email_list += manager.filtered(lambda r: r.work_email != False).mapped('work_email')

        cc = email_list and ",".join(email_list) or ''
        return cc

    @api.multi
    def exemployee_confirmation_redirect(self):
        view_id = self.env.ref('kw_eos.hr_employee_confirmation_redirect_form').id
        if view_id:
            action = {
                'name': 'Confirmation',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee.clearance',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'res_id': self.id,
                'context': {'create': False, 'edit': False}
            }
            return action

    @api.multi
    def action_convert_exemployee(self):
        self.exemployee = True
        if self.eos_id:
            self.eos_id.last_working_date = self.hr_unit_date
            self.eos_id.offboarding_type.last_working_date = self.hr_unit_date
            self.offboarding_type.manual_closing = True
        employee_rec = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
        user_rec = self.env['res.users'].sudo().search([('id', '=', self.employee_id.user_id.id)])
        if employee_rec:
            employee_rec.sudo().write({'last_working_day': self.hr_unit_date, 'active': False})
        if user_rec:
            user_rec.sudo().write({'active': False})
        json_record = False
        """ API starts """
        """ sending data to v5 for ex-employee (post method) """
        demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_eos.module_offboarding_mode_status')
        if demo_mode_enabled:
            pass
        else:
            parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
            EOSurl = parameterurl + 'MoveEOSExEmp'
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            EOSDict = {
                "userId": str(self.employee_id.kw_id),
                "LeavingDate": datetime.strptime(str(self.hr_unit_date), "%Y-%m-%d").strftime("%Y-%m-%d"),
            }
            try:
                resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
                j_data = json.dumps(resp.json())
                json_record = json.loads(j_data)
            except Exception:
                raise ValidationError("Some error occurred.Please try again later")
            if json_record.get('status') == 1:
                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'EX-Employee EOS Data',
                                                                       'new_record_log': EOSDict,
                                                                       'request_params': EOSurl,
                                                                       'response_result': json_record})
                # self.env['kw_eos_log'].sudo().create({'req_data': EOSDict,'response_res':json_record,'type': 'MoveEOSExEmp'})
        """ API ends """
        self.env.user.notify_success("Converted to Ex-Employee")
        return self.action_employee_clearance()
        # action_id = self.env.ref('kw_eos.action_hr_employee_clearance').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_resignation&view_type=list',
        #     'target': 'self',
        # }

    @api.multi
    def _check_all_done(self):
        for rec in self:
            rec.sudo().check_eos_status = rec.sudo().eos_id.sudo().state
            # print("rec.eos_id.action_to_be_taken_by",rec.eos_id.action_to_be_taken_by)
            if rec.sudo().eos_id.sudo().action_to_be_taken_by:
                rec.sudo().check_eos_pending_status = rec.sudo().eos_id.sudo().action_to_be_taken_by
            if rec.sudo().eos_id.sudo().state == "Granted":
                rec.sudo().check_eos_grant = True
            if rec.sudo().done_by_ra and rec.sudo().done_by_it and rec.sudo().done_by_admin and rec.sudo().done_by_account and rec.sudo().check_eos_grant:
                rec.sudo().check_all_done = True
            rec.sudo().compute_eos_status = "Granted" if rec.sudo().eos_id.sudo().state == "Granted" else f"Pending at {rec.sudo().eos_id.sudo().action_to_be_taken_by.name}"

    @api.model
    def action_exemployee_reminder_mail(self):
        clearance_record = self.env['hr.employee.clearance'].sudo().search(
            [('last_day_of_service', '<=', datetime.now().date())])
        for rec in clearance_record:
            if rec.check_ex_employee == False and rec.last_day_of_service <= datetime.now().date():
                param = self.env['ir.config_parameter'].sudo()
                hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
                email_list = []

                if hrd_group:
                    empls = self.env['hr.employee'].search([('id', 'in', hrd_group)])
                    email_list += empls.filtered(lambda r: r.work_email != False).mapped('work_email')

                hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
                if hrd_cc_group:
                    email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

                if email_list:
                    email = ",".join(email_list)

                    template_obj = self.env.ref('kw_eos.exemployee_reminder_mail_template')
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(email_to=email,
                                                                                          employee=rec.employee_id.name).send_mail(
                        self.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    def action_employee_clearance(self):
        finance_final_check = self.env['ir.config_parameter'].sudo().get_param('finance_approval')
        # print("emp code of finanace=====================",finance_final_check,type(finance_final_check))
        # print("login user emp code of finanace=====================",self.env.user.employee_ids.emp_code,type(self.env.user.employee_ids.emp_code))

        tree_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_report_tree').id
        form_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_form').id
        action = {
            'name': 'Clearance Form',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.clearance',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'target': 'main',
            'view_id': tree_view_id,
            'domain': [('employee_id.user_id', '=', self.env.uid)],
        }
        if self.env.user.has_group('kw_eos.group_kw_eos_manager') or self.env.user.has_group('kw_eos.group_kw_eos_officer'):
            tree1_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_report_tree_manager').id
            form_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_form').id

            action['domain'] = ['|', ('exemployee', '=', False), ('employee_id.parent_id.user_id', '=', self.env.uid)]
            action['views'] = [(tree1_view_id, 'tree'), (form_view_id, 'form')]
            action['view_id'] = tree1_view_id

        elif (self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance')
              and self.env.user.employee_ids.emp_code == str(finance_final_check)):
            action['domain'] = ['|', '&', ('done_by_account', '=', False), ('done_by_account_first_level', '=', True),
                                ('employee_id.parent_id.user_id', '=', self.env.uid)]

        elif (self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance')
              and not self.env.user.employee_ids.emp_code == str(finance_final_check)):
            action['domain'] = ['|', '&', ('done_by_account', '=', False), ('done_by_account_first_level', '!=', True),
                                ('employee_id.parent_id.user_id', '=', self.env.uid)]
        elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
            action['domain'] = ['|', ('done_by_it', '=', False), ('employee_id.parent_id.user_id', '=', self.env.uid)]
        elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin'):
            action['domain'] = ['|', ('done_by_admin', '=', False), ('employee_id.parent_id.user_id', '=', self.env.uid)]
        elif self.env.user.has_group('kw_employee.group_hr_ra'):
            attendance = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', self.env.user.employee_ids.id),
                 ('attendance_recorded_date', '=', datetime.today().date())])
            # if RA is on leave, it will show to upper RA
            if attendance and attendance.status == 'On Leave':
                action['domain'] = [('employee_id.parent_id.parent_id.user_id', '=', self.env.uid)]
            else:
                action['domain'] = [('employee_id.parent_id.user_id', '=', self.env.uid)]
        elif self.env.user.has_group('kw_eos.group_kw_eos_user'):
            action['domain'] = [('employee_id.user_id', '=', self.env.uid)]

        # print("action = ",action)
        return action

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('clearance_report'):
            ids = []
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
                # query = "select id from hr_employee_clearance where done_by_account=False"
                # self._cr.execute(query)
                # ids = self._cr.fetchall()
                # args += ['|', ('id', 'in', ids)]
                args += ['|', ('done_by_account', '=', False)]

            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                # query = "select id from hr_employee_clearance where done_by_it=False"
                # self._cr.execute(query)
                # ids = self._cr.fetchall()
                # args += ['|', ('id', 'in', ids)]
                args += ['|', ('done_by_it', '=', False)]

            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin'):
                # query = "select id from hr_employee_clearance where done_by_admin=False"
                # self._cr.execute(query)
                # ids = self._cr.fetchall()
                # args += ['|', ('id', 'in', ids)]
                args += ['|', ('done_by_admin', '=', False)]

            elif self.env.user.has_group('kw_employee.group_hr_ra'):
                # if RA on leave domain for upper RA 
                upper_ra = False
                attendance = self.env['kw_daily_employee_attendance'].search(
                    [('employee_id', '=', self.employee_id.parent_id.id),
                     ('attendance_recorded_date', '=', datetime.today().date())])
                if attendance and attendance.status == 'On Leave':
                    args += [('employee_id.parent_id.parent_id.user_id', '=', self.env.uid)]
                else:
                    args += [('employee_id.parent_id.user_id', '=', self.env.uid)]

            elif self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                # query = "select id from hr_employee_clearance where exemployee=False"
                # self._cr.execute(query)
                # ids = self._cr.fetchall()
                # args += [('id', 'in', ids)]
                args += [('exemployee', '=', False)]

            elif self.env.user.has_group('kw_eos.group_kw_eos_user'):
                args += [('employee_id.user_id', '=', self.env.uid)]

        return super(HrEmployeeClearance, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                        access_rights_uid=access_rights_uid)

    @api.multi
    def _check_ex_employee(self):
        for rec in self:
            active_emp = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])
            if rec.done_by_hr and active_emp:
                rec.check_ex_employee = True

    """ ==== View Employee feedback button method ==== """

    @api.multi
    def view_emp_eos_form(self):
        view_id = self.env.ref('kw_eos.view_employee_exit_interview_report_form').id
        rec = self.env['employee.exit.interview'].sudo().search([('employee_id', '=', self.employee_id.id)],
                                                                order='id desc', limit=1)
        if rec:
            action = {
                'name': 'Exit Interview Form',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.exit.interview',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'res_id': rec.id,
                'context': {'create': False, 'edit': False}
            }
            return action
        else:
            raise ValidationError(_('Employee Feedback not found'))


class ClearanceUpdation(models.TransientModel):
    _name = "clearance_update_wizard"
    _description = "clearance_update_wizard"

    clearance_id = fields.Many2one("hr.employee.clearance", string="Employee", required=True)
    re_hire_eligibility = fields.Boolean(string='Eligibility for Re-hire?', default=False)
    reason_for_re_hire = fields.Text(string='Reason For Re-hire')
    is_exit_settlement_complete = fields.Boolean(
        string='Are the Exit formalities and Full & Final Settlement is Complete?', default=False)
    reason_exit_settlement = fields.Text(string='Reason')
    feedback = fields.Text(string="Feedback on account of Disciplinary/Ethical/Integrity conduct on the job")
    comments_by_hr_unit = fields.Text('Comments by HR')

    @api.onchange('clearance_id')
    def update_clearance_details(self):
        if self.clearance_id:
            self.re_hire_eligibility = self.clearance_id.re_hire_eligibility
            self.reason_for_re_hire = self.clearance_id.reason_for_re_hire
            self.is_exit_settlement_complete = self.clearance_id.is_exit_settlement_complete
            self.reason_exit_settlement = self.clearance_id.reason_exit_settlement
            self.feedback = self.clearance_id.feedback
        else:
            self.re_hire_eligibility = False
            self.reason_for_re_hire = False
            self.is_exit_settlement_complete = False
            self.reason_exit_settlement = False
            self.feedback = False

    def submit_update_data(self):
        record = self.env['hr.employee.clearance'].sudo().search([('id', '=', self.clearance_id.id)])
        if record:
            record.write({'re_hire_eligibility': self.re_hire_eligibility,
                          'reason_for_re_hire': self.reason_for_re_hire,
                          'is_exit_settlement_complete': self.is_exit_settlement_complete,
                          'reason_exit_settlement': self.reason_exit_settlement,
                          'feedback': self.feedback})

    def submit_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    # @api.constrains('completed_date_by_line_manager')
    # def onchange_completed_date_by_line_manager(self):
    #     if self.completed_date_by_line_manager:
    #         if self.completed_date_by_line_manager < self.create_date.date():
    #             print("validation --------1")
    #             raise ValidationError(_('Date is less than Applied date'))
    # if self.completed_date_by_line_manager > self.last_day_of_service:
    #     raise ValidationError(_('Date is greater than Last date of service'))

    # @api.constrains('ict_administration_date')
    # def onchange_ict_administration_date(self):
    #     if self.ict_administration_date:
    #         if self.ict_administration_date < self.create_date.date():
    #             print("validation --------2")
    #             raise ValidationError(_('Date is less than Applied date'))
    # if self.ict_administration_date > self.last_day_of_service:
    #     raise ValidationError(_('Date is greater than Last date of service'))

    # @api.constrains('ict_account_date')
    # def onchange_ict_account_date(self):
    #     if self.ict_account_date:
    #         if self.ict_account_date < self.create_date.date():
    #             print("validation --------3")
    #             raise ValidationError(_('Date is less than Applied date'))
    # if self.ict_account_date > self.last_day_of_service:
    #     raise ValidationError(_('Date is greater than Last date of service'))

    # @api.constrains('ict_unit_date')
    # def onchange_ict_unit_date(self):
    #     if self.ict_unit_date:
    #         if self.ict_unit_date < self.create_date.date():
    #             print("validation --------4")
    #             raise ValidationError(_('Date is less than Applied date'))
    # if self.ict_unit_date > self.last_day_of_service:
    #     raise ValidationError(_('Date is greater than Last date of service'))
