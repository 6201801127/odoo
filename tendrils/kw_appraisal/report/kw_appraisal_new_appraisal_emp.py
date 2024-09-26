# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class KwAppraisalPageWiseReport(models.Model):
    _name           = "kw_appraisal_new_appraisal_emp"
    _description    = "New Appraisal Employee report"
    _auto           = False

    emp_id            = fields.Many2one("hr.employee",string='Employee') 
    name = fields.Char(related='emp_id.name')
    emp_code        = fields.Char(string='Employee Code')
    job_id       = fields.Many2one("hr.job",string='Designation')
    department_id       = fields.Many2one("hr.department",string='Department')
    date_of_joining       = fields.Date(string='Date Of Joining')
    emp_survey_id        = fields.Many2one("survey.survey",string='Appraisal Form')
    state = fields.Many2one('hr.appraisal.stages', string='Current Stage', track_visibility='onchange', index=True)    
    appraisal_year = fields.Char(string="Appraisal Year")
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")#16
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")

           
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} as (
                          SELECT 
                    ROW_NUMBER() OVER (order by a.emp_id) as id,
                    a.emp_id as emp_id, 
                    e.emp_code as emp_code, 
                    e.department_id as department_id, 
                    e.job_id as job_id, 
                    e.date_of_joining as date_of_joining,
                    a.emp_survey_id as emp_survey_id,
                    a.state as state,
                    a.appraisal_year as appraisal_year,
                    e.employement_type,
                    e.budget_type
                FROM hr_appraisal AS a
                JOIN hr_employee AS e ON e.id = a.emp_id
                WHERE a.emp_id IN (SELECT emp_id FROM hr_appraisal GROUP BY emp_id HAVING COUNT(emp_id) = 1)  and a.appraisal_year = '2023-24'

        )"""
        self.env.cr.execute(query)


   