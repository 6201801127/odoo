# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ProjectWiseResource(models.Model):
    _name = 'technology_wise_resource'
    _description = 'Technology Wise Resource Report'
    _auto = False



    employee_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    job_id = fields.Many2one('hr.job',string="Designation")
    emp_code = fields.Char(string="Employee Code")
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    sbu = fields.Char(string ='Employee SBU')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Technology')
    job_branch_id = fields.Many2one('kw_res_branch',string="Location")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
            	 select row_number() over(order by a.name) as id,
		 			a.id as employee_id,
                    (select primary_skill_id from resource_skill_data where employee_id=a.id ) as primary_skill_id,
					a.job_id ,a.emp_code ,
					a.emp_category,
                    a.job_branch_id ,
                   (select name from kw_sbu_master where id = a.sbu_master_id) as sbu       
                    from hr_employee a 
                    join hr_department hd on hd.id = a.department_id
                    where a.active = true and hd.code='BSS' and a.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                            )""" )

    
