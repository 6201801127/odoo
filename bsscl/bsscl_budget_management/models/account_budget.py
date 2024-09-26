from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Name', required=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', 'Accounts',
                                   domain=[('deprecated', '=', False)])
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'account.budget.post'))
    active = fields.Boolean('Active', default=True)

    # def _check_account_ids(self, vals):
    #     # Raise an error to prevent the account.budget.post to have not specified account_ids.
    #     # This check is done on create because require=True doesn't work on Many2many fields.
    #     if 'account_ids' in vals:
    #         account_ids = self.resolve_2many_commands('account_ids', vals['account_ids'])
    #     else:
    #         account_ids = self.account_ids
    #     if not account_ids:
    #         raise ValidationError(_('The budget must have at least one account.'))

    @api.model
    def create(self, vals):
        print(vals, '*******')
        # self._check_account_ids(vals)
        if not vals['account_ids']:
            raise ValidationError(_('The budget must have at least one account.'))
        return super(AccountBudgetPost, self).create(vals)

    def write(self, vals):
        if not vals['account_ids']:
            raise ValidationError(_('The budget must have at least one account.'))
        return super(AccountBudgetPost, self).write(vals)


class CrossoveredBudget(models.Model):
    _name = "crossovered.budget"
    _description = "Fund/Budget Management"
    _inherit = ['mail.thread']

    name_seq = fields.Char(string='Budget Sequence', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    name = fields.Char('Budget Name', required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user,
                              oldname='creating_user_id')
    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    crossovered_budget_line = fields.One2many('crossovered.budget.lines', 'crossovered_budget_id', 'Budget Lines',
                                              states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'account.budget.post'))
    # project_id = fields.Many2one('project.project', string="Project")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    bsscl_center_id = fields.Many2one('res.branch', string='Bsscl Center')
    # service_loc = fields.Many2one('coe.service.location', string='Project Location')
    # coe_id = fields.Many2one('coe.setup.master', 'COE')
    color = fields.Integer(string='Color Index')
    utilization_certificate = fields.Binary("Utilization Certificate")

    # @api.onchange('coe_id')
    # def onchange_coe_id_line(self):
    #     if self.coe_id:
    #         if not self.coe_id.project_id:
    #             raise UserError(_("Please Map Project For This COE"))
    #         self.project_id = self.coe_id.project_id.id
    #         self.service_loc = self.coe_id.project_id.service_loc.id
    #         self.stpi_loc = self.coe_id.project_id.stpi_loc.id
    #         self.date_from = self.coe_id.project_id.start_date
    #         self.date_to = self.coe_id.project_id.end_date
    #         self.crossovered_budget_line = None
    #         budget_unique = []
    #         line_ids = self.env['investment.details'].search(
    #             [('coe_id', '=', self.coe_id.id), ('state', '=', 'confirm')])
    #         vals_list = []
    #         for line_id in line_ids:
    #             if line_id.budgetary_id not in budget_unique:
    #                 budget_unique.append(line_id.budgetary_id)
    #         for budget_id in budget_unique:
    #             amount = 0
    #             vals = {}
    #             all_budget = line_ids.filtered(lambda bl: bl.budgetary_id == budget_id) or None
    #             for line in all_budget:
    #                 amount += line.fund_rev
    #             for line in all_budget:
    #                 vals = {
    #                     'general_budget_id': line.budgetary_id.id,
    #                     'date_from': self.date_from if self.date_from else None,
    #                     'date_to': self.date_to if self.date_to else None,
    #                     'planned_amount': amount,
    #                     'crossovered_budget_id': self.id
    #                 }
    #                 vals_list.append(vals)
    #                 break
    #         self.crossovered_budget_line = vals_list

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('crossovered.budget.seq') or _('New')
        result = super(CrossoveredBudget, self).create(vals)
        return result

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})

    @api.onchange('crossovered_budget_line')
    def crossovered_budget_line_change(self):
        for data in self.crossovered_budget_line:
            data.analytic_account_id = self.analytic_account_id.id


class CrossoveredBudgetLines(models.Model):
    _name = "crossovered.budget.lines"
    _description = "Fund/Budget Management"

    name = fields.Char(compute='_compute_line_name')
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True,
                                            required=True)
    # coe_id = fields.Many2one('coe.setup.master', 'Analytic Group',
    #                                     related='crossovered_budget_id.coe_id', readonly=True, store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', related="crossovered_budget_id.analytic_account_id")
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group',
                                        related='analytic_account_id.group_id', readonly=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    paid_date = fields.Date('Paid Date')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    planned_amount = fields.Monetary(
        'Received  Amount', compute='_compute_total_received_amount',
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Utilization Amount', help="Amount really earned/spent.")
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount', string='Theoretical Amount',
        help="Amount you are supposed to have earned/spent at this date.")
    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement (%)',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    crossovered_budget_state = fields.Selection(related='crossovered_budget_id.state', string='Budget State',
                                                store=True, readonly=True)
    position_ids = fields.One2many('account.analytic.line', 'general_budget_id', string='Budgetary Position Lines')
    tot_amount = fields.Float('Total Amount', compute='_compute_total_amount')

    declaration_amount = fields.Monetary('Declaration Amount', compute='_compute_total_declaration_amount')

    def _compute_total_declaration_amount(self):
        for data in self:
            amount = 0.0
            details_ids = self.env['planned.investment.line'].search([('budgetary_id', '=', data.general_budget_id.id),
                                                                      ('investment_id.bsscl_center_id', '=',
                                                                       data.crossovered_budget_id.bsscl_center_id.id)])
            for investment in details_ids:
                amount += investment.planned_amount
            data.declaration_amount = amount

    # declaration_amount = fields.Monetary('Declaration Amount', compute='_compute_total_declaration_amount')


    # def _compute_total_declaration_amount(self):
    #     for data in self:
    #         amount=0.0
    #         details_ids = self.env['investment.details'].search([('budgetary_id','=',data.general_budget_id.id),
    #                                                              ('coe_id', '=', data.crossovered_budget_id.coe_id.id)])
    #         for investment in details_ids:
    #             amount+=investment.total_investment
    #         data.declaration_amount = amount


    # def _compute_total_declaration_amount(self):
    #     for data in self:
    #         amount=0.0
    #         details_ids = self.env['planned.investment.line'].search([('budgetary_id','=',data.general_budget_id.id),
    #                                                                   ('investment_id.coe_id', '=', data.crossovered_budget_id.coe_id.id)])
    #         for investment in details_ids:
    #             amount+=investment.planned_amount
    #         data.declaration_amount = amount


    def _compute_total_received_amount(self):
        for data in self:
            amount=0.0
            details_ids = self.env['actual.investment.received.line'].search([('budgetary_id','=',data.general_budget_id.id),
                                                                            ('investment_id.bsscl_center_id', '=', data.crossovered_budget_id.bsscl_center_id.id)])
            for investment in details_ids:
                amount+=investment.actual_amount_received
            data.planned_amount = amount



    def _compute_total_amount(self):
        for data in self.position_ids:
            self.tot_amount += data.plus_amount

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group

        result = super(CrossoveredBudgetLines, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                                orderby=orderby, lazy=lazy)
        fields_list = ['practical_amount', 'theoritical_amount', 'percentage']
        if any(x in fields for x in fields_list):
            for group_line in result:

                # initialise fields to compute to 0 if they are requested
                if 'practical_amount' in fields:
                    group_line['practical_amount'] = 0
                if 'theoritical_amount' in fields:
                    group_line['theoritical_amount'] = 0
                if 'percentage' in fields:
                    group_line['percentage'] = 0
                    group_line['practical_amount'] = 0
                    group_line['theoritical_amount'] = 0

                if group_line.get('__domain'):
                    all_budget_lines_that_compose_group = self.search(group_line['__domain'])
                else:
                    all_budget_lines_that_compose_group = self.search([])
                for budget_line_of_group in all_budget_lines_that_compose_group:
                    if 'practical_amount' in fields or 'percentage' in fields:
                        group_line['practical_amount'] += budget_line_of_group.practical_amount

                    if 'theoritical_amount' in fields or 'percentage' in fields:
                        group_line['theoritical_amount'] += budget_line_of_group.theoritical_amount

                    if 'percentage' in fields:
                        if group_line['theoritical_amount']:
                            # use a weighted average
                            group_line['percentage'] = float(
                                (group_line['practical_amount'] or 0.0) / group_line['theoritical_amount']) * 100

        return result

    def _is_above_budget(self):
        for line in self:
            if line.percentage / 100 >= 100:
                line.is_above_budget = True
            else:
                line.is_above_budget = False

    def _compute_line_name(self):
        # just in case someone opens the budget line in form view
        for data in self:
            computed_name = data.crossovered_budget_id.name
            if data.general_budget_id:
                computed_name += ' - ' + data.general_budget_id.name
            if data.analytic_account_id:
                computed_name += ' - ' + data.analytic_account_id.name
            data.name = computed_name

    def _compute_practical_amount(self):
        for line in self:
            budgetry = line.id
            # print("===================budgetry=====",budgetry)
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [
                        ('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('state', '=', 'confirm'),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                if budgetry:
                    domain += [('general_budget_id', '=', budgetry)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to)
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0

    def _compute_theoritical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if line.date_from and line.date_to:
                if line.paid_date:
                    if today <= line.paid_date:
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    line_timedelta = line.date_to - line.date_from
                    elapsed_timedelta = today - line.date_from

                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and today < line.date_to:
                        # If today is between the budget line date_from and date_to
                        theo_amt = (
                                               elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                    else:
                        theo_amt = line.planned_amount
                line.theoritical_amount = theo_amt

    def _compute_percentage(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0)*100 / line.planned_amount)
            else:
                line.percentage = 0.00

    @api.constrains('general_budget_id', 'analytic_account_id')
    def _must_have_analytical_or_budgetary_or_both(self):
        for line in self:
            if not line.analytic_account_id and not line.general_budget_id:
                raise ValidationError(
                    _("You have to enter at least a budgetary position or analytic account on a budget line."))

    def action_open_budget_entries(self):
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
            action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to)
                                ]
            if self.general_budget_id:
                action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
        else:
            # otherwise the journal entries booked on the accounts of the budgetary postition are opened
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
            action['domain'] = [('account_id', 'in',
                                 self.general_budget_id.account_ids.ids),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to)
                                ]
        return action

    @api.constrains('date_from', 'date_to')
    def _line_dates_between_budget_dates(self):
        budget_date_from = self.crossovered_budget_id.date_from
        budget_date_to = self.crossovered_budget_id.date_to
        for data in self:
            if data.date_from:
                date_from = data.date_from
                if date_from < budget_date_from or date_from > budget_date_to:
                    raise ValidationError(
                        _('"Start Date" of the budget line should be included in the Period of the budget'))

            if data.date_to:
                date_to = data.date_to
                if date_to < budget_date_from or date_to > budget_date_to:
                    raise ValidationError(_('"End Date" of the budget line should be included in the Period of the budget'))