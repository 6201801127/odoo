from odoo import models, api, fields, tools

class ConsolidatedSBUProjectReport(models.Model):
    _name = "kw_consolidated_sbu_budget_report"
    _description = "Report For Consilidated SBU budget"
    _auto = False

    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_code_id.code', string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    sbu_name = fields.Char(string="SBU Name")
    project_id = fields.Many2one('project.project', string="Project Name")
    state = fields.Char(string='Pending At')
    project_name_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    expenses_type = fields.Char(string='Expense Type')
    project_name_code = fields.Char(string="Project Code")
    head_of_expense =  fields.Char(string='Head Of Expenses/Income')
    work_order_type =  fields.Char(string='Workorder Type')
    opp_name =  fields.Char(string='OPP Name')
    project_code =  fields.Char(string='Project Code')
    client =  fields.Char(string='Client')
    order_value =  fields.Char(string='Order value')
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
    total_budget = fields.Float('Total Budget Amount')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                select row_number() over(order by pbl.account_code_id desc) as id,pm.sbu_id as sbu_id,
                (SELECT name FROM kw_sbu_master WHERE id = pm.sbu_id) AS sbu_name,             
                pb.fiscal_year_id as fiscal_year_id,
                pbl.head_expense_type as expenses_type,
                CASE
                    WHEN pb.state = 'draft' THEN 'Yet to Apply'
                    WHEN pb.state = 'to_approve' THEN 'Pending with L2'
                    WHEN pb.state = 'approved' THEN 'Pending with Finance'
                    WHEN pb.state = 'confirm' THEN 'Pending For Approval'
                    WHEN pb.state = 'validate' THEN 'Budget Approved'
                    WHEN pb.state = 'cancel' THEN 'Cancel'
                ELSE '--'
                END AS state,
                pbl.head_of_expense as head_of_expense,
                pbl.work_order_type as work_order_type,
                pbl.opportunity_name as opp_name,
                pbl.order_code as project_code,
                pbl.client as client,
                pbl.order_id as project_id,
                pbl.project_id as project_name_id,
                pbl.project_code as project_name_code,
                pbl.order_value as order_value,
                pbl.category_id as category_id,
                pbl.account_code_id as account_code_id,
                pbl.apr_budget AS april_budget,
                pbl.may_budget AS may_budget,
                pbl.jun_budget AS june_budget,
                pbl.jul_budget AS july_budget,
                pbl.aug_budget AS august_budget,
                pbl.sep_budget AS september_budget,
                pbl.oct_budget AS october_budget,
                pbl.nov_budget AS november_budget,
                pbl.dec_budget AS december_budget,
                pbl.jan_budget AS january_budget,
                pbl.feb_budget AS february_budget,
                pbl.mar_budget AS march_budget,
                (pbl.apr_budget + pbl.may_budget + pbl.jun_budget + pbl.jul_budget + pbl.aug_budget + pbl.sep_budget + pbl.oct_budget + pbl.nov_budget + pbl.dec_budget + pbl.jan_budget + pbl.feb_budget + pbl.mar_budget) AS total_budget
                from kw_sbu_project_mapping pm
                left join kw_sbu_project_budget pb
                on pm.id =pb.budget_department
                left join kw_sbu_project_budget_line pbl on pbl.sbu_project_budget_id =pb.id
                where pb.state not in ('validate','cancel')
                )""" % (self._table))



