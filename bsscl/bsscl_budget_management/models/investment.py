from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


# class CrossoveredBudget(models.Model):
#     _inherit = "crossovered.budget"
#
#     def find_declaration_amount(self):
#         for s in self:
#             total = 0
#             investment_ids = self.env['investment.details'].sudo().search([('coe_id', '=', s.coe_id.id)])
#             for inv_id in investment_ids:
#                 total += inv_id.total_investment
#             s.declaration_amount = total / 1000
#             s.investment_ids = [(6, 0, investment_ids.ids)]
#             s.declaration_char = str(s.declaration_amount) + ' K'
#
#
#     declaration_amount = fields.Float('Investment', store=True, compute='find_declaration_amount')
#     declaration_char = fields.Char('Investment', store=True, compute='find_declaration_amount')
#     investment_ids = fields.Many2many('investment.details', compute='find_declaration_amount', string='Investments')
#     currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
#
#     @api.depends('crossovered_budget_line', 'crossovered_budget_line.declaration_amount',
#                  'crossovered_budget_line.planned_amount',
#                  'crossovered_budget_line.practical_amount')
#     def _get_budget_amount(self):
#         for record in self:
#             dec_amount = 0
#             received_amount = 0
#             utilization_amount = 0
#             if record.crossovered_budget_line:
#                 for line in record.crossovered_budget_line:
#                     dec_amount += line.declaration_amount
#                     received_amount += line.planned_amount
#                     utilization_amount += line.practical_amount
#             record.dec_amount = dec_amount
#             record.planned_amount = received_amount
#             record.utilize_amount = utilization_amount
#
#     dec_amount = fields.Float('Declaration Amount', compute="_get_budget_amount")
#     planned_amount = fields.Float('Planned Amount', compute="_get_budget_amount")
#     utilize_amount = fields.Float('Utilization Amount', compute="_get_budget_amount")
#
#     @api.model
#     def get_import_templates(self):
#         return [{
#             'label': _('Export Template for Budget with Budget Lines'),
#             'template': '/gts_coe_project_budget/static/budget-with-budgetline-import.xls'
#         }]
#
#     @api.multi
#     def action_investment_button(self):
#         investment_ids = self.investment_ids
#         action = self.env.ref('gts_coe_project_budget.action_investment').read()[0]
#         if len(investment_ids) > 1:
#             action['domain'] = [('id', 'in', investment_ids.ids)]
#         elif len(investment_ids) == 1:
#             action['views'] = [(self.env.ref('gts_coe_project_budget.investment_form').id, 'form')]
#             action['res_id'] = investment_ids.ids[0]
#         else:
#             action['domain'] = [('id', 'in', investment_ids.ids)]
#         action['context'] = {'create': False, 'edit': False}
#         return action


# class CrossoveredBudgetLines(models.Model):
#     _inherit = "crossovered.budget.lines"
#
#     declaration_amount = fields.Monetary('Declaration Amount', compute='_compute_total_declaration_amount')
#
#     def _compute_total_declaration_amount(self):
#         for data in self:
#             amount = 0.0
#             details_ids = self.env['planned.investment.line'].search([('budgetary_id', '=', data.general_budget_id.id),
#                                                                       ('investment_id.coe_id', '=',
#                                                                        data.crossovered_budget_id.coe_id.id)])
#             for investment in details_ids:
#                 amount += investment.planned_amount
#             data.declaration_amount = amount


class Investment(models.Model):
    _name = 'investment.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Investment Details'
    _rec_name = 'number'

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.depends('actual_investment_ids', 'actual_investment_ids.actual_amount_received')
    def _find_total_investment(self):
        for rec in self:
            total = 0.0
            for line in rec.actual_investment_ids:
                total += line.actual_amount_received
            rec.total_rev = total

    @api.depends('total_investment', 'total_rev')
    def _find_investment_percentage(self):
        for s in self:
            if s.total_investment > 0 and s.total_rev:
                s.percent_rev = (s.total_rev / s.total_investment) * 100

    def name_get(self):
        res = []
        for record in self:
            if record.investor_partner_id:
                name = record.investor_partner_id.name
                res.append((record.id, name))
        return res


    state = fields.Selection([
        ('draft', 'Draft'),
        ('wip', 'Waiting For Approval'),
        ('approved', 'Approved'),
        ('confirm', 'In-Progress'),
        ('cancel', 'Closed')
    ], string='Status', default='draft', track_visibility='onchange')
    name = fields.Char(string='Description', required=True, track_visibility='onchange')
    inv_type = fields.Many2one('investment.master', states=READONLY_STATES, string='Investor Type')
    budgetary_id = fields.Many2one('account.budget.post', states=READONLY_STATES, string='Budget Head')
    funded_by = fields.Selection([('investor', 'Investor'), ('partner', 'Partner'), ], string='Funded By',
                                 states=READONLY_STATES, default='investor')
    investor_partner_id = fields.Many2one('res.partner', string='Partner', states=READONLY_STATES,
                                          track_visibility='onchange')
    # partner_type_new = fields.Selection(related='investor_partner_id.partner_type_new')
    total_investment = fields.Float(string='Investment Declaration', track_visibility='onchange')
    # coe_id = fields.Many2one('coe.setup.master', string='COE name', states=READONLY_STATES, )
    bsscl_center_id = fields.Many2one('res.branch', string='Bsscl Center', states=READONLY_STATES, )
    fund_rev = fields.Float(string='Fund Received', states=READONLY_STATES, )
    date_funding = fields.Date(string='Date of Funding', states=READONLY_STATES, )
    next_date_funding = fields.Date(string='Next Funding Date', states=READONLY_STATES, )
    upload = fields.Binary(string='Upload File', attachment=True)
    upload_dec = fields.Char(string='Upload Description', track_visibility='onchange')
    number = fields.Char('Ref#', copy=False, default=lambda self: _('/'), readonly=True)
    fname = fields.Char(string="File Name", copy=False)
    total_rev = fields.Float(string='Total Received', store=True, compute='_find_total_investment')
    percent_rev = fields.Float(string='Received%', store=True, compute='_find_investment_percentage', group_operator=False)
    partner_view_type = fields.Selection([('implementation', 'Implementation Partner'),
                                          ('academic', 'Academic Partner'),
                                          ('technical', 'Technical Partner'),
                                          ('funding', 'Funding Partner'),
                                          ('knowledge', 'Knowledge Partner'),
                                          ('association', 'Industry Association'),
                                          ('industry', 'Industry Partner'),
                                          ], default='funding', string="Partner Type", states=READONLY_STATES,
                                         track_visibility='onchange')
    funding_type = fields.Selection([('new_investment', 'New Investment'),('re_investment', 'Re-Investment'),
                                     ], default='new_investment', string="Funding Type", states=READONLY_STATES,)
    funding_ref = fields.Many2one('investment.details', string="Funding Reference", states=READONLY_STATES,)
    history_ids = fields.One2many('investment.details.line', 'investment_id', 'Funding History')

    planned_investment_ids = fields.One2many('planned.investment.line', 'investment_id', 'Planned Investment')
    actual_investment_ids = fields.One2many('actual.investment.received.line', 'investment_id', 'Planned Investment')
    planned_amount_compute = fields.Float("Planned amount", compute='find_planned_amount')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)


    # @api.model
    # def get_import_templates(self):
    #     return [{
    #         'label': _('Export Template for Investment with Disbursement Lines'),
    #         'template': '/gts_coe_project_budget/static/investment.disbursement.xls'
    #     }]

    @api.depends('planned_investment_ids.planned_amount', 'total_investment')
    def find_planned_amount(self):
        amount = 0
        self.planned_amount_compute = amount
        if self.planned_investment_ids:
            for line in self.planned_investment_ids:
                amount += line.planned_amount
            self.planned_amount_compute = amount
            if self.total_investment < self.planned_amount_compute:
                raise UserError(_("Planned Amount can't be exceed than Investment Declaration."))




    def action_send_approval(self):
        self.state = 'wip'

    def action_approve(self):
        self.state = 'approved'


    def action_budget_button(self):
        budget_id = self.env['crossovered.budget'].search([('bsscl_center_id', '=', self.bsscl_center_id.id)], limit=1)
        action = self.env.ref('bsscl_budget_management.act_crossovered_budget_view_2').read()[0]
        if budget_id:
            action['domain'] = [('id', 'in', budget_id.id)]
            action['res_id'] = budget_id.id
        action['views'] = [(self.env.ref('bsscl_budget_management.crossovered_budget_view_form').id, 'form')]
        # action['context'] = {'default_coe_id': self.coe_id.id,}

        return action

    def action_set_draft(self):
        self.state = 'draft'

    # @api.onchange('coe_id')
    # def find_on_onchange(self):
    #
    #     self.stpi_loc = self.coe_id.stpi_location_id.id

    # @api.onchange('funding_type', 'funding_ref')
    # def find_investment_details(self):
    #     if self.funding_type == 're_investment' and self.funding_ref:
    #         self.investor_partner_id = self.funding_ref.investor_partner_id.id
    #         self.partner_view_type = self.funding_ref.partner_view_type
    #         self.budgetary_id = self.funding_ref.budgetary_id.id
    #         self.name = self.funding_ref.name
    #         self.coe_id = self.funding_ref.coe_id.id
    #         self.stpi_loc = self.funding_ref.stpi_loc.id
    #         self.total_investment = self.funding_ref.total_investment
    #         self.upload_dec = self.funding_ref.upload_dec
    #         self.upload = self.funding_ref.upload


    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('investment.request.seq') or _('')
        vals['number'] = number
        res = super(Investment, self).create(vals)
        return res



    def action_confirm(self):
        self.state = 'confirm'

    # def action_confirm(self):
    #     for record in self:
    #         count = 0
    #         budget_id = None
    #         # self.number = self.env['ir.sequence'].next_by_code('investment.request.seq') or _('')
    #         budget_id = self.env['crossovered.budget'].search(
    #             [('state', 'in', ['draft', 'confirm']), ('coe_id', '=', self.coe_id.id)], limit=1)
    #         if budget_id:
    #             for line in budget_id.crossovered_budget_line:
    #                 if line.general_budget_id == self.budgetary_id:
    #                     count = 1
    #                     line.write({'planned_amount': line.planned_amount + self.fund_rev})
    #             if count == 0:
    #                 line = self.env['crossovered.budget.lines'].create({
    #                     'general_budget_id': self.budgetary_id.id,
    #                     'date_from': budget_id.date_from,
    #                     'date_to': budget_id.date_to,
    #                     'planned_amount': self.fund_rev,
    #                     'analytic_account_id': budget_id.project_id.analytic_account_id.id,
    #                     'crossovered_budget_id': budget_id.id
    #                 })
    #         record.state = 'confirm'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'


class PlannedInvestmentLine(models.Model):
    _name = 'planned.investment.line'
    _rec_name = 'planned_investment_code'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.depends('investment_id.total_investment','planned_amount')
    def find_total_amount_percent(self):
        for rec in self:
            if rec.investment_id.total_investment > 0:
                rec.total_amount = (rec.planned_amount/rec.investment_id.total_investment) * 100

    investment_id = fields.Many2one('investment.details', 'Investment')
    planned_investment_code = fields.Char("Planned Investment Code")
    account_ids = fields.Many2many('account.account', string="Account head")
    budgetary_id = fields.Many2one('account.budget.post',  string='Budget Head')
    planned_amount = fields.Float("Planned Amount")
    total_amount = fields.Float("Percent Of Total Amount", store=True, compute='find_total_amount_percent', )
    planned_date = fields.Date("Planned Date of Disbursement")
    intended_utilization = fields.Text("Intended Utilization")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    # # @api.constrains('planned_amount')
    # @api.onchange('planned_amount')
    # def find_total_planned_investment(self):
    #
    #     print("================= in onchange=====", self.investment_id.total_investment)
    #     print("================ids====", self.investment_id.planned_investment_ids)
    #     if self.investment_id.planned_investment_ids:
    #         amount = 0
    #         for line in self.investment_id.planned_investment_ids:
    #             amount += line.planned_amount
    #             print("=========amount================", amount)
    #         if self.investment_id.total_investment < amount:
    #             raise UserError(_("Planned Amount can't be exceed Total Planned Amount."))



    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('planned.investment.seq') or _('')
        vals['planned_investment_code'] = number
        res = super(PlannedInvestmentLine, self).create(vals)
        return res

    @api.onchange('budgetary_id')
    def budgetary_onchange(self):
        if self.budgetary_id:
            account_list = []
            budgetary = []
            account_ids= None
            for line in self.budgetary_id:
                if line.account_ids:
                    for account in line.account_ids:
                        budgetary.append(account.id)
            if budgetary:
                account_ids = self.env['account.account'].search([('id', 'in', budgetary)])
            if account_ids:
                account_list = [account.id for account in account_ids]
            return {'domain': {'account_ids': [('id', 'in', account_list)]}}


class ActualInvestmentReceivedLine(models.Model):
    _name = 'actual.investment.received.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'investment_code'

    @api.depends('investment_id.total_investment', 'actual_amount_received')
    def find_actual_amount_percent(self):
        for rec in self:
            if rec.investment_id.total_investment > 0:
                rec.actual_amount = (rec.actual_amount_received / rec.investment_id.total_investment) * 100

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    investment_id = fields.Many2one('investment.details', 'Investment')
    investment_code = fields.Char("Actual Investment Code")
    account_ids = fields.Many2many('account.account', string="Account head")
    budgetary_id = fields.Many2one('account.budget.post', string='Budget Head')
    planned_investment_code_id = fields.Many2one('planned.investment.line', "Planned Investment Code")
    planned_amount = fields.Float("Planned Amount")
    actual_amount_received = fields.Float("Actual Amount Received")
    total_amount = fields.Float("Percent Of Total Amount")
    actual_amount = fields.Float("Percent Of Received Amount", store=True, compute='find_actual_amount_percent')
    planned_date = fields.Date("Planned Date of Disbursement")
    actual_date = fields.Date("Actual Date of Disbursement")
    intended_utilization = fields.Char("Intended Utilization")
    time_deviation  = fields.Float("Time Deviation In Months", store=True, compute='find_time_deviation')
    upload_utilization = fields.Binary("Upload Utilization Certificate") #uc
    utilization_amount = fields.Float("Utilization Amount") # amount
    partner_id = fields.Many2one(related='investment_id.investor_partner_id',String="Partner",store=True)
    bsscl_center_id = fields.Many2one(related='investment_id.bsscl_center_id',String="Bsscl Center",store=True)
    declaration_amount = fields.Float(related='investment_id.total_investment', store=True,)

    @api.onchange('actual_amount_received')
    def actual_amount_received_onchange(self):
        print("============ innnnn===================")
        if self.actual_amount_received > self.planned_amount:
            raise UserError(_("Actual Amount Received can't be exceed than Planned Amount."))


    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('actual.investment.seq') or _('')
        vals['investment_code'] = number
        res = super(ActualInvestmentReceivedLine, self).create(vals)
        return res

    @api.onchange('actual_date')
    def find_time_deviation(self):
        for rec in self:
            if rec.actual_date and rec.planned_date:
                if rec.actual_date > rec.planned_date:
                    date = (rec.actual_date - rec.planned_date).days
                    rec.time_deviation = date / 30
                if rec.planned_date > rec.actual_date :
                    date = (rec.planned_date - rec.actual_date).days
                    rec.time_deviation = date/30

    @api.onchange('planned_investment_code_id')
    def find_details(self):
        if self.planned_investment_code_id:
            self.planned_amount = self.planned_investment_code_id.planned_amount
            self.total_amount = self.planned_investment_code_id.total_amount
            self.planned_date = self.planned_investment_code_id.planned_date
            self.budgetary_id = self.planned_investment_code_id.budgetary_id.id
            self.account_ids = [(6,0,self.planned_investment_code_id.account_ids.ids)]


    @api.onchange('budgetary_id')
    def budgetary_onchange(self):
        if self.budgetary_id:
            account_list = []
            budgetary = []
            account_ids = None
            for line in self.budgetary_id:
                if line.account_ids:
                    for account in line.account_ids:
                        budgetary.append(account.id)
            if budgetary:
                account_ids = self.env['account.account'].search([('id', 'in', budgetary)])
            if account_ids:
                account_list = [account.id for account in account_ids]
            return {'domain': {'account_ids': [('id', 'in', account_list)]}}

    def approve_investment(self):
        for record in self:
            count = 0
            budget_id = None
            budget_id = self.env['crossovered.budget'].search(
                [('state', 'in', ['draft', 'confirm']), ('coe_id', '=', record.investment_id.coe_id.id)], limit=1)
            # if budget_id:
            #     for line in budget_id.crossovered_budget_line:
            #         if line.general_budget_id == self.budgetary_id:
            #             count = 1
            #             line.write({'planned_amount': line.planned_amount + record.actual_amount})
            #     if count == 0:
            #         line = self.env['crossovered.budget.lines'].create({
            #             'general_budget_id': self.budgetary_id.id,
            #             'date_from': budget_id.date_from,
            #             'date_to': budget_id.date_to,
            #             'planned_amount': record.actual_amount,
            #             'analytic_account_id': budget_id.project_id.analytic_account_id.id,
            #             'crossovered_budget_id': budget_id.id
            #         })
            record.state = 'confirm'


class InvestmentLine(models.Model):
    _name = 'investment.details.line'
    _order = 'date desc'

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    name=fields.Char('Investment Description', states=READONLY_STATES)
    investment_id = fields.Many2one('investment.details', 'Investment', states=READONLY_STATES)
    amount = fields.Float('Investment Amount', states=READONLY_STATES)
    date = fields.Date("Investment Date", states=READONLY_STATES)
    budgetary_id = fields.Many2one('account.budget.post', states=READONLY_STATES, string='Budget Head', required=True)
    account_ids = fields.Many2many('account.account', string="Account head")



    @api.onchange('budgetary_id')
    def budgetary_onchange(self):
        if self.budgetary_id:
            account_list = []
            budgetary = []
            account_ids = None
            for line in self.budgetary_id:
                if line.account_ids:
                    for account in line.account_ids:
                        budgetary.append(account.id)
            if budgetary:
                account_ids = self.env['account.account'].search([('id', 'in', budgetary)])
            if account_ids:
                account_list = [account.id for account in account_ids]
            return {'domain': {'account_ids': [('id', 'in', account_list)]}}



    def approve_investment(self):
        for record in self:
            count = 0
            budget_id = None
            budget_id = self.env['crossovered.budget'].search(
                [('state', 'in', ['draft', 'confirm']), ('coe_id', '=', record.investment_id.coe_id.id)], limit=1)
            if budget_id:
                for line in budget_id.crossovered_budget_line:
                    if line.general_budget_id == self.budgetary_id:
                        count = 1
                        line.write({'planned_amount': line.planned_amount + record.amount})
                if count == 0:
                    line = self.env['crossovered.budget.lines'].create({
                        'general_budget_id': self.budgetary_id.id,
                        'date_from': budget_id.date_from,
                        'date_to': budget_id.date_to,
                        'planned_amount': record.amount,
                        'analytic_account_id': budget_id.project_id.analytic_account_id.id,
                        'crossovered_budget_id': budget_id.id
                    })
            record.state = 'confirm'


