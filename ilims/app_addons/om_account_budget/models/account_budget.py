# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Name', required=True, tracking=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', 'Accounts',
        domain=[('deprecated', '=', False)], tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company, tracking=True)

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        if 'account_ids' in vals:
            account_ids = self.new({'account_ids': vals['account_ids']}, origin=self).account_ids
        else:
            account_ids = self.account_ids
        if not account_ids:
            raise ValidationError(_('The budget must have at least one account.'))

    @api.model
    def create(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).create(vals)

    
    def write(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).write(vals)


class CrossoveredBudget(models.Model):
    _name = "crossovered.budget"
    _description = "Budget"
    _inherit = ['mail.thread']

    name = fields.Char('Budget Name', required=True, states={'done': [('readonly', True)]}, tracking=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=False, tracking=True)
    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]}, tracking=True)
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]}, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Sent for Approval'),
        # ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True,)
    crossovered_budget_line = fields.One2many('crossovered.budget.lines', 'crossovered_budget_id', 'Budget Lines',
        states={'done': [('readonly', True)]}, copy=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company, tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Project Name', tracking=True)
    ir_attachment_ids = fields.One2many('ir.attachment', 'crossovered_budget_id', string='Document Type', tracking=True)
    is_from_project = fields.Boolean('From Project', tracking=True)
    project_stakeholder_ids = fields.Many2many('res.users', 'Stakeholders', compute='_get_project_stakeholders')
    pending = fields.Char("Pending")
    sla_signinig_date = fields.Date('SLA Signing Date')
    budget_analysis_line = fields.One2many('budget.analysis.lines', 'budget_id', string='Budget Analysis Line')

    @api.depends('analytic_account_id')
    def _get_project_stakeholders(self):
        users_obj = self.env['res.users']
        project_obj = self.env['project.project']
        for record in self:
            users_list, p_user = [], []
            if record.analytic_account_id:
                project = project_obj.search([('analytic_account_id', '=', record.analytic_account_id.id)], limit=1)
                if project:
                    for lines in project.stakeholder_ids:
                        if lines.status is True:
                            user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                            if user and user.has_group('account.group_account_user'):
                                users_list.append(user.id)
                                if user.id == self.env.user.id:
                                    p_user.append(user.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                record.project_stakeholder_ids = [(6, 0, [rec for rec in users_list])]
            else:
                record.project_stakeholder_ids = [(6, 0, p_user)]

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    # def action_budget_validate(self):
    #     self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        budget = super(CrossoveredBudget, self).create(vals)
        partner_ids = []
        if budget.user_id:
            partner_ids.append(budget.user_id.partner_id.id)
        # if partner_ids:
        #     partner_ids.append(partner_ids)
            # budget.message_subscribe(partner_ids=partner_ids)
        if budget.analytic_account_id:
            project = self.env['project.project'].search([('analytic_account_id', '=', budget.analytic_account_id.id)],
                                                         limit=1)
            if project:
                if project.program_manager_id:
                    partner_ids.append(project.program_manager_id.partner_id.id)
                if project.user_id:
                    partner_ids.append(project.user_id.partner_id.id)
        notification_ids = []
        if partner_ids:
            new_list = list(set(partner_ids))
            budget.message_subscribe(partner_ids=new_list)
            budget.message_post(partner_ids=new_list, body="Invited you to follow Budget")
            for partner in new_list:
                notification_ids.append((0, 0, {
                    'res_partner_id': partner,
                    'notification_type': 'inbox'}))
            budget.message_post(body="Invited you to follow Budget", message_type='notification',
                              subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
        if budget.ir_attachment_ids:
            for lines in budget.ir_attachment_ids:
                lines.update({'res_model': 'crossovered.budget', 'res_id': budget.id})
        return budget

    def write(self, vals):
        partner_ids = []
        if vals.get('user_id'):
            user_id = self.env['res.users'].browse(vals.get('user_id'))
            if user_id:
                partner_ids.append(user_id.partner_id.id)
        if partner_ids:
            self.message_subscribe(partner_ids=partner_ids)
        return super(CrossoveredBudget, self).write(vals)


class CrossoveredBudgetLines(models.Model):
    _name = "crossovered.budget.lines"
    _description = "Budget Line"

    name = fields.Char(compute='_compute_line_name', tracking=True)
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True, required=True, tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group', related='analytic_account_id.group_id', readonly=True, tracking=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', tracking=True)
    date_from = fields.Date('Start Date', required=True, tracking=True)
    date_to = fields.Date('End Date', required=True, tracking=True)
    paid_date = fields.Date('Paid Date', tracking=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, tracking=True)
    planned_amount = fields.Monetary(
        'Budget Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.", tracking=True)
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Actual Amount', help="Amount really earned/spent.", tracking=True)
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount', string='Theoretical Amount',
        help="Amount you are supposed to have earned/spent at this date.", tracking=True)

    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.", tracking=True)
    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
        string='Company', store=True, readonly=True, tracking=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget', tracking=True)
    crossovered_budget_state = fields.Selection(related='crossovered_budget_id.state', string='Budget State', store=True, readonly=True, tracking=True)
    remaining_amount = fields.Float(compute='_compute_remaining_amount', string='Remaining Amount', tracking=True)

    def write(self, vals):
        prev_general_budget_id = self.general_budget_id.name
        prev_analytic_account_id = self.analytic_account_id.name+' '+'-'+' '+self.analytic_account_id.partner_id.name
        prev_date_from = self.date_from
        prev_date_to = self.date_to
        prev_paid_date = self.paid_date
        prev_planned_amount = self.planned_amount
        prev_practical_amount = self.practical_amount
        prev_theoritical_amount = self.theoritical_amount
        prev_remaining_amount = self.remaining_amount
        prev_percentage = self.percentage
        rec = super(CrossoveredBudgetLines, self).write(vals)
        message_body = """<b>Budget Lines</b><br/>"""
        if prev_general_budget_id == self.general_budget_id.name:
            message_body += """• Budgetary Position: {prev_general_budget_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {general_budget_id} <br/>""".format(
                prev_general_budget_id=prev_general_budget_id, general_budget_id=self.general_budget_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Budgetary Position: {prev_general_budget_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {general_budget_id}</span><br/>""".format(
                prev_general_budget_id=prev_general_budget_id, general_budget_id=self.general_budget_id.name
            )
        if prev_analytic_account_id == self.analytic_account_id.name+' '+'-'+' '+self.analytic_account_id.partner_id.name:
            message_body += """• Analytic Account: {prev_analytic_account_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {analytic_account_id}<br/>""".format(
                prev_analytic_account_id=prev_analytic_account_id,
                analytic_account_id=self.analytic_account_id.name + ' ' + '-' + ' ' + self.analytic_account_id.partner_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Analytic Account: {prev_analytic_account_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {analytic_account_id}</span><br/>""".format(
                prev_analytic_account_id=prev_analytic_account_id,
                analytic_account_id=self.analytic_account_id.name + ' ' + '-' + ' ' + self.analytic_account_id.partner_id.name
            )
        if prev_date_from == self.date_from:
            message_body += """• Start Date: {prev_date_from} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_from}<br/>""".format(
                prev_date_from=prev_date_from, date_from=self.date_from
            )
        else:
            message_body += """<span style='color:red;'>• Start Date: {prev_date_from} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_from}</span><br/>""".format(
                prev_date_from=prev_date_from, date_from=self.date_from
            )
        if prev_date_to == self.date_to:
            message_body += """• End Date: {prev_date_to} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_to}<br/>""".format(
                prev_date_to=prev_date_to, date_to=self.date_to
            )
        else:
            message_body += """<span style='color:red;'>• End Date: {prev_date_to} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_to}</span><br/>""".format(
                prev_date_to=prev_date_to, date_to=self.date_to
            )
        if prev_paid_date == self.paid_date:
            message_body += """• Paid Date: {prev_paid_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {paid_date}<br/>""".format(
                prev_paid_date=prev_paid_date, paid_date=self.paid_date
            )
        else:
            message_body += """<span style='color:red;'>• Paid Date: {prev_paid_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {paid_date}</span><br/>""".format(
                prev_paid_date=prev_paid_date, paid_date=self.paid_date
            )
        if prev_planned_amount == self.planned_amount:
            message_body += """• Budget Amount: {prev_planned_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {planned_amount}<br/>""".format(
                prev_planned_amount=prev_planned_amount, planned_amount=self.planned_amount
            )
        else:
            message_body += """<span style='color:red;'>• Budget Amount: {prev_planned_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {planned_amount}</span><br/>""".format(
                prev_planned_amount=prev_planned_amount, planned_amount=self.planned_amount
            )
        if prev_theoritical_amount == self.theoritical_amount:
            message_body += """• Theoretical Amount: {prev_theoritical_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {theoritical_amount}<br/>""".format(
                prev_theoritical_amount=prev_theoritical_amount, theoritical_amount=self.theoritical_amount
            )
        else:
            message_body += """<span style='color:red;'>• Theoretical Amount: {prev_theoritical_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {theoritical_amount}</span><br/>""".format(
                prev_theoritical_amount=prev_theoritical_amount, theoritical_amount=self.theoritical_amount
            )
        if prev_remaining_amount == self.remaining_amount:
            message_body += """• Remaining Amount: {prev_remaining_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remaining_amount}<br/>""".format(
                prev_remaining_amount=prev_remaining_amount, remaining_amount=self.remaining_amount
            )
        else:
            message_body += """<span style='color:red;'>• Remaining Amount: {prev_remaining_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remaining_amount}</span><br/>""".format(
                prev_remaining_amount=prev_remaining_amount, remaining_amount=self.remaining_amount
            )
        if prev_percentage == self.percentage:
            message_body += """• Achievement: {prev_percentage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {percentage}""".format(
                prev_percentage=prev_percentage, percentage=self.percentage
            )
        else:
            message_body += """<span style='color:red;'>• Achievement: {prev_percentage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {percentage}</span>""".format(
                prev_percentage=prev_percentage, percentage=self.percentage
            )
        # message_body = """<b>Budget Lines</b><br/>
        #                 • Budgetary Position: {prev_general_budget_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {general_budget_id} <br/>
        #                 • Analytic Account: {prev_analytic_account_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {analytic_account_id}<br/>
        #                 • Start Date: {prev_date_from} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_from}<br/>
        #                 • End Date: {prev_date_to} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date_to}<br/>
        #                 • Paid Date: {prev_paid_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {paid_date}<br/>
        #                 • Budget Amount: {prev_planned_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {planned_amount}<br/>
        #                 • Actual Amount: {prev_practical_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {practical_amount}<br/>
        #                 • Theoretical Amount: {prev_theoritical_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {theoritical_amount}<br/>
        #                 • Remaining Amount: {prev_remaining_amount} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remaining_amount}<br/>
        #                 • Achievement: {prev_percentage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {percentage}"""\
        #     .format(prev_general_budget_id=prev_general_budget_id, general_budget_id=self.general_budget_id.name,
        #             prev_analytic_account_id=prev_analytic_account_id, analytic_account_id=self.analytic_account_id.name+' '+'-'+' '+self.analytic_account_id.partner_id.name,
        #             prev_date_from=prev_date_from, date_from=self.date_from,
        #             prev_date_to=prev_date_to, date_to=self.date_to,
        #             prev_paid_date=prev_paid_date, paid_date=self.paid_date,
        #             prev_planned_amount=prev_planned_amount, planned_amount=self.planned_amount,
        #             prev_practical_amount=prev_practical_amount, practical_amount=self.practical_amount,
        #             prev_theoritical_amount=prev_theoritical_amount, theoritical_amount=self.theoritical_amount,
        #             prev_remaining_amount=prev_remaining_amount, remaining_amount=self.remaining_amount,
        #             prev_percentage=prev_percentage, percentage=self.percentage)
        self.crossovered_budget_id.message_post(body=message_body)
        return rec


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
            if line.theoritical_amount >= 0:
                line.is_above_budget = line.practical_amount > line.theoritical_amount
            else:
                line.is_above_budget = line.practical_amount < line.theoritical_amount

    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        computed_name = self.crossovered_budget_id.name
        if self.general_budget_id:
            computed_name += ' - ' + self.general_budget_id.name
        if self.analytic_account_id:
            computed_name += ' - ' + self.analytic_account_id.name
        self.name = computed_name

    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

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
            practical_amount = self.env.cr.fetchone()[0] or 0.0
            if practical_amount < 0.00:
                line.practical_amount = practical_amount * -1
            else:
                line.practical_amount = practical_amount

    def _compute_theoritical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if not line.crossovered_budget_id.date_from or not line.crossovered_budget_id.date_to:
                raise UserError(_('Please define Budget Period before adding the budget lines!'))
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
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                else:
                    theo_amt = line.planned_amount
            line.theoritical_amount = theo_amt

    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
            else:
                line.percentage = 0.00

    def _compute_remaining_amount(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                if line.planned_amount > line.practical_amount:
                    line.remaining_amount = line.planned_amount - line.practical_amount
                else:
                    line.remaining_amount = 0.00
            else:
                line.remaining_amount = 0.00

    @api.constrains('general_budget_id', 'analytic_account_id')
    def _must_have_analytical_or_budgetary_or_both(self):
        if not self.analytic_account_id and not self.general_budget_id:
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
        for rec in self:
            budget_date_from = rec.crossovered_budget_id.date_from
            budget_date_to = rec.crossovered_budget_id.date_to
            if rec.date_from:
                date_from = rec.date_from
                if date_from < budget_date_from or date_from > budget_date_to:
                    raise ValidationError(_('"Start Date" of the budget line should be included in the Period of the budget'))
            if rec.date_to:
                date_to = rec.date_to
                if date_to < budget_date_from or date_to > budget_date_to:
                    raise ValidationError(_('"End Date" of the budget line should be included in the Period of the budget'))

    def daily_budget_email(self):
        budget_lines = self.env['crossovered.budget.lines'].search([('crossovered_budget_id.state', 'in', ('draft', 'confirm'))])
        for record in budget_lines:
            if int(record.percentage * 100) > 0:
                if int(round(record.percentage*100)) == 50:
                    notification_ids = []
                    budget_template = self.env.ref('om_account_budget.email_template_daily_budget_email_50')
                    if budget_template:
                        values = budget_template.generate_email(record.id,
                                                                ['subject', 'email_to', 'email_from',
                                                                 'body_html'])
                        values['email_to'] = record.crossovered_budget_id.user_id.partner_id.email or record.crossovered_budget_id.user_id.login
                        values['email_from'] = 'pmis.gts@gmail.com'
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    record.crossovered_budget_id.message_post(body="Budget Covered 50%", message_type='notification',
                                        subtype_xmlid='mail.mt_comment',
                                        author_id=record.crossovered_budget_id.user_id.partner_id.id,
                                        notification_ids=notification_ids, notify_by_email=False)
                if int(round(record.percentage*100)) == 70:
                    notification_ids = []
                    budget_template = self.env.ref('om_account_budget.email_template_daily_budget_email_70')
                    if budget_template:
                        values = budget_template.generate_email(record.id,
                                                                ['subject', 'email_to', 'email_from',
                                                                 'body_html'])
                        values['email_to'] = record.crossovered_budget_id.user_id.partner_id.email or record.crossovered_budget_id.user_id.login
                        values['email_from'] = 'pmis.gts@gmail.com'
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    record.crossovered_budget_id.message_post(body="Budget Covered 70%", message_type='notification',
                                        subtype_xmlid='mail.mt_comment',
                                        author_id=record.crossovered_budget_id.user_id.partner_id.id,
                                        notification_ids=notification_ids, notify_by_email=False)
                if int(round(record.percentage*100)) == 90:
                    notification_ids = []
                    budget_template = self.env.ref('om_account_budget.email_template_daily_budget_email_90')
                    if budget_template:
                        values = budget_template.generate_email(record.id,
                                                                ['subject', 'email_to', 'email_from',
                                                                 'body_html'])
                        values['email_to'] = record.crossovered_budget_id.user_id.partner_id.email or record.crossovered_budget_id.user_id.login
                        values['email_from'] = 'pmis.gts@gmail.com'
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    record.crossovered_budget_id.message_post(body="Budget Covered 90%", message_type='notification',
                                        subtype_xmlid='mail.mt_comment',
                                        author_id=record.crossovered_budget_id.user_id.partner_id.id,
                                        notification_ids=notification_ids, notify_by_email=False)
                if int(round(record.percentage*100)) > 100:
                    notification_ids = []
                    budget_template = self.env.ref('om_account_budget.email_template_daily_budget_email_overflow')
                    if budget_template:
                        values = budget_template.generate_email(record.id,
                                                                ['subject', 'email_to', 'email_from',
                                                                 'body_html'])
                        values['email_to'] = record.crossovered_budget_id.user_id.partner_id.email or record.crossovered_budget_id.user_id.login
                        values['email_from'] = 'pmis.gts@gmail.com'
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    record.crossovered_budget_id.message_post(body="Budget Overflow", message_type='notification',
                                        subtype_xmlid='mail.mt_comment',
                                        author_id=record.crossovered_budget_id.user_id.partner_id.id,
                                        notification_ids=notification_ids, notify_by_email=False)


class BudgetAnalysisLines(models.Model):
    _name = "budget.analysis.lines"
    _description = "Budget Analysis Line"

    budget_id = fields.Many2one('crossovered.budget', string='Budget')
    remarks = fields.Char('Remarks')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Crossovered Budget', tracking=True)
