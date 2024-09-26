from odoo import models, api, fields, tools

class ConsolidatedCapitalReport(models.Model):
    _name = "kw_consolidated_capital_budget_report"
    _description = "Report For Consilidated Capital budget"
    _auto = False

    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_code_id.code', string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    state = fields.Char(string='Pending At')
    remark =  fields.Text('Remark')
    date_from = fields.Date('Month Start')
    date_to = fields.Date('Month End')
    name_of_expenses =  fields.Char(string='Narration')
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
    next_fy_budget = fields.Float('Next Fy Budget')
    total_budget = fields.Float('Total Budget Amount')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            select row_number() over(order by cbl.account_code_id desc) as id,dm.department_id as department_id,
                cb.fiscal_year_id as fiscal_year_id,cbl.remark as remark,
                CASE
                    WHEN cb.state = 'draft' THEN 'Yet to Apply'
                    WHEN cb.state = 'to_approve' THEN 'Pending with L2'
                    WHEN cb.state = 'approved' THEN 'Pending with Finance'
                    WHEN cb.state = 'confirm' THEN 'Pending For Approval'
                    WHEN cb.state = 'validate' THEN 'Budget Approved'
                    WHEN cb.state = 'cancel' THEN 'Cancel'
                ELSE '--'
                END AS state,
                cbl.name_of_expenses as name_of_expenses,
                cbl.date_from as date_from,
                cbl.date_to as date_to,
                cbl.account_code_id as account_code_id,
                cbl.apr_budget AS april_budget,
                cbl.may_budget AS may_budget,
                cbl.jun_budget AS june_budget,
                cbl.jul_budget AS july_budget,
                cbl.aug_budget AS august_budget,
                cbl.sep_budget AS september_budget,
                cbl.oct_budget AS october_budget,
                cbl.nov_budget AS november_budget,
                cbl.dec_budget AS december_budget,
                cbl.jan_budget AS january_budget,
                cbl.feb_budget AS february_budget,
                cbl.mar_budget AS march_budget,
                cbl.next_fy_year AS next_fy_budget,
                (cbl.apr_budget + cbl.may_budget + cbl.jun_budget + cbl.jul_budget + cbl.aug_budget + cbl.sep_budget + cbl.oct_budget + cbl.nov_budget + cbl.dec_budget + cbl.jan_budget + cbl.feb_budget + cbl.mar_budget) AS total_budget
                from kw_budget_dept_mapping dm
                left join kw_capital_budget cb
                on dm.id =cb.budget_department
                left join kw_capital_budget_line cbl on cbl.capital_budget_id =cb.id 
                where cb.state not in ('validate','cancel')
                )""" % (self._table))



