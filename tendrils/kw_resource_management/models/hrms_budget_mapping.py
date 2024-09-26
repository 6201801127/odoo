# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class HRMSBudgetMapping(models.Model):
    _name = 'hrms_budget_mapping'
    _description = 'Resource MIS'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    # code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    role_kw_id = fields.Integer(related='emp_role.kw_id')
    
    #New Field Added on 19th April By Chandrasekhar, CR By Shivangi
    @api.depends('emp_grade','emp_band')
    def _concat_grade_band(self):
        for rec in self:
            if rec.emp_grade:
                rec.emp_grade_band = f"{rec.emp_grade.name}{'/' if rec.emp_band else ''}{rec.emp_band.name if rec.emp_band  else ''}"
                
                
    emp_code = fields.Char(string="Employee Code")
    department_id = fields.Many2one('hr.department', string="Department")
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],string="Budget Type")
    division = fields.Many2one('hr.department',"Division")
    engagement_unit = fields.Char(string="Engagement Unit")
    project_name = fields.Text(string="Project")
    tagging_start_date = fields.Text(string="Tagging Start Date")
    tagging_end_date = fields.Text(string="Tagging End Date")
    joining_type = fields.Selection([('Lateral', 'Lateral'), ('Intern', 'Intern')],string='Joined as')
    emp_grade = fields.Many2one('kwemp_grade_master', string="Grade", )
    emp_band = fields.Many2one('kwemp_band_master', string="Band", )
    emp_grade_band = fields.Char(compute="_concat_grade_band",string="Grade/band")
    edu_qualification = fields.Char(string="Education Qualification")
    parent_id = fields.Many2one('hr.employee', string="RA")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],string="Gender")
    
    primary_skill_id = fields.Many2one('kw_skill_master', string="Primary Skill")
    previous_company_experience_display_abbr = fields.Char(string="Previous Company Experience")
    csm_experience_display = fields.Char(string="CSM Experience")
    total_experience_display = fields.Char(string="Total Experience")
    certification = fields.Char(string="Certification")
    project_manager = fields.Char(string="Project Manager")
    workorder_code = fields.Char(string="WorkOrder Code")
    

    # @api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
    #     SELECT  row_number() over() AS id,id as employee_id,job_id AS designation,date_of_joining AS date_of_joining,emp_role AS emp_role,
    #     emp_category AS emp_category,employement_type as employement_type,job_branch_id as job_branch_id
    #     FROM hr_employee 
    #     where active = true and employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') and enable_payroll = 'yes')""" % (
    #         self._table))

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            WITH ed as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
                FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
                WHERE st.id=ed.stream_id AND ed.course_type != '3'
                GROUP BY ed.emp_id),

            ct as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
                FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
                WHERE st.id=ed.stream_id AND ed.course_type = '3'
                GROUP BY ed.emp_id),
            experience AS (
                SELECT
                    hr.id AS emp_id,
                    SUM(date_part('year', AGE(x.effective_to, x.effective_from)) * 12 + date_part('month', AGE(x.effective_to, x.effective_from)))::numeric AS previous_company_exp,
                    (date_part('year', AGE(CURRENT_DATE, hr.date_of_joining)) * 12 + date_part('month', AGE(CURRENT_DATE, hr.date_of_joining)))::numeric AS csm_exp
                FROM 
                    hr_employee hr
                LEFT JOIN 
                    kwemp_work_experience x ON x.emp_id = hr.id
                WHERE 
                    hr.active = TRUE
                GROUP BY 
                    hr.id, hr.date_of_joining
            ),
            project AS (
                        SELECT prj.name AS project_id,
                        prj.code AS project_code,
                        prj.sbu_id AS sbu_id,
                        rt.start_date AS date_start,
                        rt.end_date AS date_end,
                        rt.emp_id AS employee_id,
                        (select name from hr_employee hr where prj.emp_id = hr.id) AS project_manager,
                        cl.code AS workorder_code,
                        prj.crm_id

                    FROM hr_employee emp
                    
                    LEFT JOIN project_project prj ON prj.emp_id = emp.id
                    LEFT JOIN kw_project_resource_tagging rt ON rt.project_id = prj.id
                    LEFT   JOIN crm_lead cl on  prj.crm_id = cl.id
                    WHERE prj.active = TRUE AND rt.active = TRUE
                )
                SELECT row_number() over(order by hr.name) AS id,
                    hr.emp_code AS emp_code,
                    hr.id AS employee_id,
                    hr.name AS name,
                    hr.job_id AS designation,
                    hr.date_of_joining AS date_of_joining,
                    hr.department_id AS department_id,
                    hr.emp_role AS emp_role,
                    hr.emp_category AS emp_category,
                    hr.employement_type as employement_type,
                    hr.budget_type AS budget_type,
                    hr.job_branch_id AS job_branch_id,
                    hr.division AS division,
                    CASE 
                        WHEN EXISTS (SELECT 1 FROM sbu_bench_resource WHERE employee_id = hr.id) THEN 'Talent Pool'
                        WHEN EXISTS (SELECT 1 FROM unit_bench_resource WHERE employee_id = hr.id) THEN 'Unit Pool'
                        WHEN hr.sbu_master_id is null THEN (SELECT name FROM hr_department WHERE id = hr.division)
                        ELSE (SELECT name FROM kw_sbu_master WHERE id = hr.sbu_master_id)
                    END AS engagement_unit,
                    replace(regexp_replace(
                        string_agg(concat(pj.workorder_code), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS workorder_code,
                    replace(regexp_replace(
                        string_agg(concat(pj.project_manager), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS project_manager,
                    replace(regexp_replace(
                    string_agg(concat(pj.project_id, ' (', pj.project_code, ')', 
                                        (SELECT name FROM kw_sbu_master WHERE id = pj.sbu_id)), 
                                E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E',\n$', 
                    ''
                    ) AS project_name,
                    replace(regexp_replace(
                        string_agg(concat(pj.date_start), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS tagging_start_date,
                    replace(regexp_replace(
                        string_agg(concat(pj.date_end), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS tagging_end_date,
                hr.joining_type AS joining_type,
                hr.grade AS emp_grade,
                hr.emp_band AS emp_band,
                                hr.parent_id AS parent_id,
                                hr.gender AS gender,
                string_agg(DISTINCT ed.education::text,', ') AS edu_qualification,
                string_agg(DISTINCT ct.education::text,', ') AS certification,
            --  previous_company_experience_display_abbr
                CASE 
                    WHEN exp.previous_company_exp IS NOT NULL THEN
                        concat(
                            div(exp.previous_company_exp, 12)::varchar, 
                            '.', 
                            CAST(mod(exp.previous_company_exp, 12)::varchar AS varchar)
                        ) 
                    ELSE '0' 
                END AS previous_company_experience_display_abbr,
                -- csm_experience_display
                CASE 
                    WHEN exp.csm_exp IS NOT NULL THEN
                        concat(
                            div(exp.csm_exp, 12)::varchar, 
                            '.', 
                            CAST(mod(exp.csm_exp, 12)::varchar AS varchar)
                        ) 
                    ELSE 
                        '0' 
                END AS csm_experience_display,
                -- total_experience_display
                concat(
                    div((COALESCE(exp.csm_exp, 0) + COALESCE(exp.previous_company_exp, 0)), 12)::varchar, 
                    '.', 
                    CAST(mod((COALESCE(exp.csm_exp, 0) + COALESCE(exp.previous_company_exp, 0)), 12)::varchar AS varchar)
                ) AS total_experience_display,
            (select primary_skill_id from resource_skill_data where employee_id=hr.id) AS primary_skill_id
            FROM hr_employee AS hr 
            LEFT JOIN project pj ON pj.employee_id = hr.id 
            LEFT JOIN ed on ed.emp_id=hr.id
            LEFT JOIN ct on ct.emp_id=hr.id
            LEFT JOIN experience exp ON exp.emp_id = hr.id
            WHERE hr.active = TRUE 
                AND hr.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code = 'O') 
            GROUP BY hr.id, exp.previous_company_exp, exp.csm_exp)""" % (
            self._table))        

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False
            
            
# Outsource MIS Report
# Added on 19th April 
# By Chandrasekhar
# CR By Shivangi Mishra,Souravi Bose


class OutsourceHRMSBudgetMapping(models.Model):
    _name = 'outsource_hrms_budget_mapping'
    _description = 'Vendor Resource MIS'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    role_kw_id = fields.Integer(related='emp_role.kw_id')
    
    @api.depends('emp_grade','emp_band')
    def _concat_grade_band(self):
        for rec in self:
            if rec.emp_grade:
                rec.emp_grade_band = f"{rec.emp_grade.name}{'/' if rec.emp_band else ''}{rec.emp_band.name if rec.emp_band  else ''}"
                
                
    emp_code = fields.Char(string="Employee Code")
    department_id = fields.Many2one('hr.department', string="Department")
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],string="Budget Type")
    division = fields.Many2one('hr.department',"Division")
    engagement_unit = fields.Char(string="Engagement Unit")
    project_name = fields.Text(string="Project")
    tagging_start_date = fields.Text(string="Tagging Start Date")
    tagging_end_date = fields.Text(string="Tagging End Date")
    joining_type = fields.Selection([('Lateral', 'Lateral'), ('Intern', 'Intern')],string='Joined as')
    emp_grade = fields.Many2one('kwemp_grade_master', string="Grade", )
    emp_band = fields.Many2one('kwemp_band_master', string="Band", )
    emp_grade_band = fields.Char(compute="_concat_grade_band",string="Grade/band")
    edu_qualification = fields.Char(string="Education Qualification")
    parent_id = fields.Many2one('hr.employee', string="RA")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],string="Gender")
    
    primary_skill_id = fields.Many2one('kw_skill_master', string="Primary Skill")
    previous_company_experience_display_abbr = fields.Char(string="Previous Company Experience")
    csm_experience_display = fields.Char(string="CSM Experience")
    total_experience_display = fields.Char(string="Total Experience")
    certification = fields.Char(string="Certification")
    project_manager = fields.Char(string="Project Manager")
    workorder_code = fields.Char(string="WorkOrder Code")



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            WITH ed as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
                FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
                WHERE st.id=ed.stream_id AND ed.course_type != '3'
                GROUP BY ed.emp_id),

            ct as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
                FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
                WHERE st.id=ed.stream_id AND ed.course_type = '3'
                GROUP BY ed.emp_id),
            experience AS (
                SELECT
                    hr.id AS emp_id,
                    SUM(date_part('year', AGE(x.effective_to, x.effective_from)) * 12 + date_part('month', AGE(x.effective_to, x.effective_from)))::numeric AS previous_company_exp,
                    (date_part('year', AGE(CURRENT_DATE, hr.date_of_joining)) * 12 + date_part('month', AGE(CURRENT_DATE, hr.date_of_joining)))::numeric AS csm_exp
                FROM 
                    hr_employee hr
                LEFT JOIN 
                    kwemp_work_experience x ON x.emp_id = hr.id
                WHERE 
                    hr.active = TRUE
                GROUP BY 
                    hr.id, hr.date_of_joining
            ),
            project AS (
                        SELECT prj.name AS project_id,
                        prj.code AS project_code,
                        prj.sbu_id AS sbu_id,
                        rt.start_date AS date_start,
                        rt.end_date AS date_end,
                        rt.emp_id AS employee_id,
                        (select name from hr_employee hr where prj.emp_id = hr.id) AS project_manager,
                        cl.code AS workorder_code,
                        prj.crm_id

                    FROM hr_employee emp
                    JOIN kw_project_resource_tagging rt ON rt.emp_id = emp.id
                    JOIN project_project prj ON rt.project_id = prj.id
                    JOIN crm_lead cl on  prj.crm_id = cl.id
                    WHERE prj.active = TRUE AND rt.active = TRUE
                )
                SELECT row_number() over(order by hr.name) AS id,
                    hr.emp_code AS emp_code,
                    hr.id AS employee_id,
                    hr.name AS name,
                    hr.job_id AS designation,
                    hr.date_of_joining AS date_of_joining,
                    hr.department_id AS department_id,
                    hr.emp_role AS emp_role,
                    hr.emp_category AS emp_category,
                    hr.employement_type as employement_type,
                    hr.budget_type AS budget_type,
                    hr.job_branch_id AS job_branch_id,
                    hr.division AS division,
                    CASE 
                        WHEN EXISTS (SELECT 1 FROM sbu_bench_resource WHERE employee_id = hr.id) THEN 'Talent Pool'
                        WHEN EXISTS (SELECT 1 FROM unit_bench_resource WHERE employee_id = hr.id) THEN 'Unit Pool'
                        WHEN hr.sbu_master_id is null THEN (SELECT name FROM hr_department WHERE id = hr.division)
                        ELSE (SELECT name FROM kw_sbu_master WHERE id = hr.sbu_master_id)
                    END AS engagement_unit,
                    replace(regexp_replace(
                        string_agg(concat(pj.workorder_code), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS workorder_code,
                    replace(regexp_replace(
                        string_agg(concat(pj.project_manager), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS project_manager,
                    replace(regexp_replace(
                    string_agg(concat(pj.project_id, ' (', pj.project_code, ')', 
                                        (SELECT name FROM kw_sbu_master WHERE id = pj.sbu_id)), 
                                E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E',\n$', 
                    ''
                    ) AS project_name,
                    replace(regexp_replace(
                        string_agg(concat(pj.date_start), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS tagging_start_date,
                    replace(regexp_replace(
                        string_agg(concat(pj.date_end), 
                                    E'\n'), 
                        E',\n+', 
                        E',\n'
                    ), 
                    E'\n$', 
                    ''
                    ) AS tagging_end_date,
                hr.joining_type AS joining_type,
                hr.grade AS emp_grade,
                hr.emp_band AS emp_band,
                                hr.parent_id AS parent_id,
                                hr.gender AS gender,
                string_agg(DISTINCT ed.education::text,', ') AS edu_qualification,
                string_agg(DISTINCT ct.education::text,', ') AS certification,
            --  previous_company_experience_display_abbr
                CASE 
                    WHEN exp.previous_company_exp IS NOT NULL THEN
                        concat(
                            div(exp.previous_company_exp, 12)::varchar, 
                            '.', 
                            CAST(mod(exp.previous_company_exp, 12)::varchar AS varchar)
                        ) 
                    ELSE '0' 
                END AS previous_company_experience_display_abbr,
                -- csm_experience_display
                CASE 
                    WHEN exp.csm_exp IS NOT NULL THEN
                        concat(
                            div(exp.csm_exp, 12)::varchar, 
                            '.', 
                            CAST(mod(exp.csm_exp, 12)::varchar AS varchar)
                        ) 
                    ELSE 
                        '0' 
                END AS csm_experience_display,
                -- total_experience_display
                concat(
                    div((COALESCE(exp.csm_exp, 0) + COALESCE(exp.previous_company_exp, 0)), 12)::varchar, 
                    '.', 
                    CAST(mod((COALESCE(exp.csm_exp, 0) + COALESCE(exp.previous_company_exp, 0)), 12)::varchar AS varchar)
                ) AS total_experience_display,
            (select primary_skill_id from resource_skill_data where employee_id=hr.id) AS primary_skill_id
            FROM hr_employee AS hr 
            LEFT JOIN project pj ON pj.employee_id = hr.id 
            LEFT JOIN ed on ed.emp_id=hr.id
            LEFT JOIN ct on ct.emp_id=hr.id
            LEFT JOIN experience exp ON exp.emp_id = hr.id
            WHERE hr.active = TRUE 
                AND hr.employement_type IN (SELECT id FROM kwemp_employment_type WHERE code = 'O') 
            GROUP BY hr.id, exp.previous_company_exp, exp.csm_exp)""" % (
            self._table))   
        
        
    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False