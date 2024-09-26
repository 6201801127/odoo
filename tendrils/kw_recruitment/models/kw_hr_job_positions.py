# -*- coding: utf-8 -*-
import base64
import logging
import requests, json
import bs4 as bs
from datetime import date
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.modules.module import get_module_resource
from odoo.addons.http_routing.models import ir_http


class JobPositions(models.Model):
    _name = "kw_hr_job_positions"
    _description = "Job Openings"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.multi.mixin']
    # _rec_name = 'title'
    _order = 'is_published desc,title asc'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        job_ids = []
        if name:
            job_ids = self._search(
                ['|', ('title', operator, name), ('job_code', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        else:
            job_ids = self._search([] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(job_ids).name_get()

    @api.model
    def _get_year_list(self):
        years = 30
        return [(str(i), i) for i in range(years + 1)]

    @api.model
    def _get_month_list(self):
        months = 12
        return [(str(i), i) for i in range(months)]

    @api.model
    def unpublish_expired_jobs(self):
        curr_date = date.today()
        expired_jobs = self.search([('state', '=', 'recruit'), ('expiration', '<', curr_date)])
        if expired_jobs:
            expired_jobs.set_open()

    # #####------------------------Fields----------------------######
    # Recruitment Section
    mrf_id = fields.Many2one('kw_recruitment_requisition', string='Manpower Requisition',
                             domain=[('kw_job_id', '=', False), ('state', 'in', ['approve'])])
    job_id = fields.Many2one('hr.job', string='Job Position',
                             required=True, index=True, translate=True, ondelete='restrict')
    website_id = fields.Many2one('website', string='Website', )
    department_id = fields.Many2one('hr.department', string='Department' ,
                                    domain=[('parent_id', '=', False)], )
    survey_id = fields.Many2one('survey.survey', string='Interview Form', domain=[('survey_type.code', '=', 'recr')])
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)
    address_id = fields.Many2many('kw_recruitment_location', string="Job Location", required=True, )
    description = fields.Text(string='Job Details', required=True)
    summary = fields.Text(string='Summary', required=True)
    no_of_recruitment = fields.Integer(string='No. of Post', copy=False,
                                       help='Number of new employees you expect to recruit.', default=1)
    qualification = fields.Many2many(string='Qualification', comodel_name='kw_qualification_master', required=True)
    responsibility = fields.Text(string="Responsibility", )
    # experience_id = fields.Many2one(string='Experience',comodel_name='kw_job_experience',ondelete='restrict',)
    min_exp_year = fields.Selection(string='Min. Years', selection='_get_year_list', default="0")
    min_exp_month = fields.Selection(string='Min. Months', selection='_get_month_list', default="0")
    max_exp_year = fields.Selection(string='Max. Years', selection='_get_year_list', default="0")
    max_exp_month = fields.Selection(string='Max. Months', selection='_get_month_list', default="0")
    title = fields.Char(string='Job Position', required=True)
    job_publish_date = fields.Datetime("Publish Date", default=fields.Datetime.now)

    # Offer section
    hr_responsible_id = fields.Many2one('res.users', string='HR Responsible', )
    expiration = fields.Date(string='Expires On', default=fields.Date.context_today, )
    job_code = fields.Char(string='Designation Code', required=True)
    user_id = fields.Many2one('res.users', string='Recruitment Responsible', )
    applicant_survey_id = fields.Many2one('survey.survey', string='Applicant Feedback Form', domain=[('survey_type.code', '=', 'recr')])
    application_ids = fields.One2many('hr.applicant', 'job_position', "Applications")
    state = fields.Selection([('recruit', 'Recruitment in Progress'), ('open', 'Not Recruiting')],
                             string='Status', readonly=True, required=True, track_visibility='always',
                             copy=False, default='recruit', help="Set recruitment process is open or closed.")
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number of Employees",
                                    help='Number of employees currently occupying this job position.')
    no_of_hired_employee = fields.Integer(string='Hired Employees', copy=False,
                                          help='Number of hired employees for this job position during recruitment phase.')
    # application_count = fields.Integer(compute='_compute_application_count', string="Application Count")
    application_count = fields.Integer(string='No. Of Applications', compute="_compute_applicants")
    emp_category_id = fields.Many2one(string='Job Category', comodel_name='kw_job_category', ondelete='restrict', required=True)

    # shift = fields.Char(string="Shift", size=50)
    travel = fields.Boolean(string='Travel')
    # emp_status_id = fields.Many2one(string='Employee Type', comodel_name='kw_job_emp_status', ondelete='restrict',required=True, )
    industry_type = fields.Many2one(string='Functional Area', comodel_name='kw_industry_type', ondelete='restrict',
                                    required=True)
    candidate_profile = fields.Text(string='Candidate Profile', required=True)

    attachment = fields.Binary(string='Image for Website', attachment=True)
    file_name = fields.Char("File Name")
    attachment_id = fields.Char(compute='_compute_attachment_id')
    attachment_url = fields.Char(compute="_get_attachment_url")
    on_homepage = fields.Boolean(string='Show on Homepage')

    walk_in = fields.Boolean(string='Show In Walk-in')
    campus_drive = fields.Boolean('Show in Campus Drive')
    hide_in_website = fields.Boolean('Hide in Website')
    
    ###
    consultancy_id = fields.Many2many('res.partner', string='Consultancy',domain=[('consultancy','=',True)])
    panel_members_grp = fields.Many2one('kw_panel_members_master', string='Panel Members Group')
    internal_job_posting = fields.Boolean(string="Internal Job Openings",default=False)
    referred_amount = fields.Float(string='Referral Amount (INR)')

    enable_applicant_screening = fields.Boolean(string="Applicant Screening", default=True)
    panel_member = fields.Many2many('hr.employee', 'kw_hr_job_position_rel', 'employee_id', 'job_id',
                                    string='Screening Panel member')
    jd_skills_ids = fields.Many2many('jd_skills_master', 'skills_job_position_rel', 'skill_id', 'job_id',
                                    string='JD Skills')
    opening_for = fields.Selection([('global', 'Global'),('america', 'America'),('africa', 'Africa')])

    # #####--------------------------Fields------------------------######
    @api.onchange('enable_applicant_screening')
    def onchange_job_position(self):
        id = self.panel_member.ids
        if not self.enable_applicant_screening :
            self.panel_member = [(5, 0, 0)] 


    @api.constrains('expiration')
    def check_expiration(self):
        curr_date = date.today()
        for record in self:
            if record.expiration and str(record.expiration) < str(curr_date):
                raise ValidationError("Expiration date should not less than current date.")

    @api.constrains('max_exp_year','min_exp_year')
    def check_exp_year(self):
        for record in self:
            if record.max_exp_year and record.min_exp_year:
                if int(record.max_exp_year) < int(record.min_exp_year):
                    raise ValidationError("Min Years can't be greater than Max Years.")

    @api.model
    def _compute_attachment_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kw_hr_job_positions'), ('res_field', '=', 'attachment')])
            attachment_data.write({'public': True})
            record.attachment_id = attachment_data.id

    @api.model
    def _get_attachment_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.attachment_id:
                # attachment_data = self.env['ir.attachment'].browse([record.attachment_id])
                # attachment_data.public = True
                final_url = '%s/web/image/%s' % (base_url, record.attachment_id) if record.attachment_id else ''
                record.attachment_url = final_url
            else:
                record.attachment_url = ''

    # #####-------------------Constraint Validations---------------######
    @api.multi
    def name_get(self):
        rec = []
        for record in self:
            if record.job_code:
                rec.append((record.id, f"{record.title}({record.job_code})"))
            else:
                rec.append((record.id, record.title))
        return rec
        # return [(record.id, f'{record.title}  {record.job_code or ""}') for record in self]

    @api.multi
    def _compute_applicants(self):
        applicant = self.env['hr.applicant']
        for record in self:
            # if self._context.get('ijp_applicant'):
            if self._context.get('referred_candidate'):
                record.application_count = applicant.search_count(
                    [('employee_referred.user_id', '=', self.env.user.id), ('job_position', '=', record.id)])
            else:
                record.application_count = applicant.search_count([('job_position', '=', record.id)])

            #['&', ('job_position', '=', record.id), ('stage_id.sequence', '=', '0')]
            # ['&', ('job_position', '=', record.id), ('stage_id.name', '=', 'Initial Screening')])

    # @api.constrains('job_id', 'address_id', 'title')
    # def validate_job_locations(self):
    #     rec = self.env['kw_hr_job_positions'].search([]) - self
    #     for data in rec:
    #         if data.job_id.id == self.job_id.id and \
    #                 data.address_id.id == self.address_id.id and \
    #                 data.title and data.title.lower() == self.title.lower():
    #             raise ValidationError(
    #                 f"Job title '{self.title}', job position '{self.job_id.name}' and  job location '{data.address_id.name}' is exists.")

    # @api.constrains('job_code')
    # def validate_job_code(self):
    #     data = self.env['kw_hr_job_positions'].search([]) - self
    #     for record in data:
    #         if record.job_code and record.job_code.lower() == self.job_code.lower():
    #             raise ValidationError(
    #                 f"Job code {self.job_code} is already given for job {self.job_id.name}.Please try with a different one.")

    # #####-------------------Constraint Validations---------------######

    # #####--------------------Computed Methods------------------######
    @api.multi
    def _compute_application_count(self):
        read_group_result = self.env['hr.applicant'].read_group([('job_position', 'in', self.ids)], ['job_position'], ['job_position'])
        result = dict((data['job_position'][0], data['job_position_count']) for data in read_group_result)
        for job in self:
            job.application_count = result.get(job.id, 0)

    @api.multi
    def _compute_employees(self):
        for record in self:
            record.no_of_employee = self.env['hr.employee'].search_count([('job_id', '=', record.job_id.id)])

    # #####--------------------Computed Methods--------------------######

    # #####--------------------Button Action Methods-----------------######
    @api.multi
    def set_recruit(self):
        curr_date = date.today()
        for record in self:
            if record.expiration and str(record.expiration) < str(curr_date):
                raise ValidationError("Expiration date should not less than current date.")
            else:
                no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
                record.write({
                    'state': 'recruit',
                    'no_of_recruitment': no_of_recruitment,
                    'website_published': True,
                    'job_publish_date': date.today(),
                })
                record.job_id.website_published = True
            return True

    @api.multi
    def set_open(self):
        return self.write({
            'state': 'open',
            'no_of_recruitment': 0,
            'no_of_hired_employee': 0,
            'website_published': False
        })
    
    @api.multi
    def send_job_opening_notification(self):
        if self.internal_job_posting:
            # print("wwww",','.join(self.qualification.mapped('name')).replace(',',' / '))
            # print("eeeeee",','.join(self.address_id.mapped('name')).replace(',',' / '))
            # print(f"{self.title}({self.job_code})")
            # return
            ijp_mail_notify = self.env.ref('kw_recruitment.group_internal_job_posting_mail_notify').users

            # emp_data = self.env['res.users'].sudo().search([])
            # ijp_mail_notify = emp_data.filtered(lambda user: user.has_group('kw_recruitment.group_internal_job_posting_mail_notify'))
            if ijp_mail_notify:
                mail_cc = ','.join(ijp_mail_notify.mapped('employee_ids.work_email'))
                # mail_cc = user.employee_ids.work_email if user.employee_ids.work_email else ''
                # print("mail------------------->>>>>>>>>>",mail_cc)
                template_id = self.env.ref('kw_recruitment.ijp_job_opening_mail_notification')
                template_id.with_context(job_name=f"{self.title}",
                                         email_from=self.env.user.employee_ids.work_email,
                                         email_to='csm@csm.tech',
                                         email_cc=mail_cc,
                                         position=self.job_id.name,
                                         experience=f"{self.min_exp_year} - {self.max_exp_year} Years",
                                        qualification=','.join(self.qualification.mapped('name')).replace(',',' / '),
                                        job_location=','.join(self.address_id.mapped('name')).replace(',',' / ')).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("IJP Mail Notification sent successfully.")

    @api.multi
    def view_job_details(self):
        url = f"/jobs/detail/{ir_http.slug(self)}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    @api.multi
    def view_job_applications(self):
        kanban_view_id = self.env.ref('hr_recruitment.hr_kanban_view_applicant').id
        tree_view_id = self.env.ref('hr_recruitment.crm_case_tree_view_job').id
        form_view_id = self.env.ref('hr_recruitment.crm_case_form_view_job').id
        calendar_view_id = self.env.ref('hr_recruitment.hr_applicant_calendar_view').id
        graph_view_id = self.env.ref('hr_recruitment.crm_case_graph_view_job').id
        pivot_view_id = self.env.ref('hr_recruitment.crm_case_pivot_view_job').id
        activity_view_id = self.env.ref('hr_recruitment.crm_case_pivot_view_job').id
        action = {'type': 'ir.actions.act_window',
                  'name': self.title,
                  'res_model': 'hr.applicant',
                  'view_mode': 'kanban,tree,form,pivot,graph,calendar,activity',
                  'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form'),
                            (pivot_view_id, 'pivot'), (graph_view_id, 'graph'), (calendar_view_id, 'calendar'),
                            (activity_view_id, 'activity')],
                  'context': {'search_default_job_position': self.ids, 'ijp_view': True},
                  'search_view_id': (self.env.ref('hr_recruitment.view_crm_case_jobs_filter').id,)}
        return action
    
    @api.multi
    def view_referred_applicant(self):
        kanban_view_id = self.env.ref('kw_recruitment.internal_job_opening_kanban').id
        tree_view_id = self.env.ref('hr_recruitment.crm_case_tree_view_job').id
        form_view_id = self.env.ref('kw_recruitment.ijp_applicant_job_openings_form_view').id
        calendar_view_id = self.env.ref('hr_recruitment.hr_applicant_calendar_view').id
        graph_view_id = self.env.ref('hr_recruitment.crm_case_graph_view_job').id
        pivot_view_id = self.env.ref('hr_recruitment.crm_case_pivot_view_job').id
        activity_view_id = self.env.ref('hr_recruitment.crm_case_pivot_view_job').id
        action = {'type': 'ir.actions.act_window',
                  'name': self.title,
                  'res_model': 'hr.applicant',
                  'view_mode': 'kanban,tree,form,pivot,graph,calendar,activity',
                  'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form'),
                            (pivot_view_id, 'pivot'), (graph_view_id, 'graph'), (calendar_view_id, 'calendar'),
                            (activity_view_id, 'activity')],
                  'context': {'search_default_job_position': self.ids, 'ijp_view': True, 'ijp_applicant': True},
                  'domain': [('employee_referred.user_id', '=', self.env.user.id)],
                  'search_view_id': (self.env.ref('hr_recruitment.view_crm_case_jobs_filter').id,)}
        return action

    def action_job_details(self):
        form_view_id = self.env.ref('kw_recruitment.job_openings_form_view').id
        return {
            'name': 'Job Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_hr_job_positions',
            'view_mode': 'form',
            'view_id': form_view_id,
            'res_id': self.id,
            'target': 'self',
            # 'flags': {'mode': 'readonly'},
            'context': {'create': False, 'edit': False, 'delete': False, 'import': False},
        }
    
    def apply_for_self(self):
        # import pdb
        # pdb.set_trace()
        form_view_id = self.env.ref('kw_recruitment.ijp_applicant_job_openings_form_view').id
        source_id = self.env['utm.source'].sudo().search([('code', '=', 'IJP')], limit=1)
        self_source_id = self.env['utm.source'].sudo().search([('code', '=', 'self')], limit=1)
        experience = []
        for word in self.env.user.employee_ids.total_experience_display.split():
            if word.isdigit():
                experience.append(int(word))

        certifications = []
        for certification in self.env.user.employee_ids.educational_details_ids:
            if certification.course_type == '3':
                certifications.append(certification.stream_id.name)

        passout_year_list = []
        education_list = []
        education_data = False
        data=''                                        #change for apply self educational data not auto showing
        if self.env.user.employee_ids.educational_details_ids:
            education_list.clear()
            passout_year_list.clear()
            for rec in self.env.user.employee_ids.educational_details_ids.filtered(lambda x: x.course_type == '1'):
                passout_year_list.append(int(rec.passing_year))
            passout_year_list.sort()
            highest_quali = passout_year_list[-1]
            qualification = self.env['kw_qualification_master']
            for value in self.env.user.employee_ids.educational_details_ids:
                if int(value.passing_year) == int(highest_quali) and value.course_type == '1':
                    qualification_name = value.stream_id.name
                    qualification_id = qualification.sudo().search([('name', '=', qualification_name)], limit=1)
                    if not qualification_id:
                        qualification_id = qualification.sudo().create({'name': qualification_name})
                    education_list.append(qualification_id.id)
                if value.course_type == '2':
                    qualification_name = value.stream_id.name
                    qualification_id = qualification.sudo().search([('name', '=', qualification_name)], limit=1)
                    if not qualification_id:
                        qualification_id = qualification.sudo().create({'name': qualification_name})
                    education_list.append(qualification_id.id)
            
        action = {
            'name': 'Apply for self',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'context': {'create': True,
                        'edit': True,
                        'delete': False,
                        'import': False,
                        # 'default_source_id': source_id.id,
                        'default_source_id': self_source_id.id,
                        # 'default_employee_referred': self.env.user.employee_ids.id,
                        'default_job_position': self.id,
                        'default_partner_name': self.env.user.employee_ids.name,
                        'default_email_from': self.env.user.employee_ids.work_email,
                        'default_partner_mobile': self.env.user.employee_ids.mobile_phone,
                        'default_current_location': self.env.user.employee_ids.job_branch_id.alias,
                        'default_gender': self.env.user.employee_ids.gender,
                        'default_exp_year': experience[0] if experience else 0,
                        'default_exp_month': experience[1] if experience else 0,
                        'default_qualification_ids': [(6, 0, education_list)] if education_list else '',
                        # 'default_highest_qualification_ids': [(6, 0, hihest_qualification)] if hihest_qualification else '',
                        'default_certification': ', '.join(certifications) if certifications else '',
                        'ijp_view': True,
                        'default_code_ref': source_id.code,
                        },
        }

        # print("action======",action)
        return action
    
    def refer_a_candidate(self):
        form_view_id = self.env.ref('kw_recruitment.ijp_applicant_job_openings_form_view').id
        source_id = self.env['utm.source'].sudo().search([('code', '=', 'employee')], limit=1)

        return {
            'name': 'Apply for self',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'context': {'create': True,
                        'edit': True,
                        'delete': False,
                        'import': False,
                        'default_source_id': source_id.id,
                        'default_employee_referred': self.env.user.employee_ids.id,
                        'default_job_position': self.id,
                        'default_is_referred': True,
                        'referred_candidate': True,
                        'ijp_view': True,
                        'default_code_ref': source_id.code,
                        },
         }

    @api.multi
    def view_employees(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.job_id.name,
            'context': {'search_default_job_id': self.job_id.ids},
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            # 'domain': [('job_id', 'in', self.job_id.ids)],
        }

    @api.model
    def create(self, values):
        result = super(JobPositions, self).create(values)
        if values.get('mrf_id'):
            self.env['kw_recruitment_requisition'].search([('id', '=', values.get('mrf_id'))]).write(
                {'kw_job_id': result.id})
        # self.env.user.notify_success("Job Opening created successfully.")
        result.website_published = True
        return result

    @api.multi
    def write(self, values):
        group_panel_members = self.env.ref('kw_recruitment.group_hr_recruitment_pannel_member', False)
        old_panel_members_ids = []
        if 'panel_member' in values:
            for rec in self.panel_member:
                old_panel_members_ids = self.mapped('panel_member')

        res = super(JobPositions, self).write(values)

        for old_member in old_panel_members_ids:
            members = self.env['kw_hr_job_positions'].search([('state', '!=', 'open')])
            emp = members.mapped('panel_member').ids
            if old_member.id not in emp:
                if old_member.user_id:
                    group_panel_members.sudo().write({'users': [(3, old_member.user_id.id)]})

        for rec in self.panel_member:
            for record in rec.user_id:
                if not record.user_id:
                    record.sudo().write({'groups_id': [(4, group_panel_members.id)]})
        return res

    @api.multi
    def unlink(self):
        result = super(JobPositions, self).unlink()
        # self.env.user.notify_success("Job Opening(s) deleted successfully.")
        return result

    # #####--------------------Button Action Methods @-----------------######
    # Trigger website publish action
    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        if not self.website_published:
            job_id = self.job_id if self.job_id else False
            if job_id:
                job_id.website_published = True

        if self.env.user.has_group('website.group_website_publisher') and self.website_url != '#':
            # Force website to land on record's website to publish/unpublish it
            if 'website_id' in self and self.env.user.has_group('website.group_multi_website'):
                self.website_id._force()
            return self.open_website_url()
        return self.write({'website_published': not self.website_published})

    @api.constrains('description')
    def _check_description(self):
        for record in self:
            if len((bs.BeautifulSoup(record.description, features="lxml")).text.strip()) == 0:
                raise ValidationError('Description cannot be empty')

    @api.constrains('candidate_profile')
    def _check_candidate_profile(self):
        for record in self:
            if len((bs.BeautifulSoup(record.candidate_profile, features="lxml")).text.strip()) == 0:
                raise ValidationError('Candidate profile cannot be empty')