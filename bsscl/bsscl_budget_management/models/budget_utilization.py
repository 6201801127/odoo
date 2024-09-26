from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class BudgetUtalization(models.Model):
    _name = 'budget.utilization'
    _rec_name = 'budget_id'

    @api.depends('budget_utiliz_ids.expense', 'budget_utiliz_ids.revenue')
    def _tot_expense(self):
        if self.budget_utiliz_ids:
            sum_ex = sum_rev = 0.0
            for line in self.budget_utiliz_ids:
                sum_ex += line.expense
                sum_rev += line.revenue
            self.total_budget = sum_ex
            self.total_budget_rev = sum_rev

    # project_id = fields.Many2one('project.project', string="Project")
    budget_id = fields.Many2one('crossovered.budget', string="Budget")
    # coe_id = fields.Many2one('coe.setup.master', 'COE')
    budget_utiliz_ids = fields.One2many('budget.utilization.line', 'budget_untilized_id', string="Budget Utilization")
    budget_date = fields.Date("Date")
    total_budget = fields.Float("Budget Expense", compute='_tot_expense')
    total_budget_rev = fields.Float("Budget Revenue", compute='_tot_expense')


class BudgetUtalizationLine(models.Model):
    _name = 'budget.utilization.line'

    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')

    budget_untilized_id = fields.Many2one('budget.utilization', string="Budget Utilization")
    expense = fields.Float('Expense Description & Amount ')
    revenue = fields.Float('Revenue Description & Amount ')
    budget_line_date = fields.Date("Date")


class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], string="State", default='draft', track_visibility='onchange')
    bsscl_center_id = fields.Many2one('res.branch', 'Bsscl Center')
    # project_id = fields.Many2one('project.project', 'Project')
    general_budget_id = fields.Many2one('crossovered.budget.lines', 'Budgetary Position')
    plus_amount = fields.Monetary(string='Fund Amount', compute='_compute_plus_amount', store=True)
    budget_id = fields.Many2one('crossovered.budget', string="Budget")
    general_account_id = fields.Many2one('account.account', string='Account Code',
                                         readonly=False, domain=[('deprecated', '=', False)])
    investment_detail_id = fields.Many2one('investment.details', string='Partner')
    investors_ids = fields.Many2many('res.partner', string="Partners")
    investor_partner_id = fields.Many2one('res.partner', string="Partner")
    actual_general_budget_id = fields.Many2one('crossovered.budget.lines', 'Actual Budgetary Position')
    actual_general_account_id = fields.Many2one('account.account', string='Acutual Account Code',
                                                readonly=False, domain=[('deprecated', '=', False)])
    actual_investment_detail_id = fields.Many2one('investment.details', string='Partner')
    account_utilization_ids = fields.One2many('account.utilization', 'analytic_line_id', string="Fund Utilization Line")
    utilization_upload = fields.Binary('Upload', attachment=True)
    crossovered_budget_line = fields.One2many('crossovered.budget.lines', 'analytic_account_id', 'Budget Lines')
    # account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('budget_id')
    def onchange_accounts(self):
        for data in self:
            if data.budget_id:
                data.account_id = data.budget_id.analytic_account_id
                data.bsscl_center_id = data.budget_id.bsscl_center_id
            if not data.budget_id:
                data.account_id = ''
                data.bsscl_center_id = ''

    @api.onchange('general_budget_id')
    def onchange_general_budget_id(self):
        account_list = []
        budgetary = []
        account_ids = None
        for line in self.general_budget_id:
            if line.general_budget_id.account_ids:
                for account in line.general_budget_id.account_ids:
                    budgetary.append(account.id)
        if budgetary:
            account_ids = self.env['account.account'].search([('id', 'in', budgetary)])
        if account_ids:
            account_list = [account.id for account in account_ids]
        return {'domain': {'general_account_id': [('id', 'in', account_list)]}}

    @api.onchange('actual_general_budget_id')
    def onchange_actual_general_budget_id(self):
        account_list = []
        budgetary = []
        account_ids = None
        for line in self.actual_general_budget_id:
            if line.general_budget_id.account_ids:
                for account in line.general_budget_id.account_ids:
                    budgetary.append(account.id)
        if budgetary:
            account_ids = self.env['account.account'].search([('id', 'in', budgetary)])
        if account_ids:
            account_list = [account.id for account in account_ids]
        return {'domain': {'actual_general_account_id': [('id', 'in', account_list)]}}

    @api.onchange('budget_id', 'general_budget_id')
    def onchange_budget_lines(self):
        if self.budget_id and self.general_budget_id:
            investment_details = self.env['investment.details'].search([('bsscl_center_id', '=', self.bsscl_center_id.id)])
            self.account_utilization_ids = [(6, 0, [])]
            fund_lines_list = []
            if investment_details:
                for investment in investment_details:
                    declared, received, accounts = 0, 0, []
                    for line in investment.actual_investment_ids:
                        if line.budgetary_id == self.general_budget_id.general_budget_id:
                            declared += line.planned_amount
                            received += line.actual_amount_received
                            accounts = line.account_ids.ids
                    fund_utilize = self.env['account.analytic.line'].sudo().search([('bsscl_center_id', '=', self.bsscl_center_id.id),
                                                                                    ('budget_id', '=',
                                                                                     self.budget_id.id),
                                                                                    ('general_budget_id', '=',
                                                                                     self.general_budget_id.id),
                                                                                    ])
                    utilize = 0
                    if fund_utilize:
                        for fund in fund_utilize:
                            utilize += fund.amount
                    balance = received - utilize
                    fund_lines_list.append((0, 0, {
                        'company_id': self.env.user.company_id.id,
                        'partner_id': investment.investor_partner_id.id,
                        'account_ids': [(6, 0, [account for account in accounts])],
                        'declared_amount': declared,
                        'received_amount': received,
                        'utilized_amount': utilize,
                        'balance_amount': balance
                    }))
                self.account_utilization_ids = fund_lines_list

    # @api.onchange('budget_id')
    # def onchange_coe_id(self):
    #     if self.budget_id:
    #         self.coe_id = self.budget_id.coe_id.id
    #         self.project_id = self.budget_id.project_id.id
    #         self.account_id = self.budget_id.project_id.analytic_account_id.id

    @api.depends('amount')
    def _compute_plus_amount(self):
        for data in self:
            data.plus_amount = abs(data.amount)

    @api.onchange('general_account_id')
    def onchange_general_account_id(self):
        partner_list = []
        self.investors_ids = False
        self.investment_detail_id = False
        if self.general_account_id and self.account_utilization_ids:
            account_code = 0
            count = 0
            for line in self.account_utilization_ids:
                count += 1
                if self.general_account_id.id in line.account_ids.ids:
                    partner_list.append(line.partner_id.id)
                else:
                    account_code += 1
            if count == account_code:
                for line in self.account_utilization_ids:
                    partner_list.append(line.partner_id.id)
        res = {}
        if partner_list:
            investment_list = []
            for partner in partner_list:
                investment_detail = self.env['investment.details'].search(
                    [('bsscl_center_id', '=', self.bsscl_center_id.id)], limit=1)
                investment_list.append(investment_detail.id)

            if len(investment_list) == 1:
                res['domain'] = {'investment_detail_id': [('id', '=', investment_list)]}
                self.investment_detail_id = investment_list[0]
            else:
                res['domain'] = {'investment_detail_id': [('id', '=', investment_list)]}
            return res
        else:
            investment_list = []
            res['domain'] = {'investment_detail_id': [('id', '=', investment_list)]}

    # @api.onchange('general_account_id')
    # def onchange_general_account_id(self):
    #     partner_list = []
    #     self.investors_ids = False
    #     if self.general_account_id and self.account_utilization_ids:
    #         for line in self.account_utilization_ids:
    #             print('++++++++', self.general_account_id, '--', line.account_ids.ids)
    #             if self.general_account_id.id in line.account_ids.ids:
    #                 partner_list.append(line.partner_id.id)
    #     # if partner_list:
    #     #     self.investors_ids = [(6, 0, [partner for partner in partner_list])]
    #     domain = {'domain': {'investor_partner_id': [('id', '=', 1643)]}}
    #     return domain
    #     # if self.general_account_id.user_type_id.id == 16:
    #     #     self.amount = self.amount * -1

    @api.model
    def create(self, vals_list):
        amount = vals_list.get('amount', 0)
        res = super(AnalyticLine, self).create(vals_list)
        budget_id = self.env['crossovered.budget'].search([('bsscl_center_id', '=', res.bsscl_center_id.id)], limit=1)
        res.amount = amount
        res.budget_id = budget_id.id
        invest_amount = self.env['account.analytic.line'].search([('general_budget_id', '=', res.general_budget_id.id),
                                                                  (
                                                                  'general_account_id', '=', res.general_account_id.id),
                                                                  ('bsscl_center_id', '=', res.bsscl_center_id.id)])
        if len(invest_amount) == 1:
            if res.amount > 0.0:
                for lines in res.account_utilization_ids:
                    # if res.investment_detail_id.investor_partner_id.id == lines.partner_id.id:
                    if lines.balance_amount < res.amount:
                        raise UserError(_("Amount entered for utilization exceeds the remaining balance amount"))
        elif len(invest_amount) > 1:
            amount = 0
            for inve in invest_amount:
                amount += inve.amount
            receieved = 0
            for lines in res.account_utilization_ids:
                # if res.investment_detail_id.investor_partner_id.id == lines.partner_id.id:
                receieved = lines.received_amount
            if amount > receieved:
                raise UserError(_("Amount entered for utilization exceeds the remaining balance amount"))

        # print(invest_amount, '@@@@@@@@@@')
        # total_amount = 0.0
        # for amu in invest_amount:
        #     total_amount += amu.amount
        # print(total_amount, 'total')
        # total_amount = total_amount + res.amount
        # if total_amount > filter_records.actual_amount_received:
        #     raise UserError(_("Amount your trying to utilize exceeds the received amount !!"))
        return res

    def write(self, vals):
        res = super(AnalyticLine, self).write(vals)
        if 'amount' in vals:
            invest_amount = self.env['account.analytic.line'].search(
                [('general_budget_id', '=', self.general_budget_id.id),
                 ('general_account_id', '=', self.general_account_id.id),
                 ('bsscl_center_id', '=', self.bsscl_center_id.id)])
            if len(invest_amount) == 1:
                if self.amount > 0.0:
                    for lines in self.account_utilization_ids:
                        # if self.investment_detail_id.investor_partner_id.id == lines.partner_id.id:
                        if lines.balance_amount < self.amount:
                            raise UserError(
                                _("Amount entered for utilization exceeds the remaining balance amount"))
            elif len(invest_amount) > 1:
                amount = 0
                for inve in invest_amount:
                    amount += inve.amount
                receieved = 0
                for lines in self.account_utilization_ids:
                    # if self.investment_detail_id.investor_partner_id.id == lines.partner_id.id:
                    receieved = lines.received_amount
                if amount > receieved:
                    raise UserError(_("Amount entered for utilization exceeds the remaining balance amount"))

            # if self.amount > 0.0:
            #     for lines in self.account_utilization_ids:
            #         if self.investment_detail_id.investor_partner_id.id == lines.partner_id.id:
            #             if lines.balance_amount < self.amount:
            #                 raise UserError(_("Amount entered for utilization exceeds the remaining balance amount"))
        return res


    def confirm_utilization(self):
        if self.state == 'draft':
            self.state = 'confirm'

    # Hide edit button
    # edit_hide_css = fields.Html(string='CSS', sanitize=False, compute='_compute_edit_hide_css')
    #
    # @api.depends('state')
    # def _compute_edit_hide_css(self):
    #     for rec in self:
    #         if rec.state in ['confirm']:
    #             rec.edit_hide_css = '<style>.o_form_button_edit {display: none !important;}</style>'
    #         else:
    #             rec.edit_hide_css = False


class AccountUtilization(models.Model):
    _name = "account.utilization"

    analytic_line_id = fields.Many2one('account.analytic.line', string="Fund Line")
    company_id = fields.Many2one('res.company', string='Company', track_visibility='always', copy=False,
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    account_ids = fields.Many2many('account.account', string="Account Code")
    declared_amount = fields.Monetary("Declared Amount")
    received_amount = fields.Monetary("Received Amount")
    balance_amount = fields.Monetary("Balance Amount")
    utilized_amount = fields.Monetary("Utilized Amount")
