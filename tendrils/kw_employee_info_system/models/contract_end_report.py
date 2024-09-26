# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ContractEndReport(models.Model):
    _name = 'contract_end_report'
    _description = 'Contract End Report'
    _auto = False

    employee_id = fields.Many2one('hr.employee',string='Employee')
    code = fields.Char(related='employee_id.emp_code')
    name = fields.Char(related='employee_id.name')
    department = fields.Char(related='employee_id.department_id.name', string="Department")
    division = fields.Char(related='employee_id.division.name', string="Division")
    section = fields.Char(related='employee_id.section.name', string="Section")
    practise = fields.Char(related='employee_id.practise.name', string="Practice")
    designation = fields.Char(related='employee_id.job_id.name')
    start_date = fields.Date(string='Contract Start Date',related='employee_id.start_date')
    end_date = fields.Date(string='Contract End Date',related='employee_id.end_date')
    project = fields.Char(related='employee_id.emp_project_id.name', string="Project")
    
    year = fields.Integer()
    month = fields.Integer()
    days = fields.Integer()
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (

        SELECT  row_number() over() AS id,
			id AS employee_id,
			(SELECT EXTRACT(YEAR FROM end_date)) AS year,
			(SELECT EXTRACT(MONTH FROM end_date)) AS month,
			(end_date::date - CURRENT_DATE::date) AS days 
			from hr_employee 
			where (end_date::date - CURRENT_DATE::date) < 30  and active=true and employement_type in
			(select id from kwemp_employment_type where code in ('S','C'))
            )""" % (self._table))
