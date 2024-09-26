from odoo import tools
from odoo import models, fields, api


class TourBudgetReport(models.Model):
    _name = "kw_tour_budget_report"
    _description = "Tour Budget Report"
    _auto = False

    budget_head_id = fields.Many2one('kw_tour_budget_head', 'Budget Head')
    project_id = fields.Many2one('crm.lead', 'Project')
    project_name = fields.Char(related='project_id.name',string= 'Project Name')
    project_code = fields.Char(related='project_id.code', string= 'Project Code')
    code = fields.Char('Reference No.')
    budget_amount = fields.Float('Budget Amount')
    total_budget_expense = fields.Float('Spent Amount')
    remaining_amount = fields.Float('Balance Amount')
    origin_place = fields.Char('Origination Place')
    date_travel = fields.Date("Date Of Travel")
    date_return = fields.Date("Date Of Return")
    purpose = fields.Char("Purpose")
    employee_id = fields.Many2one('hr.employee', 'Employee')
    record_type = fields.Char("Record Type")
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'kw_tour_budget_report')
        self.env.cr.execute(f"""
            CREATE or REPLACE VIEW kw_tour_budget_report AS (
            WITH project_budget AS (
            SELECT
                id::integer,
                budget_head_id::integer,
                project_id::integer,
                budget_amount::numeric,
                'Declared Budget'::text AS code,
                ''::text AS purpose,
                NULL::integer AS employee_id,
                NULL::integer AS fiscal_year_id,
                NULL::date AS date_travel,
                NULL::date AS date_return,
                0.0::numeric AS total_budget_expense,
                ''::text AS origin_place,
                ''::text AS record_type,
                0.0::numeric AS remaining_amount
            FROM kw_tour_project_budget
        ),
        tours AS (
            SELECT
                kt.id::integer AS id,
                kt.budget_head_id::integer AS budget_head_id,
                kt.project_id::integer AS project_id,
                0.0::numeric AS budget_amount,
                af.id::integer AS fiscal_year_id,
                kt.code::text AS code,
                kt.purpose::text AS purpose,
                kt.employee_id::integer AS employee_id,
                kt.date_travel::date AS date_travel,
                kt.date_return::date AS date_return,
                kt.total_budget_expense::numeric AS total_budget_expense,
                e.name::text AS origin_place,
                'Blocked'::text AS record_type,
                0.0::numeric AS remaining_amount
            FROM kw_tour kt
            LEFT JOIN account_fiscalyear af ON kt.date_travel BETWEEN af.date_start AND af.date_stop
            LEFT JOIN kw_tour_city e ON kt.city_id = e.id
            JOIN crm_lead cl ON cl.id = kt.project_id
            WHERE kt.state NOT IN ('Draft', 'Rejected', 'Cancelled') 
            AND kt.id NOT IN (
                SELECT kt.id FROM kw_tour kt 
                LEFT JOIN kw_tour_settlement kts ON kts.tour_id = kt.id
                WHERE kts.state != 'Rejected'
            )
            AND kt.id NOT IN (
                SELECT kt.id FROM kw_tour kt 
                LEFT JOIN kw_tour_cancellation ktc ON ktc.tour_id = kt.id 
                WHERE ktc.state = 'Applied'
            )
        ),
        settlements AS (
            SELECT
                kts.id::integer AS id,
                kts.budget_head_id::integer AS budget_head_id,
                kt.project_id::integer AS project_id,
                0.0::numeric AS budget_amount,
                af.id::integer AS fiscal_year_id,
                kt.code::text AS code,
                kt.purpose::text AS purpose,
                kt.employee_id::integer AS employee_id,
                kt.date_travel::date AS date_travel,
                kt.date_return::date AS date_return,
                kts.total_budget_expense::numeric AS total_budget_expense,
                e.name::text AS origin_place,
                'Actual'::text AS record_type,
                0.0::numeric AS remaining_amount
            FROM kw_tour_settlement kts
            JOIN kw_tour kt ON kt.id = kts.tour_id
            LEFT JOIN account_fiscalyear af ON kt.date_travel BETWEEN af.date_start AND af.date_stop
            LEFT JOIN kw_tour_city e ON kt.city_id = e.id
            WHERE kts.state != 'Rejected'
        ),
        report_data AS (
            SELECT id, budget_head_id, project_id, budget_amount, code, purpose, 
            employee_id, date_travel, date_return, total_budget_expense, origin_place, 
            record_type, remaining_amount, fiscal_year_id 
            FROM tours 
            UNION ALL
            SELECT id, budget_head_id, project_id, budget_amount, code, purpose, 
            employee_id, date_travel, date_return, total_budget_expense, origin_place, 
            record_type, remaining_amount, fiscal_year_id 
            FROM settlements
        )
        SELECT 
            row_number() OVER (ORDER BY budget_amount DESC) AS id, 
            budget_head_id, project_id, budget_amount, code, purpose, 
            employee_id, date_travel, date_return, fiscal_year_id, 
            total_budget_expense, origin_place, record_type, 
            (budget_amount - total_budget_expense) AS remaining_amount
        FROM 
            report_data
               )""")
