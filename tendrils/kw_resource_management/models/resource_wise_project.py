# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ProjectWiseResource(models.Model):
    _name = 'resource_wise_project'
    _description = 'Resource Wise Project Report'
    _auto = False
    _order = "employee_id"


    employee_id = fields.Char(string='Resource')
    code = fields.Char(string='Employee Code')
    designation = fields.Many2one('hr.job', string='Designation')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    sbu_id = fields.Char(string="SBU")
    project_name = fields.Text(string="Project Name")
    emp_sbu_id = fields.Many2one('hr.employee', string='Project SBU')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (

      	with project as
		(select prj.name as project_id,
		 prj.code as project_code,
		 rt.emp_id as employee_id,
		 prj.crm_id
		 from hr_employee emp
		 left join project_project prj on prj.emp_id = emp.id
		 left join kw_project_resource_tagging rt on rt.project_id=prj.id
		 where prj.active = True and rt.active = True)
			
		    SELECT  row_number() over(order by emp.name) AS id,
                    emp.emp_code as code,
                    emp.name as employee_id,
                    emp.job_id as designation,
					emp.emp_category AS emp_category,
        			emp.employement_type as employement_type,
                    (select name from kw_sbu_master where id = emp.sbu_master_id) as sbu_id,
                    (select representative_id from kw_sbu_master where id = emp.sbu_master_id) as emp_sbu_id,
 					case when (string_agg(concat(pj.project_id,' (', pj.project_code,')'),', '))=' ()'then null 
					else string_agg(concat(pj.project_id,' (', pj.project_code,')'),', ') end as project_name
            
				From hr_employee as emp
				left join project pj on pj.employee_id = emp.id
                where emp.active = True
				group by emp.emp_code,emp.id,emp.sbu_master_id )""" )


 
        
class SbuProjectWiseHeadCountEmployeeDetails(models.Model):
    _name = "sbu_project_wise_get_emp_details"
    _description = "SBU & Project wise Head count Employee Details"
    _auto = False
   
    emp_id = fields.Many2one('hr.employee')
    employee_name =  fields.Char(related='emp_id.name', string='Employee Name')
    sbu_name = fields.Char(string="SBU")
    project_id =fields.Many2one('project.project',string="Project Name")
    designation_id = fields.Many2one('hr.job', string='Designation')
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT
                row_number() OVER () as id,
                (SELECT name FROM kw_sbu_master WHERE id = hr.sbu_master_id AND type = 'sbu') as sbu_name,
                a.id as project_id,
                (SELECT job_id FROM hr_employee WHERE id = b.emp_id) as designation_id,
                b.emp_id as emp_id
            --     ARRAY(SELECT CAST(unnest(string_to_array(string_agg(b.emp_id::text, ','), ',')) AS integer)) as employee_id
            FROM
                project_project a
            LEFT JOIN
                kw_project_resource_tagging b ON a.id = b.project_id
            LEFT JOIN
                hr_employee hr ON hr.id = a.emp_id 
            WHERE
                a.active = true
                AND b.active = true
                AND hr.sbu_master_id IN (SELECT id FROM kw_sbu_master WHERE type = 'sbu')
            GROUP BY
                sbu_name, (SELECT job_id FROM hr_employee WHERE id = b.emp_id),b.emp_id,a.id 
            )""" )