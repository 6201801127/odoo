# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ProjectWiseResource(models.Model):
    _name = 'project_wise_resource'
    _description = 'Project Wise Resource Tagging Report'
    _auto = False



    employee_id = fields.Many2one('hr.employee', string='Employee')
    project_name = fields.Many2one('project.project',string="Project Name")
    order_oppurtinity = fields.Char(string="WO/OPP")
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    # sbu_name = fields.Many2one('kw_sbu_master', string='SBU Name')
    sbu = fields.Char(string = 'Emp-SBU')
    resource_type = fields.Char(string='Resource Type')
    sbu_id = fields.Char(string="Project-SBU")
    # applied_eos = fields.Boolean(compute='_compute_eos')
    # category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    role_kw_id = fields.Integer(related='emp_role.kw_id')
    # budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
    #                                string="Budget Type",related='employee_id.budget_type')
    project_manager_id = fields.Many2one('hr.employee', string='Project Manager')
    project_sbu_id = fields.Many2one('hr.employee', string='Project SBU')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Technology')
    practise_id = fields.Many2one('hr.department', string='Practice')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
            select  row_number() over(order by emp.name) AS id, rt.project_id as project_name,
            p.active as active_project,
            p.emp_id as project_manager_id,
            (select primary_skill_id from resource_skill_data where employee_id = emp.id) as primary_skill_id,
            emp.practise as practise_id,
            rt.emp_id as employee_id,
            emp.job_id AS designation,
            emp.date_of_joining AS date_of_joining,
            emp.emp_code as code,
           -- emp.name as employee_name,
            emp.emp_role AS emp_role,
            emp.emp_category AS emp_category,
            emp.employement_type as employement_type,
            emp.job_branch_id as job_branch_id,
            (case when emp.sbu_type = 'sbu'  then 'SBU' when emp.sbu_type='horizontal' then 'Horizontal' end )resource_type,
            --emp.sbu_master_id as sbu_name,
            (select name from kw_sbu_master where id = emp.sbu_master_id) as sbu,
            (select name from kw_sbu_master where id = p.sbu_id) as sbu_id,
            (select representative_id from kw_sbu_master where id = p.sbu_id) as project_sbu_id,
            (select code from crm_lead where id = p.crm_id) as order_oppurtinity
          
            
            from kw_project_resource_tagging rt
            join project_project p on p.id = rt.project_id
            left join hr_employee emp on emp.id = rt.emp_id
            left join hr_department d on d.id = emp.department_id
            left join hr_job j on emp.job_id = j.id
            where rt.active = True and p.active = True and emp.active = True
            )""" )

    # @api.depends('employee_id')
    # def _compute_eos(self):
    #     for rec in self:
    #         resignation = self.env['kw_resignation'].sudo().search(
    #             [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
    #         rec.applied_eos = True if resignation else False
