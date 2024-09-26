# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
import re, random, string
import time
import datetime
from lxml import etree
import os, base64
from dateutil.relativedelta import relativedelta
from datetime import date,timedelta
from kw_utility_tools import kw_validations
from ast import literal_eval

cur_dtime = datetime.datetime.now()
cur_dt = datetime.date(year=cur_dtime.year, month=cur_dtime.month, day=cur_dtime.day)

# Model Name    : kwonboard_enrollment
# Description   :  For the enrollment of the new employees , a reference number is created and Email will be sent to the employee
# Created By    :
# Created On    : 13-Jun-2019


class kwonboard_enrollment(models.Model):
    _name = 'kwonboard_enrollment'
    _description = "Candidate Enrollment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "write_date desc"

    @api.model
    def _get_no_month(self):
        return [(str(x), str(x)) for x in range(1, 13)]
    
    @api.model
    def _get_default_branch(self):
        branch_id = self.env['accounting.branch.unit'].sudo().search([('code', '=', 'csmpl')])
        return branch_id

    otp_number = fields.Char()
    generate_time = fields.Datetime(string="Expire Datetime")
    dept_name = fields.Many2one('hr.department', string="Department", required=True,
                                domain=[('dept_type.code', '=', 'department')], help="")
    division = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
    section = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'section')])
    practise = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'practise')])

    job_id = fields.Many2one('hr.job', string="Designation", help="")
    name = fields.Char(string="Candidate Name", required=True, size=100, help="",
                       read=['base.group_user', 'kw_employee.group_hr_finance', 'kw_employee.group_hr_admin',
                             'kw_employee.group_hr_nsa'])
    firstname = fields.Char(string="Candidate first name", help="")
    middlename = fields.Char(string="Candidate middle name", help="")
    lastname = fields.Char(string="Candidate last name", help="")
    email = fields.Char(string="Personal Email Id", size=50, required=True, help="")
    mobile = fields.Char(string="Mobile No", size=15, required=True, help="")
    whatsapp_no = fields.Char(string="Whatsapp No", size=15)
    reference_no = fields.Char('Reference No.')
    emp_id = fields.Many2one('hr.employee')
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)
    location_id = fields.Many2one('kw_res_branch', string="Base Location")
    work_location_id = fields.Many2one('res.partner', string="Work Location", domain="[('parent_id', '=', company_id)]")
    work_location = fields.Char(string="Work Location", related='work_location_id.city', readonly=True)

    state = fields.Selection(
        [('1', 'Enrolled'), ('2', 'Profile Created'), ('3', 'Configuration Mapping'), ('4', 'Configuration Done'),
         ('5', 'Approved'), ('6', 'Rejected')], required=True, default='1', track_visibility='onchange')

    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU", help="SBU")
    sbu_type = fields.Selection(
        string='SBU Type',
        selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('others', 'Others')])

    uan_id = fields.Char(string="UAN", help="UAN ")
    esi_id = fields.Char(string="ESI Number", help="ESI Number")
    
    personal_bank_name = fields.Char(string="Bank Name",readonly=False)
    personal_bank_account = fields.Char(string="Account No", readonly=False)
    personal_bank_ifsc = fields.Char(string="IFSC Code")

    # Additional Fields Modified By: Chandrasekhar
    budget_type = fields.Selection(string='Budget', selection=[('treasury', 'Treasury'), ('project', 'Project')],
                                   help="Set recruitment process is employee budget.", readonly="1")
    # type_of_project_id = fields.Selection(string='Project Type', readonly=True, related="applicant_id.project_type")
    type_of_project_id = fields.Selection(string='Project Type',
                                          selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                          help="Set recruitment process is work order.", readony=True, )
    project_name_id = fields.Many2one('crm.lead', string='Project Name')
    fin_project_name_id = fields.Many2one('crm.lead', string='Project Name')
    # engagement = fields.Integer(string="Engagement Period(Months)", readonly=True, related="applicant_id.mrf_duration")
    engagement = fields.Integer(string="Engagement Period(Months)", readonly=True)
    fin_engagement = fields.Integer(string="Engagement Period(Months)")
    fin_type_of_project_id = fields.Selection(string='Project Type',
                                              selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')])
    fin_budget_type = fields.Selection(string='Budget', selection=[('treasury', 'Treasury'), ('project', 'Project')],
                                       help="Set recruitment process is employee budget.")

    # ______________________________________________

    # START : APPROVAL FIELDS#
    system_configuration = fields.Many2many('kwonboard_config_type', string="Environment Configuration")
    admin_setting_status = fields.Boolean("Admin Setting", default=False)
    nsa_setting_status = fields.Boolean("IT Setting", default=False)
    finance_setting_status = fields.Boolean("Finance Setting", default=False)
    rcm_setting_status = fields.Boolean("RCM Setting", default=True)
    
    create_full_profile = fields.Boolean("Create Full Profile", default=False)
    display_nsa_btn = fields.Boolean("IT Button Display", default=False, compute="_compute_config_setting")

    # user status field if the user belongs to the selected service group
    user_grp_id_card = fields.Boolean("ID Card Group User", default=False, compute="_compute_config_setting")
    user_grp_budget = fields.Boolean("Budget Group User", default=False, compute="_compute_config_setting")
    user_grp_outlook = fields.Boolean("Outlook Group User", default=False, compute="_compute_config_setting")
    user_grp_biometric = fields.Boolean("Biometric Group User", default=False, compute="_compute_config_setting")
    user_grp_domain_pwd = fields.Boolean("Domain Group User", default=False, compute="_compute_config_setting")
    user_grp_epbx = fields.Boolean("EPBX Group User", default=False, compute="_compute_config_setting")
    user_grp_sbu = fields.Boolean("Sbu/Divivsion/RA",default=False,compute="_compute_config_setting")
    other_user_status = fields.Boolean("NOT HR MANAGER Group User", default=False, compute="_compute_config_setting")

    emp_role = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category")
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")

    id_card_no = fields.Many2one('kw_card_master', string=u'ID Card No', domain=[('active', '=', True), ('state', '=', 'unassigned')])
    csm_email_id = fields.Char(string=u'Outlook ID', default=None)
    biometric_id = fields.Char(string=u'Biometric ID', )
    outlook_pwd = fields.Char(string=u'Outlook Password', default=None)
    epbx_no = fields.Char(string=u'EPBX', )
    domain_login_id = fields.Char(string=u'Domain ID ', )
    domain_login_pwd = fields.Char(string=u'Domain Password ', )
    # END: APPROVAL FIELDS#

    # # Personal Details ##
    birthday = fields.Date(string="Date of Birth", )
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    gender = fields.Selection(string="Gender",
                              selection=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], )
    country_id = fields.Many2one('res.country', string='Nationality')
    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    marital = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    marital_code = fields.Char(string=u'Marital Status Code ', related='marital.code')

    wedding_anniversary = fields.Date(string=u'Wedding Anniversary', )
    image = fields.Binary(string="Upload Photo", attachment=True,
                          help="Only .jpeg,.png,.jpg format are allowed. Maximum file size is 1 MB",
                          inverse="_inverse_field")
    image_name = fields.Char(string=u'Image Name', )

    present_addr_country_id = fields.Many2one('res.country', string="Present Address Country")
    present_addr_street = fields.Text(string="Present Address Line 1", size=500)
    present_addr_street2 = fields.Text(string="Present Address Line 2", size=500)
    present_addr_city = fields.Char(string="Present Address City", size=100)
    present_addr_state_id = fields.Many2one('res.country.state', string="Present Address State")
    present_addr_zip = fields.Char(string="Present Address ZIP", size=10)
    # Present address : End
    same_address = fields.Boolean(string=u'Same as Present Address', default=False)
    # Permanent address : start
    permanent_addr_country_id = fields.Many2one('res.country', string="Permanent Address Country")
    permanent_addr_street = fields.Text(string="Permanent Address Line 1", size=500)
    permanent_addr_street2 = fields.Text(string="Permanent Address Line 2", size=500)
    permanent_addr_city = fields.Char(string="Permanent Address City", size=100)
    permanent_addr_state_id = fields.Many2one('res.country.state', string="Permanent Address State")
    permanent_addr_zip = fields.Char(string="Permanent Address ZIP", size=10)

    mother_tounge_ids = fields.Many2one('kwemp_language_master', string='Mother Tongue')
    # Permanent address : End
    known_language_ids = fields.One2many('kwonboard_language_known', 'enrole_id', string='Language Known')
    # START : Educational Details##
    educational_ids = fields.One2many('kwonboard_edu_qualification', 'enrole_id', string="Educational Details")
    # END : Educational Details##

    # START : Work Experience details ###
    experience_sts = fields.Selection(string="Work Experience ", selection=[('1', 'Fresher'), ('2', 'Experience')], )
    work_experience_ids = fields.One2many('kwonboard_work_experience', 'enrole_id', string='Work Experience Details')
    # END : Work Experience details ###

    # START :for identification details ###
    identification_ids = fields.One2many('kwonboard_identity_docs', 'enrole_id', string='Identification Documents')
    applicant_id = fields.Many2one('hr.applicant', string="Job Applicant",
                                   domain=[('kw_enrollment_id', '=', False), ('stage_id.code', '=', 'OA')])
    # END : for identification details ###

    emgr_contact = fields.Char(string="Emergency Contact Person")
    emgr_phone = fields.Char(string="Emergency Phone")
    check_finance = fields.Boolean(string="Check Finance", compute="check_access_finance", default=False)
    check_rcm_onboard = fields.Boolean(string="Check RCM", compute="check_access_rcm_onboard", default=False)
    
    check_it = fields.Boolean(string="Check IT", compute="check_access_it", default=False)
    check_admin = fields.Boolean(string="Check Admin", compute="check_access_admin", default=False)
    check_manager = fields.Boolean(string="Check Manager", compute="check_access_manager", default=False)
    confirm_outl_pwd = fields.Char(string="Confirm Outlook Password")
    confirm_domain_pwd = fields.Char(string="Confirm Domain Password")
    emgr_rel = fields.Many2one('kwmaster_relationship_name', string="Relationship",
                               help="Relationship with Emergency Contact Person")
    project_id = fields.Many2one('crm.lead', string="Project")
    start_dt = fields.Date(string="Contract Start Date")
    end_dt = fields.Date(string="Contract End Date")
    employement_type_code = fields.Char(related='employement_type.code')
    direct_indirect = fields.Selection(string="Direct/Indirect", selection=[('1', 'Direct'), ('2', 'Indirect')])
    need_uid = fields.Selection(selection=[('1', 'Yes'), ('0', 'No')], string="Need UserID ?")

    tmp_emp_role = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role")
    tmp_emp_category = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category")
    tmp_employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")
    nsa_employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment", related='tmp_employement_type')
    tmp_employement_type_code = fields.Char(related='tmp_employement_type.code')

    tmp_project_id = fields.Many2one('crm.lead', string="Order Name/Code")
    tmp_start_dt = fields.Date(string="Contract Start Date")
    tmp_end_dt = fields.Date(string="Contract End Date")
    tmp_direct_indirect = fields.Selection(string="Direct/Indirect", selection=[('1', 'Direct'), ('2', 'Indirect')])
    # Travel Clause - Pratima
    will_travel = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Willing to travel?', default='0')
    travel_abroad = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Travel abroad?', default='0')
    travel_domestic = fields.Selection([('1', 'Yes'), ('0', 'No')], 'Travel domestic?', default='0')
    # MRF id Tagging - Girish
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='MRF',readonly=True)
    finance_mrf_id = fields.Many2one('kw_recruitment_requisition', string='MRF', related='mrf_id')
    check_officer = fields.Boolean('Check Officer', compute='check_access_officer')
    card_type = fields.Selection([('2', 'Access Card'),('1', 'ID Card')], 'Card Type', default='2')
    tmp_worklocation_id = fields.Many2one('kw_res_branch', string='Work Location')
    emp_worklocation = fields.Many2one('kw_res_branch', string='Work Location', compute='_compute_work_location')
    tmp_enable_attendance = fields.Selection([('yes','Yes'),('no','No')], string="Enable Attendance", default='no')
    tmp_grade = fields.Many2one('kwemp_grade_master', string="Grade")
    tmp_band = fields.Many2one('kwemp_band_master', string="Band")
    tmp_location = fields.Selection(selection=[('onsite', 'Onsite'), ('offsite', 'Offsite'), ('wfa', 'WFA'),
                                               ('hybrid', 'Hybrid')],
                                    string="Onsite/Offsite/WFA/Hybrid")
    wfa_city = fields.Many2one('res.city', string="City")
    tmp_client_loc_id = fields.Many2one('res.partner')
    tmp_client_location = fields.Char(string='Client Location')
    tmp_source_id = fields.Many2one('utm.source', string="Reference Mode", domain=[('source_type', '=', 'recruitment')])

    tmp_admin_auth = fields.Many2one('hr.employee', string="Administrative Authority")
    tmp_func_auth = fields.Many2one('hr.employee', string="Functional Authority")
    tmp_prob_compl_date = fields.Date(string="Probation Complete Date", default=cur_dt + relativedelta(months=6))
    tmp_join_date = fields.Date(string="Joining Date", default=cur_dt)
    finance_join_date = fields.Date(string="Joining Date",compute='_compute_join_date')
    it_join_date = fields.Date(string="Joining Date",compute='_compute_join_date')
    admin_join_date = fields.Date(string="Joining Date",compute='_compute_join_date')
    tmp_shift = fields.Many2one('resource.calendar', string="Shift", domain=[('employee_id', '=', False)])
    tmp_on_probation = fields.Boolean(string="Probation/Traineeship", default=False)
    tmp_username = fields.Char('User Name')

    tmp_employee_referred = fields.Many2one('hr.employee', string='Referred By')
    tmp_service_partner_id = fields.Many2one('res.partner', string='Partner')
    tmp_media_id = fields.Many2one('kw.social.media', string='Social Media')
    tmp_institute_id = fields.Many2one('res.partner', string='Institute')
    tmp_consultancy_id = fields.Many2one('res.partner', string='Consultancy')
    tmp_jportal_id = fields.Many2one('kw.job.portal', string='Job Portal')
    tmp_reference = fields.Char("Client Name")
    tmp_reference_walkindrive = fields.Char("Walk-in Drive")
    tmp_reference_print_media = fields.Char("Print Media")
    tmp_reference_job_fair = fields.Char("Job Fair")
    tmp_code_ref = fields.Char('Code', related='tmp_source_id.code')
    no_of_months = fields.Selection('_get_no_month', 'No of months')
    need_sync = fields.Boolean(string="Create in Tendrils?", default=True)
    need_user = fields.Boolean(string="Create User?", default=True)

    enable_payroll = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Enable Payroll", default='yes')
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")
    enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity")
    tmp_at_join_time = fields.Float(string="At Joining Time", )
    current = fields.Float(string="Current CTC")
    basic_at_join_time = fields.Float(string="At Joining Time")
    current_basic = fields.Float(string="Current Basic")
    hra = fields.Integer(string="HRA(%)")
    conveyance = fields.Integer(string="Conveyance(%)")
    medical_reimb = fields.Integer(string="Medical Reimbursement")
    transport = fields.Integer(string="Transport Allowance")
    productivity = fields.Float(string="Productivity Allowance")
    commitment = fields.Float(string="Commitment Allowance")
    cosolid_amnt = fields.Float(string="Consolidate Amount")
    lta_amount = fields.Float(string="LTA Amount")
    pp_amount = fields.Float(string="Professional Pursuit Amount")
    """ PF Deduction Options """
    pf_deduction = fields.Selection([('basicper', "12 % of basic"), ('avail1800', 'Flat 1,800/-')],
                                    string='PF Deduction')
    is_consolidated = fields.Boolean(string="Is Consolidated ?")

    bank_account = fields.Char(string="Account No")
    bank_id = fields.Many2one('res.bank', string="Bank")
    image_id = fields.Char(compute='_compute_image_id')
    image_url = fields.Char(string="Image URL", compute="_get_image_url")
    linkedin_url = fields.Char('Linked In Profile URL')
    tmp_contract_period = fields.Selection('_get_no_month')
    tmp_contract_year_month = fields.Selection([('year', 'Year'), ('month', 'Month')])
    contract_period = fields.Selection('_get_no_month')
    contract_year_month = fields.Selection([('year', 'Year'), ('month', 'Month')])
    profile_submit_date = fields.Date('Profile Submit Date')
    active = fields.Boolean('Active', default=True)
    branch_unit_id = fields.Many2one('accounting.branch.unit', string='Branch Unit',default=_get_default_branch)
    struct_id = fields.Many2one('hr.payroll.structure', string="Payroll Structure")
    tmp_has_band = fields.Boolean('Has Band')

    # bond_required = fields.Boolean(string="Bond Required", default=False)
    bond_required = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Bond Required", default='0')
    bond_years = fields.Selection([(i, str(i)) for i in range(0, 11)], string='Bond Year(s)')
    bond_months = fields.Selection([(i, str(i)) for i in range(0, 12)], string='Bond Month(s)')

    medical_certificate = fields.Binary(string="Medical Certificate",attachment=True,)
    certificate_name = fields.Char(string=u'Medical Certificate Name')
    medical_certifcate_attachment_id = fields.Char(compute='_compute_medical_certificate_id')

    applicant_father_name = fields.Char(string="Father's Name", size=100)
    applicant_father_dob = fields.Date(string="Father's DOB")
    applicant_mother_name = fields.Char(string="Mother's Name", size=100)
    applicant_mother_dob = fields.Date(string="Mother's DOB")

    # ### BGV configuration field add ######
    previous_emp_code = fields.Char(string="Previous Emp code")
    previous_date_of_relieving = fields.Date(string="Date of Relieving")
    reason_for_leaving = fields.Text(string="Reason for Leaving")

    previous_ra = fields.Char(string="Reporting Authority Name")
    previous_ra_mail = fields.Char(string="Reporting Authority Email")
    previous_ra_designation = fields.Char(string="Reporting Authority Designation")
    previous_ra_phone = fields.Char(string="Reporting Authority Phone", limit=20)
    previous_hr_name = fields.Char(string="HR Name")
    previous_hr_mail = fields.Char(string="HR Email")
    previous_hr_phone = fields.Char(string="HR Phone", limit=20)
    previous_salary_per_month = fields.Float(string="Salary per month")

    previous_exit_formalities_completion = fields.Selection([('Yes', 'Yes'), ('No', 'No')],
                                                            string="Exit Formalities Complete")
    reason_for_not_complete = fields.Text(string="Reason For not Complete")

    previous_payslip_available = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Payslip Available")
    reason_for_not_available = fields.Text(string="Reason for Not having Payslip")

    uploaded_payslip_doc1 = fields.Binary(string="Payslip 1", attachment=True)
    payslip_filename1 = fields.Char("file name", )
    payslip_attachment1_id = fields.Char(compute='_compute_payslip_doc_id')
    
    uploaded_payslip_doc2 = fields.Binary(string="Payslip 2", attachment=True)
    payslip_filename2 = fields.Char("file name", )
    payslip_attachment2_id = fields.Char(compute='_compute_payslip_doc_id')
    
    uploaded_payslip_doc3 = fields.Binary(string="Payslip 3", attachment=True)
    payslip_filename3 = fields.Char("file name", )
    payslip_attachment3_id = fields.Char(compute='_compute_payslip_doc_id')

    previous_relieving_letter = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Relieving Letter")
    reason_for_not_having_relieving_letter = fields.Text(string="Reason for Not Having Relieving letter")
    
    appli_differently_abled = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Differently Abled?", default="No")
    appli_blind = fields.Boolean('Blind')
    appli_deaf = fields.Boolean('Deaf')
    appli_dumb = fields.Boolean('Dumb')
    appli_orthopedically = fields.Boolean('Orthopedically Handicapped')
    appli_of_disability = fields.Integer(string="% of Disability")

    intern_offer_id = fields.Many2one(string="Offer Letter", related="applicant_id.offer_id")
    intern_offer_type = fields.Selection(
        [('Intern', 'Intern'), ('Lateral', 'Lateral'), ('RET', 'RET'), ('Offshore', 'Offshore')],
        string='Offer Letter Type', compute="_compute_offer_letter")
    intern_ctc = fields.Float(string="Monthly CTC", compute="_compute_offer_letter")
    intern_basic = fields.Float(string="Monthly Basic", compute="_compute_offer_letter")
    intern_hra = fields.Integer(string="HRA(%)", compute="_compute_offer_letter")
    intern_conveyance = fields.Integer(string="Conveyance(%)", compute="_compute_offer_letter")
    intern_pb = fields.Float(string="Productivity Allowance", compute="_compute_offer_letter")
    intern_cb = fields.Float(string="Commitment Allowance", compute="_compute_offer_letter")
    intern_lta = fields.Float(string="LTA Amount", compute="_compute_offer_letter")
    intern_pp = fields.Float(string="Professional Pursuit Amount", compute="_compute_offer_letter")
    
    medical_doc_validate = fields.Selection([('Validated','Validated'),('Not_validated','Not Validated')],string="Personal Doc Validate",track_visibility='onchange')
    medical_doc_not_valid_date = fields.Date(string="Date Submit",track_visibility='onchange')
    medical_doc_remark = fields.Text(string="Remarks",track_visibility='onchange')
    
    work_ex_doc = fields.Selection([('Validated','Validated'),('Not_validated','Not Validated')],string="Work Experiance Doc Validate",track_visibility='onchange') 
    work_ex_not_valid_date = fields.Date(string="Date Submit",track_visibility='onchange')
    work_ex_remark = fields.Text(string="Remarks",track_visibility='onchange')
    
    edu_doc_valid = fields.Selection([('Validated','Validated'),('Not_validated','Not Validated')],string="Educational Doc Validate",track_visibility='onchange')
    edu_doc_not_valid_date = fields.Date(string="Date Submit",track_visibility='onchange')
    edu_remark = fields.Text(string="Remarks",track_visibility='onchange')
    
    identiy_doc_valid = fields.Selection([('Validated','Validated'),('Not_validated','Not Validated')],string="Indentification doc Validate",track_visibility='onchange')
    identiy_valid_date = fields.Date(string="Date Submit",track_visibility='onchange')
    identity_remark = fields.Text(string="Remarks",track_visibility='onchange')

    odisha_domicile = fields.Selection([('yes','Yes'),('no','No')],string="Odisha Domicile")
    
    #####personal insurance ##################
    epf_document = fields.Binary(string="EPF Document", attachment=True)
    file_name_epf = fields.Char(string="File Name")
    
    personal_insurance = fields.Selection([('Yes','Yes'),('No','No')],string="Health Insurance")
    uplod_insurance_doc = fields.Binary(string="Insurance Document", attachment=True)
    file_name_insurance = fields.Char(string="File Name")
    insurance_validate_date = fields.Date(string="Health Insurance Validity Date")
    
    @api.onchange('medical_doc_validate','work_ex_doc','edu_doc_valid','identiy_doc_valid')
    def _onchange_valid_doc(self):
        for rec in self:
            if rec.medical_doc_validate == 'Validated':
                rec.medical_doc_not_valid_date = False
                rec.medical_doc_remark = False
            elif rec.work_ex_doc == 'Validated':
                rec.work_ex_not_valid_date = False
                rec.work_ex_remark = False
            elif rec.edu_doc_valid == 'Validated':
                rec.edu_doc_not_valid_date = False
                rec.edu_remark = False
            elif rec.identiy_doc_valid == 'Validated':
                rec.identiy_valid_date = False
                rec.identity_remark = False
                
    @api.onchange('personal_insurance','enable_epf')
    def get_insurance_check(self):
        for rec in self:
            if rec.personal_insurance == 'Yes':
                rec.uplod_insurance_doc = False
                rec.file_name_insurance = False
                rec.insurance_validate_date = False
            if rec.enable_epf == 'yes':
                rec.epf_document = False
                rec.file_name_epf = False

                
    @api.constrains('uplod_insurance_doc')
    def check_upload_document(self):
        if self.uplod_insurance_doc == False and self.personal_insurance == 'No':
            raise ValidationError(f"You have chosen {self.personal_insurance} for health insurance. You need to upload the required document.")

    @api.depends('applicant_id')
    def _compute_offer_letter(self):
        for rec in self:
            # print("applicant_id >>> ", rec.applicant_id, rec.intern_offer_id)
            offer_rec = rec.sudo().intern_offer_id
            rec.intern_offer_type = offer_rec.offer_type
            rec.intern_ctc = offer_rec.revised_amount
            for first_line in offer_rec.annexture_offer1:
                if first_line.code == 'basic':
                    rec.intern_basic = first_line.per_month
                elif first_line.code == 'hra':
                    rec.intern_hra = first_line.percentage
                elif first_line.code == 'conv':
                    rec.intern_conveyance = first_line.percentage
                elif first_line.code == 'pb':
                    rec.intern_pb = first_line.per_month
                elif first_line.code == 'cb':
                    rec.intern_cb = first_line.per_month
                elif first_line.code == 'lta':
                    rec.intern_lta = first_line.per_month
                elif first_line.code == 'pp':
                    rec.intern_pp = first_line.per_month

    @api.onchange('tmp_source_id')
    def onchange_tmp_source_id(self):
        for rec in self:
            rec.tmp_employee_referred = False
            rec.tmp_service_partner_id = False
            rec.tmp_media_id = False
            rec.tmp_consultancy_id = False
            rec.tmp_jportal_id = False
            rec.tmp_reference = False
            rec.tmp_reference_walkindrive = False
            rec.tmp_reference_print_media = False
            rec.tmp_reference_job_fair = False
            rec.tmp_institute_id = False

    @api.onchange('bond_required')
    def onchange_bond_required(self):
        for rec in self:
            if rec.bond_required == '0':
                rec.bond_years = False
                rec.bond_months = False

    @api.onchange('tmp_grade')
    def onchange_tmp_grade(self):
        for rec in self:
            rec.tmp_band = False
            if rec.tmp_grade.has_band:
                rec.tmp_has_band = True
            else:
                rec.tmp_has_band = False

    # === Enroll document smart button method ====
    @api.multi
    def button_enroll_document(self):
        return {
                'type': 'ir.actions.act_url',
                'url': f'/download_enroll_doc/{self.id}',
                'target': 'new',
        }
        

    def button_update_applicant_data(self):
        applicant_data = self.env['hr.applicant'].search([('id','=',self.applicant_id.id)])
        if applicant_data:
            vals = {}
            if applicant_data.email_from:
                vals['email'] = applicant_data.email_from
            if applicant_data.partner_mobile:
                vals['mobile'] = applicant_data.partner_mobile
            if applicant_data.department_id.active is True:
                vals['dept_name'] = applicant_data.department_id.id
            if applicant_data.job_id:
                vals['job_id'] = applicant_data.job_id.id
            if applicant_data.division.active is True:
                vals['division'] = applicant_data.division.id
            if applicant_data.section.active is True:
                vals['section'] = applicant_data.section.id
            if applicant_data.practise.active is True:
                vals['practise'] = applicant_data.practise.id
            if applicant_data.mrf_id:
                vals['mrf_id'] = applicant_data.mrf_id.id
                vals['budget_type'] = applicant_data.requisition_type
                vals['tmp_emp_role'] = applicant_data.mrf_role_id.id
                vals['project_name_id'] = applicant_data.mrf_id.project.id
                vals['fin_project_name_id'] = applicant_data.mrf_id.project.id
                vals['tmp_emp_category'] = applicant_data.mrf_categ_id.id
                vals['tmp_employement_type'] = applicant_data.mrf_type_employment.id
                vals['finance_mrf_id'] = applicant_data.mrf_id.id
            if applicant_data.gender:
                vals['gender'] = applicant_data.gender
            vals['tmp_join_date'] = applicant_data.joining_date if applicant_data.joining_date else False
            vals['tmp_source_id'] = applicant_data.source_id.id if applicant_data.source_id else False
            vals['tmp_employee_referred'] = applicant_data.employee_referred.id if applicant_data.source_id.code == 'employee' else False
            vals['tmp_jportal_id'] = applicant_data.jportal_id.id if applicant_data.source_id.code == 'job' else False
            vals['tmp_reference'] = applicant_data.reference if applicant_data.source_id.code == 'client' else False
            vals['tmp_institute_id'] = applicant_data.institute_id.id if applicant_data.source_id.code == 'institute' else False
            vals['tmp_consultancy_id'] = applicant_data.consultancy_id.id if applicant_data.source_id.code == 'consultancy' else False
            vals['tmp_media_id'] = applicant_data.media_id.id if applicant_data.source_id.code == 'social' else False
            vals['tmp_reference_walkindrive'] = applicant_data.reference_walkindrive if applicant_data.source_id.code == 'walkindrive' else False
            vals['tmp_reference_print_media'] = applicant_data.reference_print_media if applicant_data.source_id.code == 'printmedia' else False
            vals['tmp_reference_job_fair'] = applicant_data.reference_job_fair if applicant_data.source_id.code == 'jobfair' else False
            vals['tmp_service_partner_id'] = applicant_data.service_partner_id.id if applicant_data.source_id.code == 'partners' else False

            vals['bond_required'] = applicant_data.bond_required
            vals['bond_years'] = applicant_data.bond_years
            vals['bond_months'] = applicant_data.bond_months
            vals['location_id'] = applicant_data.offer_id.job_location.id
            vals['tmp_worklocation_id'] = applicant_data.offer_id.job_location.id
            vals['birthday'] = applicant_data.date_of_birth
            vals['type_of_project_id'] = applicant_data.project_type
            vals['engagement'] = applicant_data.mrf_duration
            if applicant_data.offer_id.grade.id or applicant_data.offer_id.emp_band.id:
                vals['tmp_grade'] = applicant_data.offer_id.grade.id
                vals['tmp_band'] = applicant_data.offer_id.emp_band.id

            if 'budget_type' in vals and vals['budget_type'] == 'treasury':
                record_emp_type = self.env['kwemp_employment_type'].sudo().search([('code', '=', 'P')])
                vals['employement_type'] = record_emp_type.id
                vals['tmp_employement_type'] = record_emp_type.id
            if 'budget_type' in vals and vals['budget_type'] == 'project':
                record_emp_type = self.env['kwemp_employment_type'].sudo().search([('code', '=', 'C')])
                vals['employement_type'] = record_emp_type.id
                vals['tmp_employement_type'] = record_emp_type.id
            if applicant_data.requisition_type == 'project':
                vals['tmp_start_dt'] = applicant_data.joining_date
                vals['tmp_end_dt'] = applicant_data.joining_date + relativedelta(months=int(applicant_data.mrf_duration))
                vals['start_dt'] = applicant_data.joining_date
                vals['end_dt'] = applicant_data.joining_date + relativedelta(months=int(applicant_data.mrf_duration))

            if applicant_data.offer_id.avail_pf_benefit:
                vals['enable_epf'] = 'yes'
                vals['pf_deduction'] = applicant_data.offer_id.pf_deduction

            vals['enable_payroll'] = 'yes'

            if applicant_data.offer_id.offer_type == 'Intern':
                vals['tmp_at_join_time'] = applicant_data.offer_id.first_amount if applicant_data.offer_id.first_amount else False
                vals['current'] = applicant_data.offer_id.first_amount if applicant_data.offer_id.first_amount else False
                vals['basic_at_join_time'] = applicant_data.offer_id.first_amount if applicant_data.offer_id.first_amount else False
                vals['current_basic'] = applicant_data.offer_id.first_amount if applicant_data.offer_id.first_amount else False
                vals['is_consolidated'] = True
                vals['hra'] = 0
                vals['conveyance'] = 0
                vals['productivity'] = 0
                vals['commitment'] = 0
                vals['lta_amount'] = 0
                vals['pp_amount'] = 0
            else:
                if applicant_data.offer_id:
                    pfer = applicant_data.offer_id.annexure_offer2.filtered(lambda x : x.per_month > 0 and x.code == 'pfer')
                    gratuity = applicant_data.offer_id.annexure_offer3.filtered(lambda x : x.per_month > 0 and x.code == 'gratuity')
                    current_ctc = pfer.per_month + gratuity.per_month +  applicant_data.offer_id.average_1_month
                    vals['tmp_at_join_time'] = current_ctc if current_ctc else False
                    vals['current'] = current_ctc if current_ctc else False
            
                if applicant_data.offer_id.avail_pf_benefit == True:
                    vals['enable_epf'] = 'yes'
                    vals['pf_deduction'] = applicant_data.offer_id.pf_deduction
                for first_line in applicant_data.offer_id.annexture_offer1:
                    if first_line.code == 'basic':
                        vals['basic_at_join_time'] = first_line.per_month
                        vals['current_basic'] = first_line.per_month
                    if first_line.code == 'hra':
                        vals['hra'] = first_line.percentage
                    if first_line.code == 'conv':
                        vals['conveyance'] = first_line.percentage
                    if first_line.code == 'pb':
                        vals['productivity'] = first_line.per_month
                    if first_line.code == 'cb':
                        vals['commitment'] = first_line.per_month
                    if first_line.code == 'lta':
                        vals['lta_amount'] = first_line.per_month
                    if first_line.code == 'pp':
                        vals['pp_amount'] = first_line.per_month
                for third_line in applicant_data.offer_id.annexure_offer3:
                    if third_line.code == 'gratuity':
                        if third_line.per_month > 0:
                            vals['enable_gratuity'] = 'yes'
                        else:
                            vals['enable_gratuity'] = 'no'
                if applicant_data.offer_id.offer_type == 'Lateral':
                    if applicant_data.offer_id.pt_type == 'Probation':
                        vals['tmp_on_probation'] = True
                        vals['no_of_months'] = applicant_data.offer_id.months
                        vals['tmp_prob_compl_date'] = applicant_data.offer_id.joining_date + relativedelta(months=int(applicant_data.offer_id.months))
            applicant_data.active = True
            onboard_applicant_data = self.write(vals)
            if onboard_applicant_data:
                self.env.user.notify_success(message='Applicant data Update successfully.')
    @api.onchange('mrf_id')
    def onchange_mrf_id(self):
        for rec in self:
            if rec.mrf_id:
                rec.finance_mrf_id = rec.mrf_id.id
            #     rec.budget_type = rec.mrf_id.requisition_type
            #     rec.tmp_emp_role = rec.mrf_id.role_id.id 
            #     rec.tmp_emp_category = rec.mrf_id.categ_id.id 
            #     rec.tmp_employement_type = rec.mrf_id.type_employment.id
                
            # elif rec.mrf_id.requisition_type == "project":
            #     self.type_of_project_id = rec.mrf_id.type_project
            #     self.project_name_id = rec.mrf_id.project
            #     self.engagement = rec.mrf_id.duration
            # else:
            #     rec.type_of_project_id = False
            #     rec.project_name_id = False
            #     rec.engagement = False

    @api.onchange('tmp_username')
    def check_username(self):
        for rec in self:
            if rec.tmp_username:
                enrollment_rec = self.env['kwonboard_enrollment'].sudo().search(
                    [('tmp_username', '=', rec.tmp_username),
                     '|', ('active', '=', True), ('active', '=', False)]) - self
                user_rec = self.env['res.users'].sudo().search(
                    [('login', '=', rec.tmp_username), '|', ('active', '=', True), ('active', '=', False)])
                if enrollment_rec or user_rec:
                    raise ValidationError('Username already exists, Please choose a unique username.')

    @api.onchange('tmp_contract_year_month', 'tmp_contract_period', 'tmp_start_dt')
    def _onchange_tmp_contract_year_month(self):
        if self.tmp_contract_period and self.tmp_start_dt:
            if self.tmp_contract_year_month == 'year':
                self.tmp_end_dt = self.tmp_start_dt + relativedelta(years=int(self.tmp_contract_period))
            else:
                self.tmp_end_dt = self.tmp_start_dt + relativedelta(months=int(self.tmp_contract_period))

    @api.onchange('start_dt', 'fin_engagement')
    def _onchange_contract_year_month(self):
        if self.start_dt:
            self.end_dt = self.start_dt + relativedelta(months=int(self.fin_engagement))
        # if self.contract_period and self.start_dt:
        #     if self.contract_year_month == 'year':
        #         self.end_dt = self.start_dt + relativedelta(years=int(self.contract_period))
        #     else:
        #         self.end_dt = self.start_dt + relativedelta(months=int(self.contract_period))

    @api.depends('tmp_worklocation_id')
    def _compute_work_location(self):
        for record in self:
            if record.tmp_worklocation_id:
                record.emp_worklocation = record.tmp_worklocation_id

    @api.depends('tmp_join_date')
    def _compute_join_date(self):
        for record in self:
            if record.tmp_join_date:
                record.it_join_date = record.tmp_join_date
                record.admin_join_date = record.tmp_join_date
                record.finance_join_date = record.tmp_join_date

    """ Profile image URL to be created which will be sent while syncing """
    def _compute_image_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'), ('res_field', '=', 'image')])
            attachment_data.write({'public': True})
            record.image_id = attachment_data.id
    
    def _compute_medical_certificate_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'), ('res_field', '=', 'medical_certificate')])
            attachment_data.write({'public': True})
            record.medical_certifcate_attachment_id = attachment_data.id
            
    def _compute_payslip_doc_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'),
                 ('res_field', '=', 'uploaded_payslip_doc1')])
            attachment_data.write({'public': True})
            record.payslip_attachment1_id = attachment_data.id

            attachment_data2 = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'),
                 ('res_field', '=', 'uploaded_payslip_doc2')])
            attachment_data2.write({'public': True})
            record.payslip_attachment2_id = attachment_data2.id

            attachment_data3 = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'),
                 ('res_field', '=', 'uploaded_payslip_doc3')])
            attachment_data3.write({'public': True})
            record.payslip_attachment3_id = attachment_data3.id        

    def _get_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.image_id:
                final_url = '%s/web/image/%s' % (base_url, record.image_id)
                record.image_url = final_url
            else:
                record.image_url = ''

    @api.onchange('tmp_at_join_time')
    def onchange_at_join(self):
        self.current = self.tmp_at_join_time

    # @api.constrains('tmp_at_join_time')
    # def check_tmp_at_join_time(self):
    #     if self.tmp_at_join_time == 0.00:
    #         raise ValidationError("Salary at joining time should be greater than 0.00")

    @api.onchange('basic_at_join_time')
    def _onchange_basic_at_join(self):
        self.current_basic = self.basic_at_join_time
        # grade_id = self.env['kwemp_grade'].sudo().search([('grade_id','=',self.tmp_grade.id),('band_id','=',self.tmp_band.id)])
        # if grade_id:
        # record_id = self.env['kw_grade_pay'].sudo().search([('grade','=',grade_id.id),('country','=',self.tmp_worklocation_id.country.id)])
        record_id = self.env['kw_grade_pay'].sudo().search(
            [('grade', '=', self.tmp_grade.id), ('band', '=', self.tmp_band.id),
             ('country', '=', self.tmp_worklocation_id.country.id)])
        if record_id:
            if self.basic_at_join_time > record_id.basic_max:
                return {'warning': {
                    'title': _('Validation Error'),
                    'message': (
                        f'Basic amount at join time ({self.basic_at_join_time}) is greater than Grade pay Basic max amount ({record_id.basic_max}) for Grade {record_id.grade.name}.')
                }}
            if self.basic_at_join_time < record_id.basic_min:
                return {'warning': {
                    'title': _('Validation Error'),
                    'message': (
                        f'Basic amount at join time ({self.basic_at_join_time}) is less than Grade pay Basic min amount ({record_id.basic_min} for Grade {record_id.grade.name}.')
                }}

    @api.onchange('enable_payroll')
    def onchange_payroll(self):
        if self.enable_payroll == 'no':
            self.basic_at_join_time = False
            self.bank_account = False
            self.struct_id = False
            self.bank_id = False
            self.hra = False
            self.conveyance = False
            self.medical_reimb = False
            self.transport = False
            self.productivity = False
            self.commitment = False
            self.cosolid_amnt = False
            self.enable_epf = False
            self.pf_deduction = False
            self.enable_gratuity = False
            self.current_basic = False

    def action_update_payroll_information(self):
        for rec in self:
            offer_rec = rec.applicant_id.offer_id
            if offer_rec.exists():
                # print("offer_rec >>>>>>>>>>>> ", offer_rec)
                # print("offer_rec.average_1_month >>>>>>>>>>>> ", offer_rec.average_1_month)
                rec.enable_payroll = 'yes'

                if offer_rec.offer_type == 'Intern':
                    rec.tmp_at_join_time = offer_rec.first_amount if offer_rec.first_amount else 0
                    rec.current = offer_rec.first_amount if offer_rec.first_amount else 0
                    rec.basic_at_join_time = offer_rec.first_amount if offer_rec.first_amount else 0
                    rec.current_basic = offer_rec.first_amount if offer_rec.first_amount else 0
                    rec.is_consolidated = True
                    rec.hra = 0
                    rec.conveyance = 0
                    rec.productivity = 0
                    rec.commitment = 0
                    rec.enable_gratuity = 'no'
                    rec.enable_epf = 'no'
                else:
                    pfer = offer_rec.annexure_offer2.filtered(lambda x : x.per_month > 0 and x.code == 'pfer')
                    gratuity = offer_rec.annexure_offer3.filtered(lambda x : x.per_month > 0 and x.code == 'gratuity')
                    current_ctc = pfer.per_month + gratuity.per_month + offer_rec.average_1_month
                    rec.tmp_at_join_time = current_ctc  if current_ctc else 0
                    rec.current = current_ctc  if current_ctc else 0
                    rec.is_consolidated = False
                    if offer_rec.avail_pf_benefit == True:
                        rec.enable_epf = 'yes'
                        rec.pf_deduction = offer_rec.pf_deduction
                    for first_line in offer_rec.annexture_offer1:
                        if first_line.code == 'basic':
                            rec.basic_at_join_time = first_line.per_month
                            rec.current_basic = first_line.per_month
                        if first_line.code == 'hra':
                            rec.hra = first_line.percentage
                        if first_line.code == 'conv':
                            rec.conveyance = first_line.percentage
                        if first_line.code == 'pb':
                            rec.productivity = first_line.per_month
                        if first_line.code == 'cb':
                            rec.commitment = first_line.per_month
                        if first_line.code == 'lta':
                            rec.lta_amount = first_line.per_month
                        if first_line.code == 'pp':
                            rec.pp_amount = first_line.per_month
                    for third_line in offer_rec.annexure_offer3:
                        if third_line.code == 'gratuity':
                            if third_line.per_month > 0:
                                rec.enable_gratuity = 'yes'
                            else:
                                rec.enable_gratuity = 'no'

    @api.onchange('no_of_months')
    def _onchange_no_of_months(self):
        self.tmp_prob_compl_date = self.tmp_join_date+relativedelta(months=int(self.no_of_months))

    @api.onchange('tmp_worklocation_id')
    def _onchange_work_location(self):
        self.tmp_shift = False
        return {'domain': {'tmp_shift': [('branch_id', '=', self.tmp_worklocation_id.id)]}}

    @api.onchange('tmp_location')
    def _onchange_location(self):
        self.tmp_client_location = False
        self.infra_id = False
        self.work_station_id = False

    @api.onchange('tmp_on_probation')
    def _onchange_probation(self):
        self.tmp_prob_compl_date = False

    @api.onchange('card_type')
    def _onchange_card_type(self):
        self.id_card_no = False
        return {'domain': {'id_card_no': [('card_type', '=', self.card_type), ('state', '=', 'unassigned')]}}
        
    @api.onchange('tmp_employement_type')
    def _onchange_tmp_employement_type(self):
        if self.tmp_employement_type:
            self.tmp_direct_indirect = False
            self.tmp_project_id = False
            self.tmp_start_dt = False
            self.tmp_end_dt = False
            self.tmp_contract_period = False
            self.tmp_contract_year_month = False

    @api.onchange('tmp_emp_role')
    def _onchange_tmp_emp_role(self):
        if self.tmp_emp_role and self.tmp_emp_category:
            if self.tmp_emp_role not in self.tmp_emp_category.role_ids:
                self.tmp_emp_category = False
        else:
            self.tmp_emp_category = False

        return {'domain': {'tmp_emp_category': [('role_ids', '=', self.tmp_emp_role.id)], }}

    @api.constrains('confirm_outl_pwd', 'confirm_domain_pwd', 'biometric_id', 'epbx_no', 'start_dt', 'end_dt',
                    'tmp_start_dt', 'tmp_end_dt')
    def check_constraints(self):
        enroll_rec = self.env['kwonboard_enrollment'].sudo()
        emp_rec = self.env['hr.employee'].sudo()
        for rec in self:
            if rec.outlook_pwd and rec.outlook_pwd != rec.confirm_outl_pwd:
                raise ValidationError("Outlook password and Confirm password must be same")
            if rec.domain_login_pwd and rec.domain_login_pwd != rec.confirm_domain_pwd:
                raise ValidationError("Domain password and Confirm password must be same")
            if rec.biometric_id:
                if enroll_rec.search([('biometric_id', '=', rec.biometric_id)]) - self \
                        or emp_rec.search([('biometric_id', '=', rec.biometric_id)]):
                    raise ValidationError("This Biometric ID is already assigned!")
            if rec.epbx_no:
                if enroll_rec.search([('epbx_no', '=', rec.epbx_no)]) - self \
                        or emp_rec.search([('epbx_no', '=', rec.epbx_no)]):
                    raise ValidationError("This EPBX is already assigned!")
            
    @api.onchange('end_dt')
    def _onchange_start_dt(self):
        if self.end_dt:
            if self.start_dt >= self.end_dt:
                raise ValidationError("Contract end date must not be before or equal to start date!")
            
    @api.onchange('tmp_end_dt')
    def _onchange_tmp_end_dt(self):
        if self.tmp_end_dt:
            if self.tmp_start_dt >= self.tmp_end_dt:
                raise ValidationError("Contract end date must not be before or equal to start date!")
            
    @api.constrains('tmp_start_dt')
    def _onchange_tmp_start_dt(self):
        if self.tmp_join_date and self.tmp_start_dt:
            if self.tmp_join_date > self.tmp_start_dt:
                raise ValidationError("Contract start date must not be before to join date!")        

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('group_check'):
            ids = []
            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance'):
                query = "SELECT id FROM kwonboard_enrollment WHERE finance_setting_status=False AND state='3';"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_officer'):
                query = "SELECT id FROM kwonboard_enrollment WHERE state in ('1','2','3');"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                query = "SELECT id FROM kwonboard_enrollment WHERE nsa_setting_status=False AND state='3';"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin'):
                query = "SELECT id FROM kwonboard_enrollment WHERE admin_setting_status=False AND state='3';"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]
            elif self.env.user.has_group('kw_onboarding.group_kw_onboarding_rcm'):
                query = "SELECT id FROM kwonboard_enrollment WHERE rcm_setting_status=False AND state='3';"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

            else:
                query = "SELECT id FROM kwonboard_enrollment"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

        return super(kwonboard_enrollment, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                         access_rights_uid=access_rights_uid)

    def check_access_finance(self):
        cur_user = self.env.user
        if cur_user.has_group('kw_onboarding.group_kw_onboarding_manager') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_officer'):
            for rec in self:
                rec.check_finance = True
                
    def check_access_rcm_onboard(self):
        cur_user = self.env.user
        if cur_user.has_group('kw_onboarding.group_kw_onboarding_manager') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_rcm') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_officer'):
            for rec in self:
                rec.check_rcm_onboard = True

    def check_access_it(self):
        cur_user = self.env.user
        if cur_user.has_group('kw_onboarding.group_kw_onboarding_manager') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_officer'):
            for rec in self:
                rec.check_it = True

    def check_access_admin(self):
        cur_user = self.env.user
        if cur_user.has_group('kw_onboarding.group_kw_onboarding_manager') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                or cur_user.has_group('kw_onboarding.group_kw_onboarding_officer'):
            for rec in self:
                rec.check_admin = True

    def check_access_manager(self):
        self.check_manager = False
        if self.env.user.has_group('kw_onboarding.group_kw_onboarding_manager'):
            self.check_manager = True

    def check_access_officer(self):
        self.check_officer = False
        if self.env.user.has_group('kw_onboarding.group_kw_onboarding_officer'):
            self.check_officer = True

    @api.constrains('whatsapp_no')
    def check_whatsapp_no(self):
        for record in self:
            if record.whatsapp_no:
                if not len(record.whatsapp_no) == 10:
                    raise ValidationError("Your whatsapp number is invalid for: %s" % record.whatsapp_no)
                if not re.match("^[0-9]*$", str(record.whatsapp_no)) != None:
                    raise ValidationError("Your WhatsApp number is invalid for: %s" % record.whatsapp_no)

    @api.constrains('emgr_phone')
    def check_emgr_phone(self):
        for record in self:
            if record.emgr_phone:
                if not len(record.emgr_phone) == 10:
                    raise ValidationError("Your emergency number is invalid for: %s" % record.emgr_phone)
                if not re.match("^[0-9]*$", str(record.emgr_phone)) != None:
                    raise ValidationError("Your emergency number is invalid for: %s" % record.emgr_phone)
                if record.emgr_phone == record.whatsapp_no or record.emgr_phone == record.mobile:
                    raise ValidationError("Your Emergency number can not same as WhatsApp or Primary no")
    
    @api.model
    def default_get(self, fields):
        result = super(kwonboard_enrollment, self).default_get(fields)
        configuration_type_lines = []
        types = self.env['kwonboard_config_type'].search([])
        for typ in types:
            configuration_type_lines.append(typ.id)

        result.update({
            'check_manager': self.env.user.has_group('kw_onboarding.group_kw_onboarding_manager'),
            'check_officer': self.env.user.has_group('kw_onboarding.group_kw_onboarding_officer'),
            'system_configuration': [(6, 0, configuration_type_lines)],
        })
        return result

    @api.onchange('applicant_id')
    def onchange_applicant_id(self):
        self.name = self.applicant_id.partner_name
        self.dept_name = self.applicant_id.department_id
        self.job_id = self.applicant_id.job_id
        self.email = self.applicant_id.email_from
        self.mobile = self.applicant_id.partner_mobile
        self.division = self.applicant_id.division
        self.section = self.applicant_id.section
        self.practise = self.applicant_id.practise
        self.gender = self.applicant_id.gender
        if self.applicant_id.job_position.mrf_id:
            self.tmp_emp_role = self.applicant_id.job_position.mrf_id.role_id.id 
            self.tmp_emp_category = self.applicant_id.job_position.mrf_id.categ_id.id 
            self.tmp_employement_type = self.applicant_id.job_position.mrf_id.type_employment.id
            self.tmp_project_id = self.applicant_id.job_position.mrf_id.project.id
            # print("22222222222222222")
        elif self.applicant_id.mrf_id:
            self.tmp_emp_role = self.applicant_id.mrf_id.role_id.id
            self.tmp_emp_category = self.applicant_id.mrf_id.categ_id.id
            self.tmp_employement_type = self.applicant_id.mrf_id.type_employment.id
            self.tmp_project_id = self.applicant_id.mrf_id.project.id
            # print("33333333333333333333")

    @api.onchange('dept_name')
    def onchange_department(self):
        self.division = False
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.dept_name.id), ('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('division')
    def onchange_division(self):
        self.section = False
        domain = {}
        for rec in self:
            if rec.dept_name:
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        self.practise = False
        domain = {}
        for rec in self:
            if rec.section:
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}
                
    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.work_location_id = False
        return {'domain': {'work_location_id': [('parent_id', '=', self.company_id.partner_id.id)], }}

    @api.model
    def _inverse_field(self):
        if self.image:
            bin_value = base64.b64decode(self.image)
            if not os.path.exists('onboarding_docs/' + str(self.id)):
                os.makedirs('onboarding_docs/' + str(self.id))
            full_path = os.path.join(os.getcwd() + '/onboarding_docs/' + str(self.id), self.image_name)
            # if os.path.exists(full_path):
            #     raise ValidationError("The file name "+self.filename+" exists.Please change your file name.")
            try:
                with open(os.path.expanduser(full_path), 'wb') as fp:
                    fp.write(bin_value)
                    fp.close()
            except Exception as e:
                # print(e)
                pass

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(kwonboard_enrollment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                                submenu=submenu)
        doc = etree.XML(res['arch'])
        # #condition for readonly fields, for other user groups
        if not self.env.user.multi_has_groups(['kw_onboarding.group_kw_onboarding_manager', 'kw_onboarding.group_kw_onboarding_officer']):
            for node in doc.xpath("//field[@name='company_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='name']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='image']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='work_location_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='dept_name']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='job_id']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='email']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='mobile']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='create_full_profile']"):
                node.set('modifiers', '{"readonly": true}')
            for node in doc.xpath("//field[@name='tmp_worklocation_id']"):
                node.set('modifiers', '{"readonly": true}')
        res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('same_address')
    def _change_permanent_address(self):
        if self.same_address:
            self.permanent_addr_country_id = self.present_addr_country_id
            self.permanent_addr_street = self.present_addr_street
            self.permanent_addr_street2 = self.present_addr_street2
            self.permanent_addr_city = self.present_addr_city
            self.permanent_addr_state_id = self.present_addr_state_id
            self.permanent_addr_zip = self.present_addr_zip

    @api.depends('system_configuration')
    def _compute_config_setting(self):
        for config_rec in self.system_configuration:
            for sel_group in config_rec.authorized_group:
                # #if the group is selected group or HR manage group
                if sel_group in self.env.user.groups_id:
                    self.other_user_status = True

            if self.env.user.has_group('kw_onboarding.group_kw_onboarding_manager'):
                self.other_user_status = False

            if config_rec.configuration_type_id.code == 'idcard':
                self.user_grp_id_card = True
            elif config_rec.configuration_type_id.code == 'budget':
                self.user_grp_budget = True
            elif config_rec.configuration_type_id.code == 'outlookid':
                self.user_grp_outlook = True
            elif config_rec.configuration_type_id.code == 'biometric':
                self.user_grp_biometric = True
            elif config_rec.configuration_type_id.code == 'system':
                self.user_grp_domain_pwd = True
            elif config_rec.configuration_type_id.code == 'epbx':
                self.user_grp_epbx = True
            elif config_rec.configuration_type_id.code =='sbu':
                # print("config_rec.configuration_type_id.code===============",config_rec.configuration_type_id.code)
                self.user_grp_sbu = True

        if (self.user_grp_outlook or self.user_grp_biometric or self.user_grp_domain_pwd or self.user_grp_epbx) and (
                not self.nsa_setting_status and self.state == '3'):
            self.display_nsa_btn = True

    """# onchange of present address country change the state"""
    @api.onchange('present_addr_country_id')
    def _change_present_address_state(self):
        country_id = self.present_addr_country_id.id
        self.present_addr_state_id = False
        return {'domain': {'present_addr_state_id': [('country_id', '=', country_id)], }}

    """# onchange of employee category change the role"""

    @api.onchange('emp_role', 'fin_budget_type', 'emp_category', 'employement_type', 'fin_type_of_project_id',
                  'fin_engagement', 'fin_project_name_id', 'start_dt', 'end_dt')
    def _get_categories(self):
        role_id = self.emp_role.id
        # self.emp_category = False
        for rec in self:
            rec.budget_type = rec.fin_budget_type
            rec.tmp_emp_role = rec.emp_role
            rec.tmp_emp_category = rec.emp_category
            rec.tmp_employement_type = rec.employement_type.id,
            rec.type_of_project_id = rec.fin_type_of_project_id
            rec.engagement = rec.fin_engagement
            rec.project_name_id = rec.fin_project_name_id
            rec.tmp_start_dt = rec.start_dt
            rec.tmp_end_dt = rec.end_dt
        return {'domain': {'emp_category': [('role_ids', '=', role_id)], }}

    """# onchange of permanent address country change the state"""
    @api.onchange('permanent_addr_country_id')
    def _change_permanent_address_state(self):
        country_id = self.permanent_addr_country_id.id
        self.permanent_addr_state_id = False
        if self.same_address and self.present_addr_state_id and (self.permanent_addr_country_id == self.present_addr_country_id):
            self.permanent_addr_state_id = self.present_addr_state_id
        return {'domain': {'permanent_addr_state_id': [('country_id', '=', country_id)], }}

    """ This method is used to get email of responsible person for onboarding if create_uid is odoobot 
        then use responsible person email from general settings else use email of enrollment creator 
        while communicating 
    """
    def get_email_from(self):
        email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        for rec in self:
            if rec.create_uid.id == 1 and emp_id:
                emp = self.env['hr.employee'].sudo().browse(emp_id)
                email_to, email_name = emp.work_email, emp.name
            else:
                emp = self.env['res.users'].sudo().browse(rec.create_uid.id)
                email_to, email_name = emp.email, emp.name
        return {'email_to': email_to, 'email_name': email_name}

    """ This method executes when Submit for configuration is clicked, it then sends mail notification to  
        Admin/IT/Finance group depending on the environment mapping selection.
    """
    @api.multi
    def complete_env_mapping(self):
        template = self.env.ref('kw_onboarding.config_mail_template')
        template_id = self.env['mail.template'].browse(template.id)
        email_to = self.get_email_from()
        for rec in self:
            # if all(getattr(rec, field_name) == 'Validated' for field_name in ['medical_doc_validate', 'work_ex_doc', 'edu_doc_valid', 'identiy_doc_valid']):                
            if rec.system_configuration:
                admin_setting_status = True
                finance_setting_status = True
                nsa_setting_status = True
                rcm_setting_status = True
                temp_user = []
                view_id = self.env.ref('kw_onboarding.kwonboard_enrollment_action_window').id
                for config_rec in rec.system_configuration:
                    if config_rec.configuration_type_id.code == 'idcard':
                        admin_setting_status = False
                    elif config_rec.configuration_type_id.code == 'budget':
                        finance_setting_status = False
                    elif config_rec.configuration_type_id.code in ['sbu']:
                        rcm_setting_status = False
                    else:
                        nsa_setting_status = False

                    for group in config_rec.authorized_group:
                        for user in group.users:
                            # if user.id not in config_user_id_list:
                            if config_rec.configuration_type_id.code == 'idcard':
                                mail_status = template_id.with_context(dept_name='Admin',
                                                                       user_name=user.name,
                                                                       user_mail=user.email,
                                                                       view_id=view_id,
                                                                       rec_id=rec.id,
                                                                       email_to=email_to.get('email_to')) \
                                    .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                                # rec.activity_schedule('kw_onboarding.mail_act_env_config_admin', fields.Date.today(), user_id=user.id)
                            elif config_rec.configuration_type_id.code == 'budget':
                                mail_status = template_id.with_context(dept_name='Finance',
                                                                       user_name=user.name,
                                                                       user_mail=user.email,
                                                                       view_id=view_id,
                                                                       rec_id=rec.id,
                                                                       email_to=email_to.get('email_to')) \
                                    .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                                # rec.activity_schedule('kw_onboarding.mail_act_env_config_finance', fields.Date.today(), user_id=user.id)
                            else:
                                if user.id not in temp_user:
                                    temp_user.append(user.id)
                                    mail_status = template_id.with_context(dept_name='IT',
                                                                           user_name=user.name,
                                                                           user_mail=user.email,
                                                                           view_id=view_id,
                                                                           rec_id=rec.id,
                                                                           email_to=email_to.get('email_to')) \
                                        .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                                # rec.activity_schedule('kw_onboarding.mail_act_env_config_nsa', fields.Date.today(), user_id=user.id)
                                # config_user_id_list.append(user.id)
                            # ,author_id=self.env.user.partner_id.id
                # change the status into mapped
                rec.write({'state': '3',
                           'admin_setting_status': admin_setting_status,
                           'finance_setting_status': finance_setting_status,
                           'nsa_setting_status': nsa_setting_status,
                           'rcm_setting_status': rcm_setting_status,
                           'emp_role': rec.tmp_emp_role.id,
                           'emp_category': rec.tmp_emp_category.id,
                           'employement_type': rec.tmp_employement_type.id,
                           'project_id': rec.tmp_project_id.id,
                           'start_dt': rec.tmp_start_dt,
                           'end_dt': rec.tmp_end_dt,
                           'direct_indirect': rec.tmp_direct_indirect,
                           'contract_period': rec.tmp_contract_period,
                           'contract_year_month': rec.tmp_contract_year_month,
                           'fin_engagement': rec.engagement,
                           'fin_type_of_project_id': rec.type_of_project_id,
                           'fin_budget_type': rec.budget_type})
            else:
                raise ValidationError(_('Please choose the required configurations'))
        return True

    @api.multi
    def button_take_action(self):
        view_id = self.env.ref('kw_onboarding.kwonboard_enrollment_view_form').id
        target_id = self.id
        return {
            'name': 'Configure Environment',
            'type': 'ir.actions.act_window',
            'res_model': 'kwonboard_enrollment',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'self',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True},
        }

    """ This method is used to get all designation specific employees' (which is set in general settings) email 
        which will be in cc while Admin/IT/Finance group submits configuration.
    """
    def get_designation_cc(self, rec_set=None):
        get_desig_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.employee_creation_inform_ids')
        get_emp_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.onboarding_cc_ids')
        email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        emails = ''
        email_cc = ''
        get_desig_list = literal_eval(get_desig_ids) if get_desig_ids else []
        get_emp_list = literal_eval(get_emp_ids) if get_emp_ids else []
        if rec_set == None:
            for rec in self:
                if len(get_desig_list) > 0:
                    employee = self.env['hr.employee']
                    emps = employee.sudo().search([('job_id', 'in', [int(x) for x in get_desig_list]), ('work_email', '!=', False)])
                    additional_emp = employee.sudo().search([('id', 'in', [int(x) for x in get_emp_list]), ('work_email', '!=', False)])
                    emails += ','.join(emps.mapped('work_email')) or ''
                    if additional_emp:
                        email_cc += ','.join(additional_emp.mapped('work_email')) or ''
                    if rec.create_uid.id != 1 and rec.create_uid.id != self.env['hr.employee'].sudo().browse(emp_id).user_id.id:
                        emails += ','+self.env['hr.employee'].sudo().browse(emp_id).work_email
        else:
            for rec in rec_set:
                if len(get_desig_list) > 0:
                    employee = self.env['hr.employee']
                    emps = employee.sudo().search([('job_id', 'in', [int(x) for x in get_desig_list]), ('work_email', '!=', False)])
                    additional_emp = employee.sudo().search([('id', 'in', [int(x) for x in get_emp_list]), ('work_email', '!=', False)])
                    emails += ','.join(emps.mapped('work_email')) or ''
                    if additional_emp:
                        email_cc += ','.join(additional_emp.mapped('work_email')) or ''
                    if rec.create_uid.id != 1 and rec.create_uid.id != self.env['hr.employee'].sudo().browse(emp_id).user_id.id:
                        emails += ','+self.env['hr.employee'].sudo().browse(emp_id).work_email
        return emails + ',' + email_cc

    """ This method executes when Submit IT settings is clicked and 
    checks for necessary IT settings assigned by Officer/Manager """

    @api.multi
    def complete_nsa_setting(self):
        template = self.env.ref('kw_onboarding.config_completion_mail_template')
        template_id = self.env['mail.template'].browse(template.id)
        email_to = self.get_email_from()
        for rec in self:
            for config_rec in rec.system_configuration:
                if config_rec.configuration_type_id.code == 'outlookid' and not (rec.csm_email_id and rec.outlook_pwd):
                    raise ValidationError(_(' IT settings can not be completed without outlook configuration details'))

                elif config_rec.configuration_type_id.code == 'biometric' and not rec.biometric_id:
                    raise ValidationError(_(' IT settings can not be completed without biometric configuration details'))

                elif config_rec.configuration_type_id.code == 'system' and not (rec.domain_login_id and rec.domain_login_pwd):
                    raise ValidationError(_('IT settings can not be completed without system domain configuration details'))

                elif config_rec.configuration_type_id.code == 'epbx' and not rec.epbx_no:
                    raise ValidationError(_('IT settings can not be completed without EPBX configuration details'))
            new_state = '3'
            if rec.admin_setting_status and rec.finance_setting_status and rec.rcm_setting_status:
                new_state = '4'

            rec.write({'state': new_state, 'nsa_setting_status': True})
            # if rec.nsa_setting_status == True:
            self.env.user.notify_info(message='IT settings Completed')
            # code to complete the activity
            mail_status = template_id.with_context(dept_name='IT',
                                                   user_mail=self.env.user.email,
                                                   emails_cc=self.get_designation_cc(),
                                                   email_to=email_to.get('email_to'),
                                                   user_name=email_to.get('email_name')) \
                .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                # rec.activity_feedback(['kw_onboarding.mail_act_env_config_nsa'])
        return True

    """ This method executes when Submit Finance settings is clicked and 
    checks for necessary Finance settings assigned by Officer/Manager """

    @api.multi
    def complete_finance_setting(self):
        template = self.env.ref('kw_onboarding.config_completion_mail_template')
        template_id = self.env['mail.template'].browse(template.id)
        email_to = self.get_email_from()
        for rec in self:
            if rec.direct_indirect != '2':
                if rec.emp_role and rec.emp_category and rec.employement_type:
                    new_state = '3'
                    if rec.nsa_setting_status and rec.admin_setting_status and rec.rcm_setting_status:
                        new_state = '4'
                    rec.write({'state': new_state, 'finance_setting_status': True})

                    # code to complete the activity
                    # rec.activity_feedback(['kw_onboarding.mail_act_env_config_finance'])
                    mail_status = template_id.with_context(dept_name='Finance',
                                                           user_mail=self.env.user.email,
                                                           emails_cc=self.get_designation_cc(),
                                                           email_to=email_to.get('email_to'),
                                                           user_name=email_to.get('email_name'))\
                        .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_info(message='Finance settings Completed')
                else:
                    raise ValidationError(_('Please enter all the setting details'))
            else:
                new_state = '3'
                if rec.nsa_setting_status and rec.admin_setting_status and rec.rcm_setting_status:
                    new_state = '4'

                rec.write({'state': new_state, 'finance_setting_status': True})
                mail_status = template_id.with_context(dept_name='Finance', user_mail=self.env.user.email,
                                                       emails_cc=self.get_designation_cc(),
                                                       email_to=email_to.get('email_to'),
                                                       user_name=email_to.get('email_name'))\
                    .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        return True

    """ This method executes when Submit Admin settings is clicked and 
    checks for necessary Admin settings assigned by Officer/Manager """

    @api.multi
    def complete_admin_setting(self):
        template = self.env.ref('kw_onboarding.config_completion_mail_template')
        template_id = self.env['mail.template'].browse(template.id)
        email_to = self.get_email_from()
        for rec in self:
            if rec.id_card_no:
                new_state = '3'
                if rec.nsa_setting_status and rec.finance_setting_status and rec.rcm_setting_status:
                    new_state = '4'
                rec.write({'state': new_state, 'admin_setting_status': True})
                # code to complete the activity
                # rec.activity_feedback(['kw_onboarding.mail_act_env_config_admin'])
                mail_status = template_id.with_context(dept_name='Admin',
                                                       user_mail=self.env.user.email,
                                                       emails_cc=self.get_designation_cc(),
                                                       email_to=email_to.get('email_to'),
                                                       user_name=email_to.get('email_name'))\
                    .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_info(message='Admin settings Completed')
            else:
                raise ValidationError(_('Please enter ID Card No'))
        return True

    @api.multi
    def complete_rcm_setting(self):
        if self.division and self.sbu_type and self.tmp_admin_auth.exists():
            template = self.env.ref('kw_onboarding.config_completion_mail_template')
            template_id = self.env['mail.template'].browse(template.id)
            email_to = self.get_email_from()
            for rec in self:
                if rec.sbu_master_id and rec.tmp_admin_auth and rec.division:
                    new_state = '3'
                    if rec.nsa_setting_status and rec.finance_setting_status and rec.admin_setting_status:
                        new_state = '4'
                    rec.write({'state': new_state, 'rcm_setting_status': True})
                mail_status = template_id.with_context(dept_name='RCM',
                                                       user_mail=self.env.user.email,
                                                       emails_cc=self.get_designation_cc(),
                                                       email_to=email_to.get('email_to'),
                                                       user_name=email_to.get('email_name')) \
                    .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_info(message='RCM settings Completed')
        else:
            raise ValidationError(_('Please enter Division, SBU and Reporting Authority Details'))

    """ This method is executed when Officer/Manager validates a candidature, 
    this will also create a record in Onboarding for further process."""

    @api.multi
    def make_enrole_to_employee(self):
        emp_vals = {}
        user_vals = {}
        new_user_rec = False
        # user_action = self.env.ref('kw_hr_attendance.action_my_office_time')
        user_action = self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action')
        # print("user_action==",user_action)
        for rec in self:
            if not rec.mrf_id:
                raise UserError(_('No MRF found for this applicant.'))
            if not rec.odisha_domicile:
                raise UserError(_('Please choose Odisha domicile option yes/no for this applicant.'))
            # if rec.authenticate_bool_check == False:
            #     if any(getattr(rec, field_name) == 'Not_validated' for field_name in
            #         ['medical_doc_validate', 'work_ex_doc', 'edu_doc_valid', 'identiy_doc_valid']):
            #         raise ValidationError(_('Please Validate all documents before proceeding for approval.'))

                # check for validations for selected services
            for config_rec in rec.system_configuration:
                if config_rec.configuration_type_id.code == 'idcard' and not rec.id_card_no:
                    raise ValidationError(_('Please provide all admin setting details before proceeding for approval'))
                elif config_rec.configuration_type_id.code == 'budget' and not (rec.emp_role or rec.emp_category or rec.employement_type):
                    raise ValidationError(_('Please provide all finance setting details before proceeding for approval'))
                elif config_rec.configuration_type_id.code == 'outlookid' and not (rec.csm_email_id or rec.outlook_pwd):
                    raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
                elif config_rec.configuration_type_id.code == 'biometric' and not rec.biometric_id:
                    raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
                elif config_rec.configuration_type_id.code == 'system' and not (rec.domain_login_id or rec.domain_login_pwd):
                    raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
                elif config_rec.configuration_type_id.code == 'epbx' and not rec.epbx_no:
                    raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
            # End : validation check

            if rec.tmp_employement_type.code == 'P' and rec.enable_payroll == 'yes' and rec.is_consolidated == False:
                rec.struct_id = self.env['hr.payroll.structure'].sudo().search([('code', '=', 'BASE')]).id
           
            # if rec.enable_payroll == 'yes':
            #     pass
                # if rec.basic_at_join_time <= 0 or rec.current_basic <= 0:
                #     raise ValidationError("Enter valid Basic amount")
                # if rec.hra <= 0:
                #     raise ValidationError("Enter valid HRA percentage")
                # if rec.conveyance <= 0:
                #     raise ValidationError("Enter valid Conveyance percentage")
                # if rec.productivity <= 0:
                #     raise ValidationError("Enter valid Productive bonus")
                # if rec.commitment <= 0:
                #     raise ValidationError("Enter valid Commitment bonus")
            # else:
                # if rec.cosolid_amnt <= 0:
                #     raise ValidationError("Enter valid Consolidate amount")
                # pass
            aadhar_num, passport_num = False, False
            for r in rec.identification_ids:
                if r.name == '5':
                    aadhar_num = r.doc_number
                elif r.name == '2':
                    passport_num = r.doc_number
                else:
                    pass
            if rec.tmp_username and rec.csm_email_id:
                user = self.env['res.users'].search(
                    ['&',
                     '|', ('login', '=', rec.tmp_username), ('email', '=', rec.csm_email_id),
                     '|', ('active', '=', True), ('active', '=', False)])
                if user:
                    if user.login == rec.tmp_username:
                        raise ValidationError(f"User {user.name} with same username already exists!")
                    elif user.email == rec.csm_email_id:
                        raise ValidationError(f"User {user.name} with same email already exists!")

            """ User to be created if Create User is checked """
            if rec.need_user and rec.tmp_username and rec.csm_email_id:
                user_vals['image'] = rec.image
                user_vals['name'] = rec.name
                user_vals['email'] = rec.csm_email_id
                user_vals['login'] = rec.tmp_username
                user_vals['branch_id'] = rec.location_id.id
                user_vals['action_id'] = int(user_action) if user_action else False
                # user_vals['new_joinee_id'] = rec.id

                ''' Passing branch_ids in res.users - Modified by Soumyajit Pan '''
                user_vals['branch_ids'] = [(6, 0, [rec.location_id.id])]
                user_vals['home_action_id'] = int(self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action'))

                new_user_rec = self.env['res.users'].sudo().create(user_vals)
                self.env.user.notify_success(message='Congrats ! User Creation completed.')

            """ Employee record to be created with all given details """
            emp = self.env['hr.employee'].search([('work_email', '=', rec.csm_email_id)])
            if emp and rec.csm_email_id != False:
                continue
                # raise ValidationError(f"Employee {emp.name} already exists!")
            else:

                emp_data = {
                    'base_branch_id': rec.location_id.id,
                    'job_branch_id': rec.tmp_worklocation_id.id,
                    'work_email': rec.csm_email_id,
                    'user_id': new_user_rec.id if rec.need_user and rec.tmp_username and rec.csm_email_id else False,
                    'image': rec.image,
                    'name': rec.name,
                    'department_id': rec.dept_name.id,
                    'division': rec.division.id,
                    'section': rec.section.id,
                    'practise': rec.practise.id,
                    'job_id': rec.job_id.id,
                    'resource_calendar_id': rec.tmp_shift.id if rec.tmp_shift else rec.tmp_worklocation_id.default_shift_id.id,
                    'birthday': rec.birthday,
                    'gender': rec.gender,
                    'marital_sts': rec.marital.id,
                    'domain_login_id': rec.domain_login_id,
                    'job_title': rec.job_id.name,
                    'grade': rec.tmp_grade.id,
                    'emp_band': rec.tmp_band.id,
                    'date_of_joining': rec.tmp_join_date,
                    'date_of_completed_probation': rec.tmp_prob_compl_date,
                    'on_probation': rec.tmp_on_probation,
                    'emp_category': rec.emp_category.id,
                    'id_card_no': rec.id_card_no.id,
                    'employement_type': rec.employement_type.id,
                    'emp_religion': rec.emp_religion.id,
                    'mother_tongue_id': rec.mother_tounge_ids.id,
                    'permanent_addr_city': rec.permanent_addr_city,
                    'parent_id': rec.tmp_admin_auth.id,
                    'coach_id': rec.tmp_func_auth.id,
                    'blood_group': rec.blood_group.id,
                    'country_id': rec.country_id.id,
                    'emp_refered': rec.tmp_source_id.id,
                    'emp_reference_walkindrive': rec.tmp_reference_walkindrive,
                    'emp_reference_print_media': rec.tmp_reference_print_media,
                    'emp_reference_job_fair': rec.tmp_reference_job_fair,
                    'emp_employee_referred': rec.tmp_employee_referred.id,
                    'emp_media_id': rec.tmp_media_id.id,
                    'emp_institute_id': rec.tmp_institute_id.id,
                    'emp_consultancy_id': rec.tmp_consultancy_id.id,
                    'emp_jportal_id': rec.tmp_jportal_id.id,
                    'emp_service_partner_id': rec.tmp_service_partner_id.id,
                    'emp_reference': rec.tmp_reference,
                    'emp_code_ref': rec.tmp_code_ref,
                    'present_addr_street': rec.present_addr_street,
                    'present_addr_street2': rec.present_addr_street2,
                    'present_addr_country_id': rec.present_addr_country_id.id,
                    'present_addr_city': rec.present_addr_city,
                    'present_addr_state_id': rec.present_addr_state_id.id,
                    'present_addr_zip': rec.present_addr_zip,
                    'same_address': rec.same_address,
                    'permanent_addr_street': rec.permanent_addr_street,
                    'permanent_addr_street2': rec.permanent_addr_street2,
                    'permanent_addr_country_id': rec.permanent_addr_country_id.id,
                    'permanent_addr_state_id': rec.permanent_addr_state_id.id,
                    'permanent_addr_zip': rec.permanent_addr_zip,
                    'biometric_id': rec.biometric_id,
                    'epbx_no': rec.epbx_no if rec.epbx_no and rec.epbx_no != False else '',
                    'domain_login_pwd': rec.domain_login_pwd,
                    'outlook_pwd': rec.outlook_pwd,
                    'mobile_phone': rec.mobile,
                    'emp_role': rec.emp_role.id,
                    'experience_sts': '2',  # to be sent experience as default -- Abhijit
                    'medical_reimb': rec.medical_reimb,
                    'transport': rec.transport,
                    'cosolid_amnt': rec.cosolid_amnt,
                    'struct_id': rec.struct_id.id if rec.struct_id else False,
                    'whatsapp_no': rec.whatsapp_no,
                    'emergency_contact': rec.emgr_contact,
                    'emergency_phone': rec.emgr_phone,
                    'emp_differently_abled': rec.appli_differently_abled,
                    'emp_blind': rec.appli_blind,
                    'emp_deaf': rec.appli_deaf,
                    'emp_dumb': rec.appli_dumb,
                    'emp_orthopedically': rec.appli_orthopedically,
                    'emp_of_disability': rec.appli_of_disability,
                    'known_language_ids': [[0, 0, {
                            'language_id': r.language_id.id,
                            'reading_status': r.reading_status,
                            'writing_status': r.writing_status,
                            'speaking_status': r.speaking_status,
                            'understanding_status': r.understanding_status,
                        }] for r in rec.known_language_ids],
                    'identification_ids': [[0, 0, {
                        'name': r.name,
                        'doc_number': r.doc_number,
                        'date_of_issue': r.date_of_issue,
                        'date_of_expiry': r.date_of_expiry,
                        'renewal_sts': r.renewal_sts,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                    }] for r in rec.identification_ids],
                    'educational_details_ids': [[0, 0, {
                        'course_type': r.course_type,
                        'course_id': r.course_id.id,
                        'stream_id': r.stream_id.id,
                        'university_name': r.university_name.id,
                        'passing_year': str(r.passing_year),
                        'division': r.division,
                        'marks_obtained': r.marks_obtained,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                        'passing_details': [(6, 0, r.passing_details.ids)],
                    }] for r in rec.educational_ids],
                    'work_experience_ids': [[0, 0, {
                        'country_id': r.country_id.id,
                        'name': r.name,
                        'designation_name': r.designation_name,
                        'organization_type': r.organization_type.id,
                        'industry_type': r.industry_type.id,
                        'effective_from': r.effective_from,
                        'effective_to': r.effective_to,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                    }] for r in rec.work_experience_ids],
                    'identification_id': aadhar_num,
                    'passport_id': passport_num,
                    'personal_email': rec.email,
                    'no_attendance': True if rec.tmp_enable_attendance == 'no' else False,
                    'attendance_mode_ids': [(6, 0, rec.atten_mode_ids.mapped('id'))] if rec.tmp_enable_attendance == 'yes' else False,
                    'wedding_anniversary': rec.wedding_anniversary,
                    'bank_account': rec.bank_account if rec.bank_account else False,
                    # 'bankaccount_id': rec.bank_id.id if rec.bankaccount_id else False,
                    'acc_branch_unit_id': rec.branch_unit_id.id if rec.branch_unit_id else False,
                    'image_url': rec.image_url,
                    'location': rec.tmp_location,
                    'wfa_city': rec.wfa_city.id,
                    'workstation_id': rec.work_station_id.id if rec.work_station_id else False,
                    # 'emp_project_id': rec.project_id.id if rec.project_id else False,
                    'client_location': rec.tmp_client_location if rec.tmp_client_location else False,
                    'start_date': rec.start_dt if rec.start_dt else False,
                    'end_date': rec.end_dt if rec.end_dt else False,
                    'direct_indirect': rec.direct_indirect,
                    'need_sync': False if rec.need_sync == False else True,
                    'infra_id': rec.infra_id.id if rec.infra_id else False,
                    'will_travel': rec.will_travel,
                    'travel_abroad': rec.travel_abroad,
                    'travel_domestic': rec.travel_domestic,
                    'linkedin_url': rec.linkedin_url,
                    'bond_required': rec.bond_required if rec.bond_required else False,
                    'bond_years': rec.bond_years if rec.bond_years else False,
                    'bond_months': rec.bond_months if rec.bond_months else False,
                    'medical_certificate': rec.medical_certificate if rec.medical_certificate else False,
                    'certificate_name': rec.certificate_name if rec.certificate_name else False,
                    'onboarding_id': rec.id,
                    'infra_unit_loc_id': rec.infra_unit_loc_id.id if rec.infra_unit_loc_id else False,
                    'sbu_master_id': rec.sbu_master_id.id if rec.sbu_master_id else False,
                    'sbu_type': rec.sbu_type,
                    'uan_id': rec.uan_id,
                    'esi_id': rec.esi_id,
                    'personal_bank_name': rec.personal_bank_name,
                    'personal_bank_account': rec.personal_bank_account,
                    'personal_bank_ifsc': rec.personal_bank_ifsc,
                    'mrf_id': rec.mrf_id.id if rec.mrf_id else False,
                    'budget_type': rec.budget_type,
                    'emp_project_id': rec.project_name_id.id if rec.project_name_id else False,
                    'personal_insurance' :rec.personal_insurance if rec.personal_insurance else False,
                    'uplod_insurance_doc': rec.uplod_insurance_doc,
                    'file_name_insurance': rec.file_name_insurance,
                    'insurance_validate_date': rec.insurance_validate_date,
                    'family_details_ids': [[0, 0,
                                            {'relationship_id': self.env['kwmaster_relationship_name'].sudo().search([('kw_id', '=', 3)], limit=1).id,
                                             'name': rec.applicant_father_name if rec.applicant_father_name else 'NA',
                                             'date_of_birth': rec.applicant_father_dob,
                                             'gender': 'M',
                                             'dependent': '2'}],
                                           [0, 0,
                                            {'relationship_id': self.env['kwmaster_relationship_name'].sudo().search([('kw_id', '=', 4)], limit=1).id,
                                             'name': rec.applicant_mother_name if rec.applicant_mother_name else 'NA',
                                             'date_of_birth': rec.applicant_mother_dob,
                                             'gender': 'F',
                                             'dependent': '2'}]]
                }
                # payroll fields
                # 'enable_payroll': rec.enable_payroll,
                # 'enable_epf': rec.enable_epf,
                # 'pf_deduction': rec.pf_deduction,
                # 'enable_gratuity': rec.enable_gratuity,
                # 'is_consolidated': rec.is_consolidated,
                # 'current_ctc': rec.current,
                # 'at_join_time_ctc': rec.tmp_at_join_time,
                # 'basic_at_join_time': rec.basic_at_join_time,
                # 'current_basic': rec.current_basic,
                # 'productivity': rec.productivity,
                # 'commitment': rec.commitment,
                # 'hra': rec.hra,
                # 'conveyance': rec.conveyance,

                offer_rec = rec.sudo().applicant_id.offer_id
                # print("offer_rec >>>>>>>>>>>> ", offer_rec)
                emp_data['enable_payroll'] = rec.enable_payroll if rec.enable_payroll else False
                if offer_rec.offer_type == 'Intern':
                    emp_data['at_join_time_ctc'] = offer_rec.first_amount if offer_rec.first_amount else False
                    emp_data['current_ctc'] = offer_rec.first_amount if offer_rec.first_amount else False
                    emp_data['basic_at_join_time'] = offer_rec.first_amount if offer_rec.first_amount else False
                    emp_data['current_basic'] = offer_rec.first_amount if offer_rec.first_amount else False
                    emp_data['is_consolidated'] = True
                    emp_data['hra'] = 0
                    emp_data['conveyance'] = 0
                    emp_data['productivity'] = 0
                    emp_data['commitment'] = 0
                    emp_data['lta_amount'] = 0
                    emp_data['pp_amount'] = 0
                    emp_data['enable_gratuity'] = 'no'
                    emp_data['enable_epf'] = 'no'
                else:
                    pfer = offer_rec.annexure_offer2.filtered(lambda x : x.per_month > 0 and x.code == 'pfer')
                    gratuity = offer_rec.annexure_offer3.filtered(lambda x : x.per_month > 0 and x.code == 'gratuity')
                    current_ctc = pfer.per_month + gratuity.per_month +  offer_rec.average_1_month
                    emp_data['at_join_time_ctc'] = current_ctc if current_ctc else False
                    emp_data['current_ctc'] = current_ctc if current_ctc else False
                
                    emp_data['is_consolidated'] = False
                    if offer_rec.avail_pf_benefit == True:
                        emp_data['enable_epf'] = 'yes'
                        emp_data['pf_deduction'] = offer_rec.pf_deduction
                    for first_line in offer_rec.annexture_offer1:
                        if first_line.code == 'basic':
                            emp_data['basic_at_join_time'] = first_line.per_month
                            emp_data['current_basic'] = first_line.per_month
                        if first_line.code == 'hra':
                            emp_data['hra'] = first_line.percentage
                        if first_line.code == 'conv':
                            emp_data['conveyance'] = first_line.percentage
                        if first_line.code == 'pb':
                            emp_data['productivity'] = first_line.per_month
                        if first_line.code == 'cb':
                            emp_data['commitment'] = first_line.per_month
                        if first_line.code == 'lta':
                            emp_data['lta_amount'] = first_line.per_month
                        if first_line.code == 'pp':
                            emp_data['pp_amount'] = first_line.per_month
                    for third_line in offer_rec.annexure_offer3:
                        if third_line.code == 'gratuity':
                            if third_line.per_month > 0:
                                emp_data['enable_gratuity'] = 'yes'
                            else:
                                emp_data['enable_gratuity'] = 'no'
                # print("emp_data >>>>>>>>>>>> ", emp_data)
                # print(a)
                new_emp_rec = self.env["hr.employee"].sudo().create(emp_data)

                # 'budget_type': rec.mrf_id.requisition_type if rec.mrf_id and rec.mrf_id.requisition_type else False,
                # 'type_of_project': rec.mrf_id.type_project if rec.mrf_id.type_project else False,
                # 'engagement': rec.mrf_id.duration,
                # 'emp_project_id': rec.mrf_id.project.id if rec.mrf_id.project else False,
                # 'emp_project_id': rec.applicant_id.mrf_project.id if rec.applicant_id.mrf_project else rec.mrf_id.project.id if rec.mrf_id.project else False,

                self.env.user.notify_success(message='Congrats ! Employee Creation completed.')

            """ Create bank account record in res.partner.bank """
            if rec.bank_account != False:
                bank_vals = {}
                bank = self.env['res.partner.bank'].sudo()
                bank_vals['acc_number'] = rec.bank_account
                bank_vals['bank_id'] = rec.bank_id.id
                bank_vals['partner_id'] = new_user_rec.partner_id.id

                bank.create(bank_vals)

            """ Create Post Onboarding Checklist """
            if rec.direct_indirect != '2':
                post_rec = self.env['kw_employee_onboarding_checklist'].sudo()
                post_rec_vals = {}

                post_rec_vals['employee_id'] = new_emp_rec.id
                post_rec_vals['image'] = rec.image
                post_rec_vals['designation_id'] = rec.job_id.id
                post_rec_vals['pf'] = rec.enable_epf if rec.enable_payroll == 'yes' else 'no'
                post_rec_vals['gratuity'] = rec.enable_gratuity if rec.enable_payroll == 'yes' else 'no'
                post_rec_vals['email_id_creation'] = 'yes' if rec.csm_email_id else 'no'
                post_rec_vals['telephone_extention'] = 'yes' if rec.epbx_no else 'no'
                post_rec_vals['id_card'] = 'no'  # 'yes' if rec.card_no.id else 'no' '''to be sent always as no Pratima'''
                post_rec_vals['location'] = rec.tmp_location
                post_rec_vals['work_station'] = 'yes'
                post_rec_vals['workstation_id'] = rec.work_station_id.id if rec.tmp_location == 'offsite' else False
                post_rec_vals['infra_id'] = rec.infra_id.id if rec.tmp_location == 'offsite' else False
                post_rec_vals['wfa_city'] = rec.wfa_city.id if rec.tmp_location == 'wfa' else False
                post_rec_vals['client_location'] = rec.tmp_client_location
                post_rec_vals['kw_id_generation'] = 'yes' if rec.need_sync == True else 'no'
                post_rec_vals['kw_profile_update'] = 'yes'

                post_rec.create(post_rec_vals)

            rec.write({'state': '5'})
        return True

    @api.multi
    def reject_enroll(self):
        for rec in self:
            rec.write({'state': '6'})
        return True

    @api.constrains('work_experience_ids', 'birthday')
    def validate_experience(self):
        if self.work_experience_ids:
            if not self.birthday:
                raise ValidationError("Please enter your date of birthday.")
            for experience in self.work_experience_ids:
                if str(experience.effective_from) < str(self.birthday):
                    raise ValidationError("Work experience date should not be less than date of birth.")
                except_experience = self.work_experience_ids - experience
                overlap_experience = except_experience.filtered(lambda r: r.effective_from <= experience.effective_from <= r.effective_to
                                                                          or r.effective_from <= experience.effective_to <= r.effective_to)
                if overlap_experience:
                    raise ValidationError(f"Overlapping experiences are not allowed.")

    @api.constrains('educational_ids')
    def validate_edu_data(self):
        if self.educational_ids and self.birthday:
            for record in self.educational_ids:
                if str(record.passing_year) < str(self.birthday):
                    raise ValidationError("Passing year should not be less than date of birth.")
        if self.educational_ids and not self.birthday:
            raise ValidationError("Please enter your date of birth.")

    @api.constrains('identification_ids')
    def validate_issue_date(self):
        if self.identification_ids and self.birthday:
            for record in self.identification_ids:
                if str(record.date_of_issue) < str(self.birthday):
                    raise ValidationError("Date of issue should not be less than date of birth.")
        if self.identification_ids and not self.birthday:
            raise ValidationError("Please enter your date of birth.")
    
    @api.onchange('domain_login_id')
    def check_domain_id(self):
        for record in self:
            if record.domain_login_id:
                emp_dom = self.env['hr.employee'].sudo().search(
                    [('domain_login_id', '=', record.domain_login_id), '|', ('active', '=', True), ('active', '=', False)])
                enroll_dom = self.env['kwonboard_enrollment'].sudo().search(
                    [('domain_login_id', '=', record.domain_login_id), '|', ('active', '=', True), ('active', '=', False)]) - self
                if enroll_dom or emp_dom:
                    raise ValidationError("This Domain ID already exists.")

    """# validate work email"""
    @api.onchange('csm_email_id')
    def check_work_email(self):
        for record in self:
            if record.csm_email_id:
                kw_validations.validate_email(record.csm_email_id)
                # emp_work_email = self.env['hr.employee'].sudo().search(
                #     [('work_email', '=', record.csm_email_id), '|', ('active', '=', True), ('active', '=', False)])
                # enroll_work_email = self.env['kwonboard_enrollment'].sudo().search(
                #     [('csm_email_id', '=', record.csm_email_id), '|', ('active', '=', True), ('active', '=', False)]) - self
                # if emp_work_email or enroll_work_email:
                #     raise ValidationError("This Outlook id already exists...")

    @api.onchange('sbu_type')
    def _onchange_sbu_type(self):
        self.sbu_master_id = False

    @api.constrains('email')
    def check_email(self):
        for record in self:
            kw_validations.validate_email(record.email)

        # records = self.env['kwonboard_enrollment'].search([]) - self
        # for info in records:
        #     if info.email == self.email:
        #         raise ValidationError("This  Email ID is already exist.")

    @api.constrains('present_addr_zip')
    def check_present_pincode(self):
        for record in self:
            if record.present_addr_zip:
                if not re.match("^[0-9]*$", str(record.present_addr_zip)) != None:
                    raise ValidationError("Present pincode is not valid")

    @api.constrains('permanent_addr_zip')
    def check_permanent_pincode(self):
        for record in self:
            if record.permanent_addr_zip:
                if not re.match("^[0-9]*$", str(record.permanent_addr_zip)) != None:
                    raise ValidationError("Permanent pincode is not valid")

    @api.constrains('mobile')
    def check_mobile(self):
        for record in self:
            if record.mobile:
                # if record.location_id.country.name != 'India':
                if not len(record.mobile) == 10:
                    raise ValidationError("Your number is invalid for: %s" % record.mobile)
                if not re.match("^[0-9]*$", str(record.mobile)) != None:
                    raise ValidationError("Your number is invalid for: %s" % record.mobile)
        # records = self.env['kwonboard_enrollment'].search([]) - self
        # for info in records:
        #     if info.mobile == self.mobile:
        #         raise ValidationError("This mobile number already exists.")

    @api.constrains('image')
    def _check_filename(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png']
        for rec in self:
            if rec.image:
                kw_validations.validate_file_mimetype(rec.image, allowed_file_list)
                kw_validations.validate_file_size(rec.image, 1)
    
    @api.constrains('medical_certificate')
    def _check_medical_certificate(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            if record.medical_certificate:
                kw_validations.validate_file_mimetype(record.medical_certificate, allowed_file_list)
                kw_validations.validate_file_size(record.medical_certificate, 4)
                
    @api.constrains('uploaded_payslip_doc1', 'uploaded_payslip_doc2', 'uploaded_payslip_doc3')
    def _check_payslip_doc(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            if record.uploaded_payslip_doc1:
                kw_validations.validate_file_mimetype(record.uploaded_payslip_doc1, allowed_file_list)
                kw_validations.validate_file_size(record.uploaded_payslip_doc1, 2)
            elif record.uploaded_payslip_doc2:
                kw_validations.validate_file_mimetype(record.uploaded_payslip_doc2, allowed_file_list)
                kw_validations.validate_file_size(record.uploaded_payslip_doc2, 2)
            elif record.uploaded_payslip_doc3:
                kw_validations.validate_file_mimetype(record.uploaded_payslip_doc3, allowed_file_list)
                kw_validations.validate_file_size(record.uploaded_payslip_doc3, 2)

    @api.constrains('wedding_anniversary', 'birthday')
    def validate_Birthdate_data(self):
        current_date = str(datetime.datetime.now().date())
        today = date.today()
        for record in self:
            if record.birthday:
                if today.year - record.birthday.year - ((today.month, today.day) < (record.birthday.month, record.birthday.day)) < 18:
                    raise ValidationError("You must be 18 years old.")
                if str(record.birthday) >= current_date:
                    raise ValidationError("The date of birth should be less than current date.")
                if record.wedding_anniversary:
                    if datetime.datetime.strptime(str(record.wedding_anniversary), '%Y-%m-%d') <= datetime.datetime.strptime(str(record.birthday), '%Y-%m-%d'):
                        raise ValidationError("Date of anniversary must be greater than birth date")

    """# method to override the create method and generate a random reference number"""
    @api.model
    def create(self, vals):
        tm = time.strftime('%Y')
        enroll_record_ids = self.search([], order='id desc', limit=1)
        last_id = enroll_record_ids.id
        reference_number = 'CSM' + tm[2:] + str(last_id + 1).zfill(4)
        # reference_msg = 'Hello ' + str(vals['name']) + ', your reference number is :' + str(reference_number) + '. Keep it for future reference. Please visit the link ' + self.env['ir.config_parameter'].sudo().get_param('web.base.url') + ' and fill up your details. '
        reference_msg = (f"Hello {str(vals['name'])}, your reference number is :{str(reference_number)}.",
                         f"Keep it for future reference.",
                         f"Please visit the link {self.env['ir.config_parameter'].sudo().get_param('web.base.url')} and fill up your details.")
        vals['reference_no'] = reference_number
        new_record = super(kwonboard_enrollment, self).create(vals)

        # Change state to profile submitted if create_full_profile is checked or employment type is indirect outsource
        if new_record.tmp_direct_indirect == '2' or new_record.create_full_profile:
            new_record.state = '2'
        # if new_record.create_uid.id == 1 and emp_id:
        #     emp = self.env['hr.employee'].sudo().browse(emp_id)
        #     email_to = emp.work_email
        # else:
        #     emp = self.env['res.users'].sudo().browse(new_record.create_uid.id)
        #     email_to = emp.email

        ir_config_params = request.env['ir.config_parameter'].sudo()
        demo_mode_config = ir_config_params.get_param('kw_onboarding.module_onboarding_mode_status') or False
        send_mail_config = ir_config_params.get_param('kw_onboarding.module_onboarding_mail_status') or False
        send_sms_config = ir_config_params.get_param('kw_onboarding.module_onboarding_sms_status') or False
        hrd_mail = ir_config_params.get_param('hrd_mail') or False
        email_fr = ir_config_params.get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        # For sending SMS
        if not demo_mode_config:
            if send_sms_config:
                template = self.env['send_sms'].sudo().search([('name', '=', 'Onboarding_SMS')])
                record_id = new_record.id
                self.env['send_sms'].send_sms(template, record_id)
        # Send email to candidate on creation if type of employment is other than Contractual Outsourced - Indirect
        if send_mail_config and new_record.tmp_direct_indirect != '2' and hrd_mail != False:
            template = self.env.ref('kw_onboarding.employee_email_template')
            mail_status = self.env['mail.template'].browse(template.id) \
                .with_context(email_from=hrd_mail,
                              email_cc=self.get_designation_cc(rec_set=new_record),
                              resp_mail=self.env['hr.employee'].sudo().browse(emp_id).work_email if emp_id != 'False' else '') \
                .send_mail(new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        if new_record:
            if vals.get('applicant_id'):
                self.env['hr.applicant'].search([('id', '=', vals.get('applicant_id'))]).write({'enrollment_id': new_record.id})
            self.env.user.notify_success(message='Enrollment created successfully.')
        if self.id_card_no:
            self.env['kw_card_master'].sudo().search([('id', '=', self.id_card_no.id)]).write({'state': 'assigned'})
        return new_record

    def button_send_invitation(self):
        self.send_invitation()

    def button_move_to_enrolled(self):
        self.state = '1'

    @api.multi
    def send_invitation(self):
        ir_config_params = request.env['ir.config_parameter'].sudo()
        send_mail_config = ir_config_params.get_param('kw_onboarding.module_onboarding_mail_status') or False
        hrd_mail = ir_config_params.get_param('hrd_mail') or False
        email_fr = ir_config_params.get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        for new_record in self:
            # print(send_mail_config, new_record, new_record.tmp_direct_indirect, hrd_mail)
            if send_mail_config and new_record.tmp_direct_indirect != '2' and hrd_mail != False:
                template = self.env.ref('kw_onboarding.employee_email_template')
                mail_status = self.env['mail.template'].browse(template.id) \
                    .with_context(email_from=hrd_mail,
                                  email_cc=self.get_designation_cc(rec_set=new_record),
                                  resp_mail=self.env['hr.employee'].sudo().browse(emp_id).work_email if emp_id != 'False' else '') \
                    .send_mail(new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    """ Overriding write method to be able to assign/un-assign card upon selection """
    @api.multi
    def write(self, values):
        rec = self.env['kwonboard_enrollment'].sudo().search([('id', '=', self.id)])
        card_no = rec.id_card_no.id
        result = super(kwonboard_enrollment, self).write(values)
        template = self.env.ref('kw_onboarding.applicant_validate_template') 
        list_data = []
        from datetime import datetime
        if  values.get('medical_doc_validate') == 'Not_validated':
            list_data.extend([{'name':'Medical','submit_date': datetime.strptime(values.get('medical_doc_not_valid_date'), '%Y-%m-%d').date(),'remark':values['medical_doc_remark']}])
        if values.get('work_ex_doc') == 'Not_validated':
            list_data.extend([{'name':'Work','submit_date': datetime.strptime(values.get('work_ex_not_valid_date'), '%Y-%m-%d').date(),'remark':values['work_ex_remark']}])
        if  values.get('edu_doc_valid') == 'Not_validated':
            list_data.extend([{'name':'Educational','submit_date':datetime.strptime(values.get('edu_doc_not_valid_date'), '%Y-%m-%d').date(),'remark':values.get('edu_remark')}])
        if  values.get('identiy_doc_valid') == 'Not_validated':
            list_data.extend([{'name':'Identity','submit_date':datetime.strptime(values.get('identiy_valid_date'), '%Y-%m-%d').date(),'remark':values['identity_remark']}])
        # print("list_data===========",list_data)
        # keys_of_first_dict = list_data[0].values()
        # print("Keys of the first dictionary:", keys_of_first_dict) 
        # if  'Medical' in keys_of_first_dict:
        #     print("yes=====================",list_data[0]['remark'])
        # print(k)
        if values.get('medical_doc_validate') == 'Not_validated' or values.get('work_ex_doc') == 'Not_validated' or values.get('edu_doc_valid') == 'Not_validated' or  values.get('identiy_doc_valid') == 'Not_validated':  
            mail_status = self.env['mail.template'].browse(template.id) \
            .with_context(email_from=self.env.user.employee_ids.work_email,list_applicant_data=list_data,email_to = self.applicant_id.email_from,email_cc=self.env.user.employee_ids.work_email) \
            .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        if 'id_card_no' in values:
            new_rec = self.env['kwonboard_enrollment'].sudo().search([('id', '=', self.id)])
            new_card_no = new_rec.id_card_no.id
            if card_no != new_card_no:
                old_card = self.env['kw_card_master'].sudo().search([('id', '=', card_no)])
                old_card.write({'state': 'unassigned', 'enrollment_id': False, 'employee_id': False})

                new_card = self.env['kw_card_master'].sudo().search([('id', '=', new_card_no)])
                new_card.write({'state': 'assigned', 'enrollment_id': rec.id, 'employee_id': False})
        self.env.user.notify_success(message='Enrollment updated successfully.')
        return result

    """ Overriding unlink method to be able to delete only records which are not approved """
    @api.multi
    def unlink(self):
        for rec in self:
            applicant= self.env['hr.applicant'].sudo().browse(rec.applicant_id.id)
            if applicant:
                if rec.state not in ['5']:
                    applicant.write({
                        'erroll_reference': '',
                        'kw_enrollment_id': False
                    })
            elif rec.state == '5':
                raise ValidationError(f'Approved record "{rec.name}" cannot be deleted!')
            result = super(kwonboard_enrollment, rec).unlink()
        return result

    @api.multi
    def home_action_scheduler(self):
        # user_action = self.env.ref('kw_hr_attendance.action_my_office_time')
        user_action = self.env['ir.config_parameter'].sudo().get_param('user_home_action', default=False)
        # user_action = int(self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action'))
        if user_action:
            query = f"UPDATE res_users SET action_id = {user_action} WHERE action_id is null;"
            self._cr.execute(query)
    @api.multi
    def applicant_upload_valid_doc(self):
        applicant_rec = self.env['kwonboard_enrollment'].sudo().search(['&', '|', '|', '|',('medical_doc_validate','=','Not_validated'),
            ('work_ex_doc','=','Not_validated'),('edu_doc_valid','=','Not_validated'),('identiy_doc_valid','=','Not_validated'),('state', 'in', ['2'])])
        today = date.today()
        template=self.env.ref('kw_onboarding.applicant_doc_validate_remainder_template')
        hr_user = self.env.ref('kw_onboarding.group_kw_onboarding_manager').users
        emails = ','.join(hr_user.mapped('employee_ids.work_email'))
        list_applicant_data =[]
        
        for rec in applicant_rec:
            # print(today + timedelta(days=2),"=====1st for===========",rec.medical_doc_not_valid_date,"===rem------------",today)
            # if (rec.medical_doc_validate == 'Not_validated' and rec.medical_doc_not_valid_date == today) or \
            #     (rec.work_ex_doc == 'Not_validated' and rec.work_ex_not_valid_date == today) or \
            #     (rec.edu_doc_valid == 'Not_validated' and rec.edu_doc_not_valid_date == today) or \
            #     (rec.identiy_doc_valid == 'Not_validated' and rec.identiy_valid_date == today) :
            #     if template:
            #         mail_status = self.env['mail.template'].browse(template.id) \
            #         .with_context(list_applicant_data=list_applicant_data,email_to = rec.applicant_id.email_from,email_cc=emails) \
            #     .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            if rec.medical_doc_validate in ['Not_validated'] and today ==  rec.medical_doc_not_valid_date - timedelta(days=1) or rec.medical_doc_not_valid_date + timedelta(days=2) == today:
                list_applicant_data.extend([{'name':'Medical',
                                    'date':rec.medical_doc_not_valid_date, 
                                    'remark':rec.medical_doc_remark}])
            if rec.work_ex_doc in ['Not_validated'] and (today == rec.work_ex_not_valid_date - timedelta(days=1) or today == rec.work_ex_not_valid_date + timedelta(days=2)):
                list_applicant_data.extend([{'name':'Work',
                                    'date':rec.work_ex_not_valid_date, 
                                    'remark':rec.work_ex_remark}]) 
            if rec.edu_doc_valid in ['Not_validated'] and (today ==  rec.edu_doc_not_valid_date - timedelta(days=1) or rec.edu_doc_not_valid_date + timedelta(days=2) == today):
                list_applicant_data.extend([{'name':'Educational',
                                    'date':rec.edu_doc_not_valid_date, 
                                    'remark':rec.edu_remark}])
            if rec.identiy_doc_valid in ['Not_validated'] and (today == rec.identiy_valid_date - timedelta(days=1) or today == rec.identiy_valid_date + timedelta(days=2)) :
                list_applicant_data.extend([{'name':'Identity',
                                    'date':rec.identiy_valid_date, 
                                    'remark':rec.identity_remark}])
            if template:
                mail_status = self.env['mail.template'].browse(template.id) \
                .with_context(list_applicant_data=list_applicant_data,email_to = rec.applicant_id.email_from,email_cc=emails) \
            .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                
    #    document download error log 

class DocumenterrorLog(models.Model):
    _name = 'onboading_document_download_log'
    _description = 'Onboarding Download Document Error log'


    onboarding_id = fields.Integer(string="Onboarding id")
    error_msg = fields.Text(string="Error message")
    applicant_id = fields.Text(string="Applicant")
    
