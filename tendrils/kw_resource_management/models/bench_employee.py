# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from datetime import date,datetime
from dateutil import relativedelta
import html
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import ValidationError


class SBUBenchResource(models.Model):
    _name = 'sbu_bench_resource'
    _description = 'SBU Bench Resource'
    _auto = False
    _order = "release_date desc"

    @api.depends('grade','band')
    def _compute_grade_band(self):
        for rec in self:
            if rec.band and rec.grade:
                rec.grade_band =rec.grade.name +','+' '+ rec.band.name

    employee_id = fields.Many2one('hr.employee',string='Employee')
    code = fields.Char(related='employee_id.emp_code',string='Employee Code')
    name = fields.Char(related='employee_id.name',string='Employee Name')
    designation = fields.Many2one('hr.job',string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name',string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name',string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type',string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch',string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    sbu = fields.Many2one("kw_sbu_master","SBU")
    release_date = fields.Date(string = "Effective Date")
    interval_day=fields.Integer("Days in Bench")
    remark = fields.Char('Remarks')
    # eos_status = fields.Integer()
    grade= fields.Many2one('kwemp_grade_master',string="Employee Grade")
    band= fields.Many2one('kwemp_band_master',string="Employee Band")
    grade_band=fields.Char("Grade/Band",compute='_compute_grade_band')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Skill')
    sbu_name = fields.Char(related='sbu.name', string="SBU")
    engagement_plan = fields.Char()
    engagement_plan_by_id = fields.Many2one('kw_engagement_master')
    till_date = fields.Date()
    # future_engagement = fields.selection(string='Future Engagement',
    # selection=[('project', 'Projct'), ('other', 'Other')],default='project'
    # project_id = fields.Many2one('project.project')
    # other_text  = fields.Text(string = "Other")
    # total_emp_exp = fields.Char(compute='_compute_emp_exp')
    future_projection =  fields.Char(string="Future Projection")

    experience = fields.Char(compute='_compute_total_exp')
    engagement_plan_details = fields.Text("Engagement Plan Details")
    discipline_adherence_ratings = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string="Discipline and Process adherence" )
    enhanced_roles = fields.Selection([('yes', 'Yes'),('no', 'No')],string="Recommend For Other Project")
    project_id = fields.Many2one('project.project',"Project")

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

            if total_years > 0 or total_months > 0:  
                rec.experience = " %s.%s " % (total_years, total_months)
            else:
                rec.experience = ''

    # @api.depends('remark')
    # def _compute_short_text(self):
    #     for record in self:
    #         record.short_text = 'aaa'   

    @api.multi
    def action_timesheet_details(self):
        tree_view_id = self.env.ref('kw_timesheets.account_analytic_line_view_rcm_tree').id
        return {
            'name': 'Timesheet Report',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_id': tree_view_id,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'self',
            'domain': [('employee_id', '=', self.employee_id.id),('date','>=',self.release_date)],
            'context':{'search_default_filter_this_month':1,'search_default_filter_this_week':1,'search_default_filter_today':1},
        }

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
     SELECT row_number() over() as id,
        hr.id as employee_id,
        hr.job_id as designation,
        hr.grade as grade,
        hr.emp_band as band,
        hr.name as name,
        hr.date_of_joining as date_of_joining,
        hr.emp_role as emp_role,
        hr.emp_category as emp_category,
        hr.employement_type as employement_type,
        hr.job_branch_id as job_branch_id,
--      hr.sbu_master_id as sbu,
        hr.sbu_type as sbu_type,
        (select primary_skill_id from resource_skill_data where employee_id=hr.id ) as primary_skill_id,
        (select project_id from kw_project_resource_tagging rt where rt.emp_id = hr.id order by write_date desc limit 1) as project_id,
        (select rl.release_from from kw_resource_release_log rl where rl.release_emp_id = hr.id order by create_date desc limit 1) as sbu,
		case when hr.id in (select release_emp_id from kw_resource_release_log  where hr.id = release_emp_id) 
            	then  (select create_date from kw_resource_release_log  where hr.id = release_emp_id order by create_date desc limit 1)::TIMESTAMP::DATE
				
			when  (select max(tlog.date) from sbu_tag_untag_log tlog 
				where tlog.status='untag' and hr.id = tlog.employee_id) > hr.date_of_joining
				then (select max(tlog.date) from sbu_tag_untag_log tlog 
		  		where  tlog.status='untag' and hr.id = tlog.employee_id )::TIMESTAMP::DATE
			when  hr.training_completion_date > hr.date_of_joining
				then  hr.training_completion_date
            else  hr.date_of_joining 
            end as release_date,
		case when hr.id in (select release_emp_id from kw_resource_release_log  where hr.id = release_emp_id) 
            	then (select date_part('day'::text, current_date - (select create_date from kw_resource_release_log  where hr.id = release_emp_id order by create_date desc limit 1)))
				
			when  (select max(tlog.date) from sbu_tag_untag_log tlog 
				where tlog.status='untag' and hr.id = tlog.employee_id) > hr.date_of_joining
				then (select current_date) - (select max(tlog.date) from sbu_tag_untag_log tlog 
		  		where  tlog.status='untag' and hr.id = tlog.employee_id )
            when  hr.training_completion_date > hr.date_of_joining
				then (select current_date)- hr.training_completion_date
            else (select current_date) - hr.date_of_joining 
            end as interval_day,
		    case when length((select reason from kw_resource_release_log where hr.id = release_emp_id order by create_date desc limit 1)) >= 200 then
                        concat('Release From : ',
                            (select name from kw_sbu_master where id= (select release_from from kw_resource_release_log log where log.release_emp_id = hr.id order
                                by create_date desc limit 1)),' , ','Reason : ',(select release_reason
                        from kw_resource_release_log where hr.id = release_emp_id order by create_date desc limit 1), ' ,',' ',' ',' ','Remark:',' ',(select reason
                        from kw_resource_release_log where hr.id = release_emp_id order by create_date desc limit 1))
             		when length((select reason from kw_resource_release_log where hr.id = release_emp_id order by create_date desc limit 1)) < 200 then 
                        (select concat(reason) from kw_resource_release_log where hr.id = release_emp_id order by create_date desc limit 1)
                when (select max(tlog.date) from sbu_tag_untag_log tlog 
                    where tlog.status='untag' and hr.id = tlog.employee_id) > hr.date_of_joining
                        then   'Untag from SBU' || ' ' ||
                    '(' || (select sbum.name from kw_sbu_master sbum where sbum.name= (select sbu_id from sbu_tag_untag_log as slog where slog.status='untag' and 
                    hr.id = slog.employee_id order
                    by slog.date desc limit 1)) || ')'
                else 'First Joined in Central Bench '
                        end as remark,
				
						
-- 				case
-- 				when hr.id in (select applicant_id from kw_resignation where state not in ('reject','cancel')) then 1
-- 				else 0
-- 				end as eos_status,
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
                                    when (select project_id from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    THEN (SELECT p.name FROM central_bench_engagement_log a join project_project p on a.project_id = p.id WHERE hr.id = a.emp_id  ORDER BY a.create_date DESC LIMIT 1)
                                    when (select other_text from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1) is not null
                                    then (select other_text from central_bench_engagement_log where hr.id = emp_id ORDER BY create_date desc limit 1)
                                    else null
                                end
                            else null
                        end
                    else null
                end as future_projection,
				(select discipline_adherence_ratings from kw_resource_release_log where hr.id = release_emp_id ORDER BY create_date desc limit 1) AS discipline_adherence_ratings,
				(select enhanced_roles from kw_resource_release_log where hr.id = release_emp_id ORDER BY create_date desc limit 1) AS enhanced_roles
                from hr_employee as hr 
				 
                    join kwmaster_category_name as category
                    on hr.emp_category = category.id
                    join hr_department as hrd on hrd.id= hr.department_id
                    where hr.active =true and hrd.code='BSS' and 
                    hr.emp_role in (select id from kwmaster_role_name  where code in ('DL','R','S')) and 
                    hr.emp_category in(select id from kwmaster_category_name where code in ('TTL','DEV','PM','BA','IFS','SS','SMS'))
                    and hr.sbu_master_id is null and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
					and hr.id not in (select applicant_id from kw_resignation  where state not in ('reject','cancel') and applicant_id is not null)
					and hr.id not in (select employee_id from hr_leave where state in ('validate') and  date_to > current_date and holiday_status_id in (select id from hr_leave_type where leave_code in ('MT','SAB','SPL')))
         )""" % (self._table))
        
    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search([('state','not in',['reject','cancel']),('applicant_id','=',rec.employee_id.id)],limit=1)
            rec.applied_eos = True if resignation else False


class CentralBenchWizardReport(models.TransientModel):
    _name = "central_bench_wizard_report"
    _description = "Bench List Publish"


    @api.model
    def default_get(self, fields):
        res = super(CentralBenchWizardReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='sbu_bench_resource',
        relation='sbu_bench_resource_employee_relation',
        column1='central_bench_wizard_id',
        column2='central_bench_id',
    )
    send_mail = fields.Boolean(string="Send Email")
    cc_employee = fields.Many2many('hr.employee', 'cc_tagging_employee_relation_1', 'employee_id', string='CC Employees')


    def send_mail_to_l_and_K_dept(self):
       
        if self.send_mail == True:
            admin = self.env['res.users'].sudo().search([])
            cc_emp = self.cc_employee
            mail_cc = ','.join(self.env['hr.employee'].browse(cc_emp.ids).mapped('work_email'))
            c_date = date.today()
            current_date = (c_date.strftime("%d-%b-%Y"))
            l_and_k_group = admin.filtered(lambda user: user.has_group('kw_resource_management.group_l_and_K_dept') == True)
            mail_to = ','.join(l_and_k_group.mapped('email'))
            # print(l_and_k_group,mail_to,"------------------------l and k")
            
            # template_id = self.env.ref('kw_resource_management.central_bench_engagement_mail_template')
            # print(template_id,"template id--------------->---------------------")
            # if template_id:
            #     mail = self.env['mail.template'].browse(template_id.id).with_context(
            #     email_to=mail_to,cc_emp = mail_cc,date=current_date,).send_mail(self.id,notif_layout='kwantify_theme.csm_mail_notification_light')
                    
            extra_params= {'email_to':mail_to,
            'cc_emp':mail_cc,'date':current_date
            }
            self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                            template_layout='kw_resource_management.central_bench_engagement_mail_template',
                                                            ctx_params=extra_params,
                                                            description="Talent Pool Report")
            self.env.user.notify_success("Mail Sent successfully.")





class CentralBenchSBUWizardReport(models.TransientModel):
    _name = "central_bench_sbu_wizard"
    _description = "Bench List Publish"


    @api.model
    def default_get(self, fields):
        res = super(CentralBenchSBUWizardReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='sbu_bench_resource',
        relation='sbu_bench_resource_empl_rel',
        column1='central_bench_sbu_wizard_id',
        column2='central_bench_id',
    )
    send_mail = fields.Boolean(string="Send Email",required="True")
    cc_employee = fields.Many2many('hr.employee', 'cc_tagging_employee_relation_2', 'employee_id', string='CC Employees')



    def send_mail_to_rcm(self):
        # Check if any employee has a designation without a primary skill
        if self.send_mail == True:
            for rec in self.employee_ids:
                # print(rec, "skill-----------------------------")
                if not rec.primary_skill_id:
                    raise ValidationError("Please set a skill for employees with a designation.")
            cc_emp = self.cc_employee
            mail_cc = ','.join(self.env['hr.employee'].browse(cc_emp.ids).mapped('work_email'))
            filtered_records = self.env['kw_sbu_master'].search([]).filtered(lambda rec: rec.type == 'sbu')
            # print(filtered_records,"filtered_records--------------->>>>>>>>>>>>>>>>>>")
            data = []
            for rec in filtered_records:
                # print(rec.representative_id.work_email,"*************************************************")
                mail_to = rec.representative_id.work_email
                if mail_to:
                    data.append(mail_to)
                else:
                    pass
            
            mail_to = ','.join(list(set(data)))
            
            # New Code for mail send
            skill_set = self.employee_ids.mapped('primary_skill_id')
            skill_rec = skill_set.mapped('name')
            desgn_rec = self.employee_ids.mapped('designation')
            emp_list = []
            
            for desg in desgn_rec:
                experience = self.employee_ids.filtered(lambda x: x.designation.id == desg.id).mapped('experience')
                experience.sort()
                exp_value = experience[0] if experience[0] == experience[-1] else f'{experience[0]}-{experience[-1]}'
                format_string = f'{desg.name}:{exp_value}:{len(experience)}:'
                
                for rec in skill_set:
                    filtered_skill_employees = self.employee_ids.filtered(
                        lambda x: x.primary_skill_id.id == rec.id and x.designation.id == desg.id)
                    format_string += f'{len(filtered_skill_employees)}:'
                
                emp_list.append(format_string)
            
            
            
            extra_sbu_params = {'email_to': mail_to, 'cc_emp': mail_cc, 'skill_list': skill_rec, 'emp_list': emp_list}
            
            self.env['hr.contract'].contact_send_custom_mail(
                res_id=self.id,
                notif_layout='kwantify_theme.csm_mail_notification_light',
                template_layout='kw_resource_management.central_bench_engagement_mail_to_sbu',
                ctx_params=extra_sbu_params,
                description="Bench List Report"
            )
            
            self.env.user.notify_success("Mail Sent successfully.")
