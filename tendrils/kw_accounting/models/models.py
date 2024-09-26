# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class AnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'

    project_id = fields.Many2one('crm.lead', 'Project')
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    branch_id = fields.Many2one('kw_res_branch', 'Branch')
    compute_balance = fields.Boolean('Compute Balance', compute='check_remaining_balance')
    budget_type = fields.Selection([('project', 'Project'), ('treasury', 'Treasury')], 'Budget Type')

    @api.constrains('project_id')
    def check_peoject_id(self):
        if not self._context.get('treasury'):
            for rec in self:
                project_rec = self.env['account.analytic.account'].sudo() \
                                  .search([('project_id', '=', rec.project_id.id)]) - self
                if project_rec:
                    raise ValidationError(f'{rec.project_id.name} is already tagged with {project_rec.name}!')

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        res['budget_type'] = 'treasury' if self._context.get('treasury') else 'project'
        return res

    def cost_account_analytic_line_action(self):
        view_id = self.env.ref("analytic.view_account_analytic_line_tree").id
        action = {
            'name': 'Costs',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': [('amount', '<', 0), ('account_id', '=', self.id)]
        }
        return action

    def revenue_account_analytic_line_action(self):
        view_id = self.env.ref("analytic.view_account_analytic_line_tree").id
        action = {
            'name': 'Revenue',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': [('amount', '>', 0), ('account_id', '=', self.id)]
        }
        return action

    def check_remaining_balance(self):
        for rec in self:
            for r in rec.crossovered_budget_line:
                if r.planned_amount:
                    r.write({'balance_amount': r.planned_amount - r.practical_amount})


class BudgetInherit(models.Model):
    _inherit = 'crossovered.budget'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])

    def apply_budget(self):
        for rec in self:
            rec.write({'state': 'to_approve'})
        return True


class BudgetLineInherit(models.Model):
    _inherit = 'crossovered.budget.lines'

    balance_amount = fields.Monetary('Balance Amount')
    date_from = fields.Date('Start Date', required=False)
    date_to = fields.Date('End Date', required=False)
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

    def _compute_theoritical_amount(self):
        return True

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                  'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget',
                  'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget')
    def calulate_total_planed_amount(self):
        if not self._context.get('non_treasury_budget'):
            for rec in self:
                rec.planned_amount = False
                rec.planned_amount = rec.apr_budget + rec.may_budget + rec.jun_budget + \
                                     rec.jul_budget + rec.aug_budget + rec.sep_budget + \
                                     rec.oct_budget + rec.nov_budget + rec.dec_budget + \
                                     rec.jan_budget + rec.feb_budget + rec.mar_budget


class Grouptype(models.Model):
    _name = "group_type"
    _description = "group_type"
    _rec_name = 'name'

    name = fields.Char(string="Name")


class Grouphead(models.Model):
    _name = "group_head"
    _description = "group_head"
    _rec_name = 'name'

    name = fields.Char(string="Name")


class AccountTaxInherit(models.Model):
    _inherit = 'account.tax'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')


class AccountFiscalPositionInherit(models.Model):
    _inherit = 'account.fiscal.position'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one('kw_res_branch', 'Branch')


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    kw_id = fields.Integer('KW ID')


class ProductInherit(models.Model):
    _inherit = 'product.product'

    kw_id = fields.Integer('KW ID')


# class KwAccountType(models.Model):
#     _name = 'kw_account_type'

#     name = fields.Char('Name')
#     code = fields.Char('Code')


class AccountGroupInherit(models.Model):
    _inherit = 'account.group'

    # account_type_id = fields.Many2one('kw_account_type')
    budget_type = fields.Selection([('project', 'Project'), ('treasury', 'Treasury')], 'Budget Type')

# class AccountingBranchUnit(models.Model):
# 	_name = 'accounting.branch.unit'

# 	name = fields.Char('Name')
# 	code = fields.Char('Code')
