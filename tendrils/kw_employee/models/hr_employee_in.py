# *******************************************************************************************************************
#  File Name             :   kwemp_change_ra.py
#  Description           :   This model is used to change RA 
#  Modified by           :   Monalisha Rout
#  Modified On           :   17 Aug,2020
#  Modification History  :   modified the field type of id_card_no and made a master for it.   
# *******************************************************************************************************************

# -*- coding: utf-8 -*-
"""
    This model inherits Employee(hr.employee) to add extra functionalities

"""
# -*- coding: utf-8 -*-

import re
from lxml import etree
import requests, json
from ast import literal_eval
from datetime import date, datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo import tools, _
from odoo import http
from odoo.exceptions import ValidationError, AccessError
from odoo.addons.kw_utility_tools import kw_validations
from odoo.http import request


DEFAULT_INTERNAL_GRP = 1


class hr_employee_in(models.Model):
    _inherit = "hr.employee"
    _order = "name asc, date_of_joining desc"

    """# START : additional hr setting"""
    is_wfh = fields.Boolean('WFH', default=False, readonly=False)
    kw_id = fields.Integer(string='Tendrils ID')
    emp_code = fields.Char(string=u'Employee Code', size=100)
    emp_grade = fields.Many2one(string=u'GradeX', comodel_name='kwemp_grade', ondelete='set null')
    grade = fields.Many2one('kwemp_grade_master', string='Grade')
    emp_band = fields.Many2one(string=u'Band', comodel_name='kwemp_band_master', ondelete='set null')
    date_of_joining = fields.Date(string="Joining Date")  # ,required=True
    joining_type = fields.Selection([('Lateral', 'Lateral'), ('Intern', 'Intern')], default="Lateral", string='Joined as')
    date_of_completed_probation = fields.Date(string="Probation Complete Date")
    confirmation_sts = fields.Boolean("Confirmation Status", default=False)

    onboarding_checklist = fields.Many2one(string=u'Onboarding Checklist', comodel_name='kw_employee_onboarding_checklist')
    
    # system_configuration = fields.Many2many('kwemp_config_type', string="Environment Configuration")
    # mrf = fields.Char(string='MRF ')
    emp_role = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category")
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")#16
    # default=lambda self: self.env['kwemp_employment_type'].search([('code','=','O')])
    code = fields.Char(string="Code", related='employement_type.code')
    direct_indirect = fields.Selection(string="Direct/Indirect", selection=[('1', 'Direct'), ('2', 'Indirect')])
    start_date = fields.Date(string='Contract Start Date', track_visibility='always')
    end_date = fields.Date(string='Contract End Date', track_visibility='always')
    # hide = fields.Boolean(string='Hide', compute="_compute_hide")
    onboarding_create_check = fields.Boolean(string='Onboarding Flow', default=False)

    id_card_no = fields.Many2one('kw_card_master', string=u'ID Card No',
                                 domain=[('active', '=', True), ('state', '=', 'unassigned')])
    # csm_email_id            = fields.Char(string=u'Work Email ID', size=100)

    biometric_id = fields.Char(string=u'Biometric ID', size=100)
    outlook_pwd = fields.Char(string=u'Outlook Password', size=100, groups="hr.group_hr_manager,kw_employee.group_payroll_manager")#23
    epbx_no = fields.Char(string=u'EPBX', size=100)

    domain_login_id = fields.Char(string=u'System Domain ID', size=100)
    domain_login_pwd = fields.Char(string=u'System Domain Password', size=100)
    # END : additional hr setting

    """# START : Personal Info"""
    """# start: overriding the existing fields"""
    name = fields.Char(string="Name", size=100)
    mobile_phone = fields.Char(string="Mobile No", size=15)
    work_phone = fields.Char(string="Work Phone No", size=18)
    work_location_id = fields.Many2one('res.partner', string="Work Location ID",
                                       domain="[('parent_id', '=', company_id)]", help="Employee's working location.")
    work_location = fields.Char(string="Work Location", related='work_location_id.city', readonly=True)
    work_email = fields.Char(string="Work Email", size=100)
    job_title = fields.Char(string="Job Role", size=100)
    gender = fields.Selection(groups="base.group_user")

    image = fields.Binary(string="Upload Photo",
                          help="Only .jpeg,.png,.jpg format are allowed. Maximum file size is 1 MB", required=True)

    # marital = fields.Selection(string='Marital Status', groups="base.group_user", default='single')
    # marital = fields.Many2one('kwemp_maritial_master')
    marital_sts = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    marital_code = fields.Char(string=u'Marital Status Code ')

    country_id = fields.Many2one(groups="base.group_user")
    birthday = fields.Date(groups="base.group_user")
    identification_id = fields.Char(string='Identification No (Aadhar No)', groups="base.group_user", size=100)
    passport_id = fields.Char(groups="base.group_user", size=100)

    permit_no = fields.Char(groups="base.group_user", size=100)
    visa_no = fields.Char(size=100, groups="hr.group_hr_manager,kw_employee.group_payroll_manager")#28
    visa_expire = fields.Date(groups="base.group_user")

    emergency_contact = fields.Char("Emergency Contact Person", groups="base.group_user", size=100)
    emergency_phone = fields.Char("Emergency Phone", groups="base.group_user", size=15)
    emergency_phone_2 = fields.Char("Emergency Phone 2", groups="base.group_user", size=15)
    km_home_work = fields.Integer(string="Distance From Home To Work", groups="base.group_user")

    """# End: overriding the existing fields"""

    personal_email = fields.Char(string=u'Personal EMail Id ', size=100)
    whatsapp_no = fields.Char(string=u'WhatsApp No.', size=15)
    present_addr_street = fields.Text(string="Present Address Line 1", size=500)
    present_addr_street2 = fields.Text(string="Present Address Line 2", size=500)
    present_addr_country_id = fields.Many2one('res.country', string="Present Address Country")
    present_addr_city = fields.Char(string="Present Address City", size=100)
    present_addr_state_id = fields.Many2one('res.country.state', string="Present Address State")
    present_addr_zip = fields.Char(string="Present Address ZIP", size=10)

    same_address = fields.Boolean(string=u'Same as Present Address', default=False)

    permanent_addr_country_id = fields.Many2one('res.country', string="Permanent Address Country")
    permanent_addr_street = fields.Text(string="Permanent Address Line 1", size=500)
    permanent_addr_street2 = fields.Text(string="Permanent Address Line 2", size=500)
    permanent_addr_city = fields.Char(string="Permanent Address City", size=100)
    permanent_addr_state_id = fields.Many2one('res.country.state', string="Permanent Address State")
    permanent_addr_zip = fields.Char(string="Permanent Address ZIP", size=10)

    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")

    emp_refered_from = fields.Many2one('kwemp_reference_mode_master', string="Reference Mode")
    emp_refered = fields.Many2one('utm.source', string="Reference Mode", domain=[('source_type', '=', 'recruitment')])
    emp_reference_walkindrive = fields.Char("Walk-in Drive")
    emp_reference_print_media = fields.Char("Print Media")
    emp_reference_job_fair = fields.Char("Job Fair")
    emp_code_ref = fields.Char('Code', compute='compute_code')
    emp_employee_referred = fields.Many2one('hr.employee', string='Referred By')#15
    emp_media_id = fields.Many2one('kw.social.media', string='Social Media')
    emp_institute_id = fields.Many2one('res.partner', string='Institute')
    emp_consultancy_id = fields.Many2one('res.partner', string='Consultancy')
    emp_jportal_id = fields.Many2one('kw.job.portal', string='Job Portal')
    emp_service_partner_id = fields.Many2one('res.partner', string='Partner')
    emp_reference = fields.Char("Client Name")

    # Modified By: Chandrasekhar
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='Manpower Requisition')
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")
    type_of_project = fields.Selection([('work', 'Work Order'), ('opportunity', 'Opportunity')], string="Project Type")
    engagement = fields.Integer(string="Engagement Period(Months)")
    project_name = fields.Char(string='Project Name')

    emp_differently_abled = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Differently Abled?")
    emp_blind = fields.Boolean('Blind')
    emp_deaf = fields.Boolean('Deaf')
    emp_dumb = fields.Boolean('Dumb')
    emp_orthopedically = fields.Boolean('Orthopedically Handicapped')
    emp_of_disability = fields.Integer(string="% of Disability")

    emp_odisha_domicile = fields.Selection([('yes','Yes'),('no','No')],string="Odisha Domicile")

    # ----------------------------------------------------

    @api.depends('emp_refered')
    def compute_code(self):
        for rec in self:
            rec.emp_code_ref = rec.emp_refered.code if rec.emp_refered else None
    
    @api.onchange('emp_refered')
    def onchange_emp_refered(self):
        for rec in self:
            rec.emp_reference_walkindrive = False
            rec.emp_reference_print_media = False
            rec.emp_reference_job_fair = False
            # rec.emp_code_ref = False
            rec.emp_employee_referred = False
            rec.emp_media_id = False
            rec.emp_institute_id = False
            rec.emp_consultancy_id = False
            rec.emp_jportal_id = False
            rec.emp_service_partner_id = False
            rec.emp_reference = False

    emp_refered_detail = fields.Text(string="Reference Details")

    wedding_anniversary = fields.Date(string=u'Wedding Anniversary', )
    known_language_ids = fields.One2many('kwemp_language_known', 'emp_id', string='Language Known')
    # """# END : Personal Info"""

    # """# START : Work Experience details###"""
    experience_sts = fields.Selection(string="Work Experience Details ",
                                      selection=[('1', 'Fresher'), ('2', 'Experience')], default="2")
    worked_country_ids = fields.Many2many('res.country', string='Countries Of Work Experience',
                                          groups="hr.group_hr_user")
    work_experience_ids = fields.One2many('kwemp_work_experience', 'emp_id', string='Work Experience Details')
    technical_skill_ids = fields.One2many('kwemp_technical_skills', 'emp_id', string='Technical Skills')
    # """# END : Work Experience details###"""

    # """# START : Educational Details##"""
    educational_details_ids = fields.One2many('kwemp_educational_qualification', 'emp_id', string="Educational Details")
    filter_stream = fields.Char(string="Stream", store=True, compute='_get_stream')
    # """# END : Educational Details##"""

    # """# START :for identification details ###"""
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    identification_ids = fields.One2many('kwemp_identity_docs', 'emp_id', string='Identification Documents')
    membership_assc_ids = fields.One2many('kwemp_membership_assc', 'emp_id', string='Membership Association Details')
    # """# END : for identification details ###"""

    # """# START : Family info Details##"""
    family_details_ids = fields.One2many('kwemp_family_info', 'emp_id', string="Family Info Details")
    # """# END : Family info Details##"""

    # is always computed.   , default=lambda self: self.env.user.id
    current_user = fields.Boolean("Current User", compute='_get_current_user', default=False)

    # """# START : Handbook info Details##"""
    handbook_info_details_ids = fields.One2many('kw_handbook','employee_id', string = 'Policy Tracking Details')
    show_handbook = fields.Boolean('Show Handbook', compute='check_show_handbook')
    # """# END : Handbook info Details##"""

    total_experience_display = fields.Char('Total Experience', readonly=True, compute='_compute_experience_display',
                                           store=False,
                                           help="Field allowing to see the total experience in years and months depending upon joining date and experience details")
    filter_experience_year = fields.Integer(string="Experience", store=True, compute='_compute_experience_display')
    # filter_experience_month = fields.Integer(string="Experience Month", store=True, compute='_compute_experience_display')
    color = fields.Char(compute='get_status')
    emp_display_name = fields.Char('Name.', compute='_emp_display_name')
    # added on 20 april 2020
    mother_tongue_id = fields.Many2one('kwemp_language_master', string="Mother Tongue")
    # help content for base location
    address_id = fields.Many2one('res.partner', 'Work Location', help="Employee's base location.")
    department_id = fields.Many2one('hr.department', string="Department", domain="[('dept_type.code', '=', 'department')]")
    division = fields.Many2one('hr.department', string="Division", domain="[('dept_type.code', '=', 'division')]")
    section = fields.Many2one('hr.department', string="Practice", domain="[('dept_type.code', '=', 'section')]")
    practise = fields.Many2one('hr.department', string="Section", domain="[('dept_type.code', '=', 'practice')]")
    # """# added on 14 july 2020 by Gouranga"""
    base_branch_id = fields.Many2one('kw_res_branch', 'Base Location')
    base_branch_name = fields.Char(string='Location')
    job_branch_id = fields.Many2one('kw_res_branch', 'Work Location')
    # """# added on 14 july 2020 by Gouranga"""
    bank = fields.Char(string="Bank Name", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")#2
    # functional_area_id = fields.Many2one('kw_industry_type', string="Functional Area")
    emp_project_id = fields.Many2one('crm.lead', string="Project Name/Code")
    proj_bill_amnt = fields.Integer(string="Project Billing Amount",
                                    groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    medical_reimb = fields.Integer(string="Medical Reimbursement")
    transport = fields.Integer(string="Transport")  # 26
    enable_payroll = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Enable Payroll", default='no')  # 19
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")  # 17
    enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity",
                                       groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 18
    current_ctc = fields.Float(string="Current CTC",
                               groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 14
    at_join_time_ctc = fields.Float(string=" CTC At Joining Time",
                                    groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 1
    basic_at_join_time = fields.Float(string="At Joining Time",
                                      groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 6
    current_basic = fields.Float(string="Current Basic",
                                 groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 13
    productivity = fields.Float(string="Productivity Allowance",
                                groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 25
    commitment = fields.Float(string="Commitment Allowance",
                              groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 10
    hra = fields.Integer(string="HRA(%)", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 22
    conveyance = fields.Integer(string="Conveyance(%)",
                                groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 11
    lta_amount = fields.Float(string="LTA", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 10
    pp_amount = fields.Float(string="Professional Pursuit",
                             groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 10
    image_url = fields.Char(string="Image URL")
    bank_account = fields.Char(string="Account No", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 3

    personal_bank_name = fields.Char(string="Bank Name", readonly=False)
    personal_bank_account = fields.Char(string="Account No", readonly=False)
    personal_bank_ifsc = fields.Char(string="IFSC Code")
    
    # bank_account_id=fields.Many2one('res.bank')
    partner_id = fields.Many2one('res.partner', related="user_id.partner_id")
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account Number',
                                      domain="[('partner_id','=',partner_id)]",
                                      help='Employee bank salary account',
                                      groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    bankaccount_id = fields.Many2one('res.bank', string="Bank",
                                     groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    location = fields.Selection(selection=[('onsite', 'Onsite'), ('offsite', 'Offsite'), ('wfa', 'WFA'),
                                           ('hybrid', 'Hybrid')],
                                string="Onsite/Offsite/WFA/Hybrid", default='offsite')
    wfa_city = fields.Many2one('res.city', string="City")
    # wfa_city = fields.Char(string="City")
    client_loc_id = fields.Many2one('res.partner')
    client_location = fields.Char(string='Client Location')
    current_user_id = fields.Boolean('Current User Id', compute='_get_current_user', default=False)
    on_probation = fields.Boolean(string="On Probation")
    need_sync = fields.Boolean(string="Create in Tendrils?")
    last_mail_date = fields.Date(string='Last Mail Date')
    rel_job_id = fields.Char(related='job_id.name')
    parent_id = fields.Many2one('hr.employee', 'Administrative Authority')
    coach_id = fields.Many2one('hr.employee', 'Functional Authority')
    # ra_rel_id = fields.Many2one('kwemp_change_ra')
    new_ra_id = fields.Many2one('hr.employee', string="New RA", reqired="True")
    dept_update = fields.Boolean(string='Dept Updated?', default=False)
    temp_dept_id = fields.Many2one('hr.department', string='Temp Dept.')
    last_working_day = fields.Date(string='Last Working Day')
    reason = fields.Many2one('kw_resignation_master', string='Reason')
    cv_info_details_ids = fields.One2many('kw_emp_cv_info', 'emp_id', string='CV Info')

    # dept_update = fields.Boolean(string='Dept Updated?', default=False)
    # temp_dept_id = fields.Many2one('hr.department', string='Temp Dept.')
    # """Travel Clause - Pratima"""
    will_travel = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Willing to travel?', default='0')
    travel_abroad = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Travel abroad?', default='0')
    travel_domestic = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Travel domestic?', default='0')
    linkedin_url = fields.Char(string='Linked In Profile URL')
    cosolid_amnt = fields.Float(string='Consolidate Amount',
                                groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 12
    # For payroll Esi calculation by Abhijit Swain
    esi_applicable = fields.Boolean(string='ESI APPLICABLE')  # 20
    acc_branch_unit_id = fields.Many2one('accounting.branch.unit', string='Branch Unit')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)])

    """ Bond and medical certificate """
    # bond_required = fields.Boolean(string="Bond Required", default=False)
    bond_required = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Bond Required", default='0')#8
    bond_years = fields.Selection([(i, str(i)) for i in range(0, 11)], string='Bond Year(s)')#9
    bond_months = fields.Selection([(i, str(i)) for i in range(0, 12)], string='Bond Month(s)')#7

    medical_certificate = fields.Binary(string="Medical Certificate")
    certificate_name = fields.Char(string=u'Medical Certificate Name')

    additional_department = fields.Many2many('hr.department', 'additional_department_rel', 'dept_id', 'rel_dept_id',
                                             string='Additional Department')
    additional_division = fields.Many2many('hr.department', 'additional_division_rel', 'div_id', 'rel_div_id',
                                           string='Additional Division')
    additional_section = fields.Many2many('hr.department', 'additional_section_rel', 'section_id', 'rel_section_id',
                                          string='Additional Section')
    additional_practice = fields.Many2many('hr.department', 'additional_practice_rel', 'practise_id', 'rel_practise_id',
                                           string='Additional Practice')

    onboarding_id = fields.Many2one('kwonboard_enrollment', string='Onboarding ID')
    ex_emp_id = fields.Many2one('hr.employee', string='Tag Ex-Employee', domain=[('active', '=', False)])

    uan_id = fields.Char(string="UAN", help="UAN ",
                         groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 27
    esi_id = fields.Char(string="ESI Number", help="ESI Number",
                         groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 21

    """ PF Deduction Options """
    pf_deduction = fields.Selection([('basicper', "12 % of basic"), ('avail1800', 'Flat 1,800/-')],
                                    string='PF Deduction',
                                    groups="hr.group_hr_manager,kw_employee.group_payroll_manager")  # 24
    level = fields.Many2one("kw_grade_level")
    training_completion_date = fields.Date(string='Training Completion Date')
    
    ### Insurance #############

    personal_insurance = fields.Selection([('Yes','Yes'),('No','No')],string="Health Insurance")
    uplod_insurance_doc = fields.Binary(string="Insurance Document", attachment=True)
    file_name_insurance = fields.Char(string="File Name")  
    insurance_validate_date = fields.Date(string="Health Insurance Validity Date")
      

    @api.onchange('grade')
    def onchange_emp_grade(self):
        level = self.env['kw_grade_level'].search([('grade_ids', 'in', [self.grade.id])])
        if level.exists():
            self.level = level.id
        else:
            self.level = False

    def check_show_handbook(self):
        for record in self:
            record.show_handbook = False
            if record.user_id.id == self.env.user.id:
                record.show_handbook = True

    @api.onchange('additional_department')
    def onchange_add_department(self):
        dept_child = self.mapped("additional_department.child_ids")
        self.additional_division &= dept_child
        return {'domain': {'additional_division': [('id', 'in', dept_child.ids)]}}

    @api.onchange('additional_division')
    def onchange_add_division(self):
        division_child = self.mapped("additional_division.child_ids")
        self.additional_section &= division_child
        return {'domain': {'additional_section': [('id', 'in', division_child.ids)]}}

    @api.onchange('additional_section')
    def onchange_add_section(self):
        section_child = self.mapped("additional_section.child_ids")
        self.additional_practice &= section_child
        return {'domain': {'additional_practice': [('id', 'in', section_child.ids)]}}

    @api.onchange('budget_type')
    def onchange_budget_type(self):
        if self.budget_type == 'project':
           employee_role_ids = self.env['kwmaster_role_name'].search([('code', '=', 'R')]).ids
        else:
           employee_role_ids = self.env['kwmaster_role_name'].search([('code', '!=', 'R')]).ids
        return {'domain': {'emp_role': [('id', 'in', employee_role_ids)]}}

    @api.onchange('bond_required')
    def onchange_bond(self):
        if self.bond_required == '0':
            self.bond_years = False
            self.bond_months = False

    @api.onchange('mrf_id')
    def onchange_mrf_id(self):
        for rec in self:
            if rec.mrf_id:
                rec.budget_type = rec.mrf_id.requisition_type if rec.mrf_id.requisition_type else False

    # ====== Officer group check field =====
    @api.multi
    def check_manager(self):
        if self.env.user.has_group('hr.group_hr_manager'):
            for rec in self:
                rec.check_manager_group = True
    
    check_manager_group = fields.Boolean(string="Check Manager", default=False, compute="check_manager")

    @api.multi
    def button_employee_document(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download_employee_doc/{self.id}',
            'target': 'new',
        }

    @api.multi
    def button_employee_profile_document(self):
        view_id = self.env.ref('kw_emp_profile.kw_employee_profile_form_view').id
        action_id = self.env.ref('kw_emp_profile.kw_emp_profile_action').id
        for rec in self:
            check_active_id = self.env['kw_emp_profile'].sudo().search([('user_id', '=', rec.user_id.id)])
            if check_active_id:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_emp_profile',
                    'res_id': check_active_id.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'current',
                }

    @api.constrains('current_ctc', 'at_join_time_ctc', 'basic_at_join_time', 'current_basic')
    def validate_salary_values(self):
        for rec in self:
            if rec.at_join_time_ctc > rec.current_ctc:
                raise ValidationError("Current CTC should not be less than Joining Time CTC.")
            # if rec.current_basic < rec.basic_at_join_time:
            #     raise ValidationError("Current Basic should not be less than Joining Time Basic.")

    @api.onchange('enable_payroll')
    def onchange_payroll(self):
        self.basic_at_join_time = False
        self.current_basic = False
        self.bank_account = False
        self.bank_id = False
        self.hra = False
        self.conveyance = False
        self.medical_reimb = False
        self.transport = False
        self.productivity = False
        self.commitment = False
        self.cosolid_amnt = False
        self.enable_gratuity = False
        self.enable_epf = False
        self.pf_deduction = False

    # def button_active(self):
    #      for record in self:
    #         wizard_form = self.env.ref('kw_employee.kw_emp_archieve_view_form')
    #         # print(self.env.context.get('archieve_id'))

    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'view_id': wizard_form.id,
    #             'res_model': 'kw_emp_archieve',
    #             # 'context' : {'employee_id':rec.id,'old_card':rec.id_card_no.id},# for showing the corresponding card  holder name and card number in wizard
    #             'target': 'new',

    #         }
    # @api.model
    # def button_confirm(self):
    #     self.write({'active': False})
    #     return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }
    # @api.depends('employement_type')
    # def _compute_hide(self):
    #     if self.employement_type.code == 'O':
    #         self.hide = False
    #     else:
    #         self.hide = True

    # @api.multi
    # def button_profile_check(self):
    #     check_active_id = self.env['kw_emp_profile'].sudo().search([('user_id','=',self.env.uid)])
    #     if check_active_id:
    #         # form_view_id = self.env.ref("kw_emp_profile.kw_emp_profile_form_view").id
    #         return {
    #         'name': _('Profile Check'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'kw_emp_profile',
    #         # 'view_id': form_view_id,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('emp_id', 'in', [self.id])],
    #         }

    @api.multi
    def contract_reminder_mail(self):
        contract_emp_rec = self.env['hr.employee'].sudo().search(
            [('employement_type.code', 'in', ['C', 'S']), ('end_date', '!=', False)])
        emp_list = []
        if contract_emp_rec:
            for record in contract_emp_rec:
                day_diff = record.end_date-date.today()
                if 0 <= day_diff.days <= 30:
                    emp_list.append(f"{record.emp_code if record.emp_code else '--'}:{record.name if record.name else '--'}:{record.job_id.name if record.job_id else '--'}:{record.department_id.name if record.department_id else '--'}:{record.division.name if record.division else '--'}:{record.section.name if record.section else '--'}:{record.practise.name if record.practise else '--'}:{record.emp_project_id.name}:{datetime.strptime(str(record.start_date), '%Y-%m-%d').strftime('%d-%b-%Y')}:{datetime.strptime(str(record.end_date), '%Y-%m-%d').strftime('%d-%b-%Y')}:")

        if len(emp_list) > 0:
            email_list = []
            rcm = self.env.ref('kw_employee.group_rcm').mapped('users.employee_ids')
            email_list += rcm.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
            # account_manager = self.env.ref('kw_employee.group_account_manager').mapped('users.employee_ids')
            # email_list += account_manager.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
            hrd = self.env.ref('kw_employee.group_hr').mapped('users.employee_ids')
            email_list += hrd.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
            email_list = list(filter(None, email_list))
            email = set(email_list)
            email_to = email and ",".join(email) or ''
            extra_params = {'emp_list': emp_list, 'email_to': email_to}
            self.env['hr.employee'].employee_send_custom_mail(res_id=record.id,
                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                              template_layout='kw_employee.contract_email_template',
                                                              ctx_params=extra_params,
                                                              description="Contract Closure reminder")

            self.env.user.notify_info(message='Mail sent successfully.')

    def employee_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                                  notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
            # print(values)                    

            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)

            mail.model = False
            return mail.id

    # @api.onchange('on_probation')
    # def hide_probation_complete(self):
    #     if self.on_probation is False:
    #         self.date_of_completed_probation = False

    @api.multi
    def button_employee_history(self):
        return {
            'name': _('Employee History'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_emp_history',
            'type': 'ir.actions.act_window',
            'domain': [('emp_id', 'in', [self.id])],
        }

    """#  Employee Code configure according to office branch added by Asish Ku. Nayak """
    # @api.onchange('base_branch_id')
    # def branch_change(self):
    #     if self.emp_code:
    #         self.emp_code = self.emp_code.replace(self.emp_code.split("-")[0], self.base_branch_id.branch_code)
    """# END"""

    """ added on 1st July 2020 by Monalisha"""
    """ modified on 13-Jan-2021 by Girish - commented extra code"""
    @api.onchange('image')
    def get_url(self, update=True):
        emp_id = self._origin.id if '_origin' in self else self.id
        attachment_data = self.env['ir.attachment'].search(
            [('res_id', '=', emp_id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
        attachment_data.write({'public': True})
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if attachment_data.id:
            final_url = '%s/web/image/%s' % (base_url, attachment_data.id)
            if update is False:
                return final_url
            else:
                self.image_url = final_url

    @api.constrains('attendance_mode_ids')
    def check_attendance_mode(self):
        attTypDic = {'portal': '0', 'bio_metric': '1', 'manual': '3'}
        for rec in self:
            attendance_rec = rec.attendance_mode_ids.mapped('alias')
            bothLis = ['portal', 'bio_metric']
            if len(attendance_rec) == 2:
                if all(item in attendance_rec for item in bothLis):
                    pass
                else:
                    raise ValidationError('You can only select 2 modes i.e Portal and Biometric')
            if len(attendance_rec) > 2:
                raise ValidationError('You can not select 3 modes')

    # def toggle_work(self):
    #     if self.is_wfh == True:
    #         self.write({'is_wfh': False})
    #     else:
    #         self.write({'is_wfh': True})

    @api.multi
    def view_onboarding_checklist(self):
        onboarding_checklist_view_id = self.env.ref('kw_employee.kw_employee_onboarding_checklist_view_form').id
        _action = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_employee_onboarding_checklist',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': onboarding_checklist_view_id,
                'target': 'self',
            }
        if self.onboarding_checklist:
            _action['res_id'] = self.onboarding_checklist.id
        return _action

    @api.onchange('department_id')
    def onchange_department(self):
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.department_id.id), ('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.department_id:
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.section:
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}

    @api.model
    def get_status(self):
        try:
            url = http.request.env['ir.config_parameter'].sudo().get_param('kwantify_common_api')
            if url:
                user_presence = url + '/GetEmployeePresence'
            else:
                user_presence = "https://kwportalservice.csmpl.com/OdooSynSVC.svc/GetEmployeePresence"
            # response_obj = requests.post(user_presence)
            # status_content = response_obj.content
            # resp = json.loads(status_content.decode("utf-8"))
            status_colors = ''
            resp = []
            for record in resp:
                for emp_data in self:
                    if emp_data.kw_id == int(record["UserId"]):
                        colors = int(record["UserStatus"])
                        if colors == 1:
                            status_colors = "green"
                        elif colors == 2:
                            status_colors = "yellow"
                        elif colors == 3:
                            status_colors = "info"
                        elif colors == 4:
                            status_colors = "red"
                        elif colors == 5:
                            status_colors = "gray"
                        else:
                            status_colors = "NA"
                        emp_data.color = status_colors
            # print("Response success from Service")
        except:
            for record in self:
                record.color = 'NA'
            # print("Response failed from Service")
            # get current user

    @api.multi
    def action_employee_permissions(self):
        if not self.user_id:
            raise ValidationError("Employee must tagged to a user to set permissions.")

        user_form_view_id = self.env.ref("base.view_users_form").id
        return {
            'name': 'Permissions',
            'model': 'ir.actions.act_window',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'res_id': self.user_id.id,
            'view_type': 'form',
            'views': [(user_form_view_id, 'form')],
            'view_id': user_form_view_id,
            # 'flags': {'action_buttons': True, 'mode': 'edit'},
        }

    @api.depends('educational_details_ids')
    def _get_stream(self):
        for rec in self:
            name = ""
            for stream in rec.educational_details_ids:
                name += stream.stream_id.name + " "
            rec.filter_stream = name

    @api.depends('date_of_joining', 'work_experience_ids')
    def _compute_experience_display(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.date_of_joining:
                difference = relativedelta.relativedelta(datetime.today(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months
                if difference.days >= 30:
                    total_months += difference.days // 30

            if rec.work_experience_ids:
                for exp_data in rec.work_experience_ids:
                    exp_difference = relativedelta.relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months
                    if exp_difference.days >= 30:
                        total_months += exp_difference.days // 30
                    # print ("Difference is %s year, %s months " %(total_years,total_months))
            # print ("Difference is %s year, %s months " %(total_years,total_months))

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:     
                rec.filter_experience_year = total_years
                rec.filter_experience_month = total_months
                rec.total_experience_display = " %s Years and %s Months " % (total_years, total_months)
            else:
                rec.total_experience_display = ''

    """# on change of marital status compute marital status code"""
    @api.onchange('marital_sts')
    def _compute_marital_status_code(self):
        if self.marital_sts:
            self.marital_code = self.marital_sts.code
        else:
            self.marital_code = ''

    """# get current user"""
    @api.depends('user_id')
    def _get_current_user(self):
        for rec in self:
            if self.env.user.id == rec.user_id.id:
                rec.current_user = True
                rec.current_user_id = True
            elif self.env.user.has_group('hr.group_hr_manager'):
                rec.current_user = True

    @api.onchange('emp_role')
    def _get_categories(self):
        role_id = self.emp_role.id
        self.emp_category = False
        return {'domain': {'emp_category': [('role_ids', '=', role_id)], }}

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            emp_code = f'({record.emp_code})' if record.emp_code else ''
            result.append((record.id, f'{record.name} {emp_code}'))
        return result

    @api.model
    def _emp_display_name(self):
        for record in self:
            emp_code = f'({record.emp_code})' if record.emp_code else ''
            record.emp_display_name = f'{record.name} {emp_code}'

    """# on change of same address check-box , assign present address to permanent address"""
    @api.onchange('same_address')
    def _change_permanent_address(self):
        if self.same_address:
            self.permanent_addr_country_id = self.present_addr_country_id
            self.permanent_addr_street = self.present_addr_street
            self.permanent_addr_street2 = self.present_addr_street2
            self.permanent_addr_city = self.present_addr_city
            self.permanent_addr_state_id = self.present_addr_state_id
            self.permanent_addr_zip = self.present_addr_zip

    """# onchange of present address country change the state"""
    @api.onchange('present_addr_country_id')
    def _change_present_address_state(self):
        country_id = self.present_addr_country_id.id
        self.present_addr_state_id = False
        return {'domain': {'present_addr_state_id': [('country_id', '=', country_id)], }}

    """# onchange of permanent address country change the state"""
    @api.onchange('permanent_addr_country_id')
    def _change_permanent_address_state(self):
        country_id = self.permanent_addr_country_id.id
        if self.same_address and self.present_addr_state_id and (
                self.permanent_addr_country_id == self.present_addr_country_id):
            self.permanent_addr_state_id = self.present_addr_state_id
        else:
            self.permanent_addr_state_id = False
        return {'domain': {'permanent_addr_state_id': [('country_id', '=', country_id)], }}

    @api.onchange('emp_refered_from')
    def get_refered_detail(self):
        if not self.emp_refered_from:
            self.emp_refered_detail = False

    def send_wishes(self):
        # print("send wishes")
        # print(self)
        pass

    def create_emp_user(self):
        for rec in self:
            # print(rec.mobile_phone)
            if rec.name and rec.work_email and rec.company_id:
                try:
                    # print(self._context)
                    user_rec = self.env["res.users"].sudo().create(
                        {"name": rec.name,
                         "email": rec.work_email,
                         "login": rec.work_email,
                         "active": True,
                         "company_ids": [[6, False, [rec.company_id.id]]],
                         "company_id": rec.company_id.id,
                         "sel_groups_1_9_10": DEFAULT_INTERNAL_GRP,
                         "lang": self._context.get('lang'),
                         "tz": self._context.get('tz')})
                    if user_rec:
                        rec.write({'user_id': user_rec.id})
                        # print(user_rec.a)
                        mail_status = self.env["res.users"].action_reset_password()

                        # if rec.mobile_phone:
                        #     template = self.env['send_sms'].sudo().search([('name', '=', 'User_SMS')])
                        #     record_id = rec.id
                        #     self.env['send_sms'].send_sms(template, record_id)

                except ValidationError:
                    raise ValidationError(_('User is already created using the same login'))
            else:
                raise ValidationError(_('Please enter name, email address and company'))

    @api.multi
    def write(self, vals):
        experience = vals.get('experience_sts', False)
        if experience == "1":
            if 'work_experience_ids' in vals:
                vals.pop('work_experience_ids')
        gen_emp_code = ''

        """# for reporting authority/manager add to hr RA group"""
        group_hr = self.env.ref('kw_employee.group_hr_ra', False)
        
        user = self.env['res.users']
        for rec in self:
            if 'employement_type' in vals and vals['employement_type']:
                employment_type_code = self.env['kwemp_employment_type'].sudo().browse(vals['employement_type']).code
            elif rec.employement_type:
                employment_type_code = rec.employement_type.code
            else:
                employment_type_code = None

            if 'base_branch_id' in vals:
                work_location_id = vals['base_branch_id']
            else:
                work_location_id = rec.base_branch_id.id

            if not rec.emp_code and work_location_id:
                gen_emp_code = self._generate_employee_code(work_location_id, employment_type_code=employment_type_code)
                vals['emp_code'] = gen_emp_code

            old_parent_ids = []
            if 'parent_id' in vals:
                old_parent_ids = self.mapped('parent_id')        
                    
            # old_parent_id = self.parent_id
            card_no = rec.id_card_no.id

            super(hr_employee_in, self).write(vals)

            """# for reporting authority/manager add to hr RA group"""
            for old_parent in old_parent_ids:
                if old_parent.user_id and len(old_parent.child_ids) == 0:
                    group_hr.sudo().write({'users': [(3, old_parent.user_id.id)]})
            """#  Work Location Update in User """
            if 'base_branch_id' in vals or 'job_branch_id' in vals:
                user_rec = user.sudo().search([('id', '=', rec.user_id.id)])
                if user_rec:
                    branches = rec.base_branch_id | rec.job_branch_id
                    user_rec.write({
                        'branch_id': rec.base_branch_id and rec.base_branch_id.id or False,
                        'branch_ids': [(6, 0, branches.ids)]
                    })
            """#  Work Location Update in User End"""

            """#  Employee History Creation"""
            # 'emp_code' in vals or 'name' in vals or
            if (('department_id' in vals and rec.department_id.id != vals['department_id'])
                    or ('division' in vals and rec.division.id != vals['division'])
                    or ('section' in vals and rec.section.id != vals['section'])
                    or ('practise' in vals and rec.practise.id != vals['practise'])
                    or ('job_id' in vals and rec.job_id.id != vals['job_id'])
                    or ('grade' in vals and rec.grade.id != vals['grade'])
                    or ('emp_band' in vals and rec.emp_band.id != vals['emp_band'])
                    or ('job_branch_id' in vals and rec.job_branch_id.id != vals['job_branch_id'])
                    or ('base_branch_id' in vals and rec.base_branch_id.id != vals['base_branch_id'])):
                emp_history_rec = self.env['kw_emp_history'].sudo().search([('emp_id', '=', rec.id)])
                if emp_history_rec and emp_history_rec[-1]:
                    emp_history_rec[-1].write({'end_date': date.today().strftime('%d-%B-%Y')})
                emp_history_id = self.env['kw_emp_history'].sudo().create({
                    'emp_code': rec.emp_code,
                    'emp_id': rec.id,
                    'dept_id': rec.department_id.id,
                    'division': rec.division.id,
                    'section': rec.section.id,
                    'practice': rec.practise.id,
                    'deg_ig': rec.job_id.id,
                    'grade_id': rec.grade.id,
                    'band_id': rec.emp_band.id,
                    'job_location_id': rec.work_location_id.id,
                    'job_location_city': rec.work_location,
                    'work_location_id': rec.job_branch_id.id,
                    'office_type': rec.base_branch_id.id,
                    'start_date': date.today().strftime('%d-%B-%Y'),
                    'end_date': "Till Date"
                })
            
            if 'id_card_no' in vals:
                new_card_no = rec.id_card_no.id
                if card_no != new_card_no:
                    old_card = self.env['kw_card_master'].sudo().search([('id', '=', card_no)])
                    old_card.write({'state': 'unassigned', 'employee_id': False, 'enrollment_id': False})  # made the state of old id_card_no to unassigned

                    new_card = self.env['kw_card_master'].sudo().search([('id', '=', new_card_no)])
                    new_card.write({'state': 'assigned', 'employee_id': rec.id, 'enrollment_id': False})  # made the  state of new id_card_no to assigned

        for emp_rec in self:
            if emp_rec.parent_id and emp_rec.parent_id.user_id:
                group_hr.sudo().write({'users': [(4, emp_rec.parent_id.user_id.id)]})

            if 'work_email' in vals:
                data = self.env['res.users'].sudo().search([('id', '=', rec.user_id.id)]).write({'email': vals['work_email']})

        self.env.user.notify_info(message='Employee details updated successfully.')
        return True

    # @api.multi
    # def write(self, vals):
    #     """ Synchronize user and its related employee """
    #     result = super(User, self).write(vals)
    #     employee_values = {}
    #     for fname in [f for f in ['name', 'email', 'image', 'tz'] if f in vals]:
    #         employee_values[fname] = vals[fname]
    #     if employee_values:
    #         self.env['hr.employee'].sudo().search([('user_id', 'in', self.ids)]).write(employee_values)
    #     return result

    @api.model
    def create(self, vals):
        experience = vals.get('experience_sts', False)
        if experience == "1":
            if 'work_experience_ids' in vals:
                vals.pop('work_experience_ids')

        if 'employement_type' in vals:
            employment_type_code = self.env['kwemp_employment_type'].sudo().browse(vals['employement_type']).code
        else:
            employment_type_code = None

        gen_emp_code = ''
        if ('emp_code' not in vals or not vals['emp_code']) and 'base_branch_id' in vals:
            gen_emp_code = self._generate_employee_code(vals['base_branch_id'], employment_type_code=employment_type_code)
            vals['emp_code'] = gen_emp_code

        emp_rec = super(hr_employee_in, self).create(vals)

        # depts = self.env['hr.department'].sudo().search([('dept_type.code','=','department')])
        # dept_manager_email_list = list(set([dept.manager_id.work_email for dept in depts if dept.manager_id]))
        hrd_mail = self.env['ir.config_parameter'].sudo().get_param('hrd_mail') or False
        # if hrd_mail!=False:
        #     dept_manager_email_list.append(hrd_mail)

        # For Esi payroll by Abhijit Swain
        if emp_rec.enable_payroll == 'yes' and emp_rec.current_basic != False:
            basic = emp_rec.current_basic
            hra = emp_rec.current_basic * emp_rec.hra / 100
            conveyence = emp_rec.current_basic * emp_rec.conveyance / 100
            pb = emp_rec.productivity
            cb = emp_rec.commitment
            final_gross = basic + hra + conveyence + pb + cb
            if final_gross <= 21000:
                emp_rec.esi_applicable = True
            else:
                emp_rec.esi_applicable = False

        group_finance = self.env.ref('kw_onboarding.group_kw_onboarding_finance', False)
        group_new_joinee = self.env.ref('kw_onboarding.group_kw_new_joinee', False)
        group_new_offshore_joinee = self.env.ref('kw_onboarding.group_new_offshore_join_notification', False)
        group_new_joinee_emails = ''
        finance_user_emails = ''
        group_new_joinee_offshore_emails = ''

        if group_finance:
            finance_user_email_list = [user.email for user in group_finance.users if user.email]
            finance_user_emails = ','.join(finance_user_email_list) or ''

        if group_new_joinee:
            group_new_joinee_email_list = [user.email for user in group_new_joinee.users if user.email]
            group_new_joinee_emails = ','.join(group_new_joinee_email_list) or ''
        if group_new_offshore_joinee and len(group_new_offshore_joinee.users) > 0:
            group_new_joinee_offshore_email_list = [hrd_mail] + [user.email for user in group_new_offshore_joinee.users if user.email]
            group_new_joinee_offshore_emails = ','.join(group_new_joinee_offshore_email_list) or ''  

        # dept_manager_emails = ','.join(dept_manager_email_list) or ''
        
        # Inform RA through mail on employee creation
        inform_template = self.env.ref('kw_employee.employee_creation_email_template')
        uid = request.session.uid
        ses_emp = self.search([('user_id', '=', uid)])
        if emp_rec.parent_id:
            mail = inform_template.with_context(mail_for='RA',
                                                from_email=ses_emp.work_email,
                                                email_to=emp_rec.parent_id.work_email,
                                                email_cc='', reply_to='')\
                            .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            # mail.model = False    

        # Inform new joiner group through mail on employee creation
        # code comment by : Suchitra Date: 29/may/2023  Reason: this new join mail pass through scheduler next day of 9AM 
        # if len(group_new_joinee_emails) > 0 and emp_rec.department_id.code != 'OFFS'\
        #         and ((emp_rec.grade.send_consolidated_mail is False and emp_rec.grade.has_band is False)
        #              or (emp_rec.grade.send_consolidated_mail is False and emp_rec.grade.has_band is True and emp_rec.emp_band.send_consolidated_mail is False)
        #              or (emp_rec.grade.send_consolidated_mail is False and emp_rec.grade.has_band is True and emp_rec.emp_band.send_consolidated_mail is True)
        #              or (emp_rec.grade.send_consolidated_mail is True and emp_rec.grade.has_band is True and emp_rec.emp_band.send_consolidated_mail is False)):
        #     # emp_rec.grade.send_consolidated_mail is False and
        #     email_cc = emp_rec.work_email if emp_rec.work_email else ''
        #     reply_to = emp_rec.work_email if emp_rec.work_email else ''

        #     inform_template.with_context(mail_for='HR-DEPT', from_email=ses_emp.work_email, email_to=group_new_joinee_emails, email_cc=email_cc, reply_to=reply_to) \
        #         .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # if len(group_new_joinee_offshore_emails) > 0 and emp_rec.department_id.code == 'OFFS':
        #     email_cc = emp_rec.work_email if emp_rec.work_email else ''
        #     reply_to = emp_rec.work_email if emp_rec.work_email else ''

        #     inform_template.with_context(mail_for='HR-DEPT', from_email=ses_emp.work_email, email_to=group_new_joinee_offshore_emails, email_cc=email_cc, reply_to=reply_to) \
        #         .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")     
        
        # else:
            # current_date = str(datetime.now().date()) 
            # if len(group_new_joinee_emails) > 0 and emp_rec.emp_category.code == 'Intern' and str(emp_rec.date_of_joining) == current_date:
            #     email_cc = emp_rec.work_email if emp_rec.work_email else ''
            #     reply_to = emp_rec.work_email if emp_rec.work_email else ''

            #     inform_template.with_context(mail_for='HR-DEPT', email_to=group_new_joinee_emails, email_cc=email_cc, reply_to=reply_to) \
            #         .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")       

        # Inform Finance group through mail on employee creation
        if len(finance_user_emails) > 0:
            inform_template.with_context(mail_for='Finance', from_email=ses_emp.work_email,
                                         email_to=finance_user_emails,
                                         email_cc='', reply_to='')\
                            .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        # Inform Employee through mail on employee creation
        if emp_rec.work_email:
            inform_template.with_context(mail_for='Employee', from_email=ses_emp.work_email,
                                         email_to=emp_rec.work_email,
                                         email_cc='', reply_to='')\
                                .send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        emp_history_id = self.env['kw_emp_history'].sudo().create({
            'emp_code': emp_rec.emp_code,
            'emp_id': emp_rec.id,
            'dept_id': emp_rec.department_id.id,
            'division': emp_rec.division.id,
            'section': emp_rec.section.id,
            'practice': emp_rec.practise.id,
            'deg_ig': emp_rec.job_id.id,
            'grade_id': emp_rec.grade.id,
            'band_id': emp_rec.emp_band.id,
            # 'job_location_id' : emp_rec.job_branch_id.id,
            'work_location_id': emp_rec.job_branch_id.id,
            'office_type': emp_rec.base_branch_id.id,
            'start_date': date.today().strftime('%d-%B-%Y'),
            'end_date': "Till Date"
        })

        """# Call Announcement template and make an announcement"""
        if emp_rec:
            try:
                if emp_rec.active:
                    template = self.env.ref('kw_announcement.kwannouncement_new_joinee_hr_template')
                    if template:
                        self.env['kw_announcement_template'].sudo().make_announcement(template, emp_rec.id)

                # add the user to  RA group
                if emp_rec.parent_id and emp_rec.parent_id.user_id:
                    group_hr = self.env.ref('kw_employee.group_hr_ra', False)
                    group_hr.write({'users': [(4, emp_rec.parent_id.user_id.id)]})

                self.env.user.notify_success(message="Employee created successfully.")
            except Exception as e:
                # print(e)
                pass
        return emp_rec

    @api.constrains('date_of_joining', 'birthday')
    def validate_data(self):
        current_date = str(datetime.now().date())
        for record in self:
            # if record.date_of_joining:
            #     if str(record.date_of_joining) > current_date:
            #         raise ValidationError("The date of joining should not be greater than current date.")
            if record.birthday:
                if str(record.birthday) >= current_date:
                    raise ValidationError("The date of birth should be less than current date.")

    @api.constrains('wedding_anniversary', 'birthday')
    def validate_Birthdate_data(self):
        current_date = str(datetime.now().date())
        today = date.today()
        for record in self:
            if record.birthday:
                if today.year - record.birthday.year - ((today.month, today.day) < (record.birthday.month, record.birthday.day)) < 18:
                    raise ValidationError("You must be 18 years old.")
                if record.wedding_anniversary:
                    if str(record.wedding_anniversary) <= str(record.birthday):
                        raise ValidationError("Wedding Anniversary date should not be less than birth date.")
            if record.birthday:
                if str(record.birthday) >= current_date:
                    raise ValidationError("The date of birth should be less than current date.")

    @api.constrains('visa_expire')
    def validate_visaexpire_data(self):
        for record in self:
            if record.birthday and record.visa_expire:
                if str(record.visa_expire) <= str(record.birthday):
                    raise ValidationError("Visa Expire date should not be less than birth date.")

    @api.constrains('work_email')
    def check_work_email(self):
        for record in self:
            kw_validations.validate_email(record.work_email)
            # if record.work_email:
            #     records = self.env['hr.employee'].search(
            #         [('work_email', '=', record.work_email), ('active', '=', True)]) - self
            #     if records:
            #         raise ValidationError("This email id is already existing.")

    @api.constrains('work_experience_ids', 'birthday')
    def validate_experience(self):
        if self.work_experience_ids:
            if not self.birthday:
                raise ValidationError("Please enter your date of birthday.")
            for experience in self.work_experience_ids:
                if str(experience.effective_from) < str(self.birthday):
                    raise ValidationError("Work experience date should not be less than date of birth.")
                except_experience = self.work_experience_ids - experience
                overlap_experience = except_experience.filtered(lambda r: r.effective_from <= experience.effective_from <= r.effective_to or r.effective_from <= experience.effective_to <= r.effective_to)
                if overlap_experience:
                    raise ValidationError(f"Overlapping experiences are not allowed.")

    @api.constrains('cv_info_details_ids')
    def validate_cv_info_details_ids(self):
        if self.cv_info_details_ids:
            for experience in self.cv_info_details_ids:
                if str(experience.start_month_year) < str(self.birthday):
                    raise ValidationError("Start Month and Year of CV info should not be less than date of birth.")
                # except_cv_experience = self.cv_info_details_ids - experience
                # overlap_cv_experience = except_cv_experience.filtered(
                #     lambda r: r.start_month_year <= experience.start_month_year <= r.end_month_year or r.start_month_year <= experience.end_month_year <= r.end_month_year )
                # if overlap_cv_experience:
                #     raise ValidationError(f"Overlapping cv details are not allowed.")
            
    @api.constrains('membership_assc_ids')
    def validate_membership_assc(self):
        for emp_rec in self:
            if emp_rec.membership_assc_ids and emp_rec.birthday:
                for record in emp_rec.membership_assc_ids:
                    if str(record.date_of_issue) <= str(emp_rec.birthday):
                        raise ValidationError("Membership issue date should not be less than date of birth.")

    @api.constrains('educational_details_ids')
    def validate_edu_data(self):
        if self.educational_details_ids:
            for record in self.educational_details_ids:
                if self.birthday:
                    if str(record.passing_year) < str(self.birthday):
                        raise ValidationError("Passing year should not be less than date of birth.")

        # if self.educational_details_ids and not self.birthday:
        #     raise ValidationError("Please enter your date of birth.")

    @api.constrains('identification_ids')
    def validate_issue_date(self):
        if self.identification_ids and self.birthday:
            for record in self.identification_ids:
                if str(record.date_of_issue) < str(self.birthday):
                    raise ValidationError("Date of issue should not be less than date of birth.")
        # if self.identification_ids and not self.birthday:
        #     raise ValidationError("Please enter your date of birth.")

    # @api.constrains('mobile_phone')
    # def check_mobile(self):
    #     for record in self:
    #         if record.mobile_phone:
    #             if not len(record.mobile_phone) == 10:
    #                 raise ValidationError("Your mobile number is invalid for: %s" % record.mobile_phone)
    #             elif not re.match("^[0-9]*$", str(record.mobile_phone)) != None:
    #                 raise ValidationError("Your mobile number is invalid for: %s" % record.mobile_phone)
        # records = self.env['hr.employee'].search([]) - self
        # for sssinfo in records:
        #     if record.mobile_phone:
        #         if info.mobile_phone == self.mobile_phone:
        #             raise ValidationError("This Mobile Number is already exist..")

    @api.constrains('work_phone')
    def check_phone(self):
        for record in self:
            if record.work_phone:
                if not len(record.work_phone) <= 18:
                    raise ValidationError("Your work phone no is invalid for: %s" % record.work_phone)
                elif re.match("^(\+?[\d ])+$",str(record.work_phone)) == None: #modified to allow + and space 24 april
                    raise ValidationError("Your work phone no is invalid for: %s" % record.work_phone)

    @api.constrains('date_of_joining', 'date_of_completed_probation')
    def validate_probation(self):
        for record in self:
            if record.date_of_joining:
                if str(record.date_of_completed_probation) < str(record.date_of_joining):
                    raise ValidationError("The Probation completion date should not be less than Joining date")
                # elif not record.date_of_completed_probation:
                #     raise ValidationError("Please enter Probation completion date.")

    @api.constrains('emergency_phone')
    def check_emergency_phone(self):
        for record in self:
            if record.emergency_phone:
                if not len(record.emergency_phone) <= 10:
                    raise ValidationError("Your emergency phone no is invalid for: %s" % record.emergency_phone)
                elif not re.match("^[0-9]*$", str(record.emergency_phone)) != None:
                    raise ValidationError("Your Emergency phone no is invalid for: %s" % record.emergency_phone)

    @api.constrains('personal_email')
    def check_personal_email(self):
        for record in self:
            kw_validations.validate_email(record.personal_email)

    @api.constrains('present_addr_zip')
    def check_present_pincode(self):
        for record in self:
            if record.present_addr_zip:
                if not re.match("^[0-9]*$", str(record.present_addr_zip)) != None:
                    raise ValidationError("Present pincode is not Valid")

    @api.constrains('permanent_addr_zip')
    def check_permanent_pincode(self):
        for record in self:
            if record.permanent_addr_zip:
                if not re.match("^[0-9]*$", str(record.permanent_addr_zip)) != None:
                    raise ValidationError("Permanent pincode is not valid")

    @api.onchange('emp_role')
    def _get_categories(self):
        role_id = self.emp_role.id
        self.emp_category = False
        return {'domain': {'emp_category': [('role_ids', '=', role_id)], }}

    # method to create employee code
    def _generate_employee_code(self, location_id, employment_type_code=None):
        partner_record = self.env["kw_res_branch"].sudo().browse([location_id])
        office_prefix = ''
        if partner_record.branch_code:
            office_prefix = partner_record.branch_code

        if not employment_type_code or employment_type_code != 'O':
            emp_record_ids = self.search([('employement_type.code', '!=', 'O'),
                                          '|', ('active', '=', True), ('active', '=', False)],
                                         order='id desc', limit=1)
            last_id = int(emp_record_ids.emp_code[3:]) if emp_record_ids else 1
            # print(company_code+" "+str(last_id))
            emp_code = office_prefix + "-" + str(last_id + 1).zfill(4)
        else:
            last_tmp_code = self.env['hr.employee'].sudo().search([('employement_type.code', '=', 'O'),
                                                                   '|', ('active', '=', True), ('active', '=', False)],
                                                                  order='id desc', limit=1).emp_code
            last_id = int(last_tmp_code[5:]) if last_tmp_code else 0
            emp_code = office_prefix + "-TP" + str(last_id + 1).zfill(4)

        return emp_code

    @api.model
    def fields_get(self, fields=None):
        u_id = self.env['res.users'].sudo().search([('id','=',self.env.uid)])
        if u_id.has_group('hr.group_hr_manager'):
            fields_to_hide = ['message_needaction', 'activity_ids', 'dept_update',
                              'temp_dept_id', 'resignation_reason', 'reason', 'cv_info_details_ids',
                              'address_id', 'basic_at_join_time', 'at_join_time_ctc', 'bank_account', 'additional_note',
                              'kw_attendance_log_ids', 'barcode', 'bankaccount_id', 'commitment', 'create_uid',
                              'create_date', 'family_details_ids', 'message_follower_ids', 'message_channel_ids',
                              'message_partner_ids', 'enable_gratuity', 'hra', 'id', 'identification_id', 'image_url',
                              'message_is_follower', 'write_uid', 'write_date', 'message_main_attachment_id',
                              'image_medium', 'membership_assc_ids', 'message_has_error', 'message_ids',
                              'activity_date_deadline', 'activity_summary', 'activity_type_id', 'notes',
                              'onboarding_checklist', 'onboarding_create_check', 'outlook_pwd', 'emp_refered_from',
                              'emp_refered', 'emp_religion', 'resource_id', 'skill_id', 'activity_user_id',
                              'roaster_group_ids', 'same_address', 'shift_change_log_ids', 'image_small', 'child_ids',
                              'domain_login_pwd', 'category_ids', 'tz', 'transport', 'image',
                              'website_message_ids', 'resource_calendar_id', 'zoom_email', 'bank_account_id', 'bank',
                              'certificate', 'client_loc_id', 'client_location', 'conveyance', 'need_sync', 'birthday',
                              'work_location_id', 'work_location', 'enable_epf', 'pf_deduction',
                              'educational_details_ids', 'code',
                              'google_drive_link', 'enable_payroll', 'study_field', 'identification_ids', 'rel_job_id',
                              'known_language_ids', 'last_mail_date', 'base_branch_name', 'marital_code',
                              'medical_reimb', 'mother_tongue_id', 'passport_id', 'permanent_addr_street',
                              'permanent_addr_street2', 'permanent_addr_state_id', 'permanent_addr_zip',
                              'personal_email', 'personal_bank_name', 'personal_bank_account', 'personal_bank_ifsc',
                              'present_addr_street', 'present_addr_street2', 'present_addr_state_id',
                              'present_addr_zip', 'productivity', 'emp_project_id', 'proj_bill_amnt', 'project_id',
                              'emp_refered_detail', 'emp_refered_from', 'emp_refered', 'current_basic', 'current_ctc',
                              'km_home_work', 'end_date', 'job_id', 'children', 'address_home_id', 'sinid', 'ssnid',
                              'study_school', 'spouse_birthdate', 'spouse_complete_name', 'start_date',
                              'domain_login_id', 'technical_skill_ids', 'visa_expire', 'visa_no', 'work_experience_ids',
                              'experience_sts', 'emergency_contact', 'new_ra_id',  'parent_id',
                              'attendance_ids', 'attendance_mode_ids', 'dms_user_doc_dir_access_group',
                              'dms_user_doc_dir_id', 'kw_attendance_ids', 'effective_from', 'infra_id',
                              'issue_doc_dir_access_group', 'issue_doc_dir_id', 'last_attendance_id',
                              'newly_hired_employee', 'no_attendance',  'upload_doc_dir_access_group',
                              'upload_doc_dir_id', 'emp_grade', 'total_experience_display', 'kw_id', 'marital_sts',
                              'onboarding_id', 'struct_id', 'vendor_id', 'manager', 'cosolid_amnt', 'contracts_count',
                              'payslip_boolean', 'num_payslip_count', 'payslip_count', 'uan_id', 'esi_id', 'slip_ids',
                              'esi_applicable', 'additional_department', 'additional_division', 'additional_section',
                              'additional_practice', 'allow_backdate', 'capture_status', 'emp_reference', 'vehicle',
                              'emp_consultancy_id', 'country_of_birth', 'currency_id', 'direct_indirect',
                              'effective_from', 'contract_ids', 'engagement', 'id', 'emp_reference_job_fair',
                              'emp_jportal_id', 'medical_certificate', 'certificate_name', 'medic_exam',
                              'emp_reference_print_media', 'timesheet_cost', 'timesheet_validated', 'enable_timesheet',
                              'permit_no', 'linkedin_url', 'is_consolidated', 'pin', 'timesheet_manager_id',
                              'check_manager_group']
            # 'ra_rel_id','ra_rel_id',
            res = super(hr_employee_in, self).fields_get()
            for field in fields_to_hide:
                if res.get(field):
                    res.get(field)['selectable'] = False

            fields_in_groupby = ['bank_account', 'barcode', 'temp_dept_id', 'dept_update', 'bankaccount_id', 'bank',
                                 'reason', 'base_branch_id', 'biometric_id', 'client_loc_id', 'client_location',
                                 'need_sync', 'create_uid', 'create_date', 'birthday', 'direct_indirect', 'division',
                                 'epbx_no', 'enable_epf', 'effective_from', 'emergency_contact', 'emergency_phone',
                                 'emp_code', 'enable_payroll', 'end_date', 'emp_grade',
                                 'enable_gratuity', 'id_card_no', 'identification_id', 'image_url',
                                 'last_attendance_id', 'write_uid', 'write_date', 'base_branch_name',
                                 'message_main_attachment_id', 'marital', 'marital_code', 'no_attendance',
                                 'on_probation', 'onboarding_checklist', 'onboarding_create_check', 'outlook_pwd',
                                 'pin', 'passport_id', 'permanent_addr_street', 'permanent_addr_street2',
                                 'permanent_addr_state_id', 'permanent_addr_zip', 'personal_email',
                                 'personal_bank_name', 'personal_bank_account', 'personal_bank_ifsc',
                                 'present_addr_street', 'present_addr_street2', 'present_addr_state_id',
                                 'present_addr_zip', 'date_of_completed_probation', 'emp_project_id',
                                 'emp_refered_from', 'emp_refered', 'resource_id', 'same_address', 'section',
                                 'start_date', 'domain_login_id', 'domain_login_pwd', 'issued_system',
                                 'system_location', 'user_id', 'visa_expire', 'visa_no', 'wedding_anniversary',
                                 'experience_sts', 'address_id', 'job_branch_id', 'work_location_id', 'permit_no',
                                 'resource_calendar_id', 'zoom_email', 'last_mail_date', 'Bank Account Number',
                                 'certificate', 'company_id', 'country_of_birth', 'google_drive_link', 'study_field',
                                 'mother_tongue_id', 'permanent_addr_city', 'permanent_addr_country_id',
                                 'place_of_birth', 'present_addr_city', 'present_addr_country_id', 'address_home_id',
                                 'sinid', 'ssnid', 'study_school', 'spouse_birthdate', 'spouse_complete_name',
                                 'mobile_phone', 'whatsapp_no', 'work_email', 'work_phone', 'bank_account_id',
                                 'dms_user_doc_dir_access_group', 'dms_user_doc_dir_id', 'infra_id',
                                 'issue_doc_dir_access_group', 'issue_doc_dir_id', 'new_ra_id',
                                 'upload_doc_dir_access_group', 'upload_doc_dir_id', 'workstation_id', 'commitment',
                                 'cosolid_amnt', 'contracts_count', 'conveyance', 'at_join_time_ctc', 'current_basic',
                                 'current_ctc', 'struct_id', 'payslip_boolean', 'num_payslip_count', 'payslip_count',
                                 'pf_deduction', 'productivity', 'basic_at_join_time', 'uan_id', 'esi_id', 'slip_ids',
                                 'esi_applicable', 'additional_department', 'additional_division', 'additional_section',
                                 'additional_practice', 'allow_backdate', 'capture_status', 'emp_reference', 'vehicle',
                                 'emp_consultancy_id', 'country_of_birth', 'currency_id', 'direct_indirect',
                                 'effective_from', 'contract_ids', 'engagement', 'id', 'emp_reference_job_fair',
                                 'emp_jportal_id', 'medical_certificate', 'certificate_name', 'medic_exam',
                                 'emp_reference_print_media', 'timesheet_cost', 'timesheet_validated',
                                 'enable_timesheet', 'permit_no', 'linkedin_url', 'is_consolidated', 'pin',
                                 'timesheet_manager_id', 'check_manager_group', 'manager']
            # 'ra_rel_id',
            for field in fields_in_groupby:
                if res.get(field):
                    res.get(field)['sortable'] = False
            return res
        else:
            fields_to_hide = ['at_join_time_ctc', 'will_travel', 'travel_abroad', 'travel_domestic', 'dept_update',
                              'temp_dept_id', 'in_noticeperiod', 'reason', 'resignation_reason',
                              'cv_info_details_ids', 'bank_account', 'message_needaction', 'active',
                              'activity_ids', 'basic_at_join_time', 'attendance_ids', 'kw_attendance_log_ids',
                              'attendance_mode_ids', 'barcode', 'emp_band', 'bankaccount_id', 'bank', 'base_branch_id',
                              'branch_id', 'biometric_id', 'client_loc_id', 'client_location', 'coach_id', 'code',
                              'commitment', 'company_id', 'confirmation_sts', 'conveyance', 'need_sync', 'create_uid',
                              'create_date', 'current_basic', 'current_ctc', 'kw_attendance_ids', 'birthday',
                              'department_id', 'direct_indirect', 'km_home_work', 'division', 'epbx_no', 'enable_epf',
                              'pf_deduction', 'educational_details_ids', 'effective_from', 'emergency_contact',
                              'emergency_phone', 'emp_code', 'enable_payroll', 'end_date',
                              'family_details_ids', 'message_follower_ids', 'message_channel_ids',
                              'message_partner_ids', 'gender', 'emp_grade', 'grade', 'enable_gratuity', 'hra', 'id',
                              'id_card_no', 'identification_id', 'image_url', 'identification_ids',
                              'message_is_follower', 'job_id', 'job_title', 'date_of_joining', 'kw_id',
                              'known_language_ids', 'last_attendance_id', 'write_uid', 'write_date', 'base_branch_name',
                              'work_location', 'message_main_attachment_id', 'parent_id', 'marital', 'marital_sts',
                              'marital_code', 'medical_reimb', 'image_medium', 'membership_assc_ids',
                              'message_has_error', 'message_ids', 'newly_hired_employee', 'activity_date_deadline',
                              'activity_summary', 'activity_type_id', 'no_attendance', 'notes', 'on_probation',
                              'onboarding_checklist', 'onboarding_create_check', 'location', 'outlook_pwd', 'pin',
                              'passport_id', 'permanent_addr_street', 'permanent_addr_street2',
                              'permanent_addr_state_id', 'permanent_addr_zip', 'personal_email', 'personal_bank_name',
                              'personal_bank_account', 'personal_bank_ifsc', 'practise',
                              'present_addr_street', 'present_addr_street2', 'present_addr_state_id',
                              'present_addr_zip', 'date_of_completed_probation', 'productivity', 'emp_project_id',
                              'proj_bill_amnt', 'project_id', 'emp_refered_detail', 'emp_refered_from', 'emp_refered',
                              'emp_religion', 'resource_id', 'skill_id', 'activity_user_id', 'roaster_group_ids',
                              'same_address', 'section', 'shift_change_log_ids', 'image_small', 'start_date',
                              'child_ids', 'domain_login_id', 'domain_login_pwd', 'issued_system', 'system_location',
                              'category_ids', 'tz', 'transport', 'image', 'user_id', 'visa_expire',
                              'visa_no', 'is_wfh', 'website_message_ids', 'wedding_anniversary', 'work_experience_ids',
                              'experience_sts', 'work_location', 'address_id', 'job_branch_id', 'work_location_id',
                              'permit_no', 'resource_calendar_id', 'zoom_email', 'rel_job_id', 'last_mail_date',
                              'mother_tongue_id', 'whatsapp_no', 'mobile_phone', 'permanent_addr_city',
                              'permanent_addr_country_id', 'present_addr_city', 'present_addr_country_id', 'new_ra_id',
                               'parent_id', 'attendance_ids', 'attendance_mode_ids',
                              'dms_user_doc_dir_access_group', 'dms_user_doc_dir_id', 'kw_attendance_ids',
                              'effective_from', 'infra_id', 'issue_doc_dir_access_group', 'issue_doc_dir_id',
                              'last_attendance_id', 'newly_hired_employee', 'no_attendance',
                              'upload_doc_dir_access_group', 'upload_doc_dir_id', 'study_school', 'spouse_birthdate',
                              'spouse_complete_name', 'google_drive_link', 'additional_note', 'study_field', 'children',
                              'certificate', 'sinid', 'ssnid', 'bank_account_id', 'cosolid_amnt', 'contracts_count',
                              'conveyance', 'at_join_time_ctc', 'current_basic', 'struct_id', 'payslip_boolean',
                              'num_payslip_count', 'payslip_count', 'pf_deduction', 'uan_id', 'esi_id', 'slip_ids',
                              'esi_applicable', 'additional_department', 'additional_division', 'additional_section',
                              'additional_practice', 'allow_backdate', 'capture_status', 'emp_reference', 'vehicle',
                              'emp_consultancy_id', 'country_of_birth', 'currency_id', 'direct_indirect',
                              'effective_from', 'contract_ids', 'engagement', 'id', 'emp_reference_job_fair',
                              'emp_jportal_id', 'medical_certificate', 'certificate_name', 'medic_exam',
                              'emp_reference_print_media', 'timesheet_validated', 'timesheet_cost', 'enable_timesheet',
                              'permit_no', 'linkedin_url', 'is_consolidated', 'pin', 'timesheet_manager_id',
                              'check_manager_group', 'manager']
            # 'ra_rel_id','ra_rel_id',
            res = super(hr_employee_in, self).fields_get()
            for field in fields_to_hide:
                if res.get(field):
                    res.get(field)['selectable'] = False

            fields_in_groupby = ['bank_account', 'active', 'dept_update', 'temp_dept_id', 'in_noticeperiod', 'reason',
                                 'resignation_reason', 'will_travel', 'travel_abroad', 'travel_domestic', 'barcode',
                                 'emp_band', 'bankaccount_id', 'bank', 'base_branch_id', 'biometric_id',
                                 'client_loc_id', 'client_location', 'confirmation_sts', 'need_sync', 'create_uid',
                                 'create_date', 'birthday', 'direct_indirect', 'division', 'epbx_no', 'enable_epf',
                                 'effective_from', 'emergency_contact', 'emergency_phone', 'emp_code',
                                 'enable_payroll', 'end_date', 'gender', 'emp_grade', 'grade', 'enable_gratuity',
                                 'id_card_no', 'identification_id', 'image_url', 'job_title', 'date_of_joining',
                                 'last_attendance_id', 'write_uid', 'write_date', 'base_branch_name',
                                 'message_main_attachment_id', 'marital', 'marital_sts', 'marital_code',
                                 'no_attendance', 'on_probation', 'onboarding_checklist', 'onboarding_create_check',
                                 'location', 'outlook_pwd', 'pin', 'passport_id', 'permanent_addr_street',
                                 'permanent_addr_street2', 'permanent_addr_state_id', 'permanent_addr_zip',
                                 'personal_email', 'personal_bank_name', 'personal_bank_account', 'personal_bank_ifsc',
                                 'practise', 'present_addr_street', 'present_addr_street2',
                                 'present_addr_state_id', 'present_addr_zip', 'date_of_completed_probation',
                                 'emp_project_id', 'emp_refered_from', 'emp_refered', 'emp_religion', 'resource_id',
                                 'same_address', 'section', 'start_date', 'domain_login_id', 'domain_login_pwd',
                                 'issued_system', 'system_location', 'user_id', 'visa_expire',
                                 'visa_no', 'is_wfh', 'wedding_anniversary', 'experience_sts', 'address_id',
                                 'job_branch_id', 'work_location_id', 'permit_no', 'resource_calendar_id', 'zoom_email',
                                 'mother_tongue_id', 'last_mail_date', 'present_addr_city', 'present_addr_country_id',
                                 'permanent_addr_city', 'permanent_addr_country_id', 'whatsapp_no', 'work_email',
                                 'mobile_phone', 'work_phone', 'dms_user_doc_dir_access_group', 'dms_user_doc_dir_id',
                                 'infra_id', 'issue_doc_dir_access_group', 'issue_doc_dir_id', 'new_ra_id',
                                 'upload_doc_dir_access_group', 'upload_doc_dir_id', 'workstation_id',
                                 'bank_account_id', 'certificate', 'company_id', 'google_drive_link', 'study_field',
                                 'sinid', 'ssnid', 'study_school', 'spouse_birthdate', 'spouse_complete_name',
                                 'commitment', 'cosolid_amnt', 'contracts_count', 'conveyance', 'at_join_time_ctc',
                                 'current_basic', 'current_ctc', 'struct_id', 'payslip_boolean', 'num_payslip_count',
                                 'payslip_count', 'pf_deduction', 'productivity', 'basic_at_join_time', 'uan_id',
                                 'esi_id', 'slip_ids', 'esi_applicable', 'additional_department', 'additional_division',
                                 'additional_section', 'additional_practice', 'allow_backdate', 'capture_status',
                                 'emp_reference', 'vehicle', 'emp_consultancy_id', 'country_of_birth', 'currency_id',
                                 'direct_indirect', 'effective_from', 'contract_ids', 'engagement', 'id',
                                 'emp_reference_job_fair', 'emp_jportal_id', 'medical_certificate', 'certificate_name',
                                 'medic_exam', 'emp_reference_print_media', 'timesheet_cost', 'timesheet_validated',
                                 'enable_timesheet', 'permit_no', 'linkedin_url', 'is_consolidated', 'pin',
                                 'timesheet_manager_id', 'check_manager_group', 'manager']
            # 'ra_rel_id',
            for field in fields_in_groupby:
                if res.get(field):
                    res.get(field)['sortable'] = False
            return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(hr_employee_in, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        # print(self.env.user.groups_id)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//group[@name='extra_info1']"):
            node.set('modifiers', '{"invisible": true}')
        for node in doc.xpath("//field[@name='extra_info2']"):
            node.set('modifiers', '{"invisible": true}')

        # condition for readonly fields, for other user groups
        if not self.env.user.multi_has_groups(['hr.group_hr_manager', 'hr.group_hr_user']):
            for node in doc.xpath("//field[@name='name']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='image']"):
                node.set('modifiers', '{"readonly": true}')

            for node in doc.xpath("//field[@name='address_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='work_location']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='work_email']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='mobile_phone']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='work_phone']"):
                node.set('modifiers', '{"readonly": true}')

            for node in doc.xpath("//field[@name='department_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='job_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='job_title']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='parent_id']"):
                node.set('modifiers', '{"readonly": true}')

            for node in doc.xpath("//field[@name='coach_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='resource_calendar_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='tz']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='notes']"):
                node.set('modifiers', '{"readonly": true}')

            for node in doc.xpath("//field[@name='gender']"):
                node.set('modifiers', '{"readonly": true}')

            for node in doc.xpath("//group[@name='extra_info1']"):
                node.set('modifiers', '{"invisible": true}')
            for node in doc.xpath("//field[@name='extra_info2']"):
                node.set('modifiers', '{"invisible": true}')

        res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        return {'domain': {'work_location_id': [('parent_id', '=', self.company_id.partner_id.id)], }}

    @api.constrains('image')
    def _check_employee_photo(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png']
        for record in self:
            kw_validations.validate_file_mimetype(record.image, allowed_file_list)
            kw_validations.validate_file_size(record.image, 1)

    @api.multi
    def unlink(self):
            raise ValidationError("Employee Record Can't be Deleted")
        #     record.active = False
        # return True

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        # if not self.env.user.has_group('hr.group_hr_manager') and not self.env.user.has_group('kw_employee.group_payroll_manager'):
        #     fields = self.hr_employee_user_fields()
        res = super().search_read(self.get_domain(domain), fields, offset, limit, order)
        return res

    def get_domain(self, domain):
        dept_code = False
        cust_domain = domain
        # print("cust_domain >>> ", cust_domain)
        dept_domain, dept_key = False, 0
        for i, j in enumerate(cust_domain):
            if j[0] == 'department_id' and type(j[2]) == int:
                dept_key = i
                dept_domain = j
        # print("dept_domain >>> ", dept_domain,dept_key)
        if dept_domain and dept_domain[0] == 'department_id' and type(dept_domain[2]) == int:
            dept_code = self.env['hr.department'].sudo().browse(dept_domain[2]).dept_type.code
            if dept_code:
                # print("dept_code >>> ", dept_code)
                if dept_code == 'practice':
                    temp_domain = ('practise', '=', dept_domain[2])
                elif dept_code == 'department':
                    temp_domain = ('department_id', '=', dept_domain[2])
                else:
                    temp_domain = (dept_code, '=', dept_domain[2])
                domain[dept_key] = temp_domain

        # print("domain >>> ", domain)
        return domain

    def schedule_dept(self):
        return True
        # emp_rec = self.env['hr.employee'].sudo().search([('dept_update','=',False)],limit=50)
        # for rec in emp_rec:
        #     if rec.department_id:
        #         if rec.department_id.dept_type.code == 'department':
        #             temp_dept_id=rec.department_id.id
        #             rec.write({'temp_dept_id': temp_dept_id if temp_dept_id else False, 'dept_update': True})
        #         else:
        #             if rec.department_id.dept_type.code == 'practice':
        #                 temp_dept_id = rec.department_id.id
        #                 practice = rec.department_id.id
        #                 section = rec.department_id.parent_id.id
        #                 division = rec.department_id.parent_id.parent_id.id
        #                 department = rec.department_id.parent_id.parent_id.parent_id.id
        #                 vals = {'temp_dept_id': temp_dept_id if temp_dept_id else False, 'practise': practice if practice else False, 'section': section if section else False,
        #                                 'division': division  if division else False, 'department_id': department if department else False, 'dept_update': True}
        #                 rec.write(vals)
        #             elif rec.department_id.dept_type.code == 'section':
        #                 temp_dept_id = rec.department_id.id
        #                 section = rec.department_id.id
        #                 division = rec.department_id.parent_id.id
        #                 department = rec.department_id.parent_id.parent_id.id
        #                 vals = {'temp_dept_id': temp_dept_id if temp_dept_id else False, 'section': section if section else False,
        #                                 'division': division  if division else False, 'department_id': department if department else False, 'dept_update': True}
        #                 rec.write(vals)
        #             else:
        #                 temp_dept_id = rec.department_id.id
        #                 division = rec.department_id.id
        #                 department = rec.department_id.parent_id.id
        #                 vals = {'temp_dept_id': temp_dept_id if temp_dept_id else False, 'division': division  if division else False, 'department_id': department if department else False, 'dept_update': True}
        #                 rec.write(vals)

    # For updating email id of users while updating email id of employee
    # def write(self, vals):
    #     for rec in self:
    #         if 'work_email' in vals:
    #             data = self.env['res.users'].sudo().search([('id', '=', rec.user_id.id)]).write({'email':vals['work_email']})
    #     return super(hr_employee_in, self).write(vals)
    
    # @api.multi
    # def read(self,fields=None, load='_classic_read'):
    #     if not self.env.user.has_group('hr.group_hr_manager') and not self.env.user.has_group('kw_employee.group_payroll_manager'):
    #         fields = self.hr_employee_user_fields()
    #     res = super().read(fields, load)
    #     return res

    def hr_employee_user_fields(self):
        fields = ['name', 'image', 'image_medium', 'image_small', 'parent_id', 'child_ids',
                  'coach_id', 'emp_code', 'work_email', 'work_phone', 'mobile_phone', 'whatsapp_no', 'epbx_no',
                  'resource_calendar_id', 'date_of_joining', 'company_id', 'base_branch_id', 'base_branch_name',
                  'job_branch_id', 'acc_branch_unit_id', 'department_id', 'division', 'section', 'practise',
                  'job_id', 'sbu_master_id', 'blood_group', 'employement_type', 'work_location_id', 'active',
                  'work_location', 'sbu_type', 'user_id', 'no_attendance', 'partner_id', 'kw_id', 'infra_id',
                  'emp_employee_referred']
        # print("fields >>>>>>>>>>>> ", fields)
        return fields
