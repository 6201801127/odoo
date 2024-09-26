from calendar import month
import datetime
import re
from lxml import etree
import uuid
from datetime import date, timedelta
from ast import literal_eval
from xml import dom
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class EducationMaster(models.Model):
    _name = 'kw_eq_educational_qualification_master'
    
 
class EQResource(models.Model):
    _name = 'kw_recruitment_eq_tm_mif'   
class MIFAppMenuWizard(models.TransientModel):
    _name = 'mif.app.menu.wizard'
    _description = 'MIF App Menu Wizard'

    

    def action_for_tm_resource(self):
        eq_resource = self.env['kw_eq_resources_data'].sudo().search([('resource_material_id','!=',False)])
        eq_mif = self.env['kw_recruitment_eq_tm_mif'].sudo().search([]).mapped('resource_id')
        for rec in eq_resource:
            # print('rec.resource_material_id.kw_oppertuinity_id.client_name============',rec.resource_material_id.kw_oppertuinity_id.client_name)
            if len(eq_mif) == 0 or rec.id not in eq_mif.ids:
                create_dict = {
                'opp_code':rec.resource_material_id.kw_oppertuinity_id.code,
                'opp_id':rec.resource_material_id.kw_oppertuinity_id.id,
                'resource_id':rec.id,
                'computer_provision':rec.computer_provision,
                'number_of_resource': rec.number_of_resource,
                'year_of_experience': rec.year_of_experience ,
                'estimation_id':rec.resource_material_id.id,
                'eq_category':rec.eq_category,
                'skill':rec.skill,
                'specialization':rec.specialization,
                'skill_description':rec.skill_description,
                'position':rec.position,
                'minimum_educational_qualification_id':rec.minimum_educational_qualification_id.id,
                'work_location':rec.work_location,
                'work_location_id':[[6,0,rec.work_location_id.ids]],
                'location':rec.location,
                'detailed_experience':rec.detailed_experience,
                'job_description':rec.job_description,
                'csg_head_id': rec.resource_material_id.kw_oppertuinity_id.csg_head_id.id,
                'duration_of_engagement':rec.duration_of_engagement,
                'days':rec.days,
                'presales_tl_id': rec.resource_material_id.kw_oppertuinity_id.presales_id.id,
                'acc_manager_id':rec.resource_material_id.kw_oppertuinity_id.sales_person_id.id,
                # 'presales_member_id' :rec.resource_material_id.kw_oppertuinity_id,
                # self.presales_tl_id = 
                # self.presales_member_id = 
                'pm_id' :rec.resource_material_id.kw_oppertuinity_id.pm_id.id,
                # self.sbu_lead_id = 
                'project_reviewer_id' : rec.resource_material_id.kw_oppertuinity_id.reviewer_id.id,
                'eq_ctc':rec.first_year,
                'client_name':rec.resource_material_id.kw_oppertuinity_id.client_name
                }
                self.env['kw_recruitment_eq_tm_mif'].sudo().create(create_dict)
        tree_view_id = self.env.ref("kw_eq.kw_recruitment_eq_tm_mif_view_tree").id
        # form_view_id = self.env.ref("kw_eq.kw_recruitment_eq_tm_mif_view_form").id
        return {
            'name': 'Resourc Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'res_model': 'kw_recruitment_eq_tm_mif',
            'target': 'self',
            # 'domain': [('id', 'in', mif_list)],
        }
       

    def action_for_other_resource(self):
        # tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
        form_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form").id
        return {
            'name': 'Manpower Indent Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_manpower_indent_form',
            'target': 'self',
            'flags':{'create': True},
            # 'domain': [('domain_name', '=', self.domain_name), ('client_name', '=', self.client_name)],
        }
       
class RequisitionResourceLog(models.Model):
    _name = 'kw_manpower_indent_form_log'
    _description = 'Manpower Indent Form Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    mif_id = fields.Many2one('kw_manpower_indent_form', 'MIF', ondelete='cascade')
    approver_id = fields.Many2one('hr.employee', string="Approver")
    from_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Pending'),
        ('hold', 'Hold'),
        ('revise', 'Revise'),
        ('forward', 'Forwarded'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3)
    to_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Pending'),
        ('hold', 'Hold'),
        ('revise', 'Revise'),
        ('forward', 'Forwarded'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3)


class RequisitionResource(models.Model):
    _name = "kw_manpower_indent_form"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Manpower Indent Form"
    _rec_name = "code"
    _order = "id desc"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def get_domain(self):
        if not self.env.user.has_group("kw_resource_management.group_budget_manager"):
            current_employee = self.env.user.employee_ids
            department_id = current_employee.department_id.id if current_employee else False
            return [('employement_type.code', '!=', 'O'), ('department_id', '=', department_id)]
        else:
            return [('employement_type.code', '!=', 'O')]
    
    def get_fiscal_year(self):
        current_date = date.today()
        current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', current_date), ('date_stop', '>=', current_date)], limit=1)
        return current_fiscal_year_id

    current_fy = fields.Many2one('account.fiscalyear', string='Fiscal Year',default= get_fiscal_year,readonly = "1" )
    code = fields.Char(string="Reference No.", default="New", readonly="1")
    req_raised_by_id = fields.Many2one('hr.employee', string="Request Raised by Employee", default=_default_employee,
                                       domain=lambda self: self.get_domain())
    current_user = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_ids.id)
    dept_name = fields.Many2one('hr.department', related="req_raised_by_id.department_id", string='Department',
                                track_visibility='always', readonly="1", store=True)
    sbu_id = fields.Many2one(comodel_name="kw_sbu_master", related="req_raised_by_id.sbu_master_id",
                             string="SBU/Horizontal", store=True)
    division = fields.Many2one('hr.department', string="Division")
    resource = fields.Selection(string='Resource Type', track_visibility='onchange',
                                selection=[('new', 'New'), ('replacement', 'Replacement')],
                                default='new', help="Set recruitment process is employee type.")
    employee_id = fields.Many2many('hr.employee', string='Employee Name', track_visibility='onchange',
                                   domain=['|', ('active', '=', True), ('active', '=', False)])
    job_position = fields.Many2one('hr.job', track_visibility='onchange')
    date_requisition = fields.Date(string='Date of Requisition', default=fields.Date.context_today,
                                   track_visibility='onchange')
    no_of_resource = fields.Integer('No. of Resources', track_visibility='onchange', default='1')
    qualification = fields.Text('Educational Qualification', track_visibility='onchange')
    experience = fields.Char("Work Experience", track_visibility='onchange')
    # min_exp_year = fields.Selection(string='Min. Years', selection='_get_year_list', default="0",
                                    # track_visibility='onchange')
    min_exp_year = fields.Integer(string='Min. Years',track_visibility='onchange')                               
    # max_exp_year = fields.Selection(string='Max. Years', selection='_get_year_list', default="0",
    #                                 track_visibility='onchange')
    max_exp_year = fields.Integer(string='Max. Years',track_visibility='onchange')                               
    description = fields.Text('Comment', track_visibility='onchange')
    engagement_period = fields.Selection([('Permanent', 'Permanent'), ('Specified_period', 'Specified period')],
                                         string='Engagement Period', track_visibility='onchange')

    months = fields.Integer('Engagement Period (Months)')
    year = fields.Integer('Engagement Period (Year)')

    effective_date_of_deployment = fields.Date(string="Effective Date of Deployment")

    approved_user_id = fields.Many2one("hr.employee", string="Pending At")

    state = fields.Selection([('Draft', 'Draft'), ('Applied', 'Applied'),
                              ('hold', 'Hold'), ('forward', 'Forwarded'), ('Approved', 'Approved'), ('Grant', 'Grant'),
                              ('Rejected', 'Rejected'),
                              ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange',
                             track_sequence=3, default='Draft')
    job_role_desc = fields.Html(string="Job Description",store=True)
    type_project = fields.Selection(string='Type Of Project',
                                    selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                    help="Set recruitment process is work order.")
    type_recruitment = fields.Selection(string='Type Of Resource Recruitment',
                                        selection=[('Deployment', 'Resource Deployment'),
                                                   ('Development', 'Resource Development')],
                                        help="Set recruitment process is Deployment/Development.")
    project = fields.Many2one('crm.lead', string='Project', track_visibility='onchange')
    # client_name = fields.Char(string="Client Name", related="project.client_name", store=True)
    project_code = fields.Char(string="Project Code", related="project.code", store=True)
    branch_id = fields.Many2many('kw_recruitment_location', string="Work Location")
    it_infra_provision = fields.Selection([('Client', 'Client'), ('CSM', 'CSM'),
                                           ], string="Computer Provision")
    technology = fields.Many2one('kw_skill_master', string="Technology")
    account_manager = fields.Char(string="Account Manager")
    project_manager = fields.Char(string="Project Manager")
    presales_member = fields.Char(string="Presales Member")

    sbu_check = fields.Boolean(compute="_compute_boolean_check")
    rcm_manager_check = fields.Boolean(compute="_compute_boolean_check")
    dept_bool = fields.Boolean(compute="_compute_dept_name")
    sbu_bool = fields.Boolean(compute="_compute_dept_name")
    hod_check = fields.Boolean(compute="_compute_boolean_check")
    is_mif_user = fields.Boolean(compute="_compute_boolean_check")
    pending_at = fields.Many2one("hr.employee", string="Approved by")
    pending_at_txt = fields.Char(string="Approved", compute="_compute_pending_at")
    approved_by_txt = fields.Char(string="Approved", compute="_compute_pending_at")
    approval_date = fields.Date(string="Approval Date", readonly="1")

    project_manager_check = fields.Boolean()
    rcm_comment = fields.Text(string="RCM Comment")
    
    ####### For EQ Implementation field Add #######################
    eq_category = fields.Selection([('software_support','Software Support'),('social_media_management','Social Media Management'),('consultancy_service','Consultancy Service'),('staffing_service','Staffing Service'),
                                   ], string="EQ Category")
    skill = fields.Selection(string="Skill",selection=[('technical_expert', 'Technical Expert'), ('functional_expert', 'Functional Expert'),('subject_matter_expert', 'Subject Matter Expert'),('general', 'General')])
    position = fields.Text(string="Position")
    skill_description = fields.Text(string="Skill Description")

    days = fields.Integer('Engagement Period (days)')
    minimum_educational_qualification_id = fields.Many2one('kw_eq_educational_qualification_master')
    detailed_experience = fields.Text(string="Detailed Experience")
    skill_set = fields.Text('Specialization / Certification')

    work_location = fields.Selection(string="Work Location",selection=[('csm_office', 'CSM Office'), ('client_location', 'Client Location')])
    location = fields.Text()
    # work_location_id = fields.Many2one('kw_res_branch',string='Base Location')

    job_description = fields.Text(string="Job Description")

    # sales
    acc_manager_id = fields.Many2one('hr.employee')
    csg_head_id = fields.Many2one('hr.employee')
    # presales
    presales_tl_id = fields.Many2one('hr.employee')
    presales_member_id = fields.Many2one('hr.employee')
    # delivery
    pm_id = fields.Many2one('hr.employee')
    sbu_lead_id = fields.Many2one('hr.employee')
    project_reviewer_id = fields.Many2one('hr.employee')
    estimation_id = fields.Many2one('kw_eq_estimation')
    from_eq_bool = fields.Boolean(string="From EQ")
    
    opp_code = fields.Char(related='opp_id.code')
    opp_id = fields.Many2one('crm.lead')
    opp_name = fields.Char()
    client_name = fields.Char()
    eq_mif_id = fields.Many2one('kw_recruitment_eq_tm_mif')
    special_comment_pm = fields.Text()
    special_comment_sbu = fields.Text()
    # date_of_resource_final = fields.Date()
    # special_comment_rcm = fields.Text()
    # eq_ctc = fields.Float()
    from_eq_proposed_ctc = fields.Float(string="Proposed CTC")
    from_mif_pm_ctc = fields.Float(string="MIF PM CTC")
    created_mrf = fields.Boolean(string="Created MRF",compute="check_create_mrf")
    month_days = fields.Char(compute="compute_duration")
    project_name = fields.Char(related='project.name')
    sl_no = fields.Integer(compute='compute_sl_no')
    
    
    @api.depends('estimation_id')
    def compute_sl_no(self):
        sorted_records = self.search([('estimation_id','!=',False)], order='id desc')

        # Assign serial numbers sequentially
        for index, record in enumerate(sorted_records):
            record.sl_no = index + 1
    
    
    def check_create_mrf(self):
        for rec in self:
            if self.env['kw_recruitment_requisition'].sudo().search([('mif_rec_id','=',rec.id)]):
                rec.created_mrf = True
                
    @api.depends('months','days')
    def compute_duration(self):
        for rec in self:
            if rec.months>0 and rec.days >0:
                rec.month_days = f"{rec.months} Months and {rec.days} Days"
            elif rec.months>0 and rec.days == 0:
                rec.month_days = f"{rec.months} Months"
            elif rec.months == 0 and rec.days >0:
                rec.month_days = f"{rec.days} Days"
    
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(RequisitionResource, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #     return res
    
    
    @api.constrains('from_eq_proposed_ctc','from_mif_pm_ctc')
    def check_ctc(self):
        for rec in self:
            if rec.from_mif_pm_ctc == 0.0:
                raise ValidationError('CTC must be greater than 0.00')
            if rec.from_mif_pm_ctc > rec.from_eq_proposed_ctc and rec.from_eq_proposed_ctc > 0:
                raise ValidationError('CTC must be lesser than the Proposed CTC of EQ!')

    @api.depends('approved_user_id')
    def _compute_pending_at(self):
        for rec in self:
            if rec.approved_user_id:
                rec.pending_at_txt = rec.approved_user_id.display_name
            elif rec.state == 'Approved':
                rec.pending_at_txt = 'Pending at R&CM'
            else:
                rec.pending_at_txt = ''

            if rec.pending_at and rec.state != 'Rejected':
                rec.approved_by_txt = rec.pending_at.display_name

    @api.model
    def create(self, values):
        if 'code' in values:
            new_code = values.get('code')
        else:
            code = self.env['ir.sequence'].next_by_code('self.mif_seq') or 'New'
            dept_code = ''
            dept_name = values.get('dept_name', False)
            if dept_name:
                dept_rec = self.env['hr.department'].browse(int(dept_name))
                if dept_rec.code == 'BSS':
                    dept_code = 'DEL'
                else:
                    dept_code = dept_rec.code
            new_code = 'MIF/' + dept_code + code
            values['code'] = new_code
        result = super(RequisitionResource, self).create(values)
        if result.state == 'draft':
            self.env['kw_manpower_indent_form_log'].create({
                'mif_id': result.id,
                'from_status': result.state,
                'to_status': result.state,
                'approver_id': result.env.user.employee_ids.id
            })
        print('result.eq_mif_id==============',result.eq_mif_id)
        if result.eq_mif_id:
            # print(result.eq_mif_id.mif_id,"==============result.eq_mif_id.mif_id")
            result.eq_mif_id.mif_id = result.id
        self.env.user.notify_success("Manpower Indent Form created successfully.")
        return result

    @api.depends('dept_name')
    def _compute_dept_name(self):
        for mif in self:
            mif.sbu_bool = False
            # print("mif.dept_name.code >>> ", mif.dept_name.code, mif.sbu_id, mif.sbu_id is True, len(mif.sbu_id))
            if mif.dept_name.code == 'BSS':
                mif.sbu_bool = True
                if len(mif.sbu_id) > 0 and mif.sbu_id.type == 'sbu':
                    mif.dept_bool = True
            else:
                mif.dept_bool = False

    @api.depends('current_user')
    def _compute_boolean_check(self):
        sbu_record = self.env['kw_sbu_master'].sudo().search([('type', '=', 'sbu')])
        rec_list = []
        self.sbu_check = False
        self.rcm_manager_check = False
        self.hod_check = False
        self.is_mif_user = False

        for record in sbu_record:
            rec_list.append(record.representative_id.id)

        if self.env.user.employee_ids.id in rec_list \
                and self.env.user.employee_ids.id == self.approved_user_id.id:
            self.sbu_check = True
        elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                and self.env.user.employee_ids.id == self.approved_user_id.id:
            self.hod_check = True
        elif self.env.user.has_group('kw_resource_management.group_budget_manager'):
            self.rcm_manager_check = True
        elif self.env.user.has_group("kw_recruitment.group_kw_mif_user") \
                and not self.env.user.has_group('kw_resource_management.group_budget_manager'):
            self.is_mif_user = True

    @api.onchange('employee_id')
    def _check_employee_replacement(self):
        if self.employee_id:
            if len(self.employee_id) > 1:
                raise ValidationError('Choose only one replacement.')

    @api.onchange('type_project')
    def _onchange_project_type(self):
        if not self._context.get('available_data'):
            self.project = False
            if self.type_project == 'work':
                return {'domain': {'project': [('stage_id.code', '=', 'workorder')]}}
            elif self.type_project == 'opportunity':
                return {'domain': {'project': [('stage_id.code', '=', 'opportunity')]}}
            else:
                return{'domain': {'project': []}}

    @api.onchange('project')
    def _onchange_project_manager(self):
        self.project_manager = False
        if self.project:
            project_manager = self.env['project.project'].sudo().search([('crm_id', '=', self.project.id)])
            self.project_manager = project_manager.emp_id.name

    @api.onchange('dept_name')
    def onchange_department(self):
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.dept_name.id), ('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('job_position')
    def enable_role_type(self):
        if self.job_position:
            self.job_role_desc = False
            record = self.env['hr.job.role'].sudo().search([('designations', '=', self.job_position.id)])
            self.job_role_desc = record.description

    @api.model
    def _get_year_list(self):
        years = 30
        return [(str(i), i) for i in range(years + 1)]

    @api.multi
    def compute_pending_user(self):
        # pending_manager_user = self.env.ref('kw_resource_management.group_budget_manager').users
        # rcm_manager = ','.join(pending_manager_user.mapped('employee_ids.name')) if pending_manager_user else ''
        sbu_list = self.env['kw_sbu_master'].sudo().search([('type', '=', 'sbu')])
        rec_list = []
        for record in sbu_list:
            rec_list.append(record.representative_id.id)
        # for mif in self:
        #     if mif.state in ['Approved']:
        #         mif.pending_at = "Pending At RCM"
        #         mif.write({'approved_user_id' : False})
        #     elif mif.state in ['Applied'] and mif.req_raised_by_id.id in rec_list:
        #         mif.pending_at = "Pending At RCM"
        #     elif mif.state in ['Applied'] and mif.req_raised_by_id.user_id.has_group('kw_wfh.group_hr_hod'):
        #         mif.pending_at = "Pending At RCM"
        #     # elif mif.state in ['Grant']:
        #     #     mif.pending_at = "Approved By RCM"
        #     else:
        #         pass

    @api.multi
    def send_for_approval(self):
        # emp_id = []
        # pending_manager_user = self.env.ref('kw_resource_management.group_budget_manager').users
        # for record in pending_manager_user:
        #     emp_id.append(str(record.employee_ids.id))
        # rcm_manager = ','.join(emp_id) if pending_manager_user else ''
        mif_form = self.env.ref("kw_recruitment.view_kw_manpower_indent_form").id
        if self.req_raised_by_id.id != self.req_raised_by_id.sbu_master_id.representative_id.id \
                and self.req_raised_by_id.sbu_master_id.id != False\
                and self.req_raised_by_id.sbu_master_id.type == 'sbu' \
                and not self.req_raised_by_id.user_id.has_group('kw_resource_management.group_budget_manager') :
            # MIF Applied to SBU Head
            self.write({'approved_user_id': self.req_raised_by_id.sbu_master_id.representative_id.id,
                        'state': 'Applied'})
            template = self.env.ref("kw_recruitment.mail_notify_to_take_action")
            if template:
                mail_to = self.approved_user_id.work_email
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_cc = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="Applied",
                                                                                  mail_to=mail_to,
                                                                                  mail_cc=mail_cc).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')

        elif ((self.req_raised_by_id.sbu_master_id.id != False
               # and self.req_raised_by_id.id != self.req_raised_by_id.sbu_master_id.representative_id.id \
               and self.req_raised_by_id.sbu_master_id.type != 'sbu') \
              or self.req_raised_by_id.sbu_master_id.id == False) \
                and not self.req_raised_by_id.user_id.has_group('kw_resource_management.group_budget_manager') \
                and (not self.req_raised_by_id.user_id.has_group('kw_wfh.group_hr_hod')
                     or (self.req_raised_by_id.user_id.has_group('kw_wfh.group_hr_hod')
                         and self.req_raised_by_id.id != self.dept_name.manager_id.id)):
            # MIF Applied to HOD
            self.write({'approved_user_id': self.dept_name.manager_id.id,
                        'state': 'Applied'})
            template = self.env.ref("kw_recruitment.mail_notify_to_take_action")
            if template:
                mail_to = self.approved_user_id.work_email
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_cc = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="Applied",
                                                                                  mail_to=mail_to,
                                                                                  mail_cc=mail_cc).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')

        elif self.req_raised_by_id.user_id.has_group('kw_resource_management.group_budget_manager'):
            # Applied by RCM
            self.write({'state': 'Grant',
                        'pending_at': self.env.user.employee_ids.id})
            template = self.env.ref("kw_recruitment.mail_notify_to_grant_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_recruitment.group_kw_mif_user_notify') == True)
                manager_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_to = ",".join(manager_emp.mapped('employee_ids.work_email')) or ''
                mail = self.env['mail.template'].browse(template.id).with_context(email_to=mail_to).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')

        elif self.req_raised_by_id.user_id.has_group('kw_wfh.group_hr_hod')\
                and self.req_raised_by_id.id == self.req_raised_by_id.department_id.manager_id.id:
            # Applied by HOD
            self.write({'state': 'Approved', 'approval_date': date.today(), 'pending_at': self.req_raised_by_id.id})
            template = self.env.ref("kw_recruitment.mail_notify_to_take_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
                # notify_emp = users.filtered(lambda user: user.has_group('kw_recruitment.group_kw_mif_user_notify') == True)
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_to = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail_cc = ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="HOD_applied",
                                                                                  mail_to=mail_to,
                                                                                  mail_cc=mail_cc
                                                                                  ).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        else:
            # Applied by SBU Head / Representative
            self.write({'state': 'Approved', 'approval_date': date.today(), 'pending_at': self.req_raised_by_id.id})
            template = self.env.ref("kw_recruitment.mail_notify_to_take_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
                # notify_emp = users.filtered(lambda user: user.has_group('kw_recruitment.group_kw_mif_user_notify') == True)
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_to = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail_cc = ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="SBU_applied",
                                                                                  mail_to=mail_to,
                                                                                  mail_cc=mail_cc
                                                                                  ).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        return {
            'name': "Manpower Indent Form",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_manpower_indent_form',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': mif_form,
            "res_id": self.id,
            'target': 'current',
        }

    def send_for_cancel(self):
        for rec in self:
            rec.write({'state': 'Rejected',
                       'pending_at': None,
                       'approved_user_id': None,
                       'pending_at_txt': 'Rejected'})

    def approve_sbu_head(self):
        form_view_id = self.env.ref("kw_recruitment.mif_approve_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'notify_wizard_approved',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def approved_hod(self):
        form_view_id = self.env.ref("kw_recruitment.mif_approve_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'notify_wizard_approved',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def approved_rcm_mangaer(self):
        form_view_id = self.env.ref("kw_recruitment.mif_grant_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'notify_wizard_approved',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def action_reject(self):
        form_view_id = self.env.ref("kw_recruitment.mif_reject_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject',
            'res_model': 'notify_wizard_approved',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    @api.multi
    def action_create_mrf_details(self):
        form_view_id = self.env.ref("kw_recruitment.view_manpower_requisition_form_form").id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_recruitment_requisition',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'context': {'manpower_indent_form_context': True,
                        'default_mif_rec_id': self.id,
                        'default_dept_name': self.dept_name.id,
                        'default_branch_id': self.branch_id.ids,
                        'default_sbu_id': self.sbu_id.id,
                        'default_resource': self.resource,
                        'default_employee_id': [(4, self.employee_id.id)] if self.resource == 'replacement' else [],
                        'default_job_position': self.job_position.id,
                        'default_effective_date_of_deployment': self.effective_date_of_deployment,
                        'default_no_of_resource': self.no_of_resource,
                        'default_skill_set': self.skill_set if self.skill_set else False,
                        'default_technology': self.technology.id if self.technology else False,
                        'default_qualification': self.qualification,
                        'default_job_role_desc': self.job_role_desc,
                        'default_type_project': self.type_project,
                        'default_project': self.project.id,
                        'default_it_infra_provision': self.it_infra_provision,
                        'default_min_exp_year': str(self.min_exp_year) if self.min_exp_year else False,
                        'default_max_exp_year': str(self.max_exp_year) if self.max_exp_year else False,
                        'default_eq_category': self.eq_category if self.eq_category else '',
                        'default_skill': self.skill if self.skill else '',
                        'default_position': self.position if self.position else '',
                        'default_skill_description': self.skill_description if self.skill_description else '',
                        'default_minimum_educational_qualification_id': self.minimum_educational_qualification_id.id if self.minimum_educational_qualification_id else False,
                        'default_detailed_experience': self.detailed_experience if self.detailed_experience else False,
                        # 'default_skill_set': self.qualification if self.qualification else False,
                        'default_work_location': self.work_location if self.work_location else False,
                        'default_location': self.location if self.location else '',
                        'default_branch_id': self.branch_id.ids if self.branch_id else False,
                        'default_job_description': self.job_description if self.job_description else False,
                        'default_acc_manager_id': self.acc_manager_id.id if self.acc_manager_id else False,
                        'default_csg_head_id': self.csg_head_id.id if self.csg_head_id else False,
                        'default_presales_tl_id': self.presales_tl_id.id if self.presales_tl_id else False,
                        'default_presales_member_id': self.presales_member_id.id if self.presales_member_id else False,
                        'default_pm_id': self.pm_id.id if self.pm_id else False,
                        'default_sbu_lead_id': self.sbu_lead_id.id if self.sbu_lead_id else False,
                        'default_project_reviewer_id': self.project_reviewer_id.id if self.max_exp_year else False,
                        'default_requisition_type' : 'project' if self.from_eq_bool is True else False,
                        'default_role_id': self.env['kwmaster_role_name'].sudo().search([('code','=','R')]).id if self.from_eq_bool is True else False,
                        'default_max_sal':self.from_mif_pm_ctc,
                        # 'default_opp_code': self.opp_code if self.opp_code else False,
                        # 'default_opp_name': self.opp_name if self.opp_name else False,
                        'default_client_name': self.client_name if self.client_name else False,
                        'default_duration': self.months if self.months else False,
                        'default_days': self.days,
                        'default_from_eq_bool': True if self.from_eq_bool is True else False,
                        }
        }
    def action_view_mrf_details(self):
        mrf_details = self.env['kw_recruitment_requisition'].search([('mif_rec_id','=',self.id)])
        form_view_id = self.env.ref("kw_recruitment.view_manpower_requisition_form_form").id
        return {
            'name': 'Manpower Requisition Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_recruitment_requisition',
            'target': 'self',
            'res_id': mrf_details.id,
            'context': {"create": False,"edit": True,"import":False},
        }

    def action_mif_user_access_id(self):
        emp_rec_grade = self.env['hr.employee'].sudo().search([('grade', 'in', ['M5', 'M6', 'M7', 'M8', 'M9', 'M10',
                                                                                'E1', 'E2', 'E3', 'E4', 'E5'])])
        user_group_access = self.env.ref('kw_recruitment.group_kw_mif_user')
        existing_user = user_group_access.users
        all_users = emp_rec_grade.mapped("user_id")
        new_user = existing_user - all_users if existing_user > all_users else all_users - existing_user
        # print("emp_rec_grade ================ ",existing_user,all_users," ===== ",new_user)
        if emp_rec_grade and new_user:
            new_user.write({'groups_id': [(4, user_group_access.id)]})
            
    def action_mif_fy_update(self):
        mif_record = self.env['kw_manpower_indent_form'].search([])
        for rec in mif_record:
            fy_parts = rec.code.split('/')
            fy_desired_part = fy_parts[2]
            get_financial_year = self.env['account.fiscalyear'].sudo().search([('code', '=', fy_desired_part)])
            rec.current_fy = get_financial_year.id