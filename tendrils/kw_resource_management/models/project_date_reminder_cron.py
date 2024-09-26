# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from dateutil import relativedelta
from datetime import date,datetime,timedelta


class ProjectReminderCron(models.Model):
    _name = 'project_date_reminder_cron'
    _description = 'Project Dates Reminder'
    _auto = False
    _order = "employee_id"


    employee_id = fields.Many2one('hr.employee',string='Employee')
    code = fields.Char(related='employee_id.emp_code',string='Code')
    name = fields.Char(related='employee_id.name',string='Name')
    emp_grade = fields.Many2one('kwemp_grade_master',string='Grade')
    emp_band =fields.Many2one('kwemp_band_master',string='Band')
    designation = fields.Many2one('hr.job',string='Designation')
    date_of_joining = fields.Date(string='Joining Date')
    emp_role = fields.Many2one('kwmaster_role_name',string='Role')
    emp_category = fields.Many2one('kwmaster_category_name',string='Category')
    employement_type = fields.Many2one('kwemp_employment_type',string='Type')
    job_branch_id = fields.Many2one('kw_res_branch',string='Location')
    # applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name= fields.Char(related='sbu_id.name', string='SBU')
    # project_name=fields.Text(string='Project')
    start_date=fields.Date(string='Start Date')
    end_date=fields.Date(string='End Date')
    resource_id = fields.One2many('project.project', 'emp_id')
    total_experience_display = fields.Char(compute='_compute_eos')
    practise = fields.Char(related='employee_id.practise.name',string='Practice')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Skill')
    order_opportunity = fields.Char(string='WO/OPP')
    project_name = fields.Char(string='Project Name')

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.employee_id.date_of_joining:
                difference = relativedelta.relativedelta(datetime.today(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months

            if rec.employee_id.work_experience_ids:
                for exp_data in rec.employee_id.work_experience_ids:
                    exp_difference = relativedelta.relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months
                    # print ("Difference is %s year, %s months " %(total_years,total_months))
            # print ("Difference is %s year, %s months " %(total_years,total_months))

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:     
                rec.total_experience_display = " %s.%s " % (total_years, total_months)
            else:
                rec.total_experience_display = ''

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
           WITH project AS (
                SELECT prj.name AS project_id,
                    prj.code AS project_code,
                    prj.sbu_id AS sbu_id,
                    rt.start_date AS date_start,
                    rt.end_date AS date_end,
                    rt.emp_id AS employee_id,
                    prj.crm_id,
                    crml.code As order_opportunity,
                    prj.name As project_name    
                FROM hr_employee emp
                LEFT JOIN project_project prj ON prj.emp_id = emp.id
                LEFT JOIN kw_project_resource_tagging rt ON rt.project_id = prj.id
                LEFT JOIN crm_lead crml ON crml.id = prj.crm_id                       
                WHERE prj.active = TRUE AND rt.active = TRUE
            )
            SELECT row_number() over() AS id,
                hr.id AS employee_id,
                hr.job_id AS designation,
                hr.name AS name,
                hr.date_of_joining AS date_of_joining,
                hr.emp_role AS emp_role,
				hr.grade as emp_grade,
				hr.emp_band as emp_band,
                hr.emp_category AS emp_category,
                hr.employement_type AS employement_type,
                hr.job_branch_id AS job_branch_id,
                hr.sbu_master_id AS sbu_id,
                hr.sbu_type AS sbu_type,
                pj.order_opportunity as order_opportunity,
                pj.project_name as project_name,
               
                replace(regexp_replace(
                    string_agg(concat(pj.date_start), 
                                E'\n'), 
                    E',\n+', 
                    E',\n'
                ), 
                E'\n$', 
                ''
                ) AS start_date,
                replace(regexp_replace(
                    string_agg(concat(pj.date_end), 
                                E'\n'), 
                    E',\n+', 
                    E',\n'
                ), 
                E'\n$', 
                ''
                ) AS end_date,
            (select primary_skill_id from resource_skill_data where employee_id=hr.id) AS primary_skill_id
            FROM hr_employee AS hr 
            LEFT JOIN project pj ON pj.employee_id = hr.id 
            JOIN hr_department AS hrd ON hrd.id = hr.department_id
            WHERE hr.active = TRUE 
                AND hrd.code = 'BSS' 
                AND hr.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code = 'O') 
                AND hr.sbu_type = 'sbu' 
                AND hr.sbu_master_id IS NOT NULL 
            GROUP BY hr.id,pj.project_id,pj.order_opportunity,pj.project_name
         )""" % (self._table))
        

    # regarding 20 days prior notification
    def end_date_prior_notification(self):
        reminder_date = str(date.today() + timedelta(days=20))
        projects = self.env['project_date_reminder_cron'].sudo().search([('end_date','=',reminder_date)])
        sbu = {rec.sbu_id.id for rec in projects if rec.sbu_id}
        for rec in sbu:
            sbu_master = self.env['kw_sbu_master'].browse(rec)
            name = sbu_master.representative_id.name
            email_to = sbu_master.representative_id.work_email
            req_project = self.env['project_date_reminder_cron'].sudo().search([('end_date','=',reminder_date),('sbu_name','=',sbu_master.name)])
            proj_end_date = (date.today() + timedelta(days=20)).strftime("%d-%b-%Y")
            all_user = self.env['res.users'].sudo().search([])
            manager = all_user.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
            email_cc = ','.join(manager.mapped('email'))
            template_obj = self.env.ref("kw_resource_management.end_date_reminder_mail_template")
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                name=name, email_to=email_to, email_cc=email_cc, req_project=req_project, proj_end_date=proj_end_date).send_mail(rec,
                                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light')

    #  regarding project end date expired notification
    def project_expired_cron_notification(self):
        today = str(date.today())
        projects = self.env['project_date_reminder_cron'].sudo().search([('end_date','!=',''),('end_date','<=',today)])
        sbu = {rec.sbu_id.id for rec in projects if rec.sbu_id}
        for rec in sbu:
            sbu_master = self.env['kw_sbu_master'].browse(rec)
            name = sbu_master.representative_id.name
            email_to = sbu_master.representative_id.work_email
            req_project = self.env['project_date_reminder_cron'].sudo().search([('end_date','!=',''),('end_date','<=',today),('sbu_name','=',sbu_master.name)])
            template_obj = self.env.ref("kw_resource_management.expired_date_reminder_mail_template")
            all_user = self.env['res.users'].sudo().search([])
            manager = all_user.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
            email_cc = ','.join(manager.mapped('email'))
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                name=name, email_to=email_to, email_cc=email_cc, req_project=req_project).send_mail(rec,
                                                                                 notif_layout='kwantify_theme.csm_mail_notification_light')

    # regarding no start-date or no end-date
    def project_no_start_or_end_date(self):
        projects = self.env['project_date_reminder_cron'].sudo().search(['|',('start_date','=',''),('end_date','=','')])
        sbu = {rec.sbu_id.id for rec in projects if rec.sbu_id}
        for rec in sbu:
            sbu_master = self.env['kw_sbu_master'].browse(rec)
            name = sbu_master.representative_id.name
            email_to = sbu_master.representative_id.work_email
            req_project = self.env['project_date_reminder_cron'].sudo().search(['|',('start_date','=',''),('end_date','=',''),('sbu_name','=',sbu_master.name)])
            template_obj = self.env.ref("kw_resource_management.start_end_date_reminder_template")
            all_user = self.env['res.users'].sudo().search([])
            manager = all_user.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
            email_cc = ','.join(manager.mapped('email'))
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                name=name, email_to=email_to, email_cc=email_cc, req_project=req_project).send_mail(rec,
                                                                                 notif_layout='kwantify_theme.csm_mail_notification_light')
