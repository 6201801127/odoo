from odoo import models, fields, api
from odoo import tools

class TourStatusReport(models.Model):
    _name = 'kw_tour_status_report'
    _description = 'Tour Status Report'
    _auto = False

    employee_id = fields.Many2one('hr.employee', 'Employee')
    applied_date = fields.Date("Applied Date")
    code = fields.Char("Tour Reference No.")
    project_id = fields.Many2one('crm.lead', string= "Project/OPP.")
    department = fields.Char(related='employee_id.department_id.name', string='Department Name')
    division        = fields.Char(related='employee_id.division.name', string='Division')
    section         = fields.Char(related='employee_id.section.name', string='Section')
    tour_type_id = fields.Many2one('kw_tour_type', string="Type Of Tour")
    budget_head_id = fields.Many2one('kw_tour_budget_head', string="Budget head")
    date_travel  = fields.Date("Date Of Travel")
    date_return  = fields.Date("Date Of Return") 
    state        = fields.Char("Status")
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")

  
  

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (   
                    SELECT
                    ROW_NUMBER() OVER (ORDER BY t.date_travel DESC) AS id,
                    t.code,
                    t.employee_id,
                    t.tour_type_id,
                    t.project_id,
                    DATE(t.create_date) AS applied_date,
                    t.budget_head_id,
                    af.id AS fiscal_year_id,
                    t.date_travel,
                    t.date_return,
                    CASE
                        WHEN t.state = 'Applied' AND ts.tour_id IS NULL THEN 'Pending with RA for your approval'
                        WHEN t.state = 'Approved' AND ts.tour_id IS NULL THEN 'Pending with Travel desk for ticket and hotel arrangement'
                        WHEN t.state = 'Traveldesk Approved' AND ts.tour_id IS NULL THEN 'Pending with Finance for advance payment'
                        WHEN t.state = 'Finance Approved' AND ts.tour_id IS NULL THEN 'Pending with employee for making settlement'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Applied' THEN 'Settlement request pending with RA'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Approved' THEN 'Settlement pending with Finance'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Granted' THEN 'Payment pending with Finance'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Payment Done' THEN 'Settled'
                        ELSE '--'
                    END AS state
                FROM
                    kw_tour t
                LEFT JOIN
                    kw_tour_settlement ts ON t.id = ts.tour_id
                LEFT JOIN account_fiscalyear af ON t.date_travel BETWEEN af.date_start AND af.date_stop
                
                WHERE
                    t.state NOT IN ('Draft', 'Rejected', 'Cancelled')
                    )""")	

   

    