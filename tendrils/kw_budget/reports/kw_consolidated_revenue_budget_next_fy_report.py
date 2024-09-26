from odoo import models, api, fields, tools

class ConsolidatedRevenueNextFyReport(models.Model):
    _name = "kw_consolidated_revenue_budget_next_fy_report"
    _description = "Report For Consilidated revenue budget"
    _auto = False
    _order = "account_code desc"

    budget_type = fields.Char(string='Budget Type')
    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char( string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_name_id = fields.Many2one('account.account.type', string='Group Head')
    # group_id = fields.Many2one('account.group.name',string= 'Group Name')
    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    project_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    client = fields.Char(string="Client Name")
    project_code = fields.Char(string="Project Code")
    order_value = fields.Char(string="Order Value")
    work_order_type = fields.Char(string="Work Order Type")
    opportunity_name = fields.Char(string="OPP Name")
    expense_type = fields.Char(string='Expense Type')
    category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
    apr_budget = fields.Float('April Budget')
    may_budget = fields.Float('May Budget')
    jun_budget = fields.Float('June Budget')
    jul_budget = fields.Float('July Budget')
    aug_budget = fields.Float('Aug Budget')
    sep_budget = fields.Float('Sept Budget')
    oct_budget = fields.Float('Oct Budget')
    nov_budget = fields.Float('Nov Budget')
    dec_budget = fields.Float('Dec Budget')
    jan_budget = fields.Float('Jan Budget')
    feb_budget = fields.Float('Feb Budget')
    mar_budget = fields.Float('March Budget')
    total_budget = fields.Float('Total Budget Amount')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                WITH Project_Budget_CTE AS (
                SELECT 
                'Project Budget' as budget_type,
                work_order_type,
                fiscal_year_id,
                account_code_id,
                aa.code as account_code,
                aa.group_type as group_type_id,
                aa.group_name as group_name_id,
                aa.account_head_id,
                aa.account_sub_head_id,
                project_id,
                project_code,
                opportunity_name,
                client,
                order_value,
                head_expense_type as expense_type,
                category_id,
                null::int as department_id,
                null::int as division_id,
                null::int as section_id,
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
                SUM(mar_budget) AS mar_budget,
                SUM(apr_budget + may_budget + jun_budget + jul_budget + aug_budget + sep_budget + oct_budget + nov_budget + dec_budget + jan_budget + feb_budget + mar_budget) AS total_budget
            FROM 
                kw_sbu_project_budget_line 
            LEFT JOIN 
                kw_sbu_project_budget ON kw_sbu_project_budget_line.sbu_project_budget_id = kw_sbu_project_budget.id 
            LEFT JOIN 
                account_account aa ON kw_sbu_project_budget_line.account_code_id = aa.id 
                where kw_sbu_project_budget.state not in ('validate','cancel')
            GROUP BY 
                work_order_type,
                fiscal_year_id,
                account_code_id,
                project_id,
                project_code,
                opportunity_name,
                client,
                order_value,
                head_expense_type,
                category_id,
                aa.code,
                aa.group_type,
                aa.group_name,
                aa.account_head_id,
                aa.account_sub_head_id
),

Revenue_Budget_CTE AS (
                SELECT     
                'Treasury Budget' as budget_type,
                NULL as work_order_type,
                fiscal_year_id,
                account_code_id,
                aa.code as account_code,
                aa.group_type as group_type_id,
                aa.group_name as group_name_id,
                aa.account_head_id,
                aa.account_sub_head_id,
                null::int as project_id,
                null as project_code,
                NULL as opportunity_name,
                NULL as client,
                NULL as order_value,
                expense_type as expense_type,
                null::int as category_id,
                bdm.department_id,
                bdm.division_id,
                bdm.section_id,
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
                SUM(mar_budget) AS mar_budget,
                SUM(apr_budget + may_budget + jun_budget + jul_budget + aug_budget + sep_budget + oct_budget + nov_budget + dec_budget + jan_budget + feb_budget + mar_budget) AS total_budget 
            FROM 
                kw_revenue_budget_line 
            LEFT JOIN 
                kw_revenue_budget as rb ON kw_revenue_budget_line.revenue_budget_id = rb.id 
            LEFT JOIN 
                account_account aa ON kw_revenue_budget_line.account_code_id = aa.id
            LEFT JOIN 
                kw_budget_dept_mapping bdm ON rb.budget_department = bdm.id
                where rb.state not in ('validate','cancel')
            GROUP BY 
                fiscal_year_id,
                account_code_id,
                expense_type,
                aa.code,
                aa.group_type,
                aa.group_name,
                aa.account_head_id,
                aa.account_sub_head_id,
                bdm.department_id,
                bdm.division_id,
                bdm.section_id
    ),


        report_data as
        (
        SELECT * FROM Project_Budget_CTE
        UNION ALL
        SELECT * FROM Revenue_Budget_CTE
            )
        select row_number() OVER (order by account_code_id desc) AS id, 
        budget_type, work_order_type,fiscal_year_id,account_code_id,account_code,group_type_id,group_name_id,account_head_id,
        account_sub_head_id,project_id, project_code,opportunity_name, client,order_value,expense_type, 
        category_id, department_id, division_id,section_id,apr_budget,may_budget,jun_budget,jul_budget,aug_budget,
        sep_budget,oct_budget,nov_budget,dec_budget,jan_budget,feb_budget,mar_budget,total_budget
        from report_data
                )""" % (self._table))



