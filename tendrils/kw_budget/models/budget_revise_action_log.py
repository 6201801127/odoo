from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime


class ReviseBudgetActionlogCapital(models.Model):
    _name = 'kw_revise_budget_action_log'
    _description = "Capital Budget Log"

    name_of_expenses = fields.Char('Name of expenses')
    amount_required = fields.Float('Amount Required')
    revised_amount = fields.Float(string='Revise Amount')
    total_amount = fields.Float(string='Budget Amount')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    applied_by = fields.Char(string="Applied By")
    approver_by = fields.Char(string="Approved By")
    capital_budget_line_id = fields.Many2one('kw_capital_budget_line', 'Capital Budget Line', )
    capital_budget_id = fields.Many2one('kw_capital_budget', 'Capital Budget')
    state = fields.Char('Status')
    revise_budget_status = fields.Selection(string="Revise Budget Status",
                                            selection=[('applied', 'Applied'),
                                                       ('approved_by_l2', 'Approved By L2'),
                                                       ('reject_by_l2', 'Reject By L2'),
                                                       ('approved_by_approver', 'Approved By Approver'),
                                                       ('approved_by_finance', 'Approved By Finance'),
                                                       ('rejected_by_finance', 'Rejected By Finance'),
                                                       ('approved_by_cfo', 'Approved By Finance(CFO)'),
                                                       ('rejected_by_cfo', 'Rejected By Finance(CFO)'),
                                                       ('rejected_by_approver', 'Rejected By Approver')])


class ReviseBudgetActionlogRevenue(models.Model):
    _name = 'kw_revise_revenue_budget_action_log'
    _description = "Revenue Budget Log"

    name_of_expenses = fields.Char('Name of expenses')
    total_amount = fields.Float(string='Previous Amount')
    revise_amount = fields.Float(string='Revise Amount')
    total = fields.Float(string='Total Amount')
    date = fields.Date(string='Applied Date', default=fields.Date.context_today, required=True)
    approve_date = fields.Date(string='Approve Date')
    approver_by = fields.Char(string="Applied By")
    approve_by = fields.Char(string="Approve By")
    revenue_budget_line_id = fields.Many2one('kw_revenue_budget_line', 'Revenue Budget Line', )
    revenue_budget_id = fields.Many2one('kw_revenue_budget', 'Revenue Budget')
    state = fields.Char('Status')
    revised_amount = fields.Char(string='Revise Data')
    approved = fields.Boolean(string='Approved', default=False)
    currency_id = fields.Many2one('res.currency', related='revenue_budget_id.currency_id')
    revise_budget_status = fields.Selection(string="Revise Budget Status",
                                            selection=[('applied', 'Applied'),
                                                       ('approved_by_l2', 'Approved By L2'),
                                                       ('reject_by_l2', 'Reject By L2'),
                                                       ('approved_by_approver', 'Approved By Approver'),
                                                       ('approved_by_finance', 'Approved By Finance'),
                                                       ('rejected_by_finance', 'Rejected By Finance'),
                                                       ('approved_by_cfo', 'Approved By Finance(CFO)'),
                                                       ('rejected_by_cfo', 'Rejected By Finance(CFO)'),
                                                       ('rejected_by_approver', 'Rejected By Approver')])


class ReviseBudgetActionlogProject(models.Model):
    _name = 'kw_revise_sbu_project_budget_action_log'
    _description = "Sbu Project Budget Log"

    head_of_expense = fields.Char('Head of expenses')
    # order_code = fields.Many2one('project.project', 'Order code',required=True)
    total_amount = fields.Float(string='Budget Amount')
    date = fields.Date(string='Applied Date', default=fields.Date.context_today, required=True)
    approve_date = fields.Date(string='Approve Date')
    approver_by = fields.Char(string="Applied By")
    approve_by = fields.Char(string="Approve By")
    sbu_project_budget_line_id = fields.Many2one('kw_sbu_project_budget_line', 'Project Budget Line', )
    project_budget_id = fields.Many2one('kw_sbu_project_budget', 'SBU Project Budget')
    state = fields.Char('Status')
    revised_amount = fields.Char(string='Revise Data')
    approved = fields.Boolean(string='Approved', default=False)
    currency_id = fields.Many2one('res.currency', related='project_budget_id.currency_id')
    revise_budget_status = fields.Selection(string="Revise Budget Status",
                                            selection=[('applied', 'Applied'),
                                                       ('approved_by_l2', 'Approved By L2'),
                                                       ('reject_by_l2', 'Reject By L2'),
                                                       ('approved_by_cfo', 'Approved By Finance(CFO)'),
                                                       ('rejected_by_cfo', 'Rejected By Finance(CFO)'),
                                                       ('approved_by_approver', 'Approved By Approver'),
                                                       ('approved_by_finance', 'Approved By Finance'),
                                                       ('rejected_by_finance', 'Rejected By Finance'),
                                                       ('rejected_by_approver', 'Rejected By Approver')])
