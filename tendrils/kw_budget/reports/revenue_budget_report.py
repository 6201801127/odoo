from odoo import models, api, fields, tools

class RevenueReport(models.Model):
    _name = "revenue_budget_report"
    _description = "Report For revenue budget"
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
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    expense_type = fields.Char(string='Expense Type')
    april_budget = fields.Float('Apr Budget')
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
    total_budget = fields.Float('Total Buget Amount')

    # @api.depends('april_budget', 'may_budget', 'june_budget', 'july_budget',
    #              'august_budget', 'september_budget', 'october_budget', 
    #              'november_budget', 'december_budget', 'january_budget', 
    #              'february_budget', 'march_budget')
    # def compute_total_planed_amount(self):
    #     for rec in self:
    #         rec.total_budget = rec.april_budget + rec.may_budget + rec.june_budget + \
    #                           rec.july_budget + rec.august_budget + rec.september_budget + \
    #                           rec.october_budget + rec.november_budget + rec.december_budget + \
    #                           rec.january_budget + rec.february_budget + rec.march_budget

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
                kr.fiscal_year_id AS fiscal_year_id,
                kl.expense_type as expense_type,
                kbm.department_id AS department_id,
                kbm.division_id AS division_id,
				kbm.section_id AS section_id,
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
            FROM
                kw_revenue_budget_line kl
            JOIN
                kw_revenue_budget kr ON kl.revenue_budget_id = kr.id
            JOIN
                kw_budget_dept_mapping kbm ON kr.budget_department = kbm.id
            JOIN account_account ac on ac.id = kl.account_code_id
            where kr.state = 'validate' AND kl.state = 'validate'
            GROUP BY
                kl.account_code_id,
                kr.fiscal_year_id,
                kbm.department_id,
                kbm.division_id,
                kl.expense_type,
				kbm.section_id,
                ac.group_name,
				ac.group_type,
				ac.user_type_id,
				ac.account_head_id,
                ac.account_sub_head_id
                )""" % (self._table))

    def open_revenue_report_view(self):
        record = []
        data = self.env['kw_revenue_budget_line'].search([])
        for rec in data:
            if rec.account_code_id == self.account_id and rec.revenue_budget_id.fiscal_year_id == self.fiscal_year_id and rec.revenue_budget_id.budget_department.department_id == self.department_id:
                record.append(rec.id)
        action = {
            'name': 'Revenue Budget Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'kw_revenue_budget_line',
            'domain':[('id', 'in', record)],
            'target': 'self',
            'context':{'no_create_edit':False, 'delete':False}
        }
        return action


