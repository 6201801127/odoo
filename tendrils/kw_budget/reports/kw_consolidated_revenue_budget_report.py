from odoo import models, api, fields, tools

class ConsolidatedRevenueReport(models.Model):
    _name = "kw_consolidated_revenue_budget_report"
    _description = "Report For Consilidated revenue budget"
    _auto = False
    _order = "account_code desc"

    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char( string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    state = fields.Char(string='Pending At')
    remark =  fields.Text('Remark')
    expense_type = fields.Char(string='Expense Type')
    name_of_expenses = fields.Char(string='Name of Expenses')
    april_budget = fields.Float('April Budget')
    may_budget = fields.Float('May Budget')
    june_budget = fields.Float('June Budget')
    july_budget = fields.Float('July Budget')
    august_budget = fields.Float('Aug Budget')
    september_budget = fields.Float('Sept Budget')
    october_budget = fields.Float('Oct Budget')
    november_budget = fields.Float('Nov Budget')
    december_budget = fields.Float('Dec Budget')
    january_budget = fields.Float('Jan Budget')
    february_budget = fields.Float('Feb Budget')
    march_budget = fields.Float('March Budget')
    total_budget = fields.Float('Total Budget Amount')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                select row_number() over(order by rbl.account_code_id desc) as id,dm.department_id as department_id,dm.division_id as division_id,
                dm.section_id as section_id,rb.fiscal_year_id as fiscal_year_id,rbl.expense_type as expense_type,rbl.remark as remark,
                (SELECT code FROM account_account WHERE id = rbl.account_code_id) AS account_code,   
                CASE
                    WHEN rb.state = 'draft' THEN 'Yet to Apply'
                    WHEN rb.state = 'to_approve' THEN 'Pending with L2'
                    WHEN rb.state = 'approved' THEN 'Pending with Finance'
                    WHEN rb.state = 'confirm' THEN 'Pending For Approval'
                    WHEN rb.state = 'validate' THEN 'Budget Approved'
                    WHEN rb.state = 'cancel' THEN 'Cancel'
                ELSE '--'
                END AS state,
                rbl.name_of_expenses as name_of_expenses,
                rbl.account_code_id as account_code_id,
                rbl.apr_budget AS april_budget,
                rbl.may_budget AS may_budget,
                rbl.jun_budget AS june_budget,
                rbl.jul_budget AS july_budget,
                rbl.aug_budget AS august_budget,
                rbl.sep_budget AS september_budget,
                rbl.oct_budget AS october_budget,
                rbl.nov_budget AS november_budget,
                rbl.dec_budget AS december_budget,
                rbl.jan_budget AS january_budget,
                rbl.feb_budget AS february_budget,
                rbl.mar_budget AS march_budget,
                (rbl.apr_budget + rbl.may_budget + rbl.jun_budget + rbl.jul_budget + rbl.aug_budget + rbl.sep_budget + rbl.oct_budget + rbl.nov_budget + rbl.dec_budget + rbl.jan_budget + rbl.feb_budget + rbl.mar_budget) AS total_budget
                from kw_budget_dept_mapping dm
                left join kw_revenue_budget rb
                on dm.id =rb.budget_department
                left join kw_revenue_budget_line rbl on rbl.revenue_budget_id =rb.id
                where rbl.revenue_budget_id is not null and rb.state not in ('validate','cancel')
                ORDER BY
                account_code desc
                )""" % (self._table))



