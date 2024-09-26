# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from datetime import date
import random
import uuid
from dateutil.relativedelta import relativedelta
from datetime import datetime



def _default_access_token(self):
    return uuid.uuid4().hex


class SBUResourceTagging(models.Model):
    _name = 'sbu_resource_tagging'
    _description = 'SBU Resource Tagging'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Skill')
    sbu_type = fields.Selection(
        string='Resource Type',
        selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('none', 'None')]
    )
    sbu = fields.Many2one("kw_sbu_master", "SBU")
    sbu_name = fields.Char(related='sbu.name', string="SBU")
    engagement_plan = fields.Char()
    engagement_plan_by_id = fields.Many2one('kw_engagement_master')
    till_date = fields.Date()
    future_engagement = fields.Char()
    # project_id = fields.Many2one('project.project',string="Project Name")
    # other_text  = fields.Text(string = "Other")
    future_projection =  fields.Char(string="Future Projection")
    total_experience_display = fields.Char(compute='_compute_total_exp')
    engagement_plan_details = fields.Text("Engagement Plan Details")


    @api.depends('employee_id')
    def _compute_total_exp(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.employee_id.date_of_joining:
                difference = relativedelta(datetime.now(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months

            if rec.employee_id.work_experience_ids:
                for exp_data in rec.employee_id.work_experience_ids:
                    exp_difference = relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            # Convert the total_years and total_months to a decimal format
            if total_years > 0 or total_months > 0:     
                rec.total_experience_display = " %s.%s " % (total_years, total_months)
            else:
                rec.total_experience_display = ''

    #    3-coding,7-Delivery,1-sales,19-Team/Tech lead
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT  row_number() over() as id,
                hr.id as employee_id,
                hr.job_id as designation,
                hr.name as name,
                hr.date_of_joining as date_of_joining,
                hr.emp_role as emp_role,
                hr.emp_category as emp_category,
                hr.employement_type as employement_type,
                hr.job_branch_id as job_branch_id,
                hr.sbu_type as sbu_type,
                hr.sbu_master_id as sbu,
                --(select name from kw_sbu_master where id = hr.sbu_master_id) as sbu,
               (select primary_skill_id from resource_skill_data where employee_id=hr.id ) as primary_skill_id,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date
                            else null
                        end
                    else null
                end as till_date,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then 
                                case 
                                    when (select engagement_plan from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select engagement_plan from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as engagement_plan,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then 
                                case 
                                    when (select engagement_plan_id from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select engagement_plan_id from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as engagement_plan_by_id,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then 
                                case 
                                    when (select plan_details from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select plan_details from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as engagement_plan_details,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then 
                                case 
                                    when (select future_engagement from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select future_engagement from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as future_engagement,
                case 
                    when hr.id in (select emp_id from central_bench_engagement_log where hr.id = emp_id)
                    then 
                        case 
                            when (select till_date from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)::timestamp::date >= now()::date
                            then 
                                case 
                                    when (select project_id from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    THEN (SELECT p.name FROM central_bench_engagement_log a join project_project p on a.project_id = p.id WHERE hr.id = a.emp_id  ORDER BY a.create_date DESC LIMIT 1)
                                    when (select other_text from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select other_text from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as future_projection
        from hr_employee as hr 
            join hr_department as hrd on hrd.id= hr.department_id
            where hr.active =true and hrd.code='BSS' and hr.sbu_master_id is NULL and 
            hr.emp_role in (select id from kwmaster_role_name  where code in ('DL','R','S')) and 
            hr.emp_category in(select id from kwmaster_category_name where code in ('TTL','DEV','PM','BA','IFS','SS','SMS')) and 
            hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
            and hr.id not in (select applicant_id from kw_resignation  where state not in ('reject','cancel') and applicant_id is not null)
            and hr.id not in (select employee_id from hr_leave where state in ('validate') and  date_to > current_date and holiday_status_id in (select id from hr_leave_type where leave_code in ('MT','SAB','SPL')))
    )""" % (self._table))

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False


class SBUTaggingWizard(models.TransientModel):
    _name = "sbu_tagging_wizard"
    _description = "SBU Wizard"

    @api.model
    def default_get(self, fields):
        res = super(SBUTaggingWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='sbu_resource_tagging',
        relation='sbu_tagging_employee_rel',
        column1='wizard_id',
        column2='sbu_tagging_id',
    )

    @api.model
    def _get_default_department(self):
        department_id = self.env['hr.department'].search([('code', 'in', ['bss', 'Bss', 'BSS'])], limit=1)
        return department_id.id


    sbu_tagging = fields.Selection([('tag', 'Tag'), ('untag', 'Un Tag')], string='SBU Tagging', default='tag')
    sbu_type = fields.Selection([('sbu', 'SBU'), ('horizontal', 'Horizontal')], string='Resource Type', default='sbu')
    department_id = fields.Many2one('hr.department', string="Department", domain="[('dept_type.code', '=', 'department')]",default=_get_default_department)
    division = fields.Many2one('hr.department', string="Division", domain="[('dept_type.code', '=', 'division')]")
    section = fields.Many2one('hr.department', string="Practice", domain="[('dept_type.code', '=', 'section')]")
    practise = fields.Many2one('hr.department', string="Section", domain="[('dept_type.code', '=', 'practice')]")
    sbu_master_id = fields.Many2one('kw_sbu_master', string='SBU')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Skill')
    cc_employee = fields.Many2many('hr.employee', 'cc_tagging_employee_relation', 'employee_id', string='CC Employees')
    send_mail = fields.Boolean(string="Send Email")
    emp_ids = fields.One2many('sbu_resource_manual_tagging','existing_employee_id',string='Employee Data')
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('reject','Rejected')],default='draft')

  

    @api.onchange('division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.department_id:
                rec.section = False
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.department_id:
                rec.practise = False
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}
    
    @api.onchange('sbu_type')
    def _sbu_type_onchange(self):
        self.sbu_master_id = False

    @api.onchange('sbu_tagging')
    def _sbu_tagging_onchange(self):
        if self.sbu_tagging == 'untag':
            self.sbu_type = False
        self.division = False
        self.section = False
        self.practise = False
        self.sbu_master_id = False
        self.primary_skill_id = False
        self.send_mail = False

    @api.onchange('send_mail')
    def _employee_data_onchange(self):
        for rec in self.employee_ids:
            # rec.resource = dict(rec._fields['resource'].selection).get(rec.resource)
            # qualification_data =self.env['hr.employee.mis.report'].sudo().search([('emp_id','=',rec.employee_id.id)])
            # for record in qualification_data:
            if self.send_mail ==True:
                self.emp_ids = [[0,0 ,{
                    'employee_id':rec.employee_id.id,
                    'designation':rec.designation.name,
                    'technology': rec.primary_skill_id.name,
                    'department': rec.employee_id.department_id.name,
                    'location':rec.job_branch_id.alias,
                    'type_of_employee': rec.employement_type.name,
                    'joining_date' : rec.date_of_joining.strftime("%d-%b-%Y"),
                    # 'resource': rec.employee_id.mrf_id.resource,
                    # 'replacement_of': rec.employee_id.mrf_id.employee_id.id if rec.employee_id.mrf_id.resource == 'replacement' and rec.employee_id.mrf_id.employee_id else '',
                    # 'experience': rec.employee_id.total_experience_display,
                    # 'qualification':record.edu_qualification,
                    'primary_skill_id':rec.primary_skill_id.id,
                    'state': self.state
                    }]]
            if self.send_mail == False:
                self.emp_ids = [[5 ,{
                    'employee_id':rec.employee_id.id,
                    'designation':rec.designation.name,
                    'technology': rec.primary_skill_id.name,
                    'department':rec.employee_id.department_id.name,
                    'location':rec.job_branch_id.alias,
                    'type_of_employee': rec.employement_type.name,
                    'joining_date' : rec.employee_id.date_of_joining.strftime("%d-%b-%Y"),
                    # 'resource': rec.employee_id.mrf_id.resource,
                    # 'replacement_of': rec.employee_id.mrf_id.employee_id.id if rec.employee_id.mrf_id.resource == 'replacement' and rec.employee_id.mrf_id.employee_id else '',
                    # 'experience':  rec.employee_id.total_experience_display,
                    # 'qualification':record.edu_qualification,
                    'primary_skill_id':rec.primary_skill_id.id,
                    'state': self.state
                    }]]

    def share_sbu_info_with_employee(self):
        cc_emp = self.cc_employee
        mail_to = self.sbu_master_id.representative_id.work_email
        # print("mail" ,mail_to)
        mail_cc = ','.join(self.env['hr.employee'].browse(cc_emp.ids).mapped('work_email'))
        c_date = date.today()
        current_date = (c_date.strftime("%d-%b-%Y"))
        token = _default_access_token(self)
        for rec in self.employee_ids:
            data = {
                'empl':self.env['sbu_resource_tagging'].sudo().browse(self._context.get('active_ids')).mapped('employee_id').ids,
                'sbu_id':self.sbu_master_id.id,
                'sbu':self.sbu_type,
                'status':self.sbu_tagging,
                'action_by':self.env.user.employee_ids.id,
                'employee_data' : self.id,
                'token':token,
                'context': {'current_id':self.id}

                }
            # if self.primary_skill_id:
            #     data['skill_id'] = self.primary_skill_id.id
            # else:
            #     data['skill_id'] = rec.primary_skill_id.id
        today = date.today()
        for rec in self.employee_ids:
            emp_data = {
                'employee_id': rec.employee_id.id,
                'status': self.sbu_tagging,
                'date': date.today(),
                'action_by': self.env.user.employee_ids.id,
                'sbu_type': self.sbu_type,
                # 'access_token': data['token'],
                # 'sbu_id':self.sbu_master_id.id
            }
            if self.sbu_tagging == 'tag':
                emp_data['sbu_status'] = f"{rec.name} Tagged To  {self.sbu_master_id.name}"
                emp_data['sbu_id'] = self.sbu_master_id.name
            if self.sbu_tagging == 'untag':
                emp_data['sbu_status'] = f"{rec.name} Untagged from {rec.sbu.name}"
                emp_data['sbu_id'] = rec.sbu_name

            self.env['sbu_tag_untag_log'].sudo().create(emp_data)
            engagement_history = self.env['central_bench_engagement_log'].sudo().search([('emp_id','=',rec.employee_id.id),('till_date','>=',today)])
            if engagement_history:
                query = f"update central_bench_engagement_log set till_date = '{today}' where emp_id = {rec.employee_id.id}"
                self._cr.execute(query)
                


        if self.send_mail == True:
            # template_id = self.env.ref('kw_resource_management.sbu_tag_employee_mail_template')
            extra_params= {'email_to':mail_to,
            'email_cc':mail_cc,'date':current_date,
            'sbu':self.sbu_master_id.name,
            'resource_type':self.sbu_type,
            'skill':self.primary_skill_id.name,
            }
            self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                            template_layout='kw_resource_management.sbu_tag_employee_mail_template',
                                                            ctx_params=extra_params,
                                                            description="SBU Tagging")
            self.env.user.notify_success("Mail Sent successfully.")

           
            #for sbu tagging mail history
            for rec in self.emp_ids:
                self.env['sbu_tag_untag_mail_log'].sudo().create({
                    'employee_id':rec.employee_id.id,
                    'designation':rec.designation,
                    'technology':rec.technology,
                    'department':rec.department,
                    'location':rec.location,
                    'type_of_employee':rec.type_of_employee,
                    'joining_date':rec.joining_date,
                    'resource': rec.resource,
                    # 'replacement_of':rec.replacement_of.name,
                    # 'experience':rec.experience,
                    # 'qualification':rec.qualification,
                    # 'planned_project':rec.planned_project.name,
                    'date':date.today(),

                }) 
            # for rec in self.emp_ids:
            #     self.env['sbu_approve_reject'].sudo().create({
            #         'emp_id':rec.employee_id.id,
            #         'designation':rec.designation,
            #         'technology':rec.technology,
            #         'department':rec.department,
            #         'location':rec.location,
            #         'type_of_employee':rec.type_of_employee,
            #         'joining_date':rec.joining_date,
            #         'resource': rec.resource,
            #         # 'replacement_of':rec.replacement_of.name,
            #         # 'experience':rec.experience,
            #         # 'qualification':rec.qualification,
            #         # 'planned_project':rec.planned_project.name,
            #         'date':date.today(),
            #         'state':rec.state,
            #         'sbu_master_id':self.sbu_master_id.id,
            #         'sbu_type':self.sbu_type,
            #         'sbu_tagging':self.sbu_tagging,
            #         'primary_skill_id':rec.primary_skill_id.id if not self.primary_skill_id.id else self.primary_skill_id.id,
            #     })

    
        
        query = ''
        for record in self.employee_ids:
            for rec in self:
                if rec.sbu_tagging == 'tag':
                    sbu_id = self.sbu_master_id.id
                    sbu_type = f"'{self.sbu_type}'"
                    # skill_id = self.primary_skill_id.id if self.primary_skill_id.id else record.primary_skill_id.id
                if rec.sbu_tagging == 'untag':
                    sbu_id = 'null'
                    sbu_type = 'null'
                    record.division = 'null'
                    record.section = 'null'
                    record.practise = 'null'
                    skill_id = record.primary_skill_id.id
                if rec.primary_skill_id:
                    query = f"update hr_employee set sbu_master_id = {sbu_id}, sbu_type= {sbu_type},primary_skill_id={self.primary_skill_id.id},division={self.division.id if self.division else 'null'},section={self.section.id if self.section else 'null'},practise={self.practise.id if self.practise else 'null'} where id = {record.employee_id.id}"
                else:
                    query = f"update hr_employee set sbu_master_id = {sbu_id}, sbu_type= {sbu_type} ,division={self.division.id if self.division else 'null'},section={self.section.id if self.section else 'null'},practise={self.practise.id if self.practise else 'null'} where id = {record.employee_id.id}"
            if len(query) > 0:
                self._cr.execute(query)
            record_log = self.env['kw_emp_sync_log'].sudo().search([('model_id', '=', 'hr.employee'),('rec_id','=',record.employee_id.id),('code','=',1),('status','=',0)])
            if not record_log.exists():
                record_log.create( {'model_id': 'hr.employee', 'rec_id': record.employee_id.id, 'code': 1, 'status': 0})
            else:
                pass

            


class ResourceManualTaggingMail(models.TransientModel):
    _name = 'sbu_resource_manual_tagging'
    _description = 'SBU Resource Manual Tagging'

    existing_employee_id = fields.Many2one('sbu_tagging_wizard',readonly=True)
    employee_id = fields.Many2one('hr.employee',string = "Employee")
    emp_name = fields.Char(related='employee_id.name')
    # name = fields.Char(string = "Name" )
    designation = fields.Char(string = 'Designation')
    technology = fields.Char(string='Technology')
    department = fields.Char(string='Department')
    location = fields.Char(string = "Location")
    type_of_employee =fields.Char(string = "Type Of Employee")
    resource = fields.Selection(string='Replacement/New', track_visibility='onchange',
                                selection=[('new', 'New'), ('replacement', 'Replacement')])
    
    # replacement_of = fields.Many2one('hr.employee',string = "Replacement Of" )
    # experience = fields.Char(string = "Experience")
    # qualification = fields.Char(string = "Qualification")
    # planned_project = fields.Many2one('project.project',string = "Planned Project")
    joining_date = fields.Char(string = "Date Of Joining")
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('reject','Rejected')],default='draft')
    primary_skill_id =fields.Many2one('kw_skill_master',string='Skill')
    sbu_master_id  = fields.Many2one('kw_sbu_master',string='SBU')
    sbu_boolean = fields.Boolean()

