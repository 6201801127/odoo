from odoo import models, api, fields, tools

class ProjectBudgetReport(models.Model):
    _name = "project_budget_report"
    _description = "Report For project budget"
    _auto = False

    account_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_id.code', string='Account Code')
    account_name = fields.Char(related='account_id.name', string='Account Name')
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name',string= 'Group Name')
    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    sbu_name = fields.Char(string="SBU Name")
    project_id = fields.Many2one('project.project', string="Project Name")
    order_code = fields.Char(string="Project Code")
    expense_type = fields.Char(string='Expense Type')
    project_name_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    project_code = fields.Char(string="Project Code")

    work_order_type = fields.Char(string="Work Order Type")
    opp_name = fields.Char(string="OPP Name")
    order_value = fields.Char(string="Order Value")
    client_name = fields.Char(string="Client Name")
    category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
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
    total_budget = fields.Float('Total Budget')

   
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (      
                select row_number() over() as id,
                kl.account_code_id AS account_id,
                ac.group_type as group_type_id,
                ac.group_name as group_id,
                ac.user_type_id as group_head_id,
                ac.account_head_id as account_head_id,
                ac.account_sub_head_id as account_sub_head_id,
                ks.fiscal_year_id AS fiscal_year_id,
                kbm.sbu_id AS sbu_id,
                (SELECT name FROM kw_sbu_master WHERE id = kbm.sbu_id) AS sbu_name,
                kl.order_id as project_id,
                kl.project_id as project_name_id,
                kl.project_code as project_code,
                kl.head_expense_type as expense_type,
                kl.order_code as order_code,
                kl.work_order_type as work_order_type,
                kl.opportunity_name as opp_name,
                kl.order_value as order_value,
                kl.client as client_name,
                kl.category_id as category_id,
                SUM(kl.apr_budget) AS april_budget,
                SUM(kl.may_budget) AS may_budget,
                SUM(kl.jun_budget) AS june_budget,
                SUM(kl.jul_budget) AS july_budget,
                SUM(kl.aug_budget) AS august_budget,
                SUM(kl.sep_budget) AS september_budget,
                SUM(kl.oct_budget) AS october_budget,
                SUM(kl.nov_budget) AS november_budget,
                SUM(kl.dec_budget) AS december_budget,
                SUM(kl.jan_budget) AS january_budget,
                SUM(kl.feb_budget) AS february_budget,
                SUM(kl.mar_budget) AS march_budget,
                SUM(kl.apr_budget + kl.may_budget + kl.jun_budget + kl.jul_budget + kl.aug_budget + kl.sep_budget + kl.oct_budget + kl.nov_budget + kl.dec_budget + kl.jan_budget + kl.feb_budget + kl.mar_budget) AS total_budget
                from
            kw_sbu_project_budget_line kl
            JOIN
                kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
            JOIN
                kw_sbu_project_mapping kbm ON ks.budget_department = kbm.id
            JOIN account_account ac on ac.id = kl.account_code_id
            GROUP BY
                kl.account_code_id,
                ks.fiscal_year_id,
                kl.order_id,
                kl.project_id,
                kl.project_code,
                kl.order_code,
                kl.head_expense_type,
                kl.work_order_type,
                kl.client,
                kl.opportunity_name,
                kl.order_value,
                kl.category_id,
                kbm.sbu_id,
                ac.group_name,
                ac.group_type,
                ac.user_type_id,
                ac.account_head_id,
                ac.account_sub_head_id
                )""" % (self._table))

