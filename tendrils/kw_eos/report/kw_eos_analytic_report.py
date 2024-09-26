from odoo import fields, models, api, tools
from datetime import datetime

class EOSAnalyticReport(models.Model):
    _name = 'eos_analytic_report'
    _description = 'Year On Year Exit Report'
    _auto = False

    department_id = fields.Many2one('hr.department', string='Department')
    designation_id = fields.Many2one('hr.job', string="Designation")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    fiscal_year = fields.Char(string='Fiscal Year')
    # fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    quarterly = fields.Char(string="Quarterly")
    num_resigned_employees = fields.Integer(string='Resigned Employees')
    reg_reason= fields.Char("Reason Of Exit")
    joining_date = fields.Date('Date Of Joining')
    last_working_day = fields.Date('Exit Date')
    gender= fields.Char("Gender")
    budget= fields.Char("Budget Type")
    tenure_at_csm = fields.Char("Tenure At CSM")
    work_location_id=fields.Many2one('kw_res_branch',string='Work Location')
    tenure_months = fields.Integer(string="Tenure (Months)",)

    



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (
        SELECT 
            row_number() over() AS id,
            r.fiscal_yr AS fiscal_year,
            CASE extract(quarter FROM e.last_working_day)
                when 1 then 'Q4'
                when 2 then 'Q1'
                when 3 then 'Q2'
                when 4 then 'Q3'
            END AS quarterly,
            e.id AS employee_id, 
            e.department_id AS department_id,
            e.job_id AS designation_id,
            COUNT(e.id) AS num_resigned_employees,
            r.reason AS reg_reason,
            e.date_of_joining as joining_date,
            e.last_working_day as last_working_day,
            e.gender as gender,
            e.budget_type as budget,
            e.job_branch_id as work_location_id,
            EXTRACT(year FROM age(e.last_working_day, e.date_of_joining)) || ' years, ' ||
            EXTRACT(month FROM age(e.last_working_day, e.date_of_joining)) || ' months, ' ||
            EXTRACT(day FROM age(e.last_working_day, e.date_of_joining)) || ' days' AS tenure_at_csm,
            EXTRACT(year FROM age(e.last_working_day, e.date_of_joining)) * 12 +
            EXTRACT(month FROM age(e.last_working_day, e.date_of_joining)) AS tenure_months
        FROM
            hr_employee e
        JOIN
            kw_resignation r ON e.id = r.applicant_id
        WHERE e.active=false 
        GROUP BY r.fiscal_yr,r.reason, quarterly, e.job_id, e.id,e.last_working_day
 )""" % (self._table))
        
