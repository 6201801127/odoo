# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class HorizontalWiseResource(models.Model):
    _name = 'horizontal_wise_resource'
    _description = 'Horizontal Wise Resource'
    _auto = False
    _order = "employee_id"


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
    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name= fields.Char(related='sbu_id.name', string='SBU')
    resource_id = fields.One2many('project.project', 'emp_id')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Skill')
    project_name = fields.Char('Project')

   
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
                            prj.crm_id
                        FROM hr_employee emp
                        LEFT JOIN project_project prj ON prj.emp_id = emp.id
                        LEFT JOIN kw_project_resource_tagging rt ON rt.project_id = prj.id
                        WHERE prj.active = TRUE AND rt.active = TRUE
                    )
                SELECT  row_number() over() as id,
                        hr.id as employee_id,
                        hr.job_id as designation,
                        hr.name as name,
                        hr.date_of_joining as date_of_joining,
                        hr.emp_role as emp_role,
                        hr.emp_category as emp_category,
                        hr.employement_type as employement_type,
                        hr.job_branch_id as job_branch_id,
                        hr.sbu_master_id as sbu_id,
                        hr.sbu_type as sbu_type,
                        (select primary_skill_id from resource_skill_data where employee_id = hr.id) as primary_skill_id,
                        replace(regexp_replace(
                                    string_agg(concat(pj.project_id, ' (', pj.project_code, '),'), 
                                    E'\n'), 
                                    E',\n+', 
                                    E',\n'
                                ), 
                                E',\n$', 
                                ''
                                ) AS project_name
                                
                        FROM hr_employee AS hr 
                        LEFT JOIN project pj ON pj.employee_id = hr.id 
                        join hr_department as hrd on hrd.id= hr.department_id
                        where hr.active =true and hrd.code='BSS' 
                        and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') 
                        and hr.sbu_type = 'horizontal' 
                        and hr.sbu_master_id is not Null
                        group by hr.id
         )""" % (self._table))
        