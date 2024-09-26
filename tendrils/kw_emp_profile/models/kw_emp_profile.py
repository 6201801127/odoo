# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
import re
from datetime import date, datetime,timedelta
from dateutil import relativedelta
from kw_utility_tools import kw_validations
from odoo import http
from math import ceil
from math import floor
from odoo.http import request
import base64
from odoo.tools.mimetypes import guess_mimetype


class EmployeeProfile(models.Model):
    _name = "kw_emp_profile"
    _description = "Employee Profile Details"
    _rec_name = "display_name"
    _order = "name asc"

    display_name = fields.Char(string="Name", default="My Profile", compute='_display_profile_check')
    name = fields.Char(string="Name")
    emp_id = fields.Many2one('hr.employee', string="Employee Id")
    emp_write_date = fields.Datetime(related='emp_id.write_date')
    employee_code = fields.Char(string='Employee Code')
    user_name = fields.Char(related='emp_id.user_id.login', string="Username")
    active_user = fields.Boolean(related='emp_id.user_id.active', string="User Name")
    digital_signature = fields.Binary(string="Digital Signature")
    job_position = fields.Char(related='emp_id.job_id.name', string='Designation')
    job_profile = fields.Char(string='Job Profile')
    country_id = fields.Many2one('res.country', string="Nationality")
    date_of_joining = fields.Date(string="Date of Joining")
    id_card_no = fields.Many2one('kw_card_master', string=u'ID Card No', size=100)
    outlook_pwd = fields.Char(string=u'Outlook Password', size=100)
    mobile_phone = fields.Char(string="Mobile No.", size=15)
    work_phone = fields.Char(string="Work Phone No", )
    work_location_id = fields.Many2one('res.partner', string="Work Location ID")
    work_location = fields.Many2one('kw_res_branch', string="Work Location", )
    work_email_id = fields.Char(string="Email", size=100)
    gender = fields.Char(string='Gender')
    image = fields.Binary(string="Upload Photo",
                          help="Only .jpeg,.png,.jpg format are allowed. Maximum file size is 1 MB")
    marital = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    marital_code = fields.Char(string=u'Marital Status Code ')
    wedding_anniversary = fields.Date(string=u'Wedding Anniversary')
    user_id = fields.Char('User')
    birthday = fields.Date(groups="base.group_user", string='Date of Birth')
    father_mother_spouse_name = fields.Char(string="Father/Mother/Spouse's Name")
    father_mother_spouse_no = fields.Char(string="Father/Mother/Spouse's Ph. No")
    personal_email = fields.Char(string='Personal Email Id ',)
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
    permanent_addr_city = fields.Char(string="Permanent Address City",  size=100)
    permanent_addr_state_id = fields.Many2one('res.country.state', string="Permanent Address State")
    permanent_addr_zip = fields.Char(string="Permanent Address ZIP", size=10)
    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    emergency_contact_name = fields.Char(string='Emergency contact person')
    emergency_address = fields.Text(string='Address')
    emergencye_telephone = fields.Char(string='Telephone(R)')
    emergency_city = fields.Char(string='City')
    emergency_country = fields.Many2one('res.country', string='Country')
    emergency_state = fields.Many2one('res.country.state', string='State')
    emergency_mobile_no = fields.Char(string='Emergency Mobile No 1')
    emergency_mobile_no_2 = fields.Char(string='Emergency Mobile No 2')
    known_language_ids = fields.One2many('kw_emp_profile_language_known', 'emp_id', string='Language Known')
    experience_sts = fields.Selection(string="Work Experience Details ",
                                      selection=[('1', 'Fresher'), ('2', 'Experience')], default="2")
    worked_country_ids = fields.Many2many(string='Countries Of Work Experience',
                                          comodel_name='res.country',
                                          relation='kw_emp_profile_country_rel',
                                          column1='profile_id', column2='country_id'
                                          )
    work_experience = fields.Char(string='Work Experience')
    technical_skill_ids = fields.One2many('kw_emp_profile_technical_skills', 'emp_id', string='Technical Skills')
    skill_ids = fields.One2many('kw_employee_profile_skills', 'profile_id', string='Skills')
    educational_details_ids = fields.One2many('kw_emp_profile_qualification', 'emp_id', string="Educational Details")
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    identification_ids = fields.One2many('kw_emp_profile_identity_docs', 'emp_id', string='Identification Documents')
    membership_assc_ids = fields.One2many('kw_emp_profile_membership_assc', 'emp_id',
                                          string='Membership Association Details')
    family_details_ids = fields.One2many('kw_emp_profile_family_info', 'emp_family_id', string="Family Info Details")
    total_experience_display = fields.Char('Total Experience', readonly=True, compute='_compute_total_experience',
                                           help="Field allowing to see the total experience in years and months depending upon joining date and experience details")
    work_experience_ids = fields.One2many('kw_emp_profile_work_experience', 'emp_id', string='Work Experience Details')

    survey_investigation = fields.Boolean(string='Survey & Investigation')
    design = fields.Boolean(string='Design')
    quality_control = fields.Boolean(string='Quality Control')
    project_work = fields.Boolean(string='Project Work')
    admin_legal_finance = fields.Boolean(string='Admin/Legal/Finance')
    research = fields.Boolean(string='Research')
    technology = fields.Boolean(string='Technology')
    # employee_id = fields.Many2one('hr.employee',string='Name',default=lambda self: self.env.user.employee_ids)
    whatsapp_no = fields.Char(string='WhatsApp No.', size=15)
    extn_no = fields.Char(string='Extn No.')
    approval_id = fields.Many2one('kw_emp_profile_new_data', string='Profile Approval Id')
    cv_approval_id = fields.Many2one('kw_emp_cv_profile', string='Profile Approval Id')
    department_name = fields.Char(related='emp_id.department_id.name', string="Department")
    division_name = fields.Char(related='emp_id.division.name', string="Division")
    section_name = fields.Char(related='emp_id.section.name', string="Section")
    practise_name = fields.Char(related='emp_id.practise.name', string="Practice")
    current_company = fields.Char(string='Current Company')
    previous_company_name = fields.Char(string="Previous Company", compute='_get_previous_company')
    telephone_r = fields.Char()
    telephone_o = fields.Char(string="Telephone(O)")
    telephone = fields.Char(string="Telephone")
    education = fields.Char(compute='_get_qualification', string='Education')
    cv_info_details_ids = fields.One2many('kw_emp_profile_cv_info', 'emp_id', string='CV Info')
    hide_edit_btn = fields.Char(compute='_get_approval_rec')
    base_branch_id = fields.Char(related='emp_id.base_branch_id.alias', string='Base Location')
    compute_branch = fields.Char(compute='_get_branch_id')
    account_info_sts = fields.Boolean(string='Account Info Boolean', default=False)
    personalinfo_sts = fields.Boolean(string='Personal Info Boolean', default=False)
    identification_sts = fields.Boolean(string='Identification Info Boolean', default=False)
    educational_sts = fields.Boolean(string='Educational Info Boolean', default=False)
    family_sts = fields.Boolean(string='Family Info Boolean', default=False)
    workinfo_sts = fields.Boolean(string='Work Info Boolean', default=False)
    cv_sts = fields.Boolean(string="CV Info Boolean", default=False)
    linkedin_url = fields.Char(string='LinkedIn Profile URL')
    grade = fields.Char(related='emp_id.grade.name', string='Grade')
    emp_band = fields.Char(related='emp_id.emp_band.name', string=u'Band')
    emp_level = fields.Char(related='emp_id.level.name', string='Level')
    parent_id = fields.Char(related='emp_id.parent_id.display_name', string=u'Administrative Authority')
    coach_id = fields.Char(related='emp_id.coach_id.name', string=u'Functional Authority')
    location = fields.Selection(related='emp_id.location', string="Onsite/Offsite/WFA", default='offsite')
    client_location = fields.Char(related='emp_id.client_location', string='Client Location')
    job_branch_id = fields.Char(related='emp_id.job_branch_id.alias', string='Work Location')
    work_station_name = fields.Char(compute='_compute_workstation', string="Work Station")
    infrastruct_name = fields.Char(compute='_compute_workstation', string="Infrastructure")
    handbook_info_details_ids = fields.One2many(related='emp_id.handbook_info_details_ids',
                                                string='Handbook Info Details')
    emp_pan_check_update = fields.Boolean(string="Update PAN", default=False)
    employee_job_description_view = fields.Html(compute='_compute_job_description', string=u'Job Description')
    emp_medical_certificate = fields.Binary(string="Upload Medical Certificate", help="Maximum file size is 1 MB")
    file_name = fields.Char("File Name", track_visibility='onchange')

    emp_education_doc = fields.One2many('kw_emp_profile_qualification', 'emp_id', related="educational_details_ids")
    emp_work_experiance_doc = fields.One2many('kw_emp_profile_work_experience', 'emp_id', related="work_experience_ids")
    emp_technical_skill_doc = fields.One2many('kw_emp_profile_technical_skills', 'emp_id',
                                              related="technical_skill_ids")
    emp_identity_doc = fields.One2many('kw_emp_profile_identity_docs', 'emp_id', related="identification_ids")
    emp_cv_doc = fields.Char(string="CV Download ")
    emp_medical_certi_doc = fields.Char(string="Medical Certificate Download")
    emp_assessment_doc = fields.Char(string="Probationary Assessment completion letter download")
    emp_probationary_id = fields.One2many('kw_profile_assessment_probatinary', 'empl_profile_id',
                                          string="Probationary Assessment")
    emp_offer_letter_doc = fields.Char(string="Offer Letter Download")
    emp_releaving_letter_doc = fields.Char(string="Releaving Letter")
    emp_resignation_reason = fields.Many2one('kw_resignation_master', string="Reason",
                                             related="emp_id.resignation_reason")
    emp_date_of_releaving = fields.Date(string="Date of Releaving", related="emp_id.last_working_day")
    emp_desg_ra_dept = fields.One2many('kw_emp_history_update', 'empl_profile_id', string="Employee Changes History")
    emp_project_ids = fields.One2many('kw_emp_profile_employee_project_data', 'emp_profile_id', string="Employee Projects")
    emp_reward_id = fields.One2many('kw_emp_reward_and_recognition', 'emp_profile_id', string='Reward')
    emp_apprisal_ids = fields.One2many('kw_emp_appraisal_profile', 'emp_profile_id', string="Appraisal")
    emp_assessment_monthly = fields.One2many('kw_profile_assessment_periodic', 'empl_profile_id')
    emp_relocate_doc = fields.Binary(string="Upload Relocate Document", help="Maximum file size is 1 MB")
    emp_declaration_epf = fields.Binary(string="Upload Declaration EPF ", help="Maximum file size is 1 MB")

    emp_id_check = fields.Boolean(string="employee check", compute="_get_emp_reward_record")

    emp_differently_abled = fields.Selection(related='emp_id.emp_differently_abled', string="Differently Abled?")
    emp_blind = fields.Boolean(related='emp_id.emp_blind', string='Blind')
    emp_deaf = fields.Boolean(related='emp_id.emp_deaf', string='Deaf')
    emp_dumb = fields.Boolean(related='emp_id.emp_dumb', string='Dumb')
    emp_orthopedically = fields.Boolean(related='emp_id.emp_orthopedically', string='Orthopedically Handicapped')
    emp_of_disability = fields.Integer(related='emp_id.emp_of_disability', string="% of Disability")
    appraisal_doc_ids = fields.One2many('appraisal_details_docs', 'profile_id', string='Appraisal Document')
    my_cdp = fields.One2many('cdp_query_views_', 'employee_profile_id',
                             domain=lambda self: [('designation_id', '=', self._get_current_user_designation_id())],
                             string="My CDP")
    # ('department', '=', self._get_current_user_department_id())
    organization_committee = fields.Char(string="Committee Members", compute="_compute_organization_committees")
    offboarding_type = fields.Many2one('kw_offboarding_type_master', compute='_compute_offboarding_type', store=True)

    counselling_ids = fields.One2many('pip_profile_views', 'employee_profile_id', string="PIP")

    posh_certificate = fields.Binary(string="POSH Certificate", attachment=True)



    @api.multi
    def posh_certificate_download(self):
        employee_data = self. env['kw_employee_posh_induction_details'].search([('emp_id', '=',self.emp_id.id),('status_induction','=','Complete')])
        if not employee_data:
            raise ValidationError("POSH Certificate is not found.")
        else:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/get-posh-certificate-employee/{self.emp_id.id}',
                'target': 'self',
            }

   
      
    @api.depends('emp_id')
    def _compute_offboarding_type(self):
        for profile in self:
            resignation = self.env['kw_resignation'].search([('applicant_id', '=', profile.emp_id.id)], limit=1, order='id desc')
            if resignation:
                profile.offboarding_type = resignation.offboarding_type.id
                
            else:
                profile.offboarding_type = False

    @api.depends('emp_id')
    def _compute_organization_committees(self):
        for record in self:
            if record.emp_id:
                employee_committees = []
                committees = self.env['organisation_committee'].search([])
                for committee in committees:
                    for member in committee.members:
                        if member.employee_id.id == record.emp_id.id:
                            employee_committees.append(committee.name)
                            break  # Exit the inner loop once the employee is found in the committee
                if employee_committees:
                    record.organization_committee = ", ".join(employee_committees)
                else:
                    record.organization_committee = "NA"
            else:
                record.organization_committee = False

    # emp_expiry_date = fields.Date(string='Expiry Date')
    @api.model
    def _get_current_user_designation_id(self):
        return self.env.user.job_id.id if self.env.user.job_id else False
    
    @api.model
    def _get_current_user_department_id(self):
        employee = self.env['hr.employee'].search([('department_id.id', '=', self.env.user.employee_ids.department_id.id)], limit=1)
        # print(employee.department_id.name,"=======employee.department_id.name===========================",employee)
        return employee.department_id.name if employee else False

    def _get_emp_reward_record(self):
        self.emp_id_check = True
        record_assessment = self.env['kw_feedback_details'].sudo().search(
            [('assessee_id', '=', self.emp_id.id), ('assessment_tagging_id.assessment_type', '=', 'probationary'),
             ('feedback_status', '=', '6')])
        # print("record_assessment======================", record_assessment, record_assessment.total_score, record_assessment.suggestion_remark)
        if record_assessment:
            self.update({'emp_assessment_score': record_assessment.total_score,
                         'remark_suggest': record_assessment.suggestion_remark})

    # @api.constrains('emp_medical_certificate')
    def _check_personal_document(self):
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        max_size = 1 * 1024 * 1024

        for record in self:
            if record.emp_medical_certificate and record.file_name:
                try:
                    file_extension = record.file_name.split('.')[-1].lower()
                    mimetype = guess_mimetype(base64.b64decode(self.documents))
                    if str(mimetype) not in allowed_extensions or file_extension not in allowed_extensions:
                        raise ValidationError("Invalid file type. Allowed types: %s" % ', '.join(allowed_extensions))

                    if len(record.emp_medical_certificate) > max_size:
                        raise ValidationError("File size exceeds the limit of 1MB.")
                except Exception as e:
                    # print('>>>>>>>> ', e)
                    pass

    def _compute_job_description(self):
        for record in self:
            if record.emp_id.sudo().mrf_id.job_role_desc:
                record.employee_job_description_view = record.emp_id.sudo().mrf_id.job_role_desc
            else:
                emp_role = self.env['hr.job.role'].sudo().search([('designations', '=', record.emp_id.job_id.id)])
                if emp_role.exists():
                    record.employee_job_description_view = emp_role.description
                else:
                    record.employee_job_description_view = 'Not Found'

    def _compute_workstation(self):
        for record in self:
            # record.work_station_name = record.emp_id.workstation_id.name
            # record.infrastruct_name = record.emp_id.infra_id.name
            ws = self.env['kw_workstation_master'].sudo().search([('employee_id', '=', record.emp_id.id)], limit=1)
            record.work_station_name = ws.name
            record.infrastruct_name = ws.infrastructure.name

    def _get_branch_id(self):
        for record in self:
            string = '|'
            space = ' '
            if record.base_branch_id.name:
                record.compute_branch = f'{space}{string}{space}{record.base_branch_id.name}{space}{string}{space}'

    def _get_approval_rec(self):
        for rec in self:
            approval_rec = self.env['kw_emp_profile_new_data'].sudo().search([('emp_prfl_id', '=', rec.id)])
            for record in approval_rec:
                if record.state == 'pending':
                    self.hide_edit_btn = 'Yes'
                else:
                    self.hide_edit_btn = 'No'

    """shows earliest previous company name"""

    @api.multi
    def _get_previous_company(self):
        for rec in self:
            dates = self.env['kwemp_work_experience'].sudo().search([('emp_id', '=', rec.emp_id.id)],
                                                                    order='effective_to desc', limit=1)
            if dates:
                rec.previous_company_name = dates.name
            else:
                rec.previous_company_name = '-NA-'

    """shows the maximum qualification based upon priority"""

    @api.depends('educational_details_ids')
    def _get_qualification(self):
        for rec in self:
            year = self.env['kwemp_educational_qualification'].sudo().search([('emp_id', '=', rec.emp_id.id)], order='passing_year desc', limit=1)
            if year:
                rec.education = self.env['kwmaster_course_name'].sudo().search([('id', '=', year.course_id.id)]).name
            else:
                rec.education = '-NA-'
        # for rec in self:
        #     course_lst = []
        #     for record in rec.educational_details_ids:
        #         for res in record.course_id:
        #             course_lst.append(res.name)
        #
        #     if 'Intermediate' in course_lst and 'Matriculation' in course_lst and 'Graduation' not in course_lst and 'Post Graduation' not in course_lst and '+2 Vocational' not in course_lst:
        #         rec.education = 'Intermediate'
        #     if 'Intermediate' not in course_lst and 'Matriculation' in course_lst and 'Graduation' not in course_lst and 'Post Graduation' not in course_lst and '+2 Vocational' not in course_lst:
        #         rec.education = 'Matriculation'
        #     if 'Intermediate' in course_lst and 'Matriculation' in course_lst and 'Graduation' in course_lst and 'Post Graduation' not in course_lst and '+2 Vocational' not in course_lst:
        #         rec.education = 'Graduation'
        #     if 'Intermediate' in course_lst and 'Matriculation' in course_lst and 'Graduation' in course_lst and 'Post Graduation' in course_lst and '+2 Vocational' not in course_lst:
        #         rec.education = 'Post Graduation'
        #     if 'Intermediate' in course_lst and 'Matriculation' in course_lst and 'Graduation' in course_lst and 'Post Graduation' in course_lst and '+2 Vocational' not in course_lst:
        #         rec.education = 'Post Graduation'
        #     if 'Intermediate' not in course_lst and 'Matriculation' in course_lst and 'Graduation' not in course_lst and 'Post Graduation' not in course_lst and '+2 Vocational' in course_lst:
        #         rec.education = '+2 Vocational'
        #     if 'Intermediate' not in course_lst and 'Matriculation' in course_lst and 'Graduation' in course_lst and 'Post Graduation' not in course_lst and '+2 Vocational' in course_lst:
        #         rec.education = 'Graduation'
        #     if 'Intermediate' not in course_lst and 'Matriculation' in course_lst and 'Graduation' in course_lst and 'Post Graduation' in course_lst and '+2 Vocational' in course_lst:
        #         rec.education = 'Post Graduation'
    Job_role_percentage = fields.Float(compute='calculate_job_role_percentage')
    emp_profiling_percentage = fields.Float(compute='calculate_emp_profiling_percentage')
    account_percentage = fields.Float(compute='calculate_accountinfo_percentage')
    identification_percentage = fields.Float(compute='calculate_total_percentage_profile', digits=(12, 0), store=True)
    personal_info_percentage = fields.Float(compute='calculate_total_percentage_profile', digits=(12, 0), store=True)
    workinfo_percentage = fields.Float(compute='calculate_total_percentage_profile', digits=(12, 0), store=True)
    familyinfo_percentage = fields.Float(compute='calculate_familyinfo_percentage')
    education_percentage = fields.Float(compute='calculate_total_percentage_profile', digits=(12, 0), store=True)
    cv_info_percentage = fields.Float(compute='calculate_total_percentage_profile', digits=(12, 0), store=True)
    organisation_policies_percentage = fields.Float(compute="calculate_organisational_policies_percentage")
    display_account_percentage = fields.Char(compute='diplay_acc_percentage')
    display_identity_percentage = fields.Char(compute='display_identity_percent')
    display_personal_percentage = fields.Char(compute='display_personal_percent')
    display_workinfo_percentage = fields.Char(compute='display_workinfo_percent')
    display_familyinfo_percentage = fields.Char(compute='display_familyinfo_percent')
    display_education_percentage = fields.Char(compute='display_education_percent')
    display_cv_percentage = fields.Char(compute='display_cv_percent')
    display_organisational_policies_percentage = fields.Char(compute="display_organisatinal_percent")
    display_Job_role_description = fields.Char(compute="display_Job_role_description_percent")
    display_profiling_rec = fields.Char(compute="profiling_document_percent")

    @api.model
    def display_organisatinal_percent(self):
        for record in self:
            percent = '%'
            record.display_organisational_policies_percentage = f'{ceil(record.organisation_policies_percentage)} {percent}'

    @api.model
    def display_Job_role_description_percent(self):
        for record in self:
            percent = '%'
            record.display_Job_role_description = f'{ceil(record.Job_role_percentage)} {percent}'

    @api.model
    def profiling_document_percent(self):
        for record in self:
            percent = '%'
            record.display_profiling_rec = f'{ceil(record.Job_role_percentage)} {percent}'

    @api.model
    def display_cv_percent(self):
        for record in self:
            percent = '%'
            record.display_cv_percentage = f'{ceil(record.cv_info_percentage)} {percent}'

    @api.model
    def display_familyinfo_percent(self):
        for record in self:
            percent = '%'
            record.display_familyinfo_percentage = f'{ceil(record.familyinfo_percentage)} {percent}'

    @api.model
    def display_education_percent(self):
        for record in self:
            percent = '%'
            record.display_education_percentage = f'{ceil(record.education_percentage)} {percent}'

    @api.model
    def display_workinfo_percent(self):
        for record in self:
            percent = '%'
            record.display_workinfo_percentage = f'{ceil(record.workinfo_percentage)} {percent}'

    @api.model
    def display_personal_percent(self):
        for record in self:
            percent = '%'
            record.display_personal_percentage = f'{ceil(record.personal_info_percentage)} {percent}'

    @api.model
    def diplay_acc_percentage(self):
        for record in self:
            percent = '%'
            # account_percent = f'({record.account_percentage})' if record.account_percentage else ''
            record.display_account_percentage = f'{ceil(record.account_percentage)} {percent}'

    @api.model
    def display_identity_percent(self):
        for record in self:
            percent = '%'
            record.display_identity_percentage = f'{ceil(record.identification_percentage)} {percent}'

    @api.model
    def hide_usermenu(self):
        # print('user id of logged in user is',type(self.env.uid))
        profile = self.env['kw_emp_profile'].sudo().search([('user_id', '=', self.env.uid)])
        if profile:
            return 1
        else:
            return 0

    @api.model
    def _display_profile_check(self):
        for record in self:
            record.display_name = 'My Profile'

    @api.model
    def remind_expiry_date(self):
        rec = self.env['kw_emp_profile_identity_docs'].sudo().search([])
        for val in rec:
            current_date = date.today()

            if val.date_of_expiry:
                pending_date = val.date_of_expiry-timedelta(days=30)
                expiry_date = val.date_of_expiry
                doc_name = dict(val._fields['name'].selection).get(val.name)

                if current_date == pending_date:
                    template = self.env.ref('kw_emp_profile.kw_emp_profile_passport_dl_expiry_email_template')
                    template.with_context(expiry_date=expiry_date, doc_name=doc_name).send_mail(val.emp_id.id,
                                                                                                notif_layout="kwantify_theme.csm_mail_notification_light")

    """scheduler for creating records from employee to profile"""
    @api.model
    def _add_employee_data(self):
        res = self.env['kw_emp_profile']
        uid = self._uid
        employees = self.env['hr.employee'].sudo().search([])
        for emp in employees:
            if emp.id:
                if emp.user_id.active == True:
                    profile_data = self.env['kw_emp_profile'].sudo().search([('emp_id', '=', emp.id)])
                    if len(profile_data) == 0:
                        country_list = []
                        for r in emp.worked_country_ids:
                            country_list.append(r.id)
                        res.create({
                            'emp_id': emp.id,
                            'linkedin_url': emp.linkedin_url if emp.linkedin_url else False,
                            'marital_code': emp.marital_code if emp.marital_code else False,
                            'wedding_anniversary': emp.wedding_anniversary if emp.wedding_anniversary else False,
                            'name': emp.name if emp.name else '',
                            'work_email_id': emp.work_email if emp.work_email else '',
                            'employee_code': emp.emp_code if emp.emp_code else '',
                            'mobile_phone': emp.mobile_phone if emp.mobile_phone else '',
                            'work_phone': emp.work_phone if emp.work_phone else '',
                            'user_id': emp.user_id.id if emp.user_id else '',
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
                            'emergency_contact_name': emp.emergency_contact if emp.emergency_contact else '',
                            'emergency_mobile_no': emp.emergency_phone if emp.emergency_phone else '',
                            'id_card_no': emp.id_card_no.id if emp.id_card_no else '',
                            'country_id': emp.country_id.id if emp.country_id else '',
                            'present_addr_street': emp.present_addr_street if emp.present_addr_street else '',
                            'present_addr_street2': emp.present_addr_street2 if emp.present_addr_street2 else '',
                            'blood_group': emp.blood_group.id if emp.blood_group else '',
                            'emp_medical_certificate':emp.medical_certificate if emp.medical_certificate else '',
                            'present_addr_country_id': emp.present_addr_country_id.id if emp.present_addr_country_id else '',
                            'present_addr_city': emp.present_addr_city if emp.present_addr_city else '',
                            'present_addr_state_id': emp.present_addr_state_id.id if emp.present_addr_state_id else '',
                            'present_addr_zip': emp.present_addr_zip if emp.present_addr_zip else '',
                            'whatsapp_no': emp.whatsapp_no if emp.whatsapp_no else '',
                            'marital': emp.marital_sts.id if emp.marital_sts else False,
                            'experience_sts': emp.experience_sts if emp.experience_sts else '',
                            'image': emp.image if emp.image else '',
                            'job_profile': emp.job_title if emp.job_title else '',
                            'extn_no': emp.epbx_no if emp.epbx_no else '',
                            'current_company': emp.company_id.name if emp.company_id else '',
                            'identification_ids': [[0, 0, {
                                'name': r.name,
                                'doc_number': r.doc_number,
                                'date_of_issue': r.date_of_issue,
                                'date_of_expiry': r.date_of_expiry,
                                'renewal_sts': r.renewal_sts,
                                'uploaded_doc': r.uploaded_doc,
                                # 'doc_file_name':r.doc_file_name,
                                'emp_document_id': r.id,
                            }]for r in emp.identification_ids] if emp.identification_ids else False,
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
                            }] for r in emp.work_experience_ids]if emp.work_experience_ids else False,
                            'membership_assc_ids': [[0, 0, {
                                'date_of_issue': r.date_of_issue,
                                'name': r.name,
                                'date_of_expiry': r.date_of_expiry,
                                'renewal_sts': r.renewal_sts,
                                'uploaded_doc': r.uploaded_doc,
                                'emp_membership_id': r.id,
                            }] for r in emp.membership_assc_ids],
                            'worked_country_ids': [[6, False, country_list]],
                            'technical_skill_ids': [[0, 0, {
                                'category_id': r.category_id.id,
                                'skill_id': r.skill_id.id,
                                'proficiency': r.proficiency,
                                'emp_technical_id': r.id,
                            }] for r in emp.technical_skill_ids]if emp.technical_skill_ids else False,
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
                                'expiry_date':r.expiry_date,
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
                        })

    """show the profile who have user_id as it is mapped in scheduler code"""

    @api.model
    def view_profile_employee(self):
        check_active_id = self.env['kw_emp_profile'].sudo().search([('user_id', '=', self.env.uid)]).id
        # check_id = self.env['kw_emp_profile'].sudo().search([('user_id', '=', False)]).id
        # menu_id=self.env['ir.ui.menu'].sudo().search([('name','=','Employee Profile')]).id
        if check_active_id:
            form_view_id = self.env.ref("kw_emp_profile.kw_employee_profile_form_view").id
            action_id = self.env.ref("kw_emp_profile.kw_emp_profile_action").id
            return [check_active_id, form_view_id, action_id]

    # def cv_info_details_ids_percentage(self):
    #     for rec in self:
    #         count = 0
    #         if rec.cv_info_details_ids:
    #             rec.cv_info_percentage = 100
    #         else:
    #             rec.cv_info_percentage = 0

    # def calculate_education_percentage(self):
    #     for rec in self:
    #         count = 0
    #         if rec.educational_details_ids:
    #             # education = rec.educational_details_ids.filtered(lambda r: r.course_type == '1')
    #             # if education:
    #             rec.education_percentage = 100
    #         else:
    #             rec.education_percentage = 0

    # def calculate_identification_percentage(self):
    #     for rec in self:
    #         count = 0
    #         if rec.identification_ids:
    #             # aadhar = rec.identification_ids.filtered(lambda r: r.name == '5')
    #             # if aadhar:
    #             # count += 1
    #             rec.identification_percentage = 100

    def calculate_familyinfo_percentage(self):
        for rec in self:
            if rec.family_details_ids:
                rec.familyinfo_percentage = 100

    def calculate_organisational_policies_percentage(self):
        for rec in self:
            if rec.handbook_info_details_ids:
                rec.organisation_policies_percentage = 100

    # def calculate_workinfo_percentage(self):
    #     for rec in self:
    #         if rec.work_experience_ids:
    #             rec.workinfo_percentage = 100

    def calculate_accountinfo_percentage(self):
        for rec in self:
            field_list = ['employee_code', 'digital_signature', 'date_of_joining', 'work_email_id', 'id_card_no', 'outlook_pwd']
            count = 0
            for data in field_list:
                if rec[data]:
                    count += 1
            rec.account_percentage = (count / len(field_list)) * 100

    def calculate_job_role_percentage(self):
        for rec in self:
            field_list = ['employee_job_description_view']
            count = 0
            for data in field_list:
                if rec[data]:
                    count += 1
            rec.Job_role_percentage = (count / len(field_list)) * 100

    # def calculate_personal_info_percentage(self):
    #     for rec in self:
    #         count = 0
    #         field_list = ['birthday', 'country_id', 'personal_email', 'marital', 'gender', 'emp_religion',
    #                       'mobile_phone', 'linkedin_url', 'blood_group']
    #         total_field_size = len(field_list)
    #         for fld in field_list:
    #             if rec[fld]:
    #                 count += 1
    #         rec.personal_info_percentage = (count / total_field_size) * 100

    profile_status = fields.Float(compute='calculate_total_percentage')
    display_total_percentage = fields.Char(compute='display_total_percent')

    def calculate_total_percentage(self):
        for rec in self:
            field_list = ['cv_info_details_ids', 'identification_ids', 'blood_group', 'family_details_ids',
                          'employee_code', 'digital_signature', 'digital_signature', 'date_of_joining', 'work_email_id',
                          'id_card_no', 'outlook_pwd', 'birthday', 'country_id', 'personal_email', 'marital', 'gender',
                          'emp_religion', 'mobile_phone', 'educational_details_ids', 'work_experience_ids', 'linkedin_url']
            count = 0
            for fld in field_list:
                if rec[fld]:
                    count += 1
            rec.profile_status = (count / len(field_list)) * 100

    @api.depends('birthday', 'country_id', 'personal_email', 'marital', 'gender', 'emp_religion', 'mobile_phone',
                 'linkedin_url', 'blood_group', 'identification_ids', 'educational_details_ids', 'work_experience_ids',
                 'cv_info_details_ids')
    def calculate_total_percentage_profile(self):
        for rec in self:
            count = 0
            field_list = ['birthday', 'country_id', 'personal_email', 'marital', 'gender', 'emp_religion',
                          'mobile_phone', 'linkedin_url', 'blood_group']
            total_field_size = len(field_list)
            for fld in field_list:
                if rec[fld]:
                    count += 1
            rec.personal_info_percentage = (count / total_field_size) * 100

            if rec.identification_ids:
                rec.identification_percentage = 100

            if rec.educational_details_ids:
                rec.education_percentage = 100
            else:
                rec.education_percentage = 0

            if rec.work_experience_ids:
                rec.workinfo_percentage = 100

            if rec.cv_info_details_ids:
                rec.cv_info_percentage = 100
            else:
                rec.cv_info_percentage = 0

    @api.model
    def display_total_percent(self):
        for record in self:
            percent = '%'
            record.display_total_percentage = f'{ceil(record.profile_status)} {percent}'

    @api.onchange('same_address')
    def _change_permanent_address(self):
        if self.same_address:
            self.permanent_addr_country_id = self.present_addr_country_id
            self.permanent_addr_street = self.present_addr_street
            self.permanent_addr_street2 = self.present_addr_street2
            self.permanent_addr_city = self.present_addr_city
            self.permanent_addr_state_id = self.present_addr_state_id
            self.permanent_addr_zip = self.present_addr_zip

    @api.onchange('present_addr_country_id')
    def _change_present_address_state(self):
        country_id = self.present_addr_country_id.id
        self.present_addr_state_id = False
        return {'domain': {'present_addr_state_id': [('country_id', '=', country_id)], }}

    @api.onchange('permanent_addr_country_id')
    def _change_permanent_address_state(self):
        country_id = self.permanent_addr_country_id.id
        if self.same_address and self.present_addr_state_id and (
                self.permanent_addr_country_id == self.present_addr_country_id):
            self.permanent_addr_state_id = self.present_addr_state_id
        else:
            self.permanent_addr_state_id = False
        return {'domain': {'permanent_addr_state_id': [('country_id', '=', country_id)], }}

    @api.onchange('emergency_country')
    def _change_emergency_address_state(self):
        country_id = self.emergency_country.id
        self.emergency_state = False
        return {'domain': {'emergency_state': [('country_id', '=', country_id)], }}

    @api.onchange('marital')
    def _compute_marital_status_code(self):
        if self.marital:
            self.marital_code = self.marital.code
        else:
            self.marital_code = ''

    @api.depends('date_of_joining', 'work_experience_ids')
    def _compute_total_experience(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.date_of_joining:
                difference = relativedelta.relativedelta(datetime.today(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months

            if rec.work_experience_ids:
                for exp_data in rec.work_experience_ids:
                    exp_difference = relativedelta.relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:
                rec.total_experience_display = " %s Years and %s Months " % (total_years, total_months)
            else:
                rec.total_experience_display = ''

    def _check_experience_date(self):
        for rec in self:
            if rec.work_experience_ids:
                for exp_data in rec.work_experience_ids:
                    if rec.date_of_joining:
                        if exp_data.effective_from > rec.date_of_joining:
                            raise ValidationError("Effective From must be less Date of Joining.")
                        if exp_data.effective_to > rec.date_of_joining:
                            raise ValidationError("Effective To must be less Date of Joining.")

    @api.constrains('wedding_anniversary', 'birthday')
    def validate_Birthdate_data(self):
        current_date = str(datetime.now().date())
        today = date.today()
        for record in self:
            if record.birthday:
                if today.year - record.birthday.year - (
                        (today.month, today.day) < (record.birthday.month, record.birthday.day)) < 18:
                    raise ValidationError("You must be 18 years old.")
                if record.wedding_anniversary:
                    if str(record.wedding_anniversary) <= str(record.birthday):
                        raise ValidationError("Wedding Anniversary date should not be less than birth date.")
            if record.birthday:
                if str(record.birthday) >= current_date:
                    raise ValidationError("The date of birth should be less than current date.")

    @api.constrains('work_email_id')
    def check_work_email(self):
        for record in self:
            kw_validations.validate_email(record.work_email_id)
            # if record.work_email_id:
            #     records = self.env['kw_emp_profile'].search([('work_email_id', '=', record.work_email_id)]) - self
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
                overlap_experience = except_experience.filtered(
                    lambda r: r.effective_from <= experience.effective_from <= r.effective_to or r.effective_from <= experience.effective_to <= r.effective_to )
                if overlap_experience:
                    raise ValidationError("Overlapping experiences are not allowed.")

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

    @api.constrains('identification_ids')
    def validate_issue_date(self):
        if self.identification_ids and self.birthday:
            for record in self.identification_ids:
                if str(record.date_of_issue) < str(self.birthday):
                    raise ValidationError("Date of issue should not be less than date of birth.")

    # @api.constrains('mobile_phone')
    # def check_mobile(self):
    #     for record in self:
    #         if record.mobile_phone:
    #             if not len(record.mobile_phone) == 10:
    #                 raise ValidationError("Your mobile number is invalid for: %s" % record.mobile_phone)
    #             elif not re.match("^[0-9]*$", str(record.mobile_phone)) != None:
    #                 raise ValidationError("Your mobile number is invalid for: %s" % record.mobile_phone)

    # @api.constrains('work_phone')
    # def check_phone(self):
    #     for record in self:
    #         if record.work_phone:
    #             if len(record.work_phone) <= 18:
    #                 raise ValidationError("Your work phone no is invalid for: %s" % record.work_phone)
    #             elif re.match("-^(\+?[\d ])+$",str(record.work_phone)) == None:
    #                 raise ValidationError("Your work phone no is invalid for: %s" % record.work_phone)

    @api.constrains('emergency_mobile_no', 'emergency_mobile_no_2')
    def check_emergency_phone(self):
        for record in self:
            if record.emergency_mobile_no:
                if not (record.emergency_mobile_no.isdigit()):
                    raise ValidationError("Invalid emergency phone no: %s" % record.emergency_mobile_no)
                
            if record.emergency_mobile_no_2:
                if not (record.emergency_mobile_no_2.isdigit()):
                    raise ValidationError("Invalid emergency phone no: %s" % record.emergency_mobile_no_2)

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

    def write(self, vals):
        old_lang_ids = []
        # --------------Assigning Old Value------------
        # old_state = self.state
        old_email_id = self.work_email_id
        old_date_of_joining = self.date_of_joining
        old_birthday = self.birthday
        old_work_phone = self.work_phone
        old_whatsapp_no = self.whatsapp_no
        old_extn_no = self.extn_no
        old_user_name = self.user_name
        old_digital_signature = self.digital_signature
        # old_id_card_no = self.id_card_no
        old_outlook_pwd = self.outlook_pwd
        old_country_id = self.country_id.id
        old_personal_email = self.personal_email
        old_marital = self.marital.id
        old_marital_code = self.marital_code
        old_wedding_anniversary = self.wedding_anniversary
        old_emp_religion = self.emp_religion.id
        old_mobile_phone = self.mobile_phone
        old_present_addr_street = self.present_addr_street
        old_present_addr_country_id = self.present_addr_country_id.id
        old_present_addr_city = self.present_addr_city
        old_present_addr_state_id = self.present_addr_state_id.id
        old_present_addr_zip = self.present_addr_zip
        old_same_address = self.same_address
        old_permanent_addr_country_id = self.permanent_addr_country_id.id
        old_permanent_addr_street = self.permanent_addr_street
        old_permanent_addr_city = self.permanent_addr_city
        old_permanent_addr_state_id = self.permanent_addr_state_id.id
        old_permanent_addr_zip = self.permanent_addr_zip
        old_emergency_contact_name = self.emergency_contact_name
        old_emergency_address = self.emergency_address
        old_emergencye_telephone = self.emergencye_telephone
        old_emergency_city = self.emergency_city
        old_emergency_country = self.emergency_country.id
        old_emergency_state = self.emergency_state.id
        old_emergency_mobile_no = self.emergency_mobile_no
        old_emergency_mobile_no_2 = self.emergency_mobile_no_2
        old_name = self.name
        old_user_id = self.user_id
        old_permanent_addr_street = self.permanent_addr_street
        old_blood_group = self.blood_group.id
        old_experience_sts = self.experience_sts
        old_worked_country_ids = self.worked_country_ids.ids
        old_present_addr_street2 = self.present_addr_street2
        old_permanent_addr_street2 = self.permanent_addr_street2
        old_linkedin_url = self.linkedin_url
        old_medical_cert = self.emp_medical_certificate

        technical = 0
        family = 0
        identity = 0
        education = 0
        work = 0
        membership = 0
        language = 0
        cv_info = 0
        personal_info_not_reqd_fields = ['father_mother_spouse_name','father_mother_spouse_no','telephone_r','telephone_o','telephone','emp_relocate_doc','emp_declaration_epf','employee_nps_id']

        emp_rec = super(EmployeeProfile, self).write(vals)

        if 'cv_info_details_ids' in vals:
            cv_info = 1
        if 'family_details_ids' in vals:
            family = 1
        if 'technical_skill_ids' in vals:
            technical = 1
        if 'work_experience_ids' in vals:
            work = 1
        if 'educational_details_ids' in vals:
            education = 1
        if 'membership_assc_ids' in vals:
            membership = 1
        if 'identification_ids' in vals:
            identity = 1
        if 'known_language_ids' in vals:
            language = 1

        emp_prfl_aprv = self.env['kw_emp_profile_new_data']
        emp_cv_approv = self.env['kw_emp_cv_profile']
        matching_keys_count = sum(1 for key in vals if key in personal_info_not_reqd_fields)

        if self.write_uid.id != 1 and self.user_id :
            if cv_info == 1:
                emp_cv_approv.create({'emp_cv_prfl_id' : self.id,'emp_id':self.emp_id.id,
                                'cv_info_boolean': True if cv_info == 1 else False ,'work_email_id': old_email_id, 'name': old_name,})
            if ((len(vals) > 1 and not 'cv_info_details_ids' in vals) or (len(vals) > 1 and 'cv_info_details_ids' in vals) or (len(vals) == 1 and not 'cv_info_details_ids' in vals)) and (len(vals) > matching_keys_count) :
                aprv_record = emp_prfl_aprv.create({
                'emp_prfl_id': self.id,
                'technical_skill_ids_boolean': True if technical == 1 else False,
                'known_language_ids_boolean': True if language == 1 else False,
                'educational_details_ids_boolean': True if education == 1 else False,
                'work_experience_ids_boolean': True if work == 1 else False,
                'family_details_ids_boolean': True if family == 1 else False,
                'identification_ids_boolean': True if identity == 1 else False,
                'membership_assc_ids_boolean': True if membership == 1 else False,
                # 'cv_info_boolean': True if cv_info == 1 else False,
                'linkedin_url': old_linkedin_url,
                'new_linkedin_url': vals['linkedin_url'] if 'linkedin_url' in vals else '',
                'medical_certificate':old_medical_cert,
                'upload_medical_certificate': vals['emp_medical_certificate'] if 'emp_medical_certificate' in vals else '',
                'permanent_addr_street2': old_permanent_addr_street2,
                'new_permanent_addr_street2': vals['permanent_addr_street2'] if 'permanent_addr_street2' in vals else '',
                'present_addr_street2': old_present_addr_street2,
                'new_present_addr_street2': vals['present_addr_street2'] if 'present_addr_street2' in vals else '',
                'blood_group': old_blood_group,
                'new_blood_group': vals['blood_group'] if 'blood_group' in vals else '',
                'permanent_addr_street': old_permanent_addr_street,
                'new_permanent_addr_street': vals['permanent_addr_street'] if 'permanent_addr_street' in vals else '',
                'user_id': old_user_id,
                'new_user_id': vals['user_id'] if 'user_id' in vals else '',
                'name': old_name,
                'new_name': vals['name'] if 'name' in vals else '',
                'emergency_contact_name': old_emergency_contact_name,
                'new_emergency_contact_name': vals['emergency_contact_name'] if 'emergency_contact_name' in vals else '',
                'emergency_address': old_emergency_address,
                'new_emergency_address': vals['emergency_address'] if 'emergency_address' in vals else '',
                'emergencye_telephone': old_emergencye_telephone,
                'new_emergencye_telephone': vals['emergencye_telephone'] if 'emergencye_telephone' in vals else '',
                'emergency_city': old_emergency_city,
                'new_emergency_city': vals['emergency_city'] if 'emergency_city' in vals else '',
                'emergency_country': old_emergency_country,
                'new_emergency_country': vals['emergency_country'] if 'emergency_country' in vals else '',
                'emergency_state': old_emergency_state,
                'new_emergency_state': vals['emergency_state'] if 'emergency_state' in vals else '',
                'emergency_mobile_no': old_emergency_mobile_no,
                'emergency_mobile_no_2': old_emergency_mobile_no_2,
                'new_emergency_mobile_no': vals['emergency_mobile_no'] if 'emergency_mobile_no' in vals else '',
                'new_emergency_mobile_no_2': vals['emergency_mobile_no_2'] if 'emergency_mobile_no_2' in vals else '',
                'permanent_addr_zip': old_permanent_addr_zip,
                'new_permanent_addr_zip': vals['permanent_addr_zip'] if 'permanent_addr_zip' in vals else '',
                'permanent_addr_state_id': old_permanent_addr_state_id,
                'new_permanent_addr_state_id': vals['permanent_addr_state_id'] if 'permanent_addr_state_id' in vals else '',
                'permanent_addr_city': old_permanent_addr_city,
                'new_permanent_addr_city': vals['permanent_addr_city'] if 'permanent_addr_city' in vals else '',
                'permanent_addr_country_id': old_permanent_addr_country_id,
                'new_permanent_addr_country_id': vals['permanent_addr_country_id'] if 'permanent_addr_country_id' in vals else '',
                'same_address': old_same_address,
                'new_same_address': vals['same_address'] if 'same_address' in vals else '',
                'present_addr_zip': old_present_addr_zip,
                'new_present_addr_zip': vals['present_addr_zip'] if 'present_addr_zip' in vals else '',
                'present_addr_state_id': old_present_addr_state_id,
                'new_present_addr_state_id': vals['present_addr_state_id'] if 'present_addr_state_id' in vals else '',
                'present_addr_city': old_present_addr_city,
                'new_present_addr_city': vals['present_addr_city'] if 'present_addr_city' in vals else '',
                'present_addr_country_id': old_present_addr_country_id,
                'new_present_addr_country_id': vals['present_addr_country_id'] if 'present_addr_country_id' in vals else '',
                'present_addr_street': old_present_addr_street,
                'new_present_addr_street': vals['present_addr_street'] if 'present_addr_street' in vals else '',
                'mobile_phone': old_mobile_phone,
                'new_mobile_phone': vals['mobile_phone'] if 'mobile_phone' in vals else '',
                'emp_religion': old_emp_religion,
                'new_emp_religion': vals['emp_religion'] if 'emp_religion' in vals else '',
                'wedding_anniversary': old_wedding_anniversary,
                'new_wedding_anniversary': vals['wedding_anniversary'] if 'wedding_anniversary' in vals else False,
                'marital_code': old_marital_code,
                'new_marital_code': vals['marital_code'] if 'marital_code' in vals else '',
                'marital': old_marital,
                'new_marital': vals['marital'] if 'marital' in vals else '',
                'personal_email': old_personal_email,
                'new_personal_email': vals['personal_email'] if 'personal_email' in vals else '',
                'work_email_id': old_email_id,
                'new_work_email_id': vals['work_email_id'] if 'work_email_id' in vals else '',
                'date_of_joining': old_date_of_joining,
                'new_date_of_joining': vals['date_of_joining'] if 'date_of_joining' in vals else False,
                'birthday': old_birthday,
                'new_birthday': vals['birthday'] if 'birthday' in vals else False,
                'work_phone': old_work_phone,
                'new_work_phone': vals['work_phone'] if 'work_phone' in vals else '',
                'whatsapp_no': old_whatsapp_no,
                'new_whatsapp_no': vals['whatsapp_no'] if 'whatsapp_no' in vals else '',
                'extn_no': old_extn_no,
                'new_extn_no': vals['extn_no'] if 'extn_no' in vals else '',
                'user_name': old_user_name,
                'new_user_name': vals['user_name'] if 'user_name' in vals else '',
                'digital_signature': old_digital_signature,
                'new_digital_signature': vals['digital_signature'] if 'digital_signature' in vals else '',
                'outlook_pwd': old_outlook_pwd,
                'new_outlook_pwd': vals['outlook_pwd'] if 'outlook_pwd' in vals else '',
                'country_id': old_country_id,
                'new_country_id': vals['country_id'] if 'country_id' in vals else '',
                'experience_sts': old_experience_sts,
                'new_experience_sts': vals['experience_sts'] if 'experience_sts' in vals else '',
                'worked_country_ids': [(6, 0, old_worked_country_ids)],
                'new_worked_country_ids': vals['worked_country_ids'] if 'worked_country_ids' in vals else '',
            })
            return emp_rec

    def button_view_profile(self):
        check_active_id = self.env['kw_emp_profile'].sudo().search([('user_id', '=', self.env.uid)])
        if check_active_id:
            form_view_id = self.env.ref("kw_emp_profile.view_profile_view_form").id
            return {
                'name': 'Profile Information',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_emp_profile',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': check_active_id.id,
                'view_id': form_view_id,
                'target': 'new',
                "domain": [('user_id', '!=', self.env.uid)],
            }
        else:
            pass

    @api.model
    def _get_employee_pan_url(self, user_id):
        emp_pan_url = f"/get-pan-update-of-employee"
        # print("self record=================",self.txtPAN)
        return emp_pan_url

    @api.multi
    def action_download_employee_file(self):
        for rec in self:
            if self._context.get('button') == 'CV':
                if not rec.emp_id.onboarding_id:
                    raise ValidationError("Documents not found")
                else:
                    return {
                        'type': 'ir.actions.act_url',
                        'url': f'/download_emp_cv_update_doc/{rec.emp_id.id}',
                        'target': 'self',
                    }
            elif self._context.get('button') == 'Medical':
                if not rec.emp_id.onboarding_id:
                    raise ValidationError("Documents not found")
                else:
                    return {
                        'type': 'ir.actions.act_url',
                        'url': f'/download_emp_medical_update_doc/{rec.emp_id.id}',
                        'target': 'self',
                    }
            elif self._context.get('button') == 'Offer':
                if not rec.emp_id.onboarding_id:
                    raise ValidationError("Documents not found")
                else:
                    return {
                        'type': 'ir.actions.act_url',
                        'url': f'/download_emp_offer_update_doc/{rec.emp_id.id}',
                        'target': 'self',
                    }

            elif self._context.get('button') == 'Releaving':
                exit_data = request.env['kw_resignation_experience_letter'].sudo().search(
                                            [('employee_id', '=', rec.emp_id.id)], limit=1)
                if not exit_data:
                    raise ValidationError("Documents not found")
                else:
                    return {
                        'type': 'ir.actions.act_url',
                        'url': f'/download_emp_exit_update_doc/{rec.emp_id.id}',
                        'target': 'self',
                    }


class pipempprofile(models.Model):
    _name = 'pip_profile_views'
    _description = 'PIP Query View'
    _auto = False

    reference = fields.Char(string="Reference")
    pp_id = fields.Many2one('performance_improvement_plan')
    raise_by_emp = fields.Many2one('hr.employee', string="Raised By")
    suggestion_pm = fields.Selection(string='Suggestion', selection=[('move_to_pip', 'Move to PIP'),
                                                                     ('discuss', 'Discussion with higher authority (SBU/Reviewer)')], )
    reason = fields.Char(string="Reason")
    employee_profile_id = fields.Many2one('kw_emp_profile')
    remark_pm_rev = fields.Char('Remarks(PM/Div.head)')
    pip_status = fields.Char(string="Status")
    final_decision = fields.Char(string="Final Decision")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT
                    pec.id AS id,   
                    pec.reference AS reference,
                    pec.pp_id AS pp_id,
                    pec.raise_by_emp AS raise_by_emp,
                    pec.suggestion_pm AS suggestion_pm,
                    pec.reason AS reason,
                    pec.remark_pm_rev as remark_pm_rev,
                    pec.status as pip_status,
                    pec.final_decision as final_decision,
                   ep.id AS employee_profile_id
                FROM
                    pip_hr_employee_counselling AS pec
                LEFT JOIN
                    kw_emp_profile ep ON pec.emp_id = ep.emp_id

            )
        """
        self.env.cr.execute(query)
