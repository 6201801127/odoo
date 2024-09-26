# -*- coding: utf-8 -*-
from ast import literal_eval
import re
import os
import shutil
import base64
from os import system
from PyPDF2 import PdfFileMerger
from mimetypes import guess_extension
from odoo import fields, models, api, _,SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations
from odoo.tools.mimetypes import guess_mimetype
from datetime import datetime, timezone, timedelta, time, date
from dateutil.relativedelta import relativedelta
import requests, json
import logging


_logger = logging.getLogger(__name__)



class HrApplicantStage(models.Model):
    _name = 'hr.applicant.stage'
    _description = "Applicant Stages"

    from_stage = fields.Many2one('hr.recruitment.stage', string='From')
    to_stage = fields.Many2one('hr.recruitment.stage', string='To')
    employee_id = fields.Many2one('res.users', string='Employee')
    applicant_id = fields.Many2one('hr.applicant', string='Applicant')
    date = fields.Date('Date')


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    code = fields.Char('Code')


class ScreeningReminderLog(models.Model):
    _name = 'screening_reminder_log'
    _description = "Applicants"

    # panel_members_id = fields.Many2one('hr.employee')    
    # applicants = fields.Text(string='Applicants')
    schedule_date = fields.Datetime(string="Date")
    payload = fields.Text(string="Payload")
    status = fields.Text(string="Status")


class kw_applicant_generated_Otp(models.Model):
    _name = "kw_applicant_generate_otp"
    _description = "CSM Technologies"

    applicant_id = fields.Many2one('hr_applicant', string="Applicant")
    mobile_no = fields.Char(string="Mobile Number")
    otp = fields.Char(string="One time password(OTP)")
    exp_date_time = fields.Datetime(string="Expiry Datetime")

    @api.model
    def create(self, vals):
        new_record = super(kw_applicant_generated_Otp, self).create(vals)
        return new_record

    @api.multi
    def write(self, vals):
        # self.ensure_one()  
        existing_record = super(kw_applicant_generated_Otp, self).write(vals)
        return existing_record


class HrApplicant(models.Model):
    _inherit = "hr.applicant"
    _rec_name = "name"
    _order = "id desc"

    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        if self.job_id:
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self.job_id.id),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        return False

    def _get_years(self):
        return [(i, str(i)) for i in range(1, 6)]

    @api.multi
    @api.depends('job_position')
    def _check_is_screening_enabled(self):
        for record in self:
            # print(f"record.job_position.enable_applicant_screening > {record.job_position.enable_applicant_screening} > {record.stage_id.code}")
            if (record.job_position.enable_applicant_screening and record.stage_id.code == 'IQ') \
                    or record.panel_member_id != False:
                # print("record.panel_member==================",record.panel_member_id)
                record.is_screening_enabled = True
            else:
                record.is_screening_enabled = False

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee

    @api.model
    def _get_domain(self):
        domain = [('id', '=', 0)]
        if self._context.get('panel_member_data'):
            domain = [('id', 'in', self._context.get('panel_member_data'))]
        elif self._context.get('recruitment_job_id'):
            panel = self.env['kw_hr_job_positions'].sudo().browse(self._context.get('recruitment_job_id'))
            if panel and panel.panel_member:
                panel_member_data = panel.panel_member.ids
                domain = [('id', 'in', panel_member_data)]
        return domain

    """# #----------- Modified fields----------------"""
    otp_number = fields.Char()
    generate_time = fields.Datetime(string="Expire Datetime")
    edu_data_ids = fields.One2many('hr_applicant_edu_qualification', 'applicant_id', string="Educational Details")
    experience_sts = fields.Selection(string="Work Experience ", selection=[('1', 'Fresher'), ('2', 'Experience')], )
    work_experience_ids = fields.One2many('hr_applicant_work_experience', 'applicant_id', string='Work Experience Details')
    submit_edu_work = fields.Boolean('Submit', default=False)
    
    name = fields.Char("Subject / Application Name", required=False, index=True)
    partner_name = fields.Char("Applicant's Name", required=True, index=True)
    partner_phone = fields.Char("Phone", size=15)
    partner_mobile = fields.Char("Mobile", size=15, required=False)
    email_from = fields.Char("Email", size=128, help="These people will receive email.", required=False)
    job_position = fields.Many2one('kw_hr_job_positions', "Job Position", required=True)
    job_code = fields.Char('Job Code', related="job_position.job_code", copy=False)
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)
    job_location_id = fields.Many2one('kw_recruitment_location', string="Job Location")
    """# #----------- Modified fields----------------"""

    """# #-----------Additional Fields--------------"""

    erroll_reference = fields.Char("Reference Number")
    experience = fields.Char("Experience")
    exp_year = fields.Integer(string="Year(s)", required=False)
    exp_month = fields.Integer(string="Month(s)", required=False)
    relevant_exp_year = fields.Integer(string="Year(s)", required=False)
    relevant_exp_month = fields.Integer(string="Month(s)", required=False)

    qualification = fields.Many2one("kw_qualification_master", "Qualification OLD", groups="base.group_no_one")
    qualification_ids = fields.Many2many("kw_qualification_master", string="Qualification")
    # highest_qualification_ids = fields.Many2many("kwemp_educational_qualification", string="Qualification")
    meeting_count = fields.Integer(compute='_compute_meeting_count', help='Meeting Count')
    applicant_feedback_url = fields.Char('Applicant Feedback URL')
    applicant_response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    applicant_response_state = fields.Selection(related="applicant_response_id.state",
                                                string="Applicant Feedback Stage", store=True)
    # title = fields.Char(string='Job Title')
    other_qualification = fields.Char("Other Qualification", )
    other_position = fields.Char("Other", )
    current_location = fields.Char("Current Location", )
    relevant_job = fields.Many2one('hr.job', string='Profile Relevant For', )

    """these fields are not in use any more. in view fields have invisible attribute
      changes added on 4-Feb-2020 by Avinas as per feedback of HR"""
    hiring_type = fields.Many2one('kwemp_employment_type', string='Hiring Type', )
    employee_type = fields.Selection(string='Employee Type', selection=[('new', 'New'), ('replacement', 'Replacement')],
                                     default='new', help="Set recruitment process is employee type.")
    employee_id = fields.Many2one('hr.employee', string='Replacement for', )
    # employee_id = fields.Char(string="Employee ID", )

    budget_from_date = fields.Date('From Date', default=fields.Date.context_today)
    budget_to_date = fields.Date('To Date', default=fields.Date.context_today)

    """# [Modification on 04-June-2020 (SALMA)]"""
    certification = fields.Char('Certification')
    current_ctc = fields.Float('Current CTC(Annum)')
    notice_period = fields.Integer('Notice Period')

    """referred by fields"""
    employee_referred = fields.Many2one('hr.employee', string='Referred By')
    service_partner_id = fields.Many2one('res.partner', string='Partner')
    media_id = fields.Many2one('kw.social.media', string='Social Media')
    institute_id = fields.Many2one('res.partner', string='Institute')
    registration_number = fields.Char("Registration Number")
    consultancy_id = fields.Many2one('res.partner', string='Consultancy')
    jportal_id = fields.Many2one('kw.job.portal', string='Job Portal')
    reference = fields.Char("Client Name")
    reference_walkindrive = fields.Char("Walk-in Drive")
    reference_print_media = fields.Char("Print Media")
    reference_job_fair = fields.Char("Job Fair")
    code_ref = fields.Char('Code')

    user_id = fields.Many2one('res.users', "Responsible")
    responsible_id = fields.Many2one("res.users", string="HR Responsible", default=lambda self: int(
        self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.user_id')))
    # duration = fields.Char("Duration")

    """# #-----------Additional Fields for report--------------"""
    gender = fields.Selection(string='Gender',
                              selection=[('male', 'Male'), ('female', 'Female'), ('others', 'Others'), ],
                              required=False)
    date_of_requisition = fields.Many2one('kw_recruitment_requisition', "date_requisition")
    requisition_date = fields.Date(string='requisition_date', related='date_of_requisition.date_requisition',
                                   readonly=True, store=True)

    date_of_offer = fields.Date(string='Date of Offer', default=fields.Date.context_today)
    evaluators = fields.Text(string='Evaluators', compute="_compute_evaluators")
    time_hire = fields.Date(string='Time to Hire')
    time_fill = fields.Date(string='Time to Fill')
    salary_replaced = fields.Text(string='Salary of Replaced')
    project_name = fields.Many2one('project.project', string='Project Name')
    project_pm = fields.Text(string='PM/PL/TL')

    source_id = fields.Many2one('utm.source', required=False, domain=[('source_type', '=', 'recruitment')])
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Section")
    practise = fields.Many2one('hr.department', string="Practise")
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', ondelete='restrict', track_visibility='onchange',
                               domain="['|', ('job_id', '=', False), ('job_id', '=', job_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    stage_code = fields.Char(string="Code", related='stage_id.code', store=True)
    experience_ids = fields.One2many('kw_recruitment_experience', 'applicant_id', string="Experiences")
    skill_ids = fields.Many2many("kw_skill_master", string="Technical Skills")

    """walk-in info"""
    info_source_id = fields.Selection(selection=[('csm_website', 'CSM Website'),
                                                 ('linked_in', 'Linkedin'),
                                                 ('facebook', 'Facebook'),
                                                 ('twitter', 'Twitter'),
                                                 ('google_advt', 'Google Advt'),
                                                 ('newspaper', 'News Paper'),
                                                 ('csm_employee', 'CSM Employee'),
                                                 ('others', 'Others')
                                                 ], string="Source Of Info")
    other_info = fields.Char(string="Other Source", )
    walkin_employee_reference = fields.Char(string="CSM Employee", )

    mode_of_interview = fields.Selection(string='Mode Of Interview',
                                         selection=[('zoom', 'Zoom VC'), ('telephonic', 'Telephonic')])

    uni_regd_no = fields.Char('University Regd No.')
    shortlist_date = fields.Date('Shortlist Date')
    offer_date = fields.Date('Offer Date')
    acceptance_date = fields.Date('Acceptance Date')
    hire_date = fields.Date('Hire Date')
    joining_date = fields.Date('Joining Date')
    interview_status = fields.Char('Interview Status')
    round_type = fields.Char('Round Type')
    interview_date = fields.Date('Interview Date')
    applicant_stage_ids = fields.One2many('hr.applicant.stage', 'applicant_id', string="Stages")
    kanban_state = fields.Selection([('normal', 'Grey'),
                                     ('done', 'Green'),
                                     ('blocked', 'Red')], string='Kanban State',
                                    copy=False, default='normal', required=True, track_visibility='onchange', )
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='Manpower Requisition',
                             domain=[('state', 'in', ['approve'])])
    profile_submit_date = fields.Date('Profile Submit Date')

    bond_required = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Bond Required", default='0')

    hr_discussion_mail = fields.Selection([('1', 'Yes'), ('0', 'No')], string="HR Discuss Mail Sent?", default='0')
    hr_discussion_status = fields.Selection([('approved','Approved'),('rejected','Rejected')], string="HR Discussion Form")

    bond_years = fields.Selection([(i, str(i)) for i in range(0, 11)], string='Bond Year(s)')
    bond_months = fields.Selection([(i, str(i)) for i in range(0, 12)], string='Bond Month(s)')
    
    # Additional MRF Fields value Modified By:Chandrasekhar
    project_type = fields.Selection(string='Type Of Project',
                                    selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')], default='work',
                                    help="Set recruitment process is work order.", related="mrf_id.type_project",
                                    readony=True, )
    mrf_project = fields.Many2one('crm.lead', string='Project', related="mrf_id.project", readony=True, )
    mrf_min_sal = fields.Integer(string='Min. Salary per month', related="mrf_id.min_sal", readony=True, )
    mrf_max_sal = fields.Integer(string='Max. Salary per month', related="mrf_id.max_sal", readony=True, )
    mrf_type_employment = fields.Many2one('kwemp_employment_type', string='Type of Employment',
                                          related="mrf_id.type_employment", readony=True, )
    mrf_role_id = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role",
                                  related="mrf_id.role_id", readony=True, )
    mrf_categ_id = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category",
                                   related="mrf_id.categ_id", readony=True, )
    budget_amount = fields.Integer(string='Budget Amount')

    budget_type = fields.Selection(string='Budget', selection=[('treasury', 'Treasury'), ('project', 'Project')],
                                   default='treasury', help="Set recruitment process is employee budget.")
    requisition_type = fields.Selection(string='Budget Type',
                                        selection=[('treasury', 'Treasury Budget'), ('project', 'Project Budget')],
                                        related="mrf_id.requisition_type")
    mrf_duration = fields.Integer('Engagement Period (Months)', related="mrf_id.duration", readony=True, )

    budget_updation_status = fields.Boolean(string="Active", default=False)
    is_finance_approved = fields.Boolean(string="Active", default=False)
    offer_count = fields.Integer('Offer Count')
    offer_id = fields.Many2one('hr.applicant.offer', string="Offer Letter", compute="get_odder_letter")

    cv_skill = fields.Many2many("cv_skill_master", string='CV Skills')
    cv_qualification = fields.Many2one('cv_qualification_master', string="CV Qualification")

    is_account = fields.Boolean(string="Is Account User", compute="_compute_budget_amount", default=False)

    referred_amount = fields.Float(string='Referral Amount', related='job_position.referred_amount')
    candidate_relation = fields.Selection([('1', 'Family'), ('2', 'Friend'), ('3', 'Ex Colleague'), ('4', 'Others')],
                                          string='Reference Source')
    candidate_info = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                      string='Are you aware of any suspicious processing, police investigations or disciplinary actions against the applicant?')
    candidate_relation_info = fields.Char(string='If others, please specify')
    mention_details = fields.Char("Please mention the details")
    is_referred = fields.Boolean(string="Is Referred", compute="_compute_is_referred", default=False)
    monthly_ctc_amount = fields.Float(string='Monthly CTC Negotiated')
    
    is_screening_completed = fields.Boolean(string="Is screening completed ?")
    recruitment_stage_id = fields.Many2one("hr.applicant.stage")
    panel_member_id = fields.Many2one("hr.employee", string='Panel Member', domain=_get_domain)
    is_screening_enabled = fields.Boolean(string="Is screening Enabled", compute="_check_is_screening_enabled",
                                          readonly=False)
    date_of_birth = fields.Date('Date of Birth')

    # ####offer letter Declined Reason######
    reason_choose = fields.Char(string="Reason")
    special_reason = fields.Char(string="Specify Reason")
    cv_api_log_id = fields.Many2one('cv_skills_api_log', string="CV API Log Ref.")

    priority = fields.Selection([
    ('0', 'Normal'),
    ('1', 'Average'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Excellent'),
    ('5', 'Outstanding')], "Appreciation", default='0')
    char_priority = fields.Char(string="Rating", default='0.0')
    hr_discuss_bool = fields.Boolean(string="HR discuss",default=False)
    
    company_currency_id = fields.Many2one('res.currency',string='Currency')

    # def button_send_invitation(self):
        # self.send_invitation()
        # return True

    # @api.multi
    # def send_invitation(self):
    #     ir_config_params = self.env['ir.config_parameter'].sudo()
    #     send_mail_config = ir_config_params.get_param('kw_onboarding.module_onboarding_mail_status') or False
    #     email_cc = self.env.user.employee_ids.work_email if self.env.user.employee_ids else 'tendrils@csm.tech'
    #     # emp_id = int(email_fr) if email_fr != 'False' else False
    #     tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    #     if email_cc:
    #         for record in self:
    #             if record.source_id.code != 'ceo_reference':
    #                 template = self.env.ref('kw_recruitment.applicant_invitation_email_template')
    #                 mail_status = self.env['mail.template'].browse(template.id).with_context(email_cc=email_cc, tomorrow=tomorrow_date).send_mail(record.id)

    @api.model
    def _get_employee_jd_url(self, user_id):
        emp_jd_url = f"/employee-jd-view"
        return emp_jd_url              

    def get_applicants(self):
        view_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
        return {
            'name': 'Applications',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'hr.applicant',
            'view_id': view_id,
            'res_id': self.id,
            'target': 'self',
            'context': {'recruitment_job_id': self.job_position.id},
            'flags': {'mode': 'edit'}
        }

    @api.constrains('candidate_relation')
    def check_expiration(self):
        if self._context.get('referred_candidate') and not self._context.get('self_reffered_ctx'):
            if not self.candidate_info:
                raise ValidationError("Please answer Candidate's Suspicious activity query.")
      
    @api.onchange('job_position')
    def onchange_job_position(self):
        for record in self:
            return {'domain': {'panel_member_id': [('id', 'in', record.job_position.panel_member.ids)]}}

    @api.multi
    def get_odder_letter(self):
        for applicant in self:
            offer_letters = self.env['hr.applicant.offer'].sudo().search([('applicant_id', '=', applicant.id)],
                                                                         order="id desc")
            if offer_letters:
                applicant.offer_id = offer_letters.id

    # @api.constrains('department_id')
    # def validation_department(self):
    #     for rec in self:
    #         if not rec.department_id:
    #             raise ValidationError("Department is required")
    #         if rec.requisition_type == 'project' and rec.budget_amount < 1:
    #             raise ValidationError("Budget Amount is Required")
    @api.multi
    def _compute_is_referred(self):
        for record in self:
            if self._context.get('referred_candidate'):
                record.is_referred = True
            else:
                record.is_referred = False

    def _compute_budget_amount(self):
        for record in self:
            if self.env.user.has_group('kw_recruitment.group_hr_recruitment_accounts'):
                record.is_account = True
            else:
                record.is_account = False

    def btn_submit_to_hr(self):
        if self.budget_amount < 1:
            raise ValidationError("Budget amount should be more than zero.")
        self.is_finance_approved = False

        hr_dept_users = self.env.ref('hr_recruitment.group_hr_recruitment_manager').users
        emails = ','.join(hr_dept_users.mapped('employee_ids.work_email'))

        mail_template = self.env.ref('kw_recruitment.budget_config_mail_to_hr_template')
        mail_template.with_context(dept_name='All', emails=emails).send_mail(
            self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        # action_id = self.env.ref("kw_recruitment.action_kw_recruitment_finance_take_action").id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'self',
        #     'url': f'/web#action={action_id}&model=hr.applicant&view_type=kanban',
        # }
        tree_view_id = self.env.ref("kw_recruitment.applicant_budget_validation_tree_view").id
        form_view_id = self.env.ref("kw_recruitment.applicant_budget_validation_form_view").id
        return {
            'name': 'Budget Validation',
            'type': 'ir.actions.act_window',
            # 'res_id': self.res_id,
            'res_model': 'hr.applicant',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'main',
            'domain': [('is_finance_approved', '=', True)],
            # 'flags': {'mode': 'readonly'},
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }

    def btn_mail_to_finance(self):
        if self.monthly_ctc_amount < 1:
            raise ValidationError("Monthly CTC Negotiated should be more than zero.")

        self.is_finance_approved = True
        finance_dept_users = self.env.ref('kw_recruitment.group_hr_recruitment_accounts').users
        mail_template = self.env.ref('kw_recruitment.budget_config_finance_mail_template')
        emails = ','.join(finance_dept_users.mapped('employee_ids.work_email'))
        mail_template.with_context(dept_name='Team', emails=emails).send_mail(
            self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    # ------------------------------------------------------

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

    # #attachement##
    attachment_doc = fields.Integer(compute='_get_attachment', string="Number of Attachments")
    # attachment_doc_ids = fields.One2many('recruitment_attachment','attachment_doc_id',string='Attachments')
    # applicant_ids = fields.One2many('recruitment_attachment', 'applicant_id',ondelete="set null")

    walk_in_meeting_count = fields.Integer(string='Walk In Meetings', compute='_compute_walk_in_meeting_count')

    @api.multi
    def action_walk_in_meeting(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('kw_recruitment',
                                                           'action_kw_recruitment_walk_in_meeting_act_window')
        res['domain'] = [('meeting_detail_ids.applicant_id', 'in', self.ids)]
        res['context'] = {'default_meeting_detail_ids': [[0, 0, {'applicant_id': self.id}]]}
        return res

    @api.onchange('joining_date')
    def onchange_joining(self):
        for rec in self:
            if rec.joining_date:
                rec.profile_submit_date = rec.joining_date - timedelta(days=1)

    @api.multi
    def _compute_walk_in_meeting_count(self):
        for applicant in self:
            applicant.walk_in_meeting_count = self.env['kw_recruitment_walk_in_meeting'].search_count([
                ('meeting_detail_ids.applicant_id', 'in', applicant.ids)])

    @api.multi
    def export_feedbacks(self):
        """''' This method has the following requirements ,
            1.unoconv 0.7
            2.python 3.6.9
            3.LibreOffice 6.0.7.3
        '''"""
        survey_feedbacks = self.env['survey.user_input'].sudo().search([('applicant_id', '=', self.id)], order="id desc")
        final_feedbacks = survey_feedbacks.filtered(lambda r: r.state != 'new')

        given_feedbacks = final_feedbacks.filtered(lambda r: r.user_input_line_ids.filtered(lambda x: x.answer_type == 'suggestion' and x.question_id.question == 'Status').value_suggested.value != 'Absent')
        # print("given_feedbacks >>> ", given_feedbacks)
        # print("final_feedbacks >>> ", final_feedbacks)
        # return
        if not given_feedbacks:
            raise ValidationError("No feedbacks found.")

        report = self.env.ref('kw_recruitment.kw_recruitment_interview_feedback_report')
        ctx = self.env.context.copy()
        ctx['flag'] = True

        applicant_path = f'applicant_docs/{self.id}'
        if not os.path.exists(applicant_path):
            os.makedirs(applicant_path)

        full_path = os.path.join(os.getcwd() + f'/{applicant_path}')
        try:
            merge_list = []
            for index, feedback in enumerate(given_feedbacks, start=1):
                feedback_b64_string = report.with_context(ctx).sudo().render_qweb_pdf(feedback.id)[0]
                feedback_path = f'{full_path}/{index}.pdf'

                with open(os.path.expanduser(feedback_path), 'wb') as fp:
                    fp.write(feedback_b64_string)
                    merge_list.append(feedback_path)
            # Assuming all feedback pdfs are generated
            # convert applicant document to pdf format if this is other than pdf format
            # Loop over the cvs of applicant and convert them one by one
            for index, cv in enumerate(self.document_ids):
                if cv.content_file:
                    cv_b64_string = base64.b64decode(cv.content_file)
                    # get extension of cv
                    cv_extension = guess_extension(guess_mimetype(cv_b64_string))

                    # If cv is in pdf no need to convert just write the file
                    if cv_extension == '.pdf':
                        cv_store_path = f'{full_path}/cv{index}.pdf'
                        with open(os.path.expanduser(cv_store_path), 'wb') as fp:
                            fp.write(cv_b64_string)
                            # merge_list.insert(0,cv_store_path)
                            merge_list.append(cv_store_path)
                    else:
                        # first write the file with its extension i.e cv.docx,cv.doc etc
                        with open(os.path.expanduser(f'{full_path}/cv{index}{cv_extension}'), 'wb') as fp:
                            fp.write(cv_b64_string)

                        # convert to pdf using unoconv with system command
                        cv_store_path = f'{full_path}/cv{index}{cv_extension}'
                        cv_converted_path = f'{full_path}/cv{index}.pdf'

                        try:
                            system(f'unoconv -f pdf {cv_store_path}')  # system command that will generate cv.pdf internally
                            # merge_list.insert(0, cv_converted_path)
                            merge_list.append(cv_converted_path)
                        except Exception:
                            pass

            # merge all pdf to a single file named finaloutput.pdf

            merger = PdfFileMerger(strict=False)
            full_path_output = f'{full_path}/finaloutput.pdf'

            for pdf in merge_list:
                merger.append(pdf, import_bookmarks=False)

            merger.write(full_path_output)
            merger.close()

            feedback = self.env['kw_recruitment_consolidated_feedback'].create({
                'binary_file': base64.b64encode(open(full_path_output, "rb").read()),
                'file_name': f'{self.partner_name}_feedback_consolidated.pdf',
                'applicant_id': self.id
            })

            # Clean the directory
            #             shutil.rmtree(applicant_path)

            return {
                'view_mode': 'form',
                'res_model': 'kw_recruitment_consolidated_feedback',
                'res_id': feedback.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': self.env.context,
                'nodestroy': True,
            }
        except Exception:
            # Clean the directory
            #             shutil.rmtree(applicant_path)
            raise ValidationError(
                f"Unable to convert applicant document to pdf.\nPlease try with a different extension.\n")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = str(record.partner_name)
            result.append((record.id, record_name))
        return result

    @api.multi
    def _compute_evaluators(self):
        for record in self:
            meeting_ids = self.env['calendar.event'].search([('applicant_id', '=', record.id)])
            evaluators = self.env['res.partner']
            if meeting_ids:
                for meeting in meeting_ids:
                    evaluators |= meeting.partner_ids
            if evaluators:
                record.evaluators = ','.join(evaluators.mapped('name'))
                # record.evaluators = '\n'.join(evaluators.mapped('name'))
            else:
                record.evaluators = ''

    # #attachement##
    @api.multi
    def _get_attachment(self):
        read_group_res = self.env['recruitment_attachment'].read_group(
            [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)

        for record in self:
            record.attachment_doc = attach_data.get(record.id, 0)

    """# #attachement##"""

    @api.multi
    def action_get_attachment_view(self):
        attachment_action = self.env.ref('kw_recruitment.action_recruitement_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name,
                             'default_res_id': self.ids[0],
                             'default_name': self.name,
                             'default_id': self.id}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        action['search_view_id'] = (self.env.ref('kw_recruitment.view_attachment_search').id,)
        return action

    # @api.multi
    # def name_get(self):
    #     return [(record.id, f"{record.job_position.title} {record.job_position.job_code or ' '}") for record in self]

    @api.onchange('source_id')
    def onchange_source(self):
        self.code_ref = self.source_id.code

    @api.onchange('employee_type')
    def enable_employee_type(self):
        if self.employee_type and self.employee_type == "new":
            self.employee_id = False

    @api.onchange('job_position')
    def _set_default_field(self):
        self.other_position = False
        if self.job_position:
            job = self.job_position
            if job.job_code == "others":
                self.other_position = ""
            self.job_id = job.job_id.id if job.job_id else False
            self.department_id = job.department_id.id if job.department_id else False
            self.responsible_id = job.hr_responsible_id.id if job.hr_responsible_id else False
            return {'domain': {'job_location_id': [('id', 'in', job.address_id.ids)]}}

    @api.onchange('qualification_ids')
    def enable_other_qualification(self):
        self.other_qualification = False
        for x in self.qualification_ids:
            if x and x.code == "others":
                self.other_qualification = ""

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        vals = self._onchange_stage_id_internal(self.stage_id.id)
        if vals['value'].get('date_closed'):
            self.date_closed = vals['value']['date_closed']
            
    # @api.onchange('mrf_id')
    # def onchange_of_mrf_id(self):
    #     if self.mrf_id:
    #         current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
    #         if self.mrf_id.resource == 'new':
    #             values = self.env['kw_recruitment_budget_lines'].sudo().search([('fiscalyr','=',current_fiscal_year_id.id),('mrf_id','=',self.mrf_id.id),('offer_id','=',False)],order='department_sequence asc')
    #             if self.mrf_id.max_sal and values:
    #                 if values:
    #                     for rec in values:
    #                         self.budget_amount = rec.mar_budget
    #                         return
    #                 else:
    #                     raise ValidationError("Total Budget has been used for the selected MRF,Please choose a different one")
    #             else:
    #                 self.budget_amount = self.mrf_id.max_sal
    #         else:
    #             values = self.env['hr.employee'].sudo().search([('mrf_id','=',self.mrf_id.id)]).mapped('name')
    #             if len(values) == self.mrf_id.no_of_resource:
    #                 raise ValidationError(f"Employees ({','.join(values)}) has alredy been joined with this MRF as replacement")
    #             else:
    #                 self.budget_amount = self.mrf_id.avg_replacement_sal 
                  
                
    @api.onchange('mrf_id')
    def onchange_mrf_id(self):
        if self.mrf_id:
            self.requisition_type = self.mrf_id.requisition_type
            # self.budget_type = self.mrf_id.requisition_type
            self.mrf_role_id = self.mrf_id.role_id
            self.mrf_categ_id = self.mrf_id.categ_id
            self.mrf_min_sal = self.mrf_id.min_sal
            self.mrf_max_sal = self.mrf_id.max_sal
            self.mrf_type_employment = self.mrf_id.type_employment

            if self.mrf_id.requisition_type == "project":
                self.project_type = self.mrf_id.type_project
                self.mrf_project = self.mrf_id.project
                self.mrf_duration = self.mrf_id.duration

            else:
                self.project_type = False
                self.mrf_project = False
                self.mrf_duration = False

        else:
            self.requisition_type = False
            # self.budget_type = False
            self.mrf_role_id = False
            self.mrf_categ_id = False
            self.mrf_min_sal = False
            self.mrf_max_sal = False
            self.mrf_type_employment = False
            self.project_type = False
            self.mrf_project = False
            self.mrf_duration = False

    @api.onchange('budget_type')
    def enable_budget_type(self):
        if self.budget_type and self.budget_type == "treasury":
            # self.duration = False
            self.budget_from_date = False
            self.budget_to_date = False

    @api.constrains('partner_mobile')
    def check_partner_mobile(self):
        for record in self:
            if record.partner_mobile:
                if not re.match("^[0-9+\/\-\s]*$", str(record.partner_mobile)) is not None:
                    raise ValidationError("Mobile number is invalid for: %s" % record.partner_mobile)

    @api.constrains('partner_phone')
    def check_partner_phone(self):
        for record in self:
            if record.partner_phone:
                if not re.match("^[0-9+\/\-\s]*$", str(record.partner_phone)) is not None:
                    raise ValidationError("Phone number is invalid for: %s" % record.partner_phone)

    @api.constrains('email_from')
    def check_email_from(self):
        for record in self:
            kw_validations.validate_email(record.email_from)

    @api.constrains('qualification_ids', 'other_qualification')
    def validate_other_qualification(self):
        for record in self:
            for x in record.qualification_ids:
                if x and x.code == "others" and not record.other_qualification:
                    raise ValidationError("Please give other qualification.")

    # @api.constrains('exp_year', 'exp_month')
    # def validate_experience(self):
    #     for record in self:
    #         if record.exp_year == 0 and record.exp_month == 0:
    #             raise ValidationError("Please add experience.")

    @api.constrains('source_id')
    def validate_referral(self):
        for record in self:
            if record.source_id.code == 'employee' and not record.employee_referred:
                raise ValidationError("Please enter referred by employee.")
            elif record.source_id.code == 'job' and not record.jportal_id:
                raise ValidationError("Please enter referred by job portal.")
            elif record.source_id.code == 'institute' and not record.institute_id:
                raise ValidationError("Please enter referred by institute.")
            elif record.source_id.code == 'partners' and not record.service_partner_id:
                raise ValidationError("Please enter referred by partner name.")
            elif record.source_id.code == 'social' and not record.media_id:
                raise ValidationError("Please enter referred by social media.")
            elif record.source_id.code == 'consultancy' and not record.consultancy_id:
                raise ValidationError("Please enter referred by consultancy.")
            elif record.source_id.code == 'walkindrive' and not record.reference_walkindrive:
                raise ValidationError("Please enter Walk-in Drive.")
            elif record.source_id.code == 'printmedia' and not record.reference_print_media:
                raise ValidationError("Please enter Print Media.")
            elif record.source_id.code == 'jobfair' and not record.reference_job_fair:
                raise ValidationError("Please enter Job Fair.")
            elif record.source_id.code == 'client' and not record.reference:
                raise ValidationError("Please enter Client Name.")

    @api.constrains('other_position', 'job_position')
    def validate_other_position(self):
        for record in self:
            if record.job_position and record.job_position.job_code == "others" and not record.other_position:
                raise ValidationError("Please enter other job position name.")

    @api.constrains('employee_type', 'employee_id')
    def validate_employee_type(self):
        for record in self:
            if record.employee_type and record.employee_type == "replacement" and not record.employee_id:
                raise ValidationError("Please give Employee Replacement for.")

    @api.constrains('budget_type', 'budget_from_date', 'budget_to_date')
    def validate_budget(self):
        for record in self:
            if record.budget_type and record.budget_type == "project":
                if record.budget_from_date and record.budget_to_date and record.budget_from_date > record.budget_to_date:
                    # if not record.budget_from_date:
                    #     raise ValidationError("Please choose budget from date.")
                    # if not record.budget_to_date:
                    #     raise ValidationError("Please choose budget to date.")
                    # if record.budget_from_date > record.budget_to_date:
                    raise ValidationError("Budget to date must be equal or greater than budget from date.")

    def _compute_meeting_count(self):
        for applicant in self:
            applicant.meeting_count = self.env['calendar.event'].search_count([('applicant_id', '=', applicant.id)])

    @api.multi
    def show_applicant_answers(self):
        self.ensure_one()
        return self.job_id.applicant_feedback_form.with_context(
            survey_token=self.applicant_response_id.token).action_start_kw_recruitment_survey()

    @api.multi
    def action_view_all_feedback(self):
        self.ensure_one()
        applicant_id = self.id
        meetings = self.env['calendar.event'].search(
            ['&', ('applicant_id', '=', applicant_id), ('response_id', '!=', False)])
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'self',
            'domain': [('id', 'in', [meeting.response_id.id for meeting in meetings])],
        }

    @api.multi
    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id
        # self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('kw_recruitment', 'action_calendar_form')
        # res['domain'] = [('partner_ids', 'in', self.env.user.partner_id.ids)]
        res['domain'] = [('applicant_id', '=', self.id)]
        res['context'] = {
            'visible': False,
            'default_applicant_id': self.id,
            # 'search_default_partner_ids': self.partner_id.name,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_categ_ids': category and [category.id] or False,
        }
        return res

    @api.model
    def _get_exp_years(self):
        return [(str(i), i) for i in range(1, 36)]

    def action_open_discussion_details(self):
        form_view_id = self.env.ref('kw_recruitment.view_applicant_hr_discussion_details_form').id
        # discussion_data = self.env['hr_discussion_applicant_details'].sudo().search([('applicant_id','=',self.id)])
        # if discussion_data:
        #     return {
        #         'name': 'Hr Discussion Form',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'hr_discussion_applicant_details',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'res_id' : discussion_data.id,
        #     'view_id': form_view_id,
        #     'target': 'new',

        #     }
        
        action = {
            'name': 'Hr Discussion Form',
            'type': 'ir.actions.act_window',
            'res_model': 'hr_discussion_applicant_details',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {
                'default_applicant_id': self.id,
                # 'default_designation': self.job_position.id,
                'default_department': self.department_id.id,
                'default_section': self.section.id,
                'default_date_of_joining': self.joining_date,
                'default_job_location': self.job_location_id.id,
                'default_employment_type': self.mrf_type_employment.id,}
            }
        return action

    @api.multi
    def create_enrollment(self):
        for record in self:
            # if not record.mrf_id:
            #     raise UserError(_('No MRF found for this applicant.'))
            if not record.profile_submit_date:
                raise UserError(_('No Profile Submit Date found for this applicant.'))
            if not record.department_id or not record.job_id:
                raise UserError(_('Please verify Department and Applied Job are filled.'))
            note_message = "Enrollment create link send successfully."
            record.message_post(body=note_message)
            record.hr_discuss_bool = True

            if record.partner_name:
                vals = {
                    'name': record.partner_name,
                    'applicant_id': record.id
                }
                # data= self.env["kwonboard_enrollment"]
                if record.edu_data_ids:
                    vals['educational_ids'] = [[0, 0, {
                        'course_type': r.course_type,
                        'course_id': r.course_id.id,
                        'stream_id': r.stream_id.id,
                        'university_name': r.university_name.id,
                        'passing_year': str(r.passing_year),
                        'division': r.division,
                        'marks_obtained': r.marks_obtained,
                        'passing_details': [(6, 0, r.passing_details.ids)]
                        }] for r in record.edu_data_ids]
                if record.work_experience_ids:
                    vals['work_experience_ids'] = [[0, 0, {
                        'country_id': r.country_id.id,
                        'name': r.name,
                        'designation_name': r.designation_name,
                        'organization_type': r.organization_type.id,
                        'industry_type': r.industry_type.id,
                        'effective_from': r.effective_from,
                        'effective_to': r.effective_to,
                    }] for r in record.work_experience_ids]
                if record.experience_sts:
                    vals['experience_sts'] = record.experience_sts
                if record.email_from:
                    vals['email'] = record.email_from
                if record.partner_mobile:
                    vals['mobile'] = record.partner_mobile
                if record.department_id.active is True:
                    vals['dept_name'] = record.department_id.id
                if record.job_id:
                    vals['job_id'] = record.job_id.id
                if record.division.active is True:
                    vals['division'] = record.division.id
                if record.section.active is True:
                    vals['section'] = record.section.id
                if record.practise.active is True:
                    vals['practise'] = record.practise.id
                if record.mrf_id:
                    vals['mrf_id'] = record.mrf_id.id
                    vals['budget_type'] = record.requisition_type
                    vals['tmp_emp_role'] = record.mrf_role_id.id
                    vals['project_name_id'] = record.mrf_id.project.id
                    vals['fin_project_name_id'] = record.mrf_id.project.id
                    vals['tmp_emp_category'] = record.mrf_categ_id.id
                    vals['tmp_employement_type'] = record.mrf_type_employment.id
                    vals['finance_mrf_id'] = record.mrf_id.id
                if record.gender:
                    vals['gender'] = record.gender
                vals['tmp_join_date'] = record.joining_date if record.joining_date else False
                vals['profile_submit_date'] = record.profile_submit_date if record.profile_submit_date else False

                vals['tmp_source_id'] = record.source_id.id if record.source_id else False
                vals['tmp_employee_referred'] = record.employee_referred.id if record.source_id.code == 'employee' else False
                vals['tmp_jportal_id'] = record.jportal_id.id if record.source_id.code == 'job' else False
                vals['tmp_reference'] = record.reference if record.source_id.code == 'client' else False
                vals['tmp_institute_id'] = record.institute_id.id if record.source_id.code == 'institute' else False
                vals['tmp_consultancy_id'] = record.consultancy_id.id if record.source_id.code == 'consultancy' else False
                vals['tmp_media_id'] = record.media_id.id if record.source_id.code == 'social' else False
                vals['tmp_reference_walkindrive'] = record.reference_walkindrive if record.source_id.code == 'walkindrive' else False
                vals['tmp_reference_print_media'] = record.reference_print_media if record.source_id.code == 'printmedia' else False
                vals['tmp_reference_job_fair'] = record.reference_job_fair if record.source_id.code == 'jobfair' else False
                vals['tmp_service_partner_id'] = record.service_partner_id.id if record.source_id.code == 'partners' else False

                vals['bond_required'] = record.bond_required
                vals['bond_years'] = record.bond_years
                vals['bond_months'] = record.bond_months
                vals['location_id'] = record.offer_id.job_location.id
                vals['tmp_worklocation_id'] = record.offer_id.job_location.id
                vals['birthday'] = record.date_of_birth
                vals['type_of_project_id'] = record.project_type
                vals['engagement'] = record.mrf_duration

                if record.offer_id.grade.id or record.offer_id.emp_band.id:
                    vals['tmp_grade'] = record.offer_id.grade.id
                    vals['tmp_band'] = record.offer_id.emp_band.id

                if 'budget_type' in vals and vals['budget_type'] == 'treasury':
                    record_emp_type = self.env['kwemp_employment_type'].sudo().search([('code', '=', 'P')])
                    vals['employement_type'] = record_emp_type.id
                    vals['tmp_employement_type'] = record_emp_type.id
                if 'budget_type' in vals and vals['budget_type'] == 'project':
                    record_emp_type = self.env['kwemp_employment_type'].sudo().search([('code', '=', 'C')])
                    vals['employement_type'] = record_emp_type.id
                    vals['tmp_employement_type'] = record_emp_type.id

                # if record.offer_id:
                #     vals['enable_payroll'] = 'yes'
                # if record.offer_id.offer_type == 'Lateral':
                #     vals['tmp_at_join_time'] = record.offer_id.annual_amount_lateral if record.offer_id.annual_amount_lateral else False
                #     vals['current'] = record.offer_id.annual_amount_lateral if record.offer_id.annual_amount_lateral else False
                #     vals['basic_at_join_time'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['current_basic'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['hra'] = [rec.percentage if rec.code == 'hra' else False for rec in record.offer_id.annexture_offer1][1]
                #     vals['conveyance'] = [rec.percentage if rec.code == 'conv' else False for rec in record.offer_id.annexture_offer1][2]
                #     vals['productivity'] = [rec.per_month if rec.code == 'pb' else False for rec in record.offer_id.annexture_offer1][3]
                #     vals['commitment'] = [rec.per_month if rec.code == 'cb' else False for rec in record.offer_id.annexture_offer1][4]
                #     vals['basic_at_join_time'] =  float(b)

                # if record.offer_id.offer_type == 'Intern':
                #     vals['tmp_at_join_time'] = record.offer_id.annual_amount_lateral if record.offer_id.annual_amount_lateral else False
                #     vals['current'] = record.offer_id.annual_amount_lateral if record.offer_id.annual_amount_lateral else False
                #     vals['basic_at_join_time'] = 0
                #     vals['current_basic'] = 0
                #     vals['hra'] = 0
                #     vals['conveyance'] = 0
                #     vals['productivity'] = 0
                #     vals['commitment'] = 0

                # vals['basic_at_join_time'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                # vals['current_basic'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                # vals['hra'] = [rec.percentage if rec.code == 'hra' else False for rec in record.offer_id.annexture_offer1][0]
                # vals['conveyance'] = [rec.percentage if rec.code == 'conv' else False for rec in record.offer_id.annexture_offer1][0]
                # vals['productivity'] = [rec.per_month if rec.code == 'pb' else False for rec in record.offer_id.annexture_offer1][0]
                # vals['commitment'] = [rec.per_month if rec.code == 'cb' else False for rec in record.offer_id.annexture_offer1][0]

                # if record.offer_id.offer_type == 'RET':
                #     vals['tmp_at_join_time'] = record.offer_id.monthly_ctc if record.offer_id.monthly_ctc else False
                #     vals['current'] = record.offer_id.monthly_ctc if record.offer_id.monthly_ctc else False
                #     vals['basic_at_join_time'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['current_basic'] = [rec.per_month if rec.code == 'basic' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['hra'] = [rec.percentage if rec.code == 'hra' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['conveyance'] = [rec.percentage if rec.code == 'conv' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['productivity'] = [rec.per_month if rec.code == 'pb' else False for rec in record.offer_id.annexture_offer1][0]
                #     vals['commitment'] = [rec.per_month if rec.code == 'cb' else False for rec in record.offer_id.annexture_offer1][0]

                if record.requisition_type == 'project':
                    vals['tmp_start_dt'] = record.joining_date
                    vals['tmp_end_dt'] = record.joining_date + relativedelta(months=int(record.mrf_duration))
                    vals['start_dt'] = record.joining_date
                    vals['end_dt'] = record.joining_date + relativedelta(months=int(record.mrf_duration))

                if record.offer_id.avail_pf_benefit:
                    vals['enable_epf'] = 'yes'
                    vals['pf_deduction'] = record.offer_id.pf_deduction

                vals['enable_payroll'] = 'yes'

                if record.offer_id.offer_type == 'Intern':
                    vals['tmp_at_join_time'] = record.offer_id.first_amount if record.offer_id.first_amount else False
                    vals['current'] = record.offer_id.first_amount if record.offer_id.first_amount else False
                    vals['basic_at_join_time'] = record.offer_id.first_amount if record.offer_id.first_amount else False
                    vals['current_basic'] = record.offer_id.first_amount if record.offer_id.first_amount else False
                    vals['is_consolidated'] = True
                    vals['hra'] = 0
                    vals['conveyance'] = 0
                    vals['productivity'] = 0
                    vals['commitment'] = 0
                    vals['lta_amount'] = 0
                    vals['pp_amount'] = 0
                else:
                    if record.offer_id:
                        pfer = record.offer_id.annexure_offer2.filtered(lambda x : x.per_month > 0 and x.code == 'pfer')
                        gratuity = record.offer_id.annexure_offer3.filtered(lambda x : x.per_month > 0 and x.code == 'gratuity')
                        current_ctc = pfer.per_month + gratuity.per_month + record.offer_id.average_1_month
                        vals['tmp_at_join_time'] = current_ctc if current_ctc else False
                        vals['current'] = current_ctc if current_ctc else False
                
                    if record.offer_id.avail_pf_benefit == True:
                        vals['enable_epf'] = 'yes'
                        vals['pf_deduction'] = record.offer_id.pf_deduction
                    # if record.offer_id.offer_type == 'Lateral':
                    #     vals['enable_gratuity'] = 'yes'
                    for first_line in record.offer_id.annexture_offer1:
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
                    for third_line in record.offer_id.annexure_offer3:
                        if third_line.code == 'gratuity':
                            if third_line.per_month > 0:
                                vals['enable_gratuity'] = 'yes'
                            else:
                                vals['enable_gratuity'] = 'no'
                    if record.offer_id.offer_type == 'Lateral':
                        if record.offer_id.pt_type == 'Probation':
                            vals['tmp_on_probation'] = True
                            vals['no_of_months'] = record.offer_id.months
                            vals['tmp_prob_compl_date'] = record.offer_id.joining_date + relativedelta(months=int(record.offer_id.months))
                # print('vals', vals)
                enrollment_record = self.env['kwonboard_enrollment'].sudo().create(vals)
                # print("=====",enrollment_record.tmp_at_join_time)
                if enrollment_record:
                    self.env.user.notify_success(message='Enrollment created successfully.')
                    record.write({'erroll_reference': enrollment_record.reference_no,
                                  'kw_enrollment_id': enrollment_record.id})
                    record.send_feedback_form_to_applicant()
                    if record.job_id:
                        record.job_id.write({'no_of_hired_employee': record.job_id.no_of_hired_employee + 1})
                        record.job_id.message_post(
                            body=_('New Employee %s Hired') % record.partner_name if record.partner_name else record.name,
                            subtype="hr_recruitment.mt_job_applicant_hired")
                    if record.job_position:
                        record.job_position.no_of_hired_employee = 1 if record.job_position.no_of_hired_employee == 0 else record.job_position.no_of_hired_employee + 1
                    else:
                        raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))
                    # record.active = False
            # return {
            #     "type": "ir.actions.client",
            #     'tag': "reload",
            # }
            tree_view_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
            return {
                "name": "Applicants",
                'views': [(tree_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                "res_model": 'hr.applicant',
                "res_id": self.id,
                "type": 'ir.actions.act_window',
                "target": "self",
            }

    @api.model
    def _cron_generate_payroll_entries(self):
        self.compute_generated_entries()

    @api.model
    def compute_generated_entries(self):
        onboarding_rec = self.env['kwonboard_enrollment'].search([('applicant_id', '!=', False), ('state', 'in', ('1', '2', '3', '4'))])
        # print('onboarding_reconboarding_reconboarding_rec', onboarding_rec)
        for record in onboarding_rec:
            if record.applicant_id.offer_id:
                offer_rec = record.applicant_id.offer_id
                # print('onboarding_reconboarding_reconboarding_rec', onboarding_rec,record.applicant_id,record.applicant_id.offer_id)
                vals = {
                    'tmp_at_join_time':  offer_rec.average_1_month if offer_rec.average_1_month else False,
                    'enable_payroll': 'yes',
                    'current': offer_rec.average_1_month if offer_rec.average_1_month else False
                }

                # print('int(record.offer_id)', record.applicant_id.offer_id.offer_type)

                if record.applicant_id.offer_id.offer_type == 'Intern':
                    vals['tmp_at_join_time'] = offer_rec.first_amount if offer_rec.first_amount else False
                    vals['current'] = offer_rec.first_amount if offer_rec.first_amount else False
                    vals['basic_at_join_time'] = offer_rec.first_amount if offer_rec.first_amount else False
                    vals['current_basic'] = offer_rec.first_amount if offer_rec.first_amount else False
                    vals['is_consolidated'] = True
                    vals['hra'] = 0
                    vals['conveyance'] = 0
                    vals['productivity'] = 0
                    vals['commitment'] = 0
                else:
                    vals['tmp_at_join_time'] = offer_rec.average_1_month if offer_rec.average_1_month else False
                    vals['current'] = offer_rec.average_1_month if offer_rec.average_1_month else False
                    if record.applicant_id.offer_id.avail_pf_benefit == True:
                        vals['enable_epf'] = 'yes'
                        vals['pf_deduction'] = record.applicant_id.offer_id.pf_deduction
                    # if record.offer_id.offer_type == 'Lateral':
                    #     vals['enable_gratuity'] = 'yes'
                    for first_line in record.applicant_id.offer_id.annexture_offer1:
                        # print('first_linefirst_linefirst_line', first_line)
                        if first_line.code == 'basic':
                            vals['basic_at_join_time'] = first_line.per_month
                            # print('vals', vals,first_line.percentage)
                        if first_line.code == 'basic':
                            vals['current_basic'] = first_line.per_month
                        if first_line.code == 'hra':
                            vals['hra'] = first_line.percentage
                        if first_line.code == 'conv':
                            vals['conveyance'] = first_line.percentage
                        if first_line.code == 'pb':
                            vals['productivity'] = first_line.per_month
                        if first_line.code == 'cb':
                            vals['commitment'] = first_line.per_month
                    for third_line in record.applicant_id.offer_id.annexure_offer3:
                        if third_line.code == 'gratuity':
                            if third_line.per_month > 0:
                                vals['enable_gratuity'] = 'yes'
                            else:
                                vals['enable_gratuity'] = 'no'
                # print('vals', vals)
                record.update(vals)

    @api.model
    def send_feedback_form_to_applicant(self):
        self.ensure_one()
        if self.job_id.applicant_feedback_form:
            applicant_job_survey_id = self.job_id.applicant_feedback_form
            url = applicant_job_survey_id.public_url
            if not self.applicant_response_id:
                response = self.env['survey.user_input'].create(
                    {'survey_id': applicant_job_survey_id.id,
                     'partner_id': self.responsible_id.partner_id.id})
                self.applicant_response_id = response.id
            else:
                response = self.applicant_response_id
            token = response.token
            self.applicant_feedback_url = f"{url}/{token}"
            template_id = self.env.ref('kw_recruitment.kw_hr_applicant_feedback_template')
            template_id.send_mail(self.id, force_send=True)
            return True
        

    @api.multi   
    def call_cv_rating_api(self, res):
        url = self.env['ir.config_parameter'].sudo().search([('key', '=', 'url_for_cv_rating')], limit=1)
        if  url:
            api_url = url.value

        jd_skills = res.job_position.jd_skills_ids.mapped('skill')
        clean = re.compile('<.*?>')
        jd_html_string = res.job_position.description
        jd_cleaned_data = re.sub(clean, '', jd_html_string)
        cp_html_string = res.job_position.candidate_profile
        cp_cleaned_data = re.sub(clean, '', cp_html_string)

        payload = json.dumps({
            # "payload": self.cv_api_log_id.payload,
            "must_have_skills": jd_skills,
            "jd": jd_cleaned_data,
            "cp": cp_cleaned_data,
            "ocr": res.cv_api_log_id.ocr or ""
        })
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(api_url, headers=headers, data=payload)
            response_data = response.json()
            
            self.env['cv_rating_api_response_log'].create({
                'applicant_id': res.id,
                'payload': payload,
                'response': json.dumps(response_data),
                'status': response_data.get('status'),
                'rating': response_data.get('rating'),
                'status_code': str(response_data.get('status_code'))
            })
            
            if response_data.get('status_code') == 200:
                rating = float(response_data.get('rating'))
                if rating - int(rating) >= 0.5:
                    res.priority = str(int(rating) + 1)
                else:
                    res.priority = str(int(rating))
                res.char_priority = str(rating)

        except requests.exceptions.RequestException as e:
            _logger.error('Something went wrong.Please try again later: %s', e)
            raise UserError('Something went wrong.Please try again later: %s' % str(e))
        except json.JSONDecodeError as e:
            _logger.error('No response from server.Please try again later: %s', e)
            raise UserError('No response from server.Please try again later: %s' % str(e))
        except Exception as e:
                _logger.error('Unexpected error.Please try again later: %s', e)
                raise UserError('Unexpected error.Please try again later: %s' % str(e))
        
        
    @api.model
    def create(self, vals):
        if vals.get('partner_name'):
            vals['partner_name'] = vals.get('partner_name').title()
            vals['name'] = vals.get('partner_name') + '\'s' + ' Application'
        phone = vals.get('partner_phone', False)
        mobile = vals.get('partner_mobile', False)
        if phone and not mobile:
            vals['partner_mobile'] = phone
        if not vals.get('responsible_id'):
            vals['responsible_id'] = int(self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.user_id'))

        rec = super(HrApplicant, self).create(vals)
        emp_reference = self.env['utm.source'].sudo().search([('code', '=', 'employee')])

        for record in emp_reference:
            if record.id and rec.employee_referred.id:
                mail_to = rec.employee_referred.work_email if rec.employee_referred else ''
                template_id = self.env.ref('kw_recruitment.applicant_status_to_employee_referred')
                template_id.with_context(email_to=mail_to).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Applicant details mail sent successfully.")

        if self._context.get('active_id') and not self._context.get('ijp_view'):
            doc_obj = self.env['kw_upload_cv'].browse(self.env.context.get('active_id'))
            doc_obj.applicant_id = rec.id
        """# channel message post"""
        if rec.user_id:
            tagged_user = rec.user_id
            ch_obj = self.env['mail.channel']
            channel1 = tagged_user.name + ', ' + self.env.user.name
            channel2 = self.env.user.name + ', ' + tagged_user.name
            channel = ch_obj.sudo().search(["|", ('name', 'ilike', str(channel1)), ('name', 'ilike', str(channel2))])
            if not channel:
                channel_id = ch_obj.channel_get([tagged_user.partner_id.id])
                channel = ch_obj.browse([channel_id['id']])
            channel.message_post(body=f"{rec.create_uid.name} assigned you to take interview of {rec.partner_name}",
                                 message_type='comment', subtype='mail.mt_comment',
                                 author_id=self.env.user.partner_id.id,
                                 notif_layout='mail.mail_notification_light')

        self.env.user.notify_success("Applicant details saved successfully.")

        """# email to hr responsible New Job Applied"""
        if rec.job_position.hr_responsible_id and rec.source_id.code != 'ceo_reference':
            template_id = self.env.ref('kw_recruitment.kw_job_applied_mail_template')
            template_id.send_mail(rec.id, force_send=False)

        """# email sent to Applicant Thanks mail Template"""
        if rec.email_from and rec.source_id.code != 'ceo_reference':
            template_id = self.env.ref('kw_recruitment.kw_job_applicant_applied_mail_template')
            cc_notify_users = self.env.ref('kw_recruitment.group_new_applicant_cc_notify').users
            email_cc = ','.join(cc_notify_users.mapped("email")) if cc_notify_users else (rec.responsible_id.email if rec.responsible_id else '')
            template_id.with_context(email_cc=email_cc).send_mail(rec.id, force_send=True)
        if 'job_position' in vals:
           self.call_cv_rating_api(rec) 
        return rec

    def _onchange_stage_id_internal(self, stage_id):
        if not stage_id:
            return {'value': {}}
        stage = self.env['hr.recruitment.stage'].browse(stage_id)
        if stage.fold:
            return {'value': {'date_closed': fields.datetime.now()}}
        return {'value': {'date_closed': False}}

    @api.multi
    def write(self, vals):
        # print("wrie calledddd=======",self,vals)
        if vals.get('stage_id'):
            self.env['hr.applicant.stage'].sudo().create({'from_stage': self.stage_id.id,
                                                          'to_stage': vals.get('stage_id'),
                                                          'applicant_id': self.id,
                                                          'employee_id': self.env.user.id,
                                                          'date': date.today(), })
            pre_stg_id = self.env['hr.recruitment.stage'].search([('id', '=', int(vals.get('stage_id')))])
            current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
            budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search([('fiscalyr','=',current_fiscal_year_id.id),('mrf_id','=',self.mrf_id.id),('offer_id','=',self.offer_id.id)])
            # print("budgetttttt=============",budget_lines)
            if pre_stg_id and pre_stg_id.code == 'OA':
                vals['acceptance_date'] = str(date.today().strftime("%Y-%m-%d"))
                if budget_lines:
                    # print("ppppppppppppppppp",self.offer_id.average_1_month,self.offer_id.joining_date)
                    for rec in budget_lines:
                        # print("recrecrec==",rec)
                        rec.write({
                            'resource_tobe_joined': self.id,
                        })
                        # rec.offer_id =
                        self.env['kw_recruitment_budget_lines'].sudo().get_monthly_ctc_data(self.offer_id.average_1_month,self.offer_id.joining_date,rec)
                        
                        return
            if pre_stg_id and pre_stg_id.code == 'OD':
                if budget_lines:
                    budget_lines.write({
                        'offer_id': False,
                    })

        result = super(HrApplicant, self).write(vals)
        emp_source = self.env['utm.source'].sudo().search([('code', '=', 'employee')], limit=1)
        status_id = self.env['hr.recruitment.stage'].sudo().search([('name', 'in', ['Shortlist', 'Offer Release'])])
        source = self.source_id.id
        # ens email to referrer for Short listed and Offer release
        if 'stage_id' in vals:
            if source == emp_source.id and self.employee_referred and int(vals['stage_id']) in status_id.ids:
                mail_to = self.employee_referred.work_email if self.employee_referred else ''
                template_id = self.env.ref('kw_recruitment.applicant_status_to_employee_referred')
                template_id.with_context(email_to=mail_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Applicant details mail sent successfully.")

        user_id = vals.get("user_id", False)
        for applicant in self:
            if 'stage_id' in vals and vals['stage_id'] and applicant.stage_id.code in ['OR', 'OA']:
                if not applicant.job_position:
                    raise ValidationError("Please tag applicant with a job position.")
                if not applicant.mrf_id or applicant.mrf_id.state != 'approve':
                    raise ValidationError("Applicant should be tagged to an approved MRF.")
                if applicant.mrf_id and applicant.mrf_id.requisition_type == 'project' and applicant.budget_amount < 1:
                    raise ValidationError("Applicant budget is pending validated by Finance.")
        if user_id:
            tagged_user = self.env['res.users'].browse(int(user_id))
            ch_obj = self.env['mail.channel']
            channel1 = tagged_user.name + ', ' + self.env.user.name
            channel2 = self.env.user.name + ', ' + tagged_user.name
            channel = ch_obj.sudo().search(["|", ('name', 'ilike', str(channel1)), ('name', 'ilike', str(channel2))])
            if not channel:
                channel_id = ch_obj.channel_get([tagged_user.partner_id.id])
                channel = ch_obj.browse([channel_id['id']])
            channel.message_post(body=f"{self.create_uid.name} assigned you to take interview of {self.partner_name}",
                                 message_type='comment', subtype='mail.mt_comment',
                                 author_id=self.env.user.partner_id.id,
                                 notif_layout='mail.mail_notification_light')

        exp_year = self.exp_year if vals.get('exp_year') else 0
        exp_month = self.exp_month if vals.get('exp_month') else 0
        if exp_year > 0 or exp_month > 0:
            exp_recs = self.env['survey.question'].search([('question', '=', 'Experience')])
            for usrinput in self.env['survey.user_input'].search([('applicant_id', '=', self.id)]):
                line_id = usrinput.user_input_line_ids.filtered(lambda r: r.question_id.id in exp_recs.ids)
                if line_id: line_id.write(
                    {'value_text': str(self.exp_year) + ' Year(s) ' + str(self.exp_month) + ' Month(s)'})

        if 'job_position' in vals:
           self.call_cv_rating_api(self)
        

        self.env.user.notify_success("Applicant details updated successfully.")
        return result

    # @api.multi
    # def unlink(self):
    #     for record in self:
    #         record.active = False
    #     return True

    @api.multi
    def start_recruitment_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.env['survey.user_input'].create({
                'survey_id': self.survey_id.id,
                'partner_id': self.partner_id.id,
                'applicant_id': self.id,
            })
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying # applicant_id=self.id
        return self.survey_id.with_context(survey_token=response.token).action_start_kw_recruitment_survey()

    @api.multi
    def view_recruitment_survey(self):
        """ If response is available then print this response
        otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_recruitment_survey()
        else:
            response = self.response_id
            return self.survey_id.with_context(survey_token=response.token).action_print_recruitment_survey()

    # @api.multi
    # def action_get_attachment_tree_view(self):
    #     attachment_action = self.env.ref('base.action_attachment')
    #     action = attachment_action.read()[0]
    #     action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0], 'default_name': self.name, }
    #     action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
    #     action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id,)
    #     return action

    def update_qualifications(self):
        applicants = self.env['hr.applicant'].search([('qualification', '!=', ''), ('qualification_ids', '=', False)])
        if applicants:
            for app in applicants:
                qid = self.env['kw_qualification_master'].search([('name', '=ilike', app.qualification.name)])
                if qid:
                    app.write({'qualification_ids': [(6, 0, [qid.id])]})

    def update_applicant_stage(self):
        applicants = self.env['hr.applicant'].search([('stage_id.code', 'not in', ['IQ', 'FI', 'SI', 'OR', 'OA'])])
        if applicants:
            for app in applicants:
                meeting = self.env['kw_meeting_events'].search_count([('applicant_ids', '=', app.id)])
                if meeting == 1:
                    FI_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'FI')])
                    app.write({'stage_id': FI_stage.id})
                elif meeting == 2:
                    SI_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'SI')])
                    app.write({'stage_id': SI_stage.id})

    def archieve_applicants(self):
        applicants = self.env['hr.applicant'].search([('kanban_state', '=', 'blocked')])
        if applicants:
            for app in applicants:
                app.write({'active': False})

    def shortlist_applicant(self):
        shortlist_stage = self.env['hr.recruitment.stage'].sudo().search([('code', '=', 'SH')], limit=1)
        if shortlist_stage:
            self.write({
                'stage_id': shortlist_stage.id,
                'is_screening_completed': True,
            })
            mail_to = self.responsible_id.email
            view_id = self.env.ref('hr_recruitment.crm_case_categ0_act_job').id
            template_id = self.env.ref('kw_recruitment.applicant_shortlist_mail_template')
            template_id.with_context(emails=mail_to, view_id=view_id, record_id=self.id).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Applicant Shortlisted Successfully")
    def mismatch_applicant(self):
        mismatch_stage = self.env['hr.recruitment.stage'].sudo().search([('code', '=', 'PM')], limit=1)
        if mismatch_stage:
            self.write({
                'stage_id': mismatch_stage.id,
                'is_screening_completed': True,
            })
            mail_to = self.responsible_id.email
            view_id = self.env.ref('hr_recruitment.crm_case_categ0_act_job').id
            template_id = self.env.ref('kw_recruitment.applicant_mixmatch_mail_template')
            template_id.with_context(emails=mail_to, view_id=view_id, record_id=self.id).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Applicant Profile Mismatch sent Successfully")        
        
    @api.multi
    def action_makeoffer(self):
        if self.budget_amount < 1:
            raise ValidationError(_('Budget Amount is not updated.'))
        if not self.mrf_id:
            raise ValidationError(_('Please select the MRF before creating the offer letter.'))
        if not self.offer_date:
            raise ValidationError(_('Please select the offer Date before creating the offer letter.'))

        if not self.joining_date:
            raise ValidationError(_('Please select the Joining Date before creating the offer letter.'))

        if self.offer_date:
            date = self.offer_date
        else:
            date = datetime.now().date()
        # print('datedatedatedatedate', date)

        if not self.offer_id:
            view_id = self.env.ref('kw_recruitment.view_hr_applicant_offer').id
            action = {
                'name': 'Offer Letter',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.applicant.offer',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'view_id': view_id,
                'context': {'default_designation': self.job_id.id,
                            'default_department': self.department_id.id,
                            'default_joining_date': self.joining_date,
                            'default_acceptance_date': self.acceptance_date,
                            'default_current_date': date,
                            'default_name': self.partner_name,
                            'default_job_location_id': self.job_location_id.id,
                            'default_applicant_id': self.id},
            }
            return action
        else:
            raise UserError(
                _('You have already created the offer letter to edit, please click on below offer letter field'))
                
    @api.constrains('stage_id')
    def restricting_stage_changes(self):
        offer_letters = self.env['hr.applicant.offer'].sudo().search([('applicant_id', '=', self.id)])
        self.offer_id = offer_letters.id
        if self.stage_id.code in ['OR'] and not self.offer_id:
            raise ValidationError("You can't go to Offer Release stage before offer creation")

    @api.multi
    def archive_applicant(self):
        self.write({'active': False})
        mail_to = self.employee_referred.work_email
        # print("mail",mail_to)
        template_id = self.env.ref('kw_recruitment.applicant_refused_mail_to_employee_referred')
        template_id.with_context(emails=mail_to).send_mail(self.id,
                                                           notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Applicant details mail sent successfully.")

    @api.multi
    def view_referrel_report(self):
        tree_view_id = self.env.ref('kw_recruitment.ijp_hr_applicant_referral_report_view_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Employee Referral Report',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'res_model': 'hr.applicant',
            'domain': [('source_id.code', '=', 'employee')]
            # 'domain': [('employee_referred.user_id', '=', self.env.user.id)]
        }
        return action
        # if  self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):  
        #     action['domain'] = [('employee_referred','!=', False)]
        # else:
        #     action['domain']=[('employee_referred.user_id','=', self.env.user.id)]
        # return action

    @api.multi
    def panel_screening_reminder(self):
        # print("self=========",self)
        view_id = self.env.ref('kw_recruitment.sreening_actions_window').id
        applicants = self.env['hr.applicant'].search(
            [('stage_id.code', '=', 'SC'), ('is_screening_completed', '!=', True),
             ('job_position.state', '=', 'recruit')])
        # print("applicant=======",applicants)
        panel_member = applicants.mapped('job_position.panel_member')
        # print("panel=======================",panel_member)
        stage_record = self.env['hr.applicant.stage']

        # print("panel++++++++",panel_member)

        for member in panel_member:
            applicants_ids = applicants.filtered(lambda r: member.id in r.job_position.panel_member.ids)
            applicant_list = []
            for applicant in applicants_ids:
                stage_record_id = stage_record.sudo().search(
                    [('to_stage.name', 'ilike', 'Screening'), ('applicant_id', '=', applicant.id)], order='id desc',
                    limit=1)
                # print("stage_record_id create====",stage_record_id.create_date)
                if stage_record_id.create_date and stage_record_id.create_date < datetime.now():
                    # print("11111111",(datetime.now() - stage_record_id.create_date).total_seconds() / 3600)
                    if ((datetime.now() - stage_record_id.create_date).total_seconds() / 3600) > 24:
                        applicant_list.append(applicant)
            if applicant_list:
                panel_email = member.mapped('work_email')[0] if member.mapped('work_email') else ''
                # print("panel_email====",panel_email)
                panel_member_name = member.mapped('name')[0] if member.mapped('name') else ''
                # print("panel_memb/er_name====",panel_member_name)
                screening_log = self.env['screening_reminder_log'].sudo().create({
                    'schedule_date': datetime.now(),
                    'payload': applicant_list,
                    'status': 'Success',
                })
                template_id = self.env.ref('kw_recruitment.screening_reminder_mail_to_panel_member')
                template_id.with_context(emails=panel_email, applicant=applicant_list, panel_member_name=panel_member_name,view_id=view_id).send_mail(screening_log.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Screening Reminder sent successfully.")

    def ijp_cc_mail(self):
        mail_to_hr = self.env.ref('kw_recruitment.group_internal_job_posting_mail_notify').users
        cc_emails = ','.join(mail_to_hr.mapped('partner_id.email')) if mail_to_hr else ''
        if self.job_position.hr_responsible_id and self.job_position.hr_responsible_id.partner_id.email :
            cc_emails += ','+self.job_position.hr_responsible_id.partner_id.email
        return cc_emails
    
    
# class EducationalData(models.Model):
#     _inherit="kwonboard_edu_qualification"


#     applican_id = fields.Many2one('hr.applicant', string="Applicant ID") 
