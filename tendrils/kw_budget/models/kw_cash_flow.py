from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError

class BudgetCashFlow(models.Model):
    _name = 'kw_cash_flow'
    _description = "Cash Flow"
    _rec_name = 'fiscal_year_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal


    fiscal_year_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', default=_default_financial_yr, required=True,
                                     track_visibility='always')
    capital_flow_line_ids = fields.One2many('kw_cash_flow_capital', 'cash_flow_id', string="Capital-B/S Items")
    revenue_flow_line_ids = fields.One2many('kw_cash_flow_revenue', 'cash_flow_id', string="Revenue-B/S Items")
    project_flow_line_ids = fields.One2many('kw_cash_flow_project', 'cash_flow_id', string="Project-B/S Items")

    # _sql_constraints = [
    #     ('unique_fiscal_year', 'UNIQUE(fiscal_year_id)', 'Each record must have a unique fiscal year.')
    # ]

    @api.constrains('fiscal_year_id')
    def _check_unique_fiscal_year(self):
        for record in self:
            if self.search_count([('fiscal_year_id', '=', record.fiscal_year_id.id)]) > 1:
                raise ValidationError("This fiscal year already exists.")


class CapitalBudgetCashFlow(models.Model):
    _name = 'kw_cash_flow_capital'
    _description = "Cash Flow Capital Budget"

    capital_budget_item = fields.Char( string="Budget Item")
    name_of_expense = fields.Char('Receipts/Payments')
    name = fields.Char(string="Name")
    account_code_id = fields.Many2one('account.account', string="Account Code")
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    total = fields.Float('Total' , compute='get_total_amount')
    cash_flow_id = fields.Many2one('kw_cash_flow')

    @api.depends('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget', 'dec_budget',
                 'jan_budget', 'feb_budget', 'mar_budget')
    def get_total_amount(self):
        for rec in self:
            rec.total = (rec.apr_budget + rec.may_budget + rec.jun_budget +
                         rec.jul_budget + rec.aug_budget + rec.sep_budget + rec.oct_budget +
                         rec.nov_budget + rec.dec_budget + rec.jan_budget + rec.feb_budget +
                         rec.mar_budget)



class RevenueBudgetCashFlow(models.Model):
    _name = 'kw_cash_flow_revenue'
    _description = "Cash Flow Revenue Budget"

    revenue_budget_item = fields.Char(string="Budget Item")
    name_of_expense = fields.Char('Receipts/Payments')
    name = fields.Char(string="Name")
    account_code_id = fields.Many2one('account.account', string="Account Code")
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    total = fields.Float('Total' , compute='get_total_amount')
    cash_flow_id = fields.Many2one('kw_cash_flow')

    @api.depends('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget', 'dec_budget',
                 'jan_budget', 'feb_budget', 'mar_budget')
    def get_total_amount(self):
        for rec in self:
            rec.total = (rec.apr_budget  + rec.may_budget + rec.jun_budget +
                          rec.jul_budget + rec.aug_budget + rec.sep_budget + rec.oct_budget +
                          rec.nov_budget + rec.dec_budget + rec.jan_budget + rec.feb_budget +
                          rec.mar_budget)




class ProjectBudgetCashFlow(models.Model):
    _name = 'kw_cash_flow_project'
    _description = "Cash Flow Project Budget"

    project_budget_item = fields.Char(string="Budget Item")
    name_of_expense = fields.Char('Receipts/Payments')
    name = fields.Char(string="Name")
    account_code_id = fields.Many2one('account.account', string="Account Code")
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    total = fields.Float('Total', compute='get_total_amount')
    cash_flow_id = fields.Many2one('kw_cash_flow')

    @api.depends('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget', 'dec_budget',
                 'jan_budget', 'feb_budget', 'mar_budget')
    def get_total_amount(self):
        for rec in self:
            rec.total = (rec.apr_budget + rec.may_budget + rec.jun_budget +
                         rec.jul_budget + rec.aug_budget + rec.sep_budget + rec.oct_budget +
                         rec.nov_budget + rec.dec_budget + rec.jan_budget + rec.feb_budget +
                         rec.mar_budget)





