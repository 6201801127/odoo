# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ForecastedReleaseReport(models.Model):
    _name = 'forecasted_release_report'
    _description = 'Forecasted Release Report'
    _auto = False


    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name= fields.Char(related='sbu_id.name', string='SBU')
    order_oppurtunity = fields.Char(string='KW WO/OPP')
    project_name = fields.Char(string="Project Name")
    emp_id = fields.Char(string="PM Name")
    resource_name = fields.Char(string='Resource Name')
    code = fields.Char(string='Resource Code')
    job_id = fields.Many2one('hr.job',string='Designation')
    emp_role = fields.Many2one('kwmaster_role_name', string='Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Category')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Technology')
    end_date = fields.Date(string='Planned Released Date')
    extend_date = fields.Char(string='Extended Released Date')
    year = fields.Integer(string='Fiscal Year')
    apr = fields.Integer(string="April")
    may = fields.Integer(string="May")
    jun = fields.Integer(string="June")
    jul = fields.Integer(string="July")
    aug = fields.Integer(string="August")
    sep = fields.Integer(string="September")
    oct = fields.Integer(string="October")
    nov = fields.Integer(string="November")
    dec = fields.Integer(string="December")
    jan = fields.Integer(string="January")
    feb = fields.Integer(string="February")
    mar = fields.Integer(string="March")
        

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (

    select row_number() over() AS id,
       (select sbu_master_id from hr_employee where id = rt.emp_id) as sbu_id,
       (select code from crm_lead where id = prj.crm_id) as order_oppurtunity,
	   prj.name as project_name,
	   (select name from hr_employee where id=rt.emp_id)as resource_name,
	   (select name from hr_employee where id = prj.emp_id)as emp_id,
	   rt.end_date,
       EXTRACT(YEAR FROM rt.end_date) AS year,
	   (select emp_code from hr_employee where id = rt.emp_id) as code,
	   (select job_id from hr_employee where id = rt.emp_id) as job_id,
	   (select emp_role from hr_employee where id = rt.emp_id) as emp_role,
       (select emp_category from hr_employee where id = rt.emp_id) as emp_category,
	   (select primary_skill_id from resource_skill_data rsd where rsd.employee_id = rt.emp_id) as primary_skill_id,
	   '' as extend_date,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 4 THEN 1 ELSE 0 END AS apr,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 5 THEN 1 ELSE 0 END AS may,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 6 THEN 1 ELSE 0 END AS jun,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 7 THEN 1 ELSE 0 END AS jul,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 8 THEN 1 ELSE 0 END AS aug,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 9 THEN 1 ELSE 0 END AS sep,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 10 THEN 1 ELSE 0 END AS oct,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 11 THEN 1 ELSE 0 END AS nov,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 12 THEN 1 ELSE 0 END AS dec,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 1 THEN 1 ELSE 0 END AS jan,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 2 THEN 1 ELSE 0 END AS feb,
        CASE WHEN EXTRACT(MONTH FROM rt.end_date) = 3 THEN 1 ELSE 0 END AS mar
	   
            
	   from kw_project_resource_tagging as rt
       join project_project as prj on prj.id = rt.project_id
       where prj.active = True and rt.active = True
				
				 )""" )


