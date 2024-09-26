from calendar import month
import re
import uuid
from datetime import date,timedelta
from ast import literal_eval
from xml import dom
from odoo import tools, _
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RequisitionLog(models.Model):
    _name = 'kw_recruitment_requisition_log'
    _description = 'Manpower Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF', ondelete='cascade')
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


class RequisitionApproval(models.Model):
    _name = 'kw_recruitment_requisition_approval'
    _description = 'MRF Approval'
    _order = 'id desc'

    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Token', default=_default_access_token)
    mrf_id = fields.Many2one('kw_recruitment_requisition', 'MRF Linked', ondelete='cascade')
    applicant_id = fields.Many2one('hr.applicant', 'Applicant Linked', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Employee', domain=[('user_id', '!=', False)])
    offer_id = fields.Many2one('hr.applicant.offer', 'Offer', ondelete='cascade')
    status = fields.Boolean(default=True)
    otp = fields.Char(string="OTP")
    expire_time = fields.Datetime(string="Expire Time")
    
    
class MRFAppMenuWizard(models.TransientModel):
    _name = 'mrf.app.menu.wizard'
    _description = 'MRF App Menu Wizard'

    def mrf_action_for_tm_resource(self):
        mrf_from_eq = self.env['kw_manpower_indent_form'].sudo().search([('eq_mif_id','!=',False),('from_eq_bool','=',True),('state','=','Grant')]).mapped('id')
        tree_view_id = self.env.ref('kw_recruitment.view_kw_manpower_indent_form_eq_tm_tree').id
        return {
            'name': 'MIF Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'res_model': 'kw_manpower_indent_form',
            'target': 'self',
            'domain': [('id', 'in', mrf_from_eq)],
        }
    
    def mrf_action_for_other_resource(self):
        mrf_from_other = self.env['kw_manpower_indent_form'].sudo().search([('eq_mif_id','=',False),('from_eq_bool','=',False),('state','=','Grant')]).mapped('id')
        tree_view_id = self.env.ref('kw_recruitment.view_kw_manpower_indent_form_eq_tm_tree').id
        return {
            'name': 'MIF Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'res_model': 'kw_manpower_indent_form',
            'target': 'self',
            'domain': [('id', 'in', mrf_from_other)],
        }

class Requisition(models.Model):
    _name = "kw_recruitment_requisition"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Manpower Requisition"
    _rec_name = "code"
    _order = "id desc"

    @api.depends('current_user')
    def _compute_visibility_approver(self):
        for mrf in self:
            # if mrf.current_user.id:
            #     emp = self.env['hr.employee']
            #     Parameters = self.env['ir.config_parameter'].sudo()
            #     first_level_emp = literal_eval(Parameters.get_param('kw_recruitment.employee_first_level_ids', '[]'))
            #     first_approver_list = literal_eval(Parameters.get_param('kw_recruitment.first_level_approver_ids', '[]'))
            #     second_approver_list = literal_eval(Parameters.get_param('kw_recruitment.second_level_approver_ids', '[]'))
            #     all_emp = emp.browse(first_approver_list) + emp.browse(second_approver_list) + emp.browse(first_level_emp)
            #     # approver_list = first_approver_list.strip('][').split(', ')
            #     # approver_list.append(second_approver_list.strip('][').split(', '))
            #     employee = self.env['hr.employee'].search(
            #         [('id', 'in', all_emp.ids), ('user_id', '=', mrf.current_user.id)])
            #     if employee:
            #         mrf.approver_field = True
            #     else:
            #         mrf.approver_field = False

            # Edit Post Approval
            if mrf.state == 'sent' and mrf.env.user.has_group('kw_resource_management.group_budget_manager'):
                mrf.field_edit_post_approval = True
            else:
                mrf.field_edit_post_approval = False

    @api.depends('current_user')
    def _compute_sal(self):
        if self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            self.hide_sal = False
        else:
            parameters = self.env['ir.config_parameter'].sudo()
            first_level_emp = literal_eval(parameters.get_param('kw_recruitment.employee_first_level_ids'))
            first_level_approver_ids = literal_eval(parameters.get_param('kw_recruitment.first_level_approver_ids'))
            second_level_approver_ids = literal_eval(parameters.get_param('kw_recruitment.second_level_approver_ids'))
            final_employee_list = first_level_emp + first_level_approver_ids + second_level_approver_ids

            if self.env.user.employee_ids.id in final_employee_list:
                self.hide_sal = False
            else:
                self.hide_sal = True
        # print("hide_sal", self.hide_sal)
    
    def _compute_visibility_action(self):
        for mrf in self:
            if mrf.current_user.id == self.env.user.id:
                mrf.user_inv = True
            else:
                mrf.user_inv = False

    def _compute_is_final_approver(self):
        for mrf in self:
            emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if emp.id in self.last_approver_ids.ids:
                # print("user id compared=== 2 here")
                mrf.is_final_approver = True
            else:
                # print("user id not compared== 2 here")
                mrf.is_final_approver = False

    @api.depends('current_user')
    def _get_raisedby(self):
        for mrf in self:
            emp = self.env['hr.employee'].search([('user_id', '=', mrf.env.user.id)])
            if emp.job_id:
                mrf.req_raised_by = emp.display_name + " - " + emp.job_id.name
            else:
                mrf.req_raised_by = emp.display_name

    @api.depends('dept_name')
    def _compute_dept_name(self):
        for mrf in self:
            if mrf.dept_name.code == 'BSS':
                mrf.dept_bool = True
            else:
                mrf.dept_bool = False

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def get_role_id(self):
        domain = [('id', '=', [])]
        if self._context.get('requisition_type') == "treasury" and not self._context.get('is_type_project'):
            roles = self.env['kwmaster_role_name'].search([('code', '!=', 'R')]).ids
            domain = [('id', 'in', roles)]
        elif self._context.get('requisition_type') == "project":
            roles = self.env['kwmaster_role_name'].search([('code', '=', 'R')], limit=1)
            domain = [('id', 'in', roles.ids)]

        return domain

    # #####------------------------Fields----------------------######
    name_of_business = fields.Many2one('kw_business_unit', string='Name of the Business Unit')
    current_user = fields.Many2one('res.users', default=lambda self: self.env.user)
    req_raised_by = fields.Char('Raised By', compute='_get_raisedby', store=True, track_visibility='onchange')
    req_raised_by_id = fields.Many2one('hr.employee', string="Request raised by Employee", default=_default_employee)
    user_inv = fields.Boolean(compute='_compute_visibility_action', string='Field',
                              help='Make buttons invisible once sent for approval button clicked.')
    approver_field = fields.Boolean(compute='_compute_visibility_approver', string='Field',
                                    help='Make approver field invisible.',track_visibility='onchange')
    approver_id = fields.Many2one('hr.employee', string="Approver", track_visibility='onchange')
    forwarder_id = fields.Many2one('hr.employee', string="Forwarder", related='approver_id')
    note = fields.Text('Comment', track_visibility='always', track_sequence=6)
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Pending'),
                              ('hold', 'Hold'), ('revise', 'Revise'),
                              ('forward', 'Forwarded'), ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange',
                             track_sequence=3, default='draft')
    forwarded = fields.Boolean(default=False)
    final_approver_ids = fields.Many2many('hr.employee', 'emp_approver_rel', 'mrf_id', 'emp_id',
                                          string="Final Approvers")
    last_approver_ids = fields.Many2many('hr.employee', 'emp_approver_rel_last', 'mrf_id', 'emp_id',
                                         string="Last Approvers")
    is_final_approver = fields.Boolean(compute='_compute_is_final_approver', )
    requisition_type = fields.Selection(track_visibility='onchange', string='Budget Type',
                                        selection=[('treasury', 'Treasury Budget'), ('project', 'Project Budget')],
                                        help="1. Treasury budget. \n2. Project Budget (It will ask for project selection)")
    project = fields.Many2one('crm.lead', string='Project', track_visibility='onchange')
    project_code = fields.Char(string="Project Code", related="project.code", store=True)
    # project_id = fields.Many2one('project.project', string='Project')
    resource = fields.Selection(string='Resource Type', track_visibility='onchange',
                                selection=[('new', 'New'), ('replacement', 'Replacement')],
                                default='new', help="Set recruitment process is employee type.")
    dept_bool = fields.Boolean(string='Dep Bool', compute='_compute_dept_name')
    effective_date_of_deployment = fields.Date(string="Effective Date of Deployment")
    sbu_id = fields.Many2one(comodel_name="kw_sbu_master", string="SBU/Horizontal")
    employee_id = fields.Many2many('hr.employee', string='Employee Name', track_visibility='onchange',
                                   domain=['|', ('active', '=', True), ('active', '=', False)])
    role_id = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role", domain=get_role_id,
                              track_visibility='onchange')
    categ_id = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category",
                               track_visibility='always')
    date_requisition = fields.Date(string='Date of Requisition', default=fields.Date.context_today,
                                   track_visibility='onchange')
    no_of_resource = fields.Integer('No. of Resources', track_visibility='onchange',default='1')
    skill_set = fields.Text('Special Requirement')
    qualification = fields.Text('Educational Qualification', track_visibility='onchange')
    experience = fields.Char("Work Experience", track_visibility='onchange')
    min_exp_year = fields.Selection(string='Min. Years', selection='_get_year_list', default="0",
                                    track_visibility='onchange')
    max_exp_year = fields.Selection(string='Max. Years', selection='_get_year_list', default="0",
                                    track_visibility='onchange')
    job_position = fields.Many2one('hr.job', track_visibility='onchange')
    salary_month = fields.Char("Salary per Month")
    min_sal = fields.Integer('Min. Salary', track_visibility='onchange', default="0", store=True)
    max_sal = fields.Integer('Max. Salary', track_visibility='onchange', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    branch_id = fields.Many2many('kw_recruitment_location', string="Work Location")
    type_project = fields.Selection(string='Type Of Project',
                                    selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                    help="Set recruitment process is work order.")
    date_of_joining = fields.Date(string=' Tentative Date of Joining', default=fields.Date.context_today)
    duration = fields.Integer('Engagement Period (Months)')
    days=fields.Integer('Engagement Period (days)')
    name_of_workorder = fields.Char(string='Name of the Work Order')
    billing_date = fields.Date(string='Effective date of billing', default=fields.Date.context_today)
    end_date_contract = fields.Date(string='End date of the contract  ', default=fields.Date.context_today)
    type_employment = fields.Many2one('kwemp_employment_type', string='Type of Employment', )
    actual_joining = fields.Date(string='Date of Actual Joining ', default=fields.Date.context_today)
    end_service = fields.Date(string='End Date of Service', default=fields.Date.context_today)
    actual_sal = fields.Integer('Actual Salary (CTC) per Month')
    code = fields.Char(string="Reference No.", default="New", readonly="1")
    user_in_second_label = fields.Boolean(compute='compute_user_in_second_label')

    dept_name = fields.Many2one('hr.department', string='Department', domain=[('parent_id', '=', False)],
                                track_visibility='always')
    kw_job_id = fields.Many2one('kw_hr_job_positions', string='Job Ref#')
    pending_at = fields.Char(string="Pending At", compute="compute_pending_user")
    forward_check = fields.Boolean(string="Forward Check", compute="compute_check_forward")
    rcm_check = fields.Boolean(string="RCM Check", compute="compute_check_forward")
    rcm_group = fields.Boolean(string="RCM Check", compute="compute_check_forward")
    is_mrf_user = fields.Boolean(string="MRF Check", compute="compute_check_forward")
    rcm_head = fields.Boolean(string="RCM Head", compute="compute_check_forward")
    hod_check= fields.Boolean("HOD Check",compute="compute_check_forward")
    forward_to_ceo = fields.Boolean(string="Forward to ceo")
    hold_user_id = fields.Many2one("res.users", string="Hold By")
    active = fields.Boolean(string="Active", default=True)
    approved_user_id = fields.Many2one("res.users", string="Approved By")
    order_sequence = fields.Char(string="Order", compute="compute_order", store=True)

    description = fields.Text('Comment')
    forwared_note = fields.Char('Comment', track_visibility='always', track_sequence=7)
    approved_note = fields.Char('Comment', track_visibility='always', track_sequence=9)
    forwarded_dt = fields.Date('Forwarded Date')
    approved_dt = fields.Date('Approved Date')
    field_edit_post_approval = fields.Boolean(compute='_compute_visibility_approver', string='Edit Post Approval')
    employment_is = fields.Selection(string='Employment', track_visibility='onchange',
                                     selection=[('temporary', 'Temporary'), ('permanent', 'Permanent')],
                                     help="Set treasury project employment type: Temporary or Permanent")
    employment_duration = fields.Integer('Employment duration (months)', default=1, track_visibility='onchange')
    hide_sal = fields.Boolean(compute='_compute_sal', string='Hide Sal')
    current_ctc = fields.Integer(string="Current CTC")
    extra_load_on_budget = fields.Integer(string="Extra load on Budget")
    is_type_of_project = fields.Boolean(string='Is type of project')
    technology = fields.Many2one('kw_skill_master', string="Technology")
    is_tag_user = fields.Boolean(string="TAG Check", compute="compute_check_forward")
    only_mrf_user = fields.Boolean(string="Check MRF", compute="compute_check_mrf")
    is_report_manager = fields.Boolean(string="Check Report Manager", compute="compute_check_forward")
    avg_replacement_sal = fields.Integer(string="Average Salary per resource", compute="compute_avg_sal")
    dept_planned_budget = fields.Integer(string="Department Planned Budget")
    dept_remaining_budget = fields.Integer(string="Department Remaining Budget")
    job_role_desc = fields.Html(string="Job Description")
    is_nicsi = fields.Boolean(string="Is NICSI?", default=False)
    mif_rec_id = fields.Many2one("kw_manpower_indent_form", string="MIF", domain=[('state', '=', 'Grant')])
    is_talent_pool = fields.Boolean(string="Talent Pool")
    notify_hr = fields.Boolean(string="Is Notify HR?",default=False)

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
    work_location_id = fields.Many2one('kw_res_branch',string='Base Location')

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
    from_eq_bool = fields.Boolean(string="From EQ",default=False)
    
    opp_code = fields.Char()
    opp_id = fields.Many2one('crm.lead')
    opp_name = fields.Char(related='opp_id.name')
    client_name = fields.Char(related='opp_id.client_short_name')
    it_infra_provision = fields.Selection([('Client', 'Client'), ('CSM', 'CSM'),
                                           ], string="Computer Provision")
    special_comment_rcm = fields.Text()
    proposed_ctc = fields.Float()
    type_payroll = fields.Selection(string="Type",selection=[('ksl_payroll','KSL Payroll'),('csm_payroll','CSM Payroll')])
    project_name = fields.Char(related='project.name')
    
    # @api.constrains('proposed_ctc','max_sal')
    # def check_ctc(self):
    #     for rec in self:
    #         if rec.max_sal > rec.proposed_ctc and rec.proposed_ctc > 0:
    #             raise ValidationError('CTC must be lesser than the Proposed CTC of EQ!')

    # def _auto_init(self):
    #     super(Requisition, self)._auto_init()
    #     self.env.cr.execute("update kw_recruitment_requisition set approver_id =54  where id in (139,168,619)")
        # self.env.cr.execute("update kw_recruitment_requisition set code = replace(code, 'Treasury', 'Project') where id = 675")
        # self.env.cr.execute("update kw_recruitment_requisition set code = replace(code, 'Treasury', 'Project') where id = 676")

    @api.onchange('technology', 'job_position', 'min_exp_year', 'no_of_resource', 'dept_name', 'resource', 'employee_id')
    def onchange_budget_details(self):
        if self.no_of_resource < 1:
            self.env.user.notify_danger("Number of resource cannot be Zero.")
            return
        # if self.requisition_type == 'treasury':
        #     # print("inside untage code====treasury==========")
        #     current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
        #     self.tag_budget_line_to_mrf(current_fiscal_year_id,self)
            
        # if self.resource == 'replacement' and self.employee_id:
        #     contract_record = self.env['hr.contract'].sudo().search(['|','&',('employee_id','=',self.employee_id.id),('active','=',True),('active','=',False)],limit = 1,order='id desc')
        #     self.max_sal = contract_record.wage
        #     self.avg_replacement_sal = self.max_sal/self.no_of_resource if self.max_sal else 0 
            
    # @api.constrains('no_of_resource')
    # def check_budget_availibility(self):
    #     current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
    #
    #     budget_lines = budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(
    #         [('fiscalyr', '=', current_fiscal_year_id.id), ('mrf_id', '=', False), ('offer_id', '=', False),
    #          ('dept_id', '=', self.dept_name.id), ('technology', '=', self.technology.id),
    #          ('designation', '=', self.job_position.id), ('exp_year', '=', self.min_exp_year),
    #          ('status', '=', 'publish'), ('resource_joined', '=', False), ('resource_tobe_joined', '=', False),
    #          ('mar_budget', '!=', False)], order='department_sequence asc', limit=int(self.no_of_resource))
    #     # if not self.max_sal:
    #     #     raise ValidationError("Salary is not updated,Please notify to TAG")
    #     # if self.no_of_resource > len(budget_lines):
    #     #     raise ValidationError("No Budget found. Please change the the parameters such as Experience, Position, Experience, Technology and Try again..")
        
    @api.multi
    def tag_budget_line_to_mrf(self,current_fiscal_year_id,record):
        # print("self._context==",self._context)
        data = False
        if record._origin.id:
            query = f"""select * from budget_line_mrf where kw_recruitment_requisition_id = {record._origin.id}"""
            # print("query data==========++++++++++++++++",record._origin.id,record.id)
            # print("untage query--==222222",query)
            self._cr.execute(query)
            data = self._cr.fetchall()
        # print("data in side update budget===========================",data)
        treasury_budget_id, total_planned, total_incurred, total_remaining = False, False, False, False
        # print("dynamic method called==================",record,record.no_of_resource,len(record.budget_id))
        """ update  Department wise budget details """
        if current_fiscal_year_id:
            # print("inside dynamic if============")
            """ order by id as should be changes to order by department_sequence after testing """
            treasury_budget_id = self.env['kw_recruitment_budget_lines'].search(
                [('fiscalyr', '=', current_fiscal_year_id.id), ('dept_id', '=', record.dept_name.id)],
                order='department_sequence asc')
        # print("treasury_budget_id====",treasury_budget_id,record.dept_name)
        if treasury_budget_id:
            # print("inside/ dynamic if 2======")
            total_planned, total_incurred, total_remaining = self.env['kw_recruitment_treasury_budget_line'].get_budget_calculations(treasury_budget_id.ids)
            # print("---------------------",total_planned, total_incurred, total_remaining)
            if not record.dept_planned_budget or not record.dept_remaining_budget:
                record.dept_planned_budget = total_planned
                if total_incurred == 0 or total_incurred is None:
                    record.dept_remaining_budget = total_planned
                else:
                    record.dept_remaining_budget = total_remaining
        else:
            # print("inside dynam/ic else===========")
            record.dept_planned_budget = 0
            record.dept_remaining_budget = 0
        if record.technology and record.job_position and record.min_exp_year and record.resource == 'new':
            # if record.no_of_resource != len(record.budget_id):
            # print("inside /dynamic iffff=======================")
            budget_lines = self.get_budget_lines(current_fiscal_year_id,record)
            # print("budget_lines in dynamic====+++++++++++",budget_lines,record.budget_id)
            # if budget_lines:
                # self.update_budget_id(record)
                # if len(budget_lines) < len(record.budget_id):
            if record.no_of_resource < len(record.budget_id):
                # print("---------------dddddtttttattattatatt---1-----",record.budget_id[:-1])
                # print("record.budget_id==",record.budget_id.mapped('department_sequence'),record.budget_id,record.budget_id[::-1][:(len(record.budget_id)-record.no_of_resource)].ids)
                if self._origin and data:
                    self.update_budget_id(record,budget_lines,data)
                else:
                    self.update_max_sal(record.budget_id[::-1][:(record.no_of_resource)].ids,record)
                    record.budget_id =  [(6, 0,record.budget_id[::-1][:(record.no_of_resource)].ids[::-1])]
            # elif record.no_of_resource > len(budget_lines):
            #     self.env.user.notify_danger("No Budget found. Please change the the parameters such as Experience, Position, Experience, Technology and Try again.")
            elif record.no_of_resource and not len(record.budget_id):
                # print("inside condition")
                if self._origin and data:
                    self.update_budget_id(record, budget_lines, data)
                else:
                    self.update_max_sal(budget_lines.ids, record)
                    record.budget_id = [(6, 0, budget_lines.ids)]
            elif record.budget_id and record.no_of_resource > len(record.budget_id):
                # print("---------------dddddtttttattattatatt----2----",record.budget_id[:-1],self,data)
                if self._origin and data:
                    # print("inside origin no of resource greater than------------------------------------ ")
                    self.update_budget_id(record,budget_lines,data)
                else:
                    # if not self._context.get('manpower_requisition_context'):
                    # print("inside context of onchangeeeeeeeeeeeeeeee-------------------------------",self._context,data,record.budget_id+budget_lines[:record.no_of_resource-len(record.budget_id)])
                    if record.no_of_resource <= len(budget_lines):
                        # print("record.budget_id==",record.budget_id)
                        # print("budget_lines[::-1]==",budget_lines[::-1])
                        # print("[:record.no_of_resource-len(record.budget_id)]==",record.no_of_resource-len(record.budget_id))
                        # print("record.budget_id+budget_lines[::-1][:record.no_of_resource-len(record.budget_id)]==",record.budget_id+budget_lines[::-1][:record.no_of_resource-len(record.budget_id)])
                        formatted_data = self.get_filtered_data((record.budget_id+budget_lines[::-1][:record.no_of_resource-len(record.budget_id)]).ids)
                        self.update_max_sal(formatted_data, record)
                        record.budget_id = [(6, 0, formatted_data)]
                        # print("record.budget_id==",record.budget_id)
                    else:
                        # print("inside first else==========================")
                        self.budget_id = [(5, 0, 0)]
                        self.env.user.notify_danger("No budget found for mentioned job position, number of resource, experience and technology.")

            elif record.no_of_resource <= len(budget_lines):
                # print("new elif condition",budget_lines.ids[:record.no_of_resource])
                record.budget_id = [(6, 0, (budget_lines.ids[::-1][:record.no_of_resource]))]
                self.update_max_sal(budget_lines.ids, record)
                
            elif record.no_of_resource == len(budget_lines):
                # print("--------------dddddtttttattattatatt------3-------,",budget_lines.ids)
                if self._origin and data:
                    self.update_budget_id(record, budget_lines, data)
                else:
                    self.update_max_sal(budget_lines.ids, record)
                    record.budget_id = [(6, 0, budget_lines.ids)]
            else:
                # print("inside second else===========================")
                self.budget_id = [(5, 0, 0)]
                self.env.user.notify_danger("No budget found for mentioned job position, number of resource, experience and technology.")

            # print("=====-------",record.budget_id)
            monthly_budgte = budget_lines.mapped('mar_budget')
            # print("------",record.no_of_resource,len(monthly_budgte),monthly_budgte)
            # if record.no_of_resource == len(monthly_budgte):
                # if len(set(monthly_budgte)) == 1:
                #     record.max_sal = int(str(list(set(monthly_budgte))[0] if monthly_budgte else 0))
                # record.max_sal = sum(map(int, monthly_budgte)) if monthly_budgte else 0
            
        # else:
        #     record.max_sal = record.employee_id.current_ctc
        #     record.avg_replacement_sal = record.max_sal/record.no_of_resource if record.max_sal else 0
    
    def update_max_sal(self,budget_lines,record):
        if budget_lines:
            monthly_budgte = self.env['kw_recruitment_budget_lines'].sudo().browse(budget_lines).mapped('mar_budget')
            # print("monthlu budget=================",monthly_budgte)
            record.max_sal = sum(map(int, monthly_budgte)) if monthly_budgte else 0
        
    def update_budget_id(self,mrf_record,budget_lines,data):
        if mrf_record._origin or mrf_record.id:
            all_list_data = []
            for rec in data:
                all_list_data.append(list(rec)[1])
            if all_list_data:
                # print("last output--",len(all_list_data)+len(budget_lines))
                if mrf_record.no_of_resource == (len(all_list_data)+len(budget_lines)):
                    # print("last condition-----------")
                    dynamic_data = self.get_filtered_data(all_list_data+budget_lines.ids)
                    self.update_max_sal(dynamic_data, mrf_record)
                    mrf_record.budget_id = [(6, 0, dynamic_data)]
                elif mrf_record.no_of_resource == len(all_list_data):
                    # print("3333333333333--",all_list_data,mrf_record.no_of_resource,budget_lines)
                    dynamic_data = self.get_filtered_data(all_list_data)
                    self.update_max_sal(dynamic_data,mrf_record)
                    mrf_record.budget_id = [(6, 0, dynamic_data)]
                elif len(all_list_data) < mrf_record.no_of_resource <= (len(all_list_data) + len(budget_lines)):
                    # print("11111111111111--",all_list_data,mrf_record.no_of_resource,budget_lines,all_list_data+budget_lines.ids[:mrf_record.no_of_resource-len(all_list_data)])
                    dynamic_data = all_list_data+budget_lines.ids[:mrf_record.no_of_resource-len(all_list_data)]
                    dynamic_data.sort(reverse=True)
                    # print('dynamic data======66666666666=========================',dynamic_data)
                    dynamic_data = self.get_filtered_data(dynamic_data)
                    self.update_max_sal(dynamic_data,mrf_record)
                    mrf_record.budget_id =  [(6, 0,dynamic_data)]
                elif mrf_record.no_of_resource != 0 and mrf_record.no_of_resource < len(all_list_data):
                    all_list_data.sort(reverse=False)
                    # print("dynamic value==============",dynamic_data)
                    filtered_dt = self.get_filtered_data(all_list_data)
                    dynamic_data = filtered_dt[::-1][:-(len(all_list_data) - mrf_record.no_of_resource)]
                    self.update_max_sal(dynamic_data, mrf_record)
                    mrf_record.budget_id = [(6, 0, dynamic_data)]
                elif mrf_record.no_of_resource > len(budget_lines):
                    # print("validation======++++++++++++++++++++")
                    self.budget_id = [(5, 0, 0)]
                    self.env.user.notify_danger("No Budget found. Please change the the parameters such as Experience, Position, Experience, Technology and Try again.")

    def get_filtered_data(self,records):
        # print("recordsrecordsrecordsrecords----",records)
        arranged_data_list = []
        data_list = []
        if records:
            all_datas = self.env['kw_recruitment_budget_lines'].sudo().browse(records)
            new_datas = all_datas.mapped('department_sequence')
            data_list.append(str(new_datas))
            # print("new_datas==11111111=",new_datas,data_list[0])
            if new_datas:
                new_datas.sort(reverse=False)
                formatted_list = list(data_list[0][1:-1].split(', '))
                for rec in new_datas:
                    # print("formatted_list=======",formatted_list.index(f"{rec}"),all_datas[formatted_list.index(f"{rec}")])
                    arranged_data_list.append(all_datas[formatted_list.index(f"{rec}")].id)
            # print("arranged_data_list===",arranged_data_list)
        return arranged_data_list[::-1]

    def get_budget_lines(self, current_fiscal_year_id, record):
        # print("record.no_of_resource====",record.no_of_resource)
        budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(
            [('fiscalyr', '=', current_fiscal_year_id.id), ('mrf_id', '=', False), ('offer_id', '=', False),
             ('dept_id', '=', record.dept_name.id), ('technology', '=', record.technology.id),
             ('designation', '=', record.job_position.id), ('exp_year', '=', record.min_exp_year),
             ('status', '=', 'publish'), ('resource_joined', '=', False), ('resource_tobe_joined', '=', False),
             ('mar_budget', '!=', False)], order='department_sequence asc', limit=int(record.no_of_resource))
        # print("=+ssssssssssssssssssssss+=",budget_lines)
        return budget_lines
            
    @api.multi
    @api.depends('req_raised_by')
    def compute_check_mrf(self):
        """Checking RCM Head OR TAG"""
        for rec in self:
            if rec.env.user.has_group('kw_resource_management.group_budget_manager'):
                rec.only_mrf_user = True
            elif rec.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
                rec.only_mrf_user = True
            elif rec.env.user.has_group('kw_wfh.group_hr_hod'):
                rec.only_mrf_user = True  
            elif rec.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                rec.only_mrf_user = True   
            else:
                rec.only_mrf_user = False
       
    @api.onchange('type_project')
    def onchange_project_type(self):
        if self.type_project == 'opportunity' and self.is_nicsi is False and self.from_eq_bool == False:
            self.is_type_of_project = True
            self.requisition_type = 'treasury'
            if self.requisition_type == 'treasury':
                return {'warning': {
                    'title': ('Alert'),
                    'message': (f"The Budget type has been changed to Treasury budget.")
                }}
        else:
            self.requisition_type = 'project'
    
    # @api.multi
    # @api.depends('max_sal','no_of_resource')
    # def compute_budget(self):
    #     treasury_budget_id, total_planned, total_incurred, total_remaining = False,False,False,False
    #     current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
    #     if current_fiscal_year_id:
    #         treasury_budget_id = self.env['kw_recruitment_treasury_budget_line'].search([('fiscalyr','=',current_fiscal_year_id.id),('department_id','=',self.dept_name.id)])
    #     print("==========",treasury_budget_id)
    #     if treasury_budget_id:
    #         total_planned, total_incurred, total_remaining = self.get_budget_calculations(treasury_budget_id.ids)
    #         print("22222222222222222222",total_planned, total_incurred, total_remaining)
    #         self.dept_planned_budget = total_planned
    #         self.dept_remaining_budget = total_remaining
    #     else:
    #         self.dept_planned_budget = 0
    #         self.dept_remaining_budget = 0
    @api.multi
    @api.depends('max_sal', 'no_of_resource')
    def compute_avg_sal(self):
        for rec in self:
            if rec.max_sal and rec.no_of_resource:
                rec.avg_replacement_sal = rec.max_sal/rec.no_of_resource
            else:
                rec.avg_replacement_sal = 0

    @api.multi
    @api.depends('req_raised_by')
    def compute_check_forward(self):
        """Checking RCM Head OR TAG OR REPORT MANAGER"""
        Parameters = self.env['ir.config_parameter'].sudo()
        ceo_head = literal_eval(Parameters.get_param('kw_recruitment.second_level_approver_ids', '[]'))
        emp = self.env['hr.employee'].browse(ceo_head)
        rcm_head = literal_eval(Parameters.get_param('kw_recruitment.rcm_head', '[]'))
        rcm_head_ids = self.env['hr.employee'].browse(rcm_head)
        tag_users = set(literal_eval(Parameters.get_param('kw_recruitment.tag_head', '[]')) + literal_eval(
            Parameters.get_param('kw_recruitment.notify_cc_ids', '[]')))
        tag_ids = self.env['hr.employee'].browse(tag_users)

        if self.env.user.employee_ids.id == self.approver_id.id:
            self.hod_check = True
        elif self.env.user.has_group('kw_recruitment.group_rcm_head_user'):
            self.rcm_group = True
            self.rcm_check = False
        elif self.env.user.has_group('kw_resource_management.group_budget_manager') \
                and self.env.user.employee_ids.id in rcm_head_ids.ids:
            self.rcm_head = True
        elif self.env.user.has_group('kw_recruitment.group_tag_budget_user') \
                and self.env.user.employee_ids.id in tag_ids.ids:
            self.rcm_check = True
        elif self.env.user.has_group('kw_wfh.group_hr_hod'):
            self.hod_check = True
        elif self.env.user.employee_ids.id == emp.id:
            self.hod_check = True
        elif self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager'):
            self.is_report_manager = True
        elif not self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager') \
                or not self.env.user.has_group('kw_recruitment.group_tag_budget_user') \
                or not self.env.user.has_group('kw_wfh.group_hr_hod') \
                or not self.env.user.has_group('kw_resource_management.group_budget_manager'):
            self.is_mrf_user = True
        else:
            if not self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                self.rcm_check = False
        if self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
            self.is_tag_user = True

        """ Fetching CEO office employee from general settings """
        parameters = self.env['ir.config_parameter'].sudo()
        ceo_office_employee = literal_eval(parameters.get_param('kw_recruitment.employee_first_level_ids','[]'))
        ceo_office_employees = self.env['hr.employee'].search([('id', 'in', ceo_office_employee)]).ids
        for rec in self:
            if self.create_uid.employee_ids.id in ceo_office_employees:
                rec.forward_check = True
            else:
                rec.forward_check = False

    @api.depends('state')
    def compute_order(self):
        state_mapping = {'draft': 'a', 'sent': 'b', 'hold': 'c', 'forward': 'd', 'approve': 'e', 'reject': 'f'}
        for mrf in self:
            mrf.order_sequence = state_mapping[mrf.state]

    @api.multi
    def compute_pending_user(self):
        pending_manager_user = self.env.ref('kw_resource_management.group_budget_manager').users
        rcm_manager = ','.join(pending_manager_user.mapped('employee_ids.name')) if pending_manager_user else ''
        param = self.env['ir.config_parameter'].sudo()
        to_users = literal_eval(param.get_param('kw_recruitment.rcm_head', '[]'))
        employee_rcm_tag = self.env['hr.employee'].search([('id', 'in', to_users)])
        second_level_approver = literal_eval(param.get_param('kw_recruitment.second_level_approver_ids', '[]'))
        employee = self.env['hr.employee'].search([('id', 'in', second_level_approver)])

        record_config_dept = self.env['mrf_approver_department_config'].sudo().search([])
        for r in self:
            for rec in record_config_dept:
                if rec.approver_id == r.approver_id and r.state in ['forward', 'hold']:
                    r.pending_at = rec.approver_id.name

        for mrf in self:
            if mrf.state == "sent":
                mrf.pending_at = ','.join([rec.name for rec in employee_rcm_tag])
            elif self.env.user.in_first_level_employee() and mrf.forward_to_ceo and mrf.state in ['forward', 'hold']:
                mrf.pending_at = employee.name
            elif mrf.state == 'reject':
                mrf.pending_at = ''
            elif (not mrf.role_id or not mrf.categ_id) and mrf.state != 'draft':
                mrf.pending_at = 'Pending at TAG'
            # elif mrf.state == "hold":
            #     mrf.pending_at = mrf.hold_user_id.employee_ids and mrf.hold_user_id.employee_ids[-1].display_name or mrf.hold_user_id.name

    @api.depends('current_user')
    def compute_user_in_second_label(self):
        parameters = self.env['ir.config_parameter'].sudo()
        second_approver_list = literal_eval(parameters.get_param('kw_recruitment.second_level_approver_ids'))
        for mrf in self:
            if mrf.current_user.employee_ids and mrf.current_user.employee_ids[-1] \
                    and mrf.current_user.employee_ids[-1].id in second_approver_list \
                    and not self._context.get('manpower_requisition_context'):
                mrf.user_in_second_label = True

    @api.multi
    def get_hr_email(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_group = literal_eval(param.get_param('kw_recruitment.notify_cc_ids','[]'))
        all_jobs = self.env['hr.employee'].browse(cc_group)
        email_list = []
        if cc_group:
            empls = self.env['hr.employee'].search([('id', 'in', all_jobs.ids)])
            if empls:
                email_list = [emp.work_email for emp in empls if emp.work_email]
            if email_list == []:
                email_list = ['asit.mohanty@csm.tech', 'ratandeep.mohanty@csm.tech']
        return ",".join(email_list)

    def _get_all_child_department(self, dept_ids):
        child_recs = dept_ids.mapped('child_ids')
        if child_recs:
            return child_recs | self._get_all_child_department(child_recs)
        else:
            return child_recs

    @api.onchange('employee_id', 'current_ctc', 'max_sal')
    def _check_employee_replacement(self):
        if self.employee_id:
            if len(self.employee_id) > 1:
                raise ValidationError('Choose only one replacement.')
    #         self.current_ctc = self.employee_id.current_ctc
    #         if self.max_sal > 0 and self.current_ctc > 0:
    #             self.extra_load_on_budget = self.max_sal - self.current_ctc
    
    @api.onchange('dept_name', 'approver_id', 'employee_id')
    def _get_dept_approver(self):
        if self._context.get('manpower_requisition_context'):
            approvers = self.env['mrf_approver_department_config'].sudo().search([])
            approver_list = []
            for record in approvers:
                if self.dept_name.id in record.department_ids.ids:
                    approver_list.append(record.approver_id.id)
                    self.approver_id = approver_list[0] if approver_list else False
            return {'domain': {'approver_id': [('id', 'in', approver_list)]}}
        # else:
        #     for rec in self:
        #         employees_list = []
        #         Parameters = self.env['ir.config_parameter'].sudo()
        #         first_approver_list = Parameters.get_param('kw_recruitment.first_level_approver_ids','[]')
        #         approver_list = first_approver_list.strip('][').split(', ')

        #         employees = self.env['hr.employee'].search([('id', 'in', [int(employee_id) for employee_id in approver_list])])
        #         if employees:
        #             employees_list = [emp.id for emp in employees]

        #         if rec.dept_name:
        #             dept_child_ids = self._get_all_child_department(rec.dept_name)
        #             dept_child_ids += rec.dept_name
        #             # print(dept_child_ids)
        #             # MRF Creator RA is CEO scenario
        #             if not self.env.user.employee_ids.parent_id.parent_id:
        #                 employees_list = [self.env.user.employee_ids.parent_id.id]
        #             return {'domain': {'approver_id': [('id', 'in', employees_list)],
        #                             'employee_id': [('department_id', 'in', dept_child_ids.ids),
        #                                             ('user_id', '!=', self.env.user.id), '|', ('active', '=', False),
        #                                             ('active', '=', True)]}, }
        #         else:
        #             if not self.env.user.employee_ids.parent_id.parent_id:
        #                 employees_list = [self.env.user.employee_ids.parent_id.id]
        #             return {'domain': {'approver_id': [('id', 'in', employees_list)],
        #                             'employee_id': [('user_id', '!=', self.env.user.id), '|', ('active', '=', False),
        #                                             ('active', '=', True)]}, }

    @api.onchange('type_project')
    def _onchange_project_type(self):
        if not self._context.get('default_project'):
            self.project = False
            if self.type_project == 'work':
                return {'domain': {'project': [('stage_id.code', '=', 'workorder')]}}
            elif self.type_project == 'opportunity':
                return {'domain': {'project': [('stage_id.code', '=', 'opportunity')]}}
        else:
            if self.type_project == 'work':
                return {'domain': {'project': [('stage_id.code', '=', 'workorder')]}}
            elif self.type_project == 'opportunity':
                return {'domain': {'project': [('stage_id.code', '=', 'opportunity')]}}

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('approval_label_check'):
            Parameters = self.env['ir.config_parameter'].sudo()
            first_approver_list = literal_eval(Parameters.get_param('kw_recruitment.first_level_approver_ids'))
            first_level_emp = literal_eval(Parameters.get_param('kw_recruitment.employee_first_level_ids'))
            if self.env.user.in_second_level_approval() or self.env.user.in_first_level_employee():
                args += ['|', '|', '|', ('state', '=', 'forward'), '&', ('state', '=', 'sent'),
                         ('current_user.employee_ids', 'in', first_approver_list), '&', ('state', '=', 'hold'),
                         ('hold_user_id', '=', self.env.user.id),'&', ('state', '=', 'sent'),
                         ('current_user.employee_ids', 'in', first_level_emp)]
            elif self.env.user.in_first_level_approval():
                args += ['|', '&', ('state', '=', 'sent'), ('approver_id', 'in', self.env.user.employee_ids.ids),
                         '&', ('state', '=', 'hold'), ('hold_user_id', '=', self.env.user.id)]
            else:
                args += [('id', 'in', [])]
        
        return super(Requisition, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                access_rights_uid=access_rights_uid)

    @api.onchange('role_id')
    def _get_categories(self):
        role_id = self.role_id.id
        self.categ_id = False
        return {'domain': {'categ_id': [('role_ids', '=', role_id)], }}

    @api.model
    def _get_year_list(self):
        years = 30
        return [(str(i), i) for i in range(years + 1)]

    @api.onchange('resource')
    def enable_resource_type(self):
        if self.resource and self.resource == "new":
            self.employee_id = False
        if self.resource and self.resource == "replacement":
            self.no_of_resource = 1

    @api.onchange('category_id')
    def enable_category_type(self):
        if self.category_id:
            self.skill_id = False
            return {'domain': {'skill_id': [('category_id', '=', self.category_id.id)], }}

    @api.onchange('job_position')
    def enable_role_type(self):
        if self.job_position:
            self.job_role_desc = False
            record = self.env['hr.job.role'].sudo().search([('designations', '=', self.job_position.id)])
            self.job_role_desc = record.description

    @api.onchange('requisition_type')
    def check_requisition_type(self):
        if self.requisition_type == 'project' and self.type_project == 'opportunity':
            self.is_type_of_project = False
        if self.requisition_type and self.requisition_type == "treasury" and not self.is_type_of_project:
            # self.type_employment = False
            self.role_id = False
            self.type_project = False
            # self.project_name = False
            self.project = False
            self.duration = False
            # self.date_of_joining = False
            self.name_of_business = False
            self.name_of_workorder = False
            self.billing_date = False
            self.end_date_contract = False
            # return {'domain': {'type_employment': [('code', '=', 'P')], 'role_id': []}}
            roles = self.env['kwmaster_role_name'].search([('code', '!=', 'R')]).ids
            return {'domain': {'role_id': [('id', '=', roles)]}}
        elif self.requisition_type and self.requisition_type == "project":
            # self.type_employment = False
            lst_roles = []
            roles = self.env['kwmaster_role_name'].search([('code', '=', 'R')],limit=1)
            # for role in roles:
            #     lst_roles.append(role.id)
            if self._context.get('manpower_requisition_context'):
                self.role_id = roles.id
            return {'domain': {'role_id': [('id', '=', roles.ids)]}}
            # return {'domain': {'type_employment': [('code', 'in', ['O', 'C'])],'role_id': [('id', '=', lst_roles)]}}

    # @api.onchange('mif_rec_id')
    # def onchange_mif_rec_id(self):
    #     if self.mif_rec_id:
    #         self.dept_name = self.mif_rec_id.dept_name.id
    #         self.branch_id = self.mif_rec_id.branch_id.ids
    #         self.sbu_id = self.mif_rec_id.sbu_id.ids
    #         self.resource = self.mif_rec_id.resource
    #         self.employee_id = self.mif_rec_id.employee_id.id if self.mif_rec_id.resource == 'replacement' else False
    #         self.job_position = self.mif_rec_id.job_position.id
    #         self.effective_date_of_deployment = self.mif_rec_id.effective_date_of_deployment
    #         self.no_of_resource = self.mif_rec_id.no_of_resource
    #         self.skill_set = self.mif_rec_id.skill_set if self.mif_rec_id.skill_set else False
    #         self.technology = self.mif_rec_id.technology.id if self.mif_rec_id.technology else False
    #         self.qualification = self.mif_rec_id.qualification
    #         self.type_project = self.mif_rec_id.type_project
    #         self.project = self.mif_rec_id.project.id if self.mif_rec_id.project else False
    #         self.min_exp_year = self.mif_rec_id.min_exp_year if self.mif_rec_id.min_exp_year else False
    #         self.max_exp_year = self.mif_rec_id.max_exp_year if self.mif_rec_id.max_exp_year else False
    #         self.job_role_desc = self.mif_rec_id.job_role_desc

    @api.model
    def create(self, values):
        # print(" >>>>>>>>>>>>> ", 'code' in values, values.get('code'))
        result = super(Requisition, self).create(values)
        print("valuess===========create==========================",result.requisition_type)
        code = self.env['ir.sequence'].next_by_code('self.mrf_seq') or 'New'
        dept_code = ''
        new_code = ''
        requisition = (result.requisition_type).capitalize()
        # print("valuess=====================================",values)
        if result.state == 'draft':
            # print("inside result===========")
            self.env['kw_recruitment_requisition_log'].create({
                'mrf_id': result.id,
                'from_status': result.state,
                'to_status': result.state,
                'approver_id': result.env.user.employee_ids.id
            })
        # print("after create valuess=====================================",values,result,self)
        
        dept_name = result.dept_name
        if dept_name:
            # dept = self.env['hr.department'].browse([dept_name.id])
            if dept_name.code == 'BSS':
                dept_code = 'DEL'
            else:
                dept_code = dept_name.code
        new_code = 'MRF/' + dept_code + '/' + requisition + code
        result.code = new_code
        result.created_mrf = True if result.from_eq_bool is True else False
        print("result.created_mrf============================", result.created_mrf)
        if result.requisition_type == 'treasury':
            if result.budget_id:
                for rec in result.budget_id:
                    rec.write({
                        'mrf_id': result.id,
                    })
        self.env.user.notify_success("Manpower Requisition Form created successfully.")
        return result

    @api.multi
    def write(self, values):
        # print("valuess===========write==========================",values,self)
        if values.get('requisition_type'):
            requisition = (values.get('requisition_type')).capitalize()
            dept = self.dept_name
            rec = list(self.code.rpartition('/')[-3].split('/'))
            new_code = 'MRF/' + str(dept.code) + '/' + str(requisition) + '/' + rec[3] +'/'+ str(self.code.rpartition('/')[-1])
            values['code'] = new_code

        if not self.req_raised_by:
            emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if emp.job_id:
                values['req_raised_by'] = emp.display_name + " - " + emp.job_id.name
            else:
                values['req_raised_by'] = emp.name
        if values.get('state'):
            self.env['kw_recruitment_requisition_log'].create({
                'mrf_id': self.id,
                'from_status': self.state,
                'to_status': values.get('state'),
                'approver_id': self.env.user.employee_ids.id
            })
        count_data = False
        # pre_data = self.budget_id
        pre_data = self.get_filtered_data(self.budget_id.ids)
        
        if 'budget_id' in values and self.budget_id:
            # print("valssss========++++++++++",len(list(values['budget_id'][0][2])))
            if len(list(values['budget_id'][0][2])) < len(self.budget_id):
                # print("into next----")
                count_data = len(self.budget_id) - len(list(values['budget_id'][0][2]))
            
        result = super(Requisition, self).write(values)
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
   
        budget_lines = self.get_budget_lines(current_fiscal_year_id, self)
        # print("count_data==",count_data)
        # print("budget_lines==",budget_lines)
        if self.requisition_type == 'treasury' and 'budget_id' in values:
            if len(list(values['budget_id'][0][2])) < int(len(pre_data)) and 'no_of_resource' in values:
                # print("0000000000000000",self.budget_id)
                # print("======count_datacount_datacount_datacount_datacount_data===========",count_data)
                if count_data:
                    # print("pre_data====",pre_data,pre_data[:count_data])
                    query = f"""update kw_recruitment_budget_lines set mrf_id = null where id in ({str(pre_data[:count_data])[1:-1]})"""
                    # print("untage query--==222222",query)
                    self._cr.execute(query)

            elif 'no_of_resource' in values and values['no_of_resource'] > len(self.budget_id) and budget_lines:
                # print("---------------dddddtttttattattatatt----2----",self.budget_id[:-1])
                self.budget_id = [(6, 0, (self.budget_id + budget_lines[:self.no_of_resource - len(self.budget_id)]).ids)]
            else:
                if 'budget_id' in values:
                    # formatted_data = self.env['kw_recruitment_budget_lines'].browse(self.get_filtered_data(self.budget_id.ids))
                    # print("-----------------------",self.budget_id,formatted_data)
                    # for rec in formatted_data:
                    for rec in self.budget_id:
                        # print("rec===",rec)
                        rec.write({
                            'mrf_id': self.id,
                        })
        if 'code' not in values and not self._context.get("hide_alert"):
            self.env.user.notify_success("MRF updated successfully.")
        return result

    @api.constrains('resource', 'employee_id')
    def validate_employee(self):
        for record in self:
            if record.resource and record.resource == "replacement" and not record.employee_id:
                raise ValidationError("Please give employee name.")
            # elif record.employee_id:
            #     data= self.env['kw_recruitment_requisition'].sudo()
            #     if data.search([('employee_id', '=', record.employee_id.id)]) - self:
            #         raise ValidationError("Replacement Hiring is already completed for the said resource. Please check with RCM / TAG team.")

    @api.constrains('requisition_type', 'project')
    def validate_project(self):
        for record in self:
            if record.requisition_type and record.requisition_type == "project" and not record.project:
                raise ValidationError("Please give Project name")

    @api.constrains('min_exp_year', 'max_exp_year','from_eq_bool')
    def validate_experience(self):
        if int(self.max_exp_year) < int(self.min_exp_year) and not self.from_eq_bool :
            raise ValidationError("Max. experience year can not be less than min. experience year")

    # @api.constrains('min_sal', 'max_sal')
    # def validate_salary(self):
    #     if self.min_sal == 0 or self.max_sal == 0:
    #         raise ValidationError("Min. and Max. salary should be greater than Zero.")
    #     if self.max_sal < self.min_sal:
    #         raise ValidationError("Max. salary should be more than min. salary")

    # @api.depends('extra_load_on_budget', 'max_sal')
    # def calculate_extra_load(self):
    #     for extra_load in self:
    #         extra_load.extra_load_on_budget = extra_load.max_sal - extra_load.current_ctc

    # @api.constrains('extra_load_on_budget')
    # def _validate_extra_load(self):
    #     if self.extra_load_on_budget:
    #         if int(self.extra_load_on_budget) > 0:
    #             raise ValidationError("Your extra load on budget is %s. Do you want to proceed?" % self.extra_load_on_budget)
    
    # @api.constrains('max_sal')
    # def validate_salary_per_month(self):
    #     print("--------------------------------------->")
    #     if self.max_sal == 0:
    #         raise ValidationError("Please contact Hr for salary updation.")

    @api.constrains('no_of_resource')
    def validate_no_of_resource(self):
        # print("self.no_of_resource=====",self.no_of_resource)
        if self.no_of_resource == 0:
            pass
            # raise ValidationError("Number of resource can not be 0")

    def get_mail_activity_details(self):
        res_id = self.id
        res_model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)]).id
        date_deadline = date.today()
        note = "Action pending on mrf request."
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id  # todo is default
        # print(locals())
        return res_model_id, res_id, date_deadline, note, activity_type_id

    @api.multi
    def send_for_approval(self):
        # if not self._context.get('manpower_requisition_context'):
        #     Parameters = self.env['ir.config_parameter'].sudo()
        #     first_approver_list = literal_eval(Parameters.get_param('kw_recruitment.first_level_approver_ids', '[]'))
        #     if self.max_sal < 1 and self.env.user.employee_ids.id in first_approver_list:
        #         raise ValidationError('Please update salary information.')
        #     wizard_form = self.env.ref('kw_recruitment.mrf_bugetwarning_view', False)
        #     # if self.extra_load_on_budget > 0 and self.resource == 'replacement':
        #     #     return {
        #     #         'type': 'ir.actions.act_window',
        #     #         'view_type': 'form',
        #     #         'view_mode': 'form',
        #     #         'view_id': wizard_form.id,
        #     #         'res_model': 'display.message',
        #     #         'target': 'new',
        #     #         'context': {'default_mrf_id': self.id, 'default_extra_load_on_budget': self.extra_load_on_budget}
        #     #     }
        #     # else:
        #     self.send_for_approval1()
        # else:
        self.send_to_takeaction()
        
    @api.multi
    def mrf_validate(self):  
        if not self.max_sal:
            raise ValidationError("Salary is not updated,Please Notify to TAG.")
        else:
            self.write({'state': 'approve'}) 
        
    @api.multi
    def mrf_reopen(self):  
        self.write({'state': 'draft'})  
           
    @api.multi
    def send_to_takeaction(self):
        # users_data = self.env['res.users'].sudo().search([])
        # rcm_head = users_data.filtered( lambda user : user.has_group('kw_resource_management.group_budget_manager') == True)
        # work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
        self.write({'state': 'sent'})
        # mrf_token = self.env['kw_recruitment_requisition_approval'].create(
        #     {'mrf_id': self.id,
        #      'employee_id': self.approver_id.id})
        logtable = self.env['kw_recruitment_requisition_log'].search(
            [('mrf_id', '=', self.id), ('to_status', '=', 'sent')], limit=1)
        mrfview = self.env.ref('kw_recruitment.kw_mrf_rcm_checkpoint_act_window')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
        db_name = self._cr.dbname
        param = self.env['ir.config_parameter'].sudo()
        to_users = literal_eval(param.get_param('kw_recruitment.rcm_head', '[]'))
        tag_to = self.env['hr.employee'].browse(to_users).mapped('work_email')[0]
        cc_users = set(literal_eval(param.get_param('kw_recruitment.approval_ids', '[]'))
                       + literal_eval(param.get_param('kw_recruitment.notify_cc_ids', '[]'))
                       + literal_eval(param.get_param('kw_recruitment.tag_head', '[]')))
        tag_cc = ','.join(self.env['hr.employee'].browse(cc_users).mapped('work_email'))

        template_obj = self.env.ref('kw_recruitment.template_for_email_notification_rcm_head')
        if template_obj:
            # token=mrf_token.access_token,
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                dbname=db_name,
                action_id=action_id,
                email_to=tag_to,
                email_cc=tag_cc).send_mail(logtable.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        if not self.role_id or not self.categ_id:
            # print("inside self role and category if")
            param = self.env['ir.config_parameter'].sudo()
            cc_group = literal_eval(param.get_param('kw_recruitment.tag_head', '[]'))
            tag_to_mail = ','.join(self.env['hr.employee'].browse(cc_group).mapped('work_email'))
            tag_cc_users_mail = set(literal_eval(param.get_param('kw_recruitment.approval_ids', '[]'))
                                    + literal_eval(param.get_param('kw_recruitment.notify_cc_ids', '[]')))
            tag_cc_user = ','.join(self.env['hr.employee'].browse(tag_cc_users_mail).mapped('work_email'))
            template_obj = self.env.ref('kw_recruitment.tag_employee_mail_template')
            if template_obj:
                if template_obj:
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                        dbname=db_name,
                        action_id=action_id,
                        emp_name='Team',
                        email_to=tag_cc_user,
                        email_cc=tag_to_mail).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light')
                self.env.user.notify_success("MRF Applied successfully.")

    # @api.multi
    # def send_for_approval1(self):
    #     print("inside approval======")
    #     # self.get_mail_activity_details()
    #     # mail_activity = self.env['mail.activity']
    #     """#Generate Token"""
    #     MRF_token = self.env['kw_recruitment_requisition_approval'].create(
    #         {'mrf_id': self.id,
    #          'employee_id': self.approver_id.id})

    #     self.write({'state': 'sent'})
    #     logtable = self.env['kw_recruitment_requisition_log'].search(
    #         [('mrf_id', '=', self.id), ('to_status', '=', 'sent')], limit=1)
    #     mrfview = self.env.ref('kw_recruitment.kw_recruitment_requisition_pending_act_window')
    #     action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
    #     db_name = self._cr.dbname
    #     if self.approver_id and self.approver_id.parent_id:
    #         # Mark done activity if found for current user
    #         # res_model_id,res_id,_,_,_= self.get_mail_activity_details()
    #         # activity = mail_activity.search([('res_id', '=', res_id), ('res_model_id', '=', res_model_id),('user_id','=',self._uid)])
    #         # if activity:
    #         #     activity.action_feedback() # makes done activity
    #         # create activity for approver
    #         # if self.approver_id.user_id:
    #         #     res_model_id, res_id, date_deadline, note, activity_type_id = self.get_mail_activity_details()
    #         # mail_activity.create({
    #         #     'res_model_id': res_model_id,
    #         #     'activity_type_id': activity_type_id,
    #         #     'res_id': res_id,
    #         #     'date_deadline': date_deadline,
    #         #     'user_id': self.approver_id.user_id.id,
    #         #     'note': note})
    #         # Get Log ID
    #         template_obj = self.env.ref('kw_recruitment.template_for_approval')
    #         if template_obj:
    #             mail = self.env['mail.template'].browse(template_obj.id).with_context(
    #                 dbname=db_name,
    #                 token=MRF_token.access_token,
    #                 action_id=action_id).send_mail(logtable.id, email_values={'email_to': self.approver_id.work_email},
    #                                                notif_layout='kwantify_theme.csm_mail_notification_light')
    #             self.env.user.notify_success("Mail sent successfully.")
    #     elif self.approver_id and not self.approver_id.parent_id:
    #         viewapprove = self.env.ref('kw_recruitment.kw_recruitment_requisition_approved_act_window')
    #         action_id = self.env['ir.actions.act_window'].search([('view_id', '=', viewapprove.id)], limit=1).id
    #         template_obj = self.env.ref('kw_recruitment.template_for_approval_witout_approver')
    #         if template_obj:
    #             mail = self.env['mail.template'].browse(template_obj.id).with_context(
    #                 dbname=db_name,
    #                 token=MRF_token.access_token,
    #                 action_id=action_id,
    #                 approver=self.approver_id.name,
    #                 mailto=self.approver_id.work_email).send_mail(logtable.id,
    #                                                               notif_layout='kwantify_theme.csm_mail_notification_light')
    #             self.env.user.notify_success("Mail sent successfully.")
    #     else:
    #         """# # Fist approver to Second Approver where First Approver is the MRF Creator"""
    #         Parameters = self.env['ir.config_parameter'].sudo()
    #         sec_level_approver_config = Parameters.get_param('kw_recruitment.second_level_approver_ids')
    #         sec_level_approver_list = sec_level_approver_config.strip('][').split(', ')
    #         if sec_level_approver_list:
    #             emps = self.env['hr.employee'].search([('id', 'in', [int(i) for i in sec_level_approver_list])])
    #             self.write({'last_approver_ids': [(6, 0, emps.ids)]})
    #             template_obj = self.env.ref('kw_recruitment.template_for_approval_witout_approver')
    #             approvers = self.env['hr.employee'].search([('id', 'in', [int(rec) for rec in sec_level_approver_list])])
    #             if approvers:
    #                 # approvers = self.env['hr.employee'].search([('job_id', 'in', jobs.ids)])
    #                 for approver in approvers:
    #                     # start :- activity code
    #                     # res_model_id, res_id, date_deadline, note, activity_type_id = self.get_mail_activity_details()
    #                     # if approver.user_id:
    #                     # mail_activity.create({
    #                     #     'res_model_id': res_model_id,
    #                     #     'activity_type_id': activity_type_id,
    #                     #     'res_id': res_id,
    #                     #     'date_deadline': date_deadline,
    #                     #     'user_id': approver.user_id.id,
    #                     #     'note': note})
    #                     # end :- activity code
    #                     if template_obj:
    #                         MRFt = self.env['kw_recruitment_requisition_approval'].create(
    #                             {'mrf_id': self.id, 'employee_id': approver.id})
    #                         mail = self.env['mail.template'].browse(template_obj.id).with_context(
    #                             dbname=db_name,
    #                             token=MRFt.access_token,
    #                             action_id=action_id,
    #                             approver=approver.name,
    #                             mailto=approver.work_email).send_mail(logtable.id,
    #                                                                   notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                   force_send=True)
    #                         self.env.user.notify_success("Mail sent successfully.")
    #     return True

    def get_notification_user_emails(self):
        param = self.env['ir.config_parameter'].sudo()
        approval_ids = literal_eval(param.get_param('kw_recruitment.approval_ids'))
        all_jobs = self.env['hr.employee'].browse(approval_ids)
        email_list = []
        if approval_ids:
            empls = self.env['hr.employee'].search([('id', 'in', all_jobs.ids)])
            if empls:
                email_list = [emp.work_email for emp in empls if emp.work_email]
        return ",".join(email_list)

    @api.multi
    def action_approved(self):
        if self._context.get('manpower_requisition_context'):
            wizard_form = self.env.ref('kw_recruitment.final_mrf_approve_view', False)
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': wizard_form.id,
                'res_model': 'kw.mrf.final.approve',
                'target': 'new',
                'context': {'default_mrf_id': self.id, }
            }
        else:
            if self.max_sal < 1:
                raise ValidationError('Please update salary information.')
            wizard_form = self.env.ref('kw_recruitment.mrf_approve_view', False)
            check_sal = True if self.extra_load_on_budget > 0 and self.resource == 'replacement' else False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': wizard_form.id,
                'res_model': 'kw.mrf.final.approve',
                'target': 'new',
                'context': {'default_mrf_id': self.id, 'default_extra_load_on_budget': self.extra_load_on_budget,
                            'default_check_salary': check_sal}
            }

    @api.multi
    def action_approved_forward(self):
        if self.max_sal < 1:
            raise ValidationError('Please update salary information.')
        wizard_form = self.env.ref('kw_recruitment.mrf_approve_forward_view', False)
        check_sal = True if self.extra_load_on_budget > 0 and self.resource == 'replacement' else False
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw.mrf.approve',
            'target': 'new',
            'context': {'default_mrf_id': self.id, 'default_extra_load_on_budget': self.extra_load_on_budget,
                        'default_check_salary': check_sal}
        }

    @api.multi
    def action_revise(self):
        wizard_form = self.env.ref('kw_recruitment.mrf_revise_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw.mrf.revise',
            'target': 'new',
            'context': {'default_mrf_id': self.id}
        }

    @api.multi
    def action_hold(self):
        wizard_form = self.env.ref('kw_recruitment.mrf_hold_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw.mrf.hold',
            'target': 'new',
            'context': {'default_mrf_id': self.id}
        }
    
    def action_validate(self):
        # self.update_budget_rcm()
        if not self.max_sal and self.from_eq_bool == False:
            raise ValidationError("Please notify TAG for Salary updation")
        else:
            wizard_form = self.env.ref('kw_recruitment.mrf_rcm_valiadate_view', False)

            if self.notify_hr != True and self.type_payroll == 'ksl_payroll':
                self.write({'notify_hr': True})
                logtable = self.env['kw_recruitment_requisition_log'].search(
                [('mrf_id', '=', self.id), ('to_status', '=', 'draft')], limit=1)
                mrf_view = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
                action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrf_view.id)], limit=1).id
                db_name = self._cr.dbname
                """ HR is Fetched from general setting """
                template_obj = self.env.ref('kw_recruitment.hr_mrf_notify_mail_template')
                user_groups = self.env.ref('kw_recruitment.group_core_hr').users
                tag_to = ','.join(user_groups.mapped('email'))

                if template_obj:
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    emp_name='HR',
                    email_to=tag_to).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
                    self.env.user.notify_success("Mail sent successfully.")
            else:
                raise ValidationError("You have Already Notify to HR")
        return {
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': wizard_form.id,
        'res_model': 'kw.mrf.validate',
        'target': 'new',
        'context': {'default_mrf_id': self.id}
        } 

  
      
    def action_forward_to_ceo(self):
        self.update_budget_rcm()
        if not self.role_id or not self.categ_id:
            raise ValidationError("Please notify TAG for Employee Role & Category updation")
        else:
            wizard_form = self.env.ref('kw_recruitment.mrf_rcm_forward_to_ceo_view', False)
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': wizard_form.id,
                'res_model': 'kw.mrf.forward_to_ceo',
                'target': 'new',
                'context': {'default_mrf_id': self.id}
            }    
    
    def action_reject(self):
        wizard_form = self.env.ref('kw_recruitment.mrf_reject_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw.mrf.reject',
            'target': 'new',
            'context': {'default_mrf_id': self.id}
        }

    def action_edited(self):
        wizard_form = self.env.ref('kw_recruitment.mrf_edited_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw.mrf.edited',
            'target': 'new',
            'context': {'default_mrf_id': self.id}
        }
        
    def action_button_rcm_checkpoint(self):
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
        treasury_budget_id = self.env['kw_recruitment_budget_lines'].search(
            [('fiscalyr', '=', current_fiscal_year_id.id), ('dept_id', '=', self.dept_name.id)], order='id asc')
        if treasury_budget_id:
            total_planned, total_incurred, total_remaining = self.env['kw_recruitment_treasury_budget_line'].get_budget_calculations(treasury_budget_id.ids)
            if total_incurred == 0 or total_incurred is None:
                self.dept_remaining_budget = total_planned
            else:
                self.dept_remaining_budget = total_planned - total_incurred
        view_form = self.env.ref('kw_recruitment.view_kw_mrf_rcm_checkpoint_form')
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_recruitment_requisition',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': view_form.id,
            'target': 'self',
        }
        if self.env.user.has_group('kw_recruitment.group_tag_budget_user') \
                or self.env.user.has_group('kw_resource_management.group_budget_manager'):
            action['context'] = {'requisition_type': self.requisition_type, 'is_type_project': self.is_type_of_project,
                                 'edit': True, 'show_validation': True, 'hide_alert': True}
            action['flags'] = {'mode': 'edit'}
        elif self.env.user.has_group('kw_wfh.group_hr_hod') or self.env.user.in_second_level_approval():
            action['context'] = {'create': False, 'edit': False, 'show_validation': True, 'hide_alert': True}
        # elif self.env.user.has_group(('kw_resource_management.group_budget_manager')) :
            # action['context']= {'requisition_type': self.requisition_type,'is_type_project': self.is_type_of_project,'edit':True}
            # action['flags']={'mode': 'edit'}
        else:
            action['context'] = {'requisition_type': self.requisition_type, 'is_type_project': self.is_type_of_project,
                                 'edit': False, 'show_validation': True, 'hide_alert': True}

        return action

    def send_to_tag(self):
        if self.state != 'draft':
            self.write({'state': 'draft'})
        # users_data = self.env['res.users'].sudo().search([])
        logtable = self.env['kw_recruitment_requisition_log'].search(
            [('mrf_id', '=', self.id), ('to_status', '=', 'draft')], limit=1)
        mrf_view = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrf_view.id)], limit=1).id
        db_name = self._cr.dbname
        """ Tag is Fetched from general setting  """
        # manager = users_data.filtered(lambda user: user.has_group('kw_recruitment.group_tag_budget_user') == True)
        template_obj = self.env.ref('kw_recruitment.tag_employee_mail_template')

        param = self.env['ir.config_parameter'].sudo()
        to_users = literal_eval(param.get_param('kw_recruitment.approval_ids', '[]'))
        tag_to = self.env['hr.employee'].browse(to_users).mapped('work_email')[0]
        cc_users = literal_eval(param.get_param('kw_recruitment.notify_cc_ids', '[]'))
        tag_cc = ','.join(self.env['hr.employee'].browse(cc_users).mapped('work_email'))

        # for rec in manager:
        #     mrf_token = self.env['kw_recruitment_requisition_approval'].create({'mrf_id': self.id,
        #                                                                         'employee_id': rec.employee_ids.id})
        # token=mrf_token.access_token,
        if template_obj:
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                dbname=db_name,
                action_id=action_id,
                emp_name='TAG',
                email_cc=tag_cc,
                email_to=tag_to).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Mail sent successfully.")
            
    def mrf_send_to_hr(self):
        if self.notify_hr != True:
            self.write({'notify_hr': True})
            logtable = self.env['kw_recruitment_requisition_log'].search(
                [('mrf_id', '=', self.id), ('to_status', '=', 'draft')], limit=1)
            mrf_view = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
            action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrf_view.id)], limit=1).id
            db_name = self._cr.dbname
            """ HR is Fetched from general setting  """
            template_obj = self.env.ref('kw_recruitment.hr_mrf_notify_mail_template')
            user_groups = self.env.ref('kw_recruitment.group_core_hr').users
            # param = self.env['ir.config_parameter'].sudo()
            # to_users = literal_eval(param.get_param('kw_recruitment.hr_approval_ids', '[]'))
            # if to_users:
            #     empl = self.env['hr.employee'].browse(to_users)
            #     for user in empl:
            #         user = user.user_id
            #         user.sudo().write({'groups_id': [(4, user_groups.id)]})
            # tag_to = self.env['hr.employee'].browse(to_users).mapped('work_email')
            # cc_users = literal_eval(param.get_param('kw_recruitment.notify_cc_ids', '[]'))
            tag_to = ','.join(user_groups.mapped('email'))
            # for rec in manager:
            #     mrf_token = self.env['kw_recruitment_requisition_approval'].create({'mrf_id': self.id,
            #                                                                         'employee_id': rec.employee_ids.id})
            # token=mrf_token.access_token,
            if template_obj:
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    emp_name='HR',
                    email_to=tag_to).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Mail sent successfully.")
        else:
            raise ValidationError("You have Already Notify to HR")

    @api.multi
    def update_budget_rcm(self):
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].sudo().get_fiscal_year()
        if self.requisition_type == 'treasury':
            if self.technology and self.job_position and self.min_exp_year and self.resource == 'new':
                if self.no_of_resource != len(self.budget_id):
                    if self.no_of_resource and self.budget_id:
                        if self.no_of_resource > len(self.budget_id) :
                            raise ValidationError(f"Budget is available for {len(self.budget_id)} resource.Please contact Finance department.")

                    budget_lines = self.env['kw_recruitment_budget_lines'].sudo().search(
                        [('fiscalyr', '=', current_fiscal_year_id.id), ('mrf_id', '=', False), ('offer_id', '=', False),
                         ('dept_id', '=', self.dept_name.id), ('technology', '=', self.technology.id),
                         ('designation', '=', self.job_position.id), ('exp_year', '=', self.min_exp_year),
                         ('status', '=', 'publish')], order='department_sequence asc')

                    # print("print budget lines inside update budget rcm=======================------------------------+++++++++++++++++++++",budget_lines)
                        
                    monthly_budgte = budget_lines.mapped('mar_budget')
                    if budget_lines:
                        # print("inside budget lines==========+++++++++++++++++++++")
                        if not self.budget_id:
                            # print("inside 222222222222222222=========")
                            if self.no_of_resource < len(budget_lines):
                                # print("inside 3333333333333")
                                self.max_sal = int(str(list(set(monthly_budgte))[0]))
                                self.budget_id =  [(6, 0,budget_lines.ids[:self.no_of_resource])]
                                # print("self.bu/dget_id=================",self.budget_id,budget_lines.ids[:self.no_of_resource])
                            else:
                                raise ValidationError(
                                    f"Total resource is {self.no_of_resource} and total budget available is {len(budget_lines)} .")

                    elif self.no_of_resource == len(monthly_budgte):
                        if len(set(monthly_budgte)) == 1:
                            self.max_sal = int(str(list(set(monthly_budgte))[0]))
                        else:
                            raise ValidationError("Different Budget data Found for required Details. Please contact Finance department.")

                    elif self.no_of_resource and self.max_sal == 0:
                        logtable = self.env['kw_recruitment_requisition_log'].search([('mrf_id', '=', self.id), ('to_status', '=', 'draft')], limit=1)
                        # print('logtableeeeeeeeeeeeeee================++++++++++',logtable)
                        tag_manager = self.env.ref('kw_recruitment.group_tag_budget_user').users
                        tag_to = ','.join(tag_manager.mapped('employee_ids.work_email'))
                        finance_user = self.env.ref('kw_recruitment.group_hr_recruitment_accounts').users
                        cc_user = ','.join(finance_user.mapped('employee_ids.work_email'))
                        template_obj = self.env.ref('kw_recruitment.budget_not_found_mail_notification_template')
                    
                        if template_obj:
                            # print("inside templtae========+++++++++++++++++++++++++++============")
                            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                                emp_name='TAG',
                                email_cc=tag_to,
                                email_to=cc_user).send_mail(logtable.id,notif_layout='kwantify_theme.csm_mail_notification_light')
                            self.env.user.notify_success("Mail sent successfully.")
                        # raise ValidationError(f"Maximum number of resources can be {len(budget_lines)}")

                    else:
                        self.budget_id = [(5, 0, 0)]
                        # print("inside else validation==========================+++++++++++++++++++++++++++++++++++++++++++++")
                        # raise ValidationError(f"Maximum number of resources can be {len(budget_lines)}")

            # else:
            #     self.max_sal = self.employee_id.current_ctc
            #     # print("inside else=========================================================================")
            #     self.avg_replacement_sal = self.max_sal / self.no_of_resource if self.max_sal else 0

    def send_to_rcm(self):
        if self.max_sal:
            self.write({'state': 'draft'})
            logtable = self.env['kw_recruitment_requisition_log'].search(
                [('mrf_id', '=', self.id), ('to_status', '=', 'draft')], limit=1)
            mrfview = self.env.ref('kw_recruitment.view_manpower_requisition_form_form')
            action_id = self.env['ir.actions.act_window'].search([('view_id', '=', mrfview.id)], limit=1).id
            db_name = self._cr.dbname
            template_obj = self.env.ref('kw_recruitment.notify_to_rcm_mail_template')
            param = self.env['ir.config_parameter'].sudo()
            to_users = literal_eval(param.get_param('kw_recruitment.rcm_head', '[]'))
            rcm_tag_to = self.env['hr.employee'].browse(to_users)
            if rcm_tag_to and template_obj:
                # mrf_token = self.env['kw_recruitment_requisition_approval'].create({'mrf_id': self.id, 'employee_id': rcm_tag_to.id})
                cc_users = set(literal_eval(param.get_param('kw_recruitment.approval_ids', '[]'))
                               + literal_eval(param.get_param('kw_recruitment.notify_cc_ids', '[]')))
                tag_cc = ','.join(self.env['hr.employee'].browse(cc_users).mapped('work_email'))
                # token = mrf_token.access_token if mrf_token else False,
                email_to = ','.join(rcm_tag_to.mapped('work_email'))
                # rcm_tag_to.mapped('work_email')[0]
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    dbname=db_name,
                    action_id=action_id,
                    emp_name='All',
                    email_cc=tag_cc,
                    email_to=email_to).send_mail(logtable.id, notif_layout='kwantify_theme.csm_mail_notification_light')
                self.env.user.notify_success("Mail sent successfully.")
        else:
            raise ValidationError("Please Update Salary Information.")

    def action_create_job(self):
        createjob = self.env['kw_hr_job_positions']
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': createjob,
            'res_model': 'kw_hr_job_positions',
            'target': 'self',
            'context': {'default_department_id': self.dept_name.id,
                        'default_job_id': self.job_position.id,
                        'default_address_id': [self.branch_id.id],
                        'default_min_exp_year': self.min_exp_year,
                        'default_max_exp_year': self.max_exp_year,
                        'default_no_of_recruitment': self.no_of_resource,
                        }
        }

    def update_access_mrf(self):
        mrf_grade_emp = self.env['mrf_employee_grade_access'].search([]).mapped('grade_ids')
        grades = self.env['kwemp_grade_master'].search([('id', 'in', list(set(mrf_grade_emp.ids)))])
        # grades = self.env['kwemp_grade_master'].search([('name', 'in', ['M6', 'M7', 'M8', 'M9', 'M10'])])
        employees = self.env['hr.employee'].search([('grade', 'in', grades.ids)])
        if employees:
            group_id = self.env.ref('kw_recruitment.group_kw_mrf_user')
            group_id.users = [(4, empl.user_id.id) for empl in employees]

    @api.model
    def default_get(self, fields):
        res = super(Requisition, self).default_get(fields)
        if (self._context.get('manpower_requisition_context')
                or self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager')
                and not self._context.get('manpower_indent_form_context')):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            # print("employee=======",employee)
            if employee:
                res['dept_name'] = employee.department_id.id
                approver_list = self.env['mrf_approver_department_config'].sudo().search(
                    [('department_ids', 'in', employee.department_id.ids)], limit=1)
                if approver_list:
                    # if approver_list and not self.env.user.in_first_level_employee():
                    res['approver_id'] = approver_list.approver_id.id
                # if self.env.user.in_first_level_employee():
        return res

    def get_mrf_access_employees(self):
        grade_rec_ids = self.env['mrf_employee_grade_access'].sudo().search([]).mapped('grade_ids')
        employee = self.env['hr.employee'].sudo().search([('grade', 'in', list(set(grade_rec_ids.ids)))])
        return employee

    @api.multi
    def action_redirect_mrf_all_view(self):
        # employee = self.get_mrf_access_employees()
        # if self.env.user.employee_ids.id in employee.ids:
        if self.env.user.has_group('kw_recruitment.group_kw_mrf_user') \
                or self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager') \
                or self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager'):
            tree_view_id = self.env.ref('kw_recruitment.view_kw_mrf_tree').id
            form_view_id = self.env.ref('kw_recruitment.view_kw_mrf_form').id
            action = {
                'name': 'MRF',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_recruitment_requisition',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'target': 'self',
                # 'context' : {'manpower_requisition_context':True}
            }
            """ Dynamic Domain for MRF """
            if self.env.user.has_group('kw_recruitment.group_kw_mrf_user'):
                action['domain'] = [('create_uid','=',self.env.user.id)]
            if self.env.user.has_group('kw_wfh.group_hr_hod'):
                action['domain'] = [('dept_name','=',self.env.user.employee_ids.department_id.id)]
            if self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager') \
                    or self.env.user.has_group('kw_resource_management.group_budget_manager') \
                    or self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                action['domain'] = []
            if self.env.user.in_second_level_approval() \
                    or self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager'):
                action['domain'] = []
            if self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager') \
                    and not self.env.user.in_second_level_approval() \
                    or self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager') \
                    and not self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager') \
                    or self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager') \
                    and not self.env.user.has_group('kw_resource_management.group_budget_manager') \
                    or self.env.user.has_group('kw_recruitment.group_kw_mrf_report_manager') \
                    and not self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                action['context'] = {'manpower_requisition_context': True, 'create': False, 'edit': False,
                                     'delete': False}
            else:
                action['context'] = {'manpower_requisition_context': True}
                # print("action-----",action)
            return action
        # else:
        #     raise ValidationError(f"You Don't have access.")
    
    @api.multi
    def action_redirect_mrf_takeaction_view(self):
        # employee = self.get_mrf_access_employees()
        # if self.env.user.employee_ids.id in employee.ids:
        if self.env.user.has_group('kw_recruitment.group_kw_mrf_user') \
                or self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            tree_view_id = self.env.ref('kw_recruitment.view_kw_mrf_rcm_checkpoint_tree').id
            # form_view_id = self.env.ref('kw_recruitment.view_kw_mrf_rcm_checkpoint_form').id
            action = {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_recruitment_requisition',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree')],
                'target': 'self',
                'context': {'manpower_requisition_context': True}
            }
            """ Dynamic Domain for MRF """
            Parameters = self.env['ir.config_parameter'].sudo()
            rcm_head = literal_eval(Parameters.get_param('kw_recruitment.rcm_head', '[]'))
            emp = self.env['hr.employee'].browse(rcm_head)
            if self.env.user.has_group('kw_recruitment.group_kw_mrf_user'):
                action['domain'] = [('state', '!=', 'draft'), ('create_uid', '=', self.env.user.id)]
            if self.env.user.has_group('kw_resource_management.group_budget_manager') \
                    and self.env.user.employee_ids.id == emp.id:
                action['domain'] = [('state', 'in', ['sent', 'forward']), ('state', '!=', 'draft')]
            elif self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                action['domain'] = [('state', 'in', ['sent', 'forward']), ('state', '!=', 'draft')]
            elif self.env.user.has_group('kw_wfh.group_hr_hod'):
                action['domain'] = [('approver_id', '=', self.env.user.employee_ids.id),
                                    ('state', 'in', ['forward', 'hold']), ('state', '!=', 'draft')]
            else:
                # print("inside elseeeeeeeeee of action")
                # for special case such assss Sanakarshan sir is not in HOD group
                action['domain'] = [('approver_id', '=', self.env.user.employee_ids.id),
                                    ('state', 'in', ['forward', 'hold']), ('state', '!=', 'draft')]

            """ Fetching CEO office employee from general settings """
            if self.env.user.in_second_level_approval():
                action['domain'] = [('forward_to_ceo', '=', True)]
            return action
        # else:
        #     raise ValidationError(f"You Don't have access.")

    @api.multi
    def action_redirect_approved_mrf_view(self):
        # employee = self.get_mrf_access_employees()
        # if self.env.user.employee_ids.id in employee.ids:
        if self.env.user.has_group('kw_recruitment.group_kw_mrf_user') \
                or self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            tree_view_id = self.env.ref('kw_recruitment.view_kw_mrf_approve_action_tree').id
            form_view_id = self.env.ref('kw_recruitment.view_kw_mrf_approve_actions_form').id
            action = {
                'name': 'Approved MRF',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_recruitment_requisition',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'target': 'self',
                'context' : {'manpower_requisition_context':True}
            }
            """ Dynamic Domain for MRF """
            if self.env.user.has_group('kw_recruitment.group_kw_mrf_user'):
                action['domain'] = [('create_uid', '=', self.env.user.id), ('state', '=', 'approve')]
            if self.env.user.has_group('kw_wfh.group_hr_hod'):
                action['domain'] = [('dept_name', '=', self.env.user.employee_ids.department_id.id),
                                    ('state', 'in', ['forward'])]
            if self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager') \
                    or self.env.user.has_group('kw_resource_management.group_budget_manager') \
                    or self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                action['domain'] = [('state', '=', 'approve')]

            return action
        # else:
        #     raise ValidationError(f"You Don't have access.")

    def action_mrf_to_mif_create(self):
        mrf_record = self.env['kw_recruitment_requisition'].sudo().search([('mif_rec_id', '=', False)], limit=25)
        # print("mrf_record >>>>>>>>>>>> ", mrf_record)
        for rec in mrf_record:
            codee = ''
            code = ''
            if not rec.mif_rec_id:
                codee = rec.code.replace('MRF', 'MIF')
                code = codee.replace("/Treasury", "")
                code = code.replace("/Project", "")
                code = code.replace("/FTE", "")
                code = code.replace("/RET", "")
                # if '/Treasury' in codee:
                #     pass
                # else:
                # print("rec.create_uid.employee_ids.id,==================",rec.branch_id.ids, rec.code, code)
                mif_rec = self.env['kw_manpower_indent_form'].sudo().create({'code': code,
                                                                             'req_raised_by_id': rec.create_uid.employee_ids.id,
                                                                             'sbu_id': rec.sbu_id.id if rec.sbu_id else '',
                                                                             'resource': rec.resource,
                                                                             'employee_id': rec.employee_id.id if self.resource == 'replacement' else '',
                                                                             'job_position': rec.job_position.id if rec.job_position else '',
                                                                             'date_requisition': rec.date_requisition if rec.date_requisition else '',
                                                                             'no_of_resource': rec.no_of_resource,
                                                                             'skill_set': rec.skill_set,
                                                                             'qualification': rec.qualification,
                                                                             'min_exp_year': rec.min_exp_year if rec.min_exp_year else '',
                                                                             'max_exp_year': rec.max_exp_year if rec.max_exp_year else '',
                                                                             'description': rec.description,
                                                                             'effective_date_of_deployment': rec.effective_date_of_deployment,
                                                                             'type_project': rec.type_project,
                                                                             'project': rec.project.id,
                                                                             'branch_id': [(4, id, False) for id in rec.branch_id.ids],
                                                                             'technology': rec.technology.id
                                                                             })
                rec.mif_rec_id = mif_rec.id


    def render_mrf_report_view_actions(self):
        # param = self.env['ir.config_parameter'].sudo()
        # to_users = literal_eval(param.get_param('kw_recruitment.hr_approval_ids', '[]'))
        # if to_users:
        #     empl = self.env['hr.employee'].browse(to_users)
        user_groups = self.env.ref('kw_recruitment.group_core_hr')
            # for user in empl:
            #     user = user.user_id
            #     user.write({'groups_id': [(4, user_groups.id)]})
        if self.env.user in user_groups.users:
            mrf_data = self.env['kw_recruitment_requisition'].sudo().search([('notify_hr','=',True)])
            mrf_ids = mrf_data.mapped('id')
        
        if mrf_ids:
            tree_view_id = self.env.ref('kw_recruitment.view_manpower_requisition_hr_tree').id
            form_view_id = self.env.ref('kw_recruitment.view_manpower_requisition_hr_form').id
            
            action = {
                'name': 'MRF',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_recruitment_requisition',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', mrf_ids),('state','in',['draft','approve'])],
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'target': 'self',
            }
            return action
                

class MrfReportConfig(models.Model):
    _name = "kw_mrf_report_access"
    _description = "MRF Report Access"
    _rec_name = 'name'

    name = fields.Char(default='MRF Report Access')
    employee_ids = fields.Many2many('hr.employee', 'report_mrf_kw_employee_rel', 'mrf_id', 'emp_id', string="Employees",
                                    track_visibility='onchange')

    @api.constrains('name')
    def restrict_multiple_record(self):
        records = self.env['kw_mrf_report_access'].sudo().search([])
        if records and len(records) > 1:
            raise ValidationError("You cannot create multiple record.")

    @api.model
    def create(self, vals):
        if 'employee_ids' in vals and vals['employee_ids']:
            report_access_users = self.env.ref('kw_recruitment.group_kw_mrf_report_manager', False)
            report_managers = self.env['hr.employee'].sudo().browse(vals['employee_ids'][0][2])
            for rec in report_managers:
                report_access_users.sudo().write({'users': [(4, rec.user_id.id)]})
                self.env.user.notify_success("Users added to the Report Manager group")

        res = super(MrfReportConfig, self).create(vals)
        self.env.user.notify_success(message='Report access has been given successfully.')
        return res

    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee']
        if 'employee_ids' in vals and vals['employee_ids']:
            report_access_users = self.env.ref('kw_recruitment.group_kw_mrf_report_manager', False)
            report_managers = employee.sudo().browse(vals['employee_ids'][0][2])
            remove_users_access = self.employee_ids - report_managers
            for rec in report_managers:
                report_access_users.sudo().write({'users': [(4, rec.user_id.id)]})
                self.env.user.notify_success("Users added to the Report Manager group")
            if len(remove_users_access)>0:
                for rec in remove_users_access:
                    report_access_users.sudo().write({'users': [(3, rec.user_id.id)]})

        res = super(MrfReportConfig, self).write(vals)
        self.env.user.notify_success(message='Report access has been given successfully.')
        return res


class display_message(models.Model):
    _name = "display.message"
    _description = "display.message"

    extra_load_on_budget = fields.Integer('Extra load on Budget')
    mrf_id = fields.Many2one('kw_recruitment_requisition', 'Requisition')

    def save_message(self):
        if self.mrf_id:
            self.mrf_id.send_for_approval1()
            return {'type': 'ir.actions.act_window_close'}

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}