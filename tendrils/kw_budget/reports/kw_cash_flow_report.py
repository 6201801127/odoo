from odoo import models, api, fields, tools

class CashFlowReport(models.Model):
    _name = "kw_cash_flow_report"
    _description = "Report For Cash Flow"
    _auto = False
    _order = "particulars desc"

    particulars = fields.Char('Particulars')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    budget_type = fields.Selection([('capital', 'Capital'), ('revenue', 'Revenue'), ('bs_items', 'B/S Items')], string="Budget Type")
    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_code_id.code', string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    name =  fields.Char(string='Name')
    name_of_expense = fields.Char('Receipts/Payments')
    apr_budget = fields.Float('Apr Budget')
    may_budget = fields.Float('May Budget')
    jun_budget = fields.Float('Jun Budget')
    jul_budget = fields.Float('Jul Budget')
    aug_budget = fields.Float('Aug Budget')
    sep_budget = fields.Float('Sep Budget')
    oct_budget = fields.Float('Oct Budget')
    nov_budget = fields.Float('Nov Budget')
    dec_budget = fields.Float('Dec Budget')
    jan_budget = fields.Float('Jan Budget')
    feb_budget = fields.Float('Feb Budget')
    mar_budget = fields.Float('Mar Budget')
    total_budget = fields.Float('Total', compute='get_total_amount', store=False)

    def get_total_amount(self):
        for rec in self:
            rec.total_budget = (rec.apr_budget  + rec.may_budget + rec.jun_budget +
                          rec.jul_budget + rec.aug_budget + rec.sep_budget + rec.oct_budget +
                          rec.nov_budget + rec.dec_budget + rec.jan_budget + rec.feb_budget +
                          rec.mar_budget)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                				SELECT   
                    ROW_NUMBER() OVER (ORDER BY budget_type DESC) AS id,
                    particulars AS particulars,
                    fiscal_year_id AS fiscal_year_id,
                    budget_type AS budget_type,
                    account_code_id AS account_code_id,
                    name_of_expenses AS name_of_expense,
                    name as name,
                    apr_budget AS apr_budget,
                    may_budget AS may_budget,
                    jun_budget AS jun_budget,
                    jul_budget AS jul_budget,
                    aug_budget AS aug_budget,
                    sep_budget AS sep_budget,
                    oct_budget AS oct_budget,
                    nov_budget AS nov_budget,
                    dec_budget AS dec_budget,
                    jan_budget AS jan_budget,
                    feb_budget AS feb_budget,
                    mar_budget AS mar_budget 
                FROM 
                    
                (SELECT 
                    'Capital Expenses' AS particulars,
                    fiscal_year_id,
                    'capital' AS budget_type,
                    NULL::int AS account_code_id,
                    NULL AS name_of_expenses,
                    NULL As name,
                    SUM(apr_budget) AS apr_budget,
                    SUM(may_budget) AS may_budget,
                    SUM(jun_budget) AS jun_budget,
                    SUM(jul_budget) AS jul_budget,
                    SUM(aug_budget) AS aug_budget,
                    SUM(sep_budget) AS sep_budget,
                    SUM(oct_budget) AS oct_budget,
                    SUM(nov_budget) AS nov_budget,
                    SUM(dec_budget) AS dec_budget,
                    SUM(jan_budget) AS jan_budget,
                    SUM(feb_budget) AS feb_budget,
                    SUM(mar_budget) AS mar_budget
                FROM
                    kw_capital_budget_line
                LEFT JOIN kw_capital_budget ON kw_capital_budget_line.capital_budget_id = kw_capital_budget.id 
                GROUP BY 
                    fiscal_year_id
                
            UNION ALL
                
                    select 'Treasury Income' AS particulars,
								rv.fiscal_year_id AS fiscal_year_id,
								'Revenue' AS budget_type,
								NULL::int AS account_code_id,
								NULL AS name_of_expenses,
								NULL AS name,
                                -1 * sum(apr_budget) as apr_budget, -1 * sum(may_budget) as may_budget, -1 * sum(jun_budget) as jun_budget, -1 * sum(jul_budget) as jul_budget, -1 * sum(aug_budget) as aug_budget, -1 * sum(sep_budget) as sep_budget, 
                                    -1 * sum(oct_budget) as oct_budget, -1 * sum(nov_budget) as nov_budget, -1 * sum(dec_budget) as dec_budget, -1 * sum(jan_budget) as jan_budget, -1 * sum(feb_budget) as feb_budget, -1 * sum(mar_budget) as mar_budget
                            FROM 
                                kw_revenue_budget_line AS rvl  
                            JOIN 
                                kw_revenue_budget AS rv ON rv.id = rvl.revenue_budget_id
                            WHERE 
                                rvl.expense_type = 'Income'  group by rv.fiscal_year_id
								
			UNION ALL	
								
							SELECT  'Treasury Expenses' AS particulars,
									rv.fiscal_year_id AS fiscal_year_id,
									'Revenue' AS budget_type,
									NULL::int AS account_code_id,
									NULL AS name_of_expenses,
									NULL AS name,                                
                                    sum(apr_budget) as apr_budget, sum(may_budget) as may_budget, sum(jun_budget) as jun_budget, sum(jul_budget) as jul_budget, sum(aug_budget) as aug_budget, sum(sep_budget) as sep_budget, 
                                    sum(oct_budget) as oct_budget, sum(nov_budget) as nov_budget, sum(dec_budget) as dec_budget, sum(jan_budget) as jan_budget, sum(feb_budget) as feb_budget, sum(mar_budget) as mar_budget
                                FROM 
                                    kw_revenue_budget_line AS rvl 
                                JOIN 
                                    kw_revenue_budget AS rv ON rv.id = rvl.revenue_budget_id
                                WHERE 
                                    rvl.expense_type = 'Expenses' group by rv.fiscal_year_id
				 
			UNION ALL
                
                    select 'Project Income' AS particulars,
								rv.fiscal_year_id AS fiscal_year_id,
								'Project' AS budget_type,
								NULL::int AS account_code_id,
								NULL AS name_of_expenses,
								NULL AS name,
                                -1 * sum(apr_budget) as apr_budget, -1 * sum(may_budget) as may_budget, -1 * sum(jun_budget) as jun_budget, -1 * sum(jul_budget) as jul_budget, -1 * sum(aug_budget) as aug_budget, -1 * sum(sep_budget) as sep_budget, 
                                    -1 * sum(oct_budget) as oct_budget, -1 * sum(nov_budget) as nov_budget, -1 * sum(dec_budget) as dec_budget, -1 * sum(jan_budget) as jan_budget, -1 * sum(feb_budget) as feb_budget, -1 * sum(mar_budget) as mar_budget                            FROM 
                                kw_sbu_project_budget_line AS rvl  
                            JOIN 
                                kw_sbu_project_budget AS rv ON rv.id = rvl.sbu_project_budget_id
                            WHERE 
                                rvl.head_expense_type = 'Income'  group by rv.fiscal_year_id
								
			UNION ALL	
								
							SELECT  'Project Expenses' AS particulars,
								rv.fiscal_year_id AS fiscal_year_id,
								'Project' AS budget_type,
								NULL::int AS account_code_id,
								NULL AS name_of_expenses,
								NULL AS name,
                                sum(apr_budget) as apr_budget, sum(may_budget) as may_budget, sum(jun_budget) as jun_budget, sum(jul_budget) as jul_budget, sum(aug_budget) as aug_budget, sum(sep_budget) as sep_budget, 
                                    sum(oct_budget) as oct_budget, sum(nov_budget) as nov_budget, sum(dec_budget) as dec_budget, sum(jan_budget) as jan_budget, sum(feb_budget) as feb_budget, sum(mar_budget) as mar_budget
                            FROM 
                                kw_sbu_project_budget_line AS rvl  
                            JOIN 
                                kw_sbu_project_budget AS rv ON rv.id = rvl.sbu_project_budget_id
                            WHERE 
                                rvl.head_expense_type = 'Expenses'  group by rv.fiscal_year_id

			UNION ALL
                SELECT
                    'B/S Items' AS particulars,
                    fiscal_year_id,
                    'bs_items' AS budget_type,
                    account_code_id,
                    name_of_expense AS name_of_expenses,
                    name as name,
                    apr_budget,
                    may_budget,
                    jun_budget,
                    jul_budget,
                    aug_budget,
                    sep_budget,
                    oct_budget,
                    nov_budget,
                    dec_budget,
                    jan_budget,
                    feb_budget,
                    mar_budget
                FROM (
                    SELECT 
                        account_code_id,
                        name_of_expense,
                        name as name,
                        apr_budget,
                        may_budget,
                        jun_budget,
                        jul_budget,
                        aug_budget,
                        sep_budget,
                        oct_budget,
                        nov_budget,
                        dec_budget,
                        jan_budget,
                        feb_budget,
                        mar_budget,
                        cash_flow_id
                    FROM
                        kw_cash_flow_capital
                    UNION ALL
                    SELECT 
                        account_code_id,
                        name_of_expense,
                        name as name,
                        apr_budget,
                        may_budget,
                        jun_budget,
                        jul_budget,
                        aug_budget,
                        sep_budget,
                        oct_budget,
                        nov_budget,
                        dec_budget,
                        jan_budget,
                        feb_budget,
                        mar_budget,
                        cash_flow_id
                    FROM
                        kw_cash_flow_revenue
                    UNION ALL
                    SELECT 
                        account_code_id,
                        name_of_expense,
                        name as name,
                        apr_budget,
                        may_budget,
                        jun_budget,
                        jul_budget,
                        aug_budget,
                        sep_budget,
                        oct_budget,
                        nov_budget,
                        dec_budget,
                        jan_budget,
                        feb_budget,
                        mar_budget,
                        cash_flow_id
                    FROM
                        kw_cash_flow_project
                ) AS bs_items
                LEFT JOIN kw_cash_flow ON bs_items.cash_flow_id = kw_cash_flow.id) AS abc 
                                               
            )
        """ % (self._table,))
