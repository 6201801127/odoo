# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api
from odoo.addons.kw_advance_claim.models.kw_apply_salary_advance import state_selection as ApplySalState
from odoo.addons.kw_advance_claim.models.kw_apply_petty_cash import state_selection as PettyCashState
from odoo.addons.kw_advance_claim.models.kw_claim_settlement import state_selection as ClaimSettleState
from .tour_models import set_journal_sequence_code, get_partner
from odoo.exceptions import ValidationError


ApplySalState = [('draft', 'New'), ('applied', 'Applied'),
                 ('approve', 'Approved'), ('hold', 'Hold'),
                 ('grant', 'Grant'), ('post', 'Posted'),
                 ('cancel', 'Cancelled'), ('reject', 'Rejected')]

PettyCashState = [('draft', 'New'), ('applied', 'Applied'),
                  ('approve', 'Approved'), ('hold', 'Hold'),
                  ('grant', 'Grant'), ('post', 'Posted'),
                  ('cancel', 'Cancelled'), ('reject', 'Rejected')]

ClaimSettleState = [('draft', 'New'), ('applied', 'Applied'),
                    ('approve', 'Approved'), ('cancel', 'Cancelled'),
                    ('hold', 'Hold'), ('reject', 'Rejected'),
                    ('grant', 'Grant'), ('post', 'Posted')]


class KwApplySalaryAdvanceInherit(models.Model):
    _inherit = "kw_advance_apply_salary_advance"

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.depends('name')
    @api.multi
    def _compute_btn_access(self):
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'approve' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state in ['grant', 'release'] \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True

    def post_journal_entry(self):
        for rec in self:
            rec_partner = get_partner(self, rec.employee_id)
            line_id_vals = []
            salary_adv_account = self.env['kw_advance_claim_accounting_configuration'].sudo().search(
                [('code', '=', 'sa')]).account_id

            for r in range(2):
                if r == 1 and salary_adv_account:
                    line_id_vals.append([0, 0, {
                        'account_id': salary_adv_account.id,
                        'partner_id': rec_partner.id if rec_partner else False,
                        'department_id': rec.employee_id.department_id.id,
                        'debit': rec.adv_amnt,
                    }])
                else:
                    line_id_vals.append([0, 0, {
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'credit': rec.adv_amnt
                    }])

            # Setting sequence code of Journal Entry
            if rec.journal_id:
                seq_code = set_journal_sequence_code(self, rec.journal_id)

                # Creating journal entry
                account_move_id = self.env['account.move'].sudo().create({
                    'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
                    'date': date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': f'{rec.employee_id.name} - Salary Advance',
                    'line_ids': line_id_vals,
                })
                rec.write({'state': 'post', 'account_move_id': account_move_id.id})
                self.env.user.notify_success(message='Journal entry has been created!')

        return True


class KwApplyPettyCashAdvanceInherit(models.Model):
    _inherit = "kw_advance_apply_petty_cash"

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.depends('name')
    @api.multi
    def _compute_btn_access(self):
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'approve' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state in ['grant', 'release'] \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True

    def post_journal_entry(self):
        for rec in self:

            rec_partner = get_partner(self, rec.user_emp_id)
            line_id_vals = []
            petty_cash_account = self.env['kw_advance_claim_accounting_configuration'].sudo().search(
                [('code', '=', 'pca')]).account_id

            for r in range(2):
                if r == 1 and petty_cash_account:
                    line_id_vals.append([0, 0, {
                        'account_id': petty_cash_account.id,
                        'partner_id': rec_partner.id if rec_partner else False,
                        'department_id': rec.user_emp_id.department_id.id,
                        'debit': rec.advance_amt,
                    }])
                else:
                    line_id_vals.append([0, 0, {
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'credit': rec.advance_amt
                    }])

            # Setting sequence code of Journal Entry
            if rec.journal_id:
                seq_code = set_journal_sequence_code(self, rec.journal_id)

                # Creating journal entry
                account_move_id = self.env['account.move'].sudo().create({
                    'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
                    'date': date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': f'{rec.user_emp_id.name} - Petty Cash',
                    'line_ids': line_id_vals,
                })
                rec.write({'state': 'post', 'account_move_id': account_move_id.id})
                self.env.user.notify_success(message='Journal entry has been created!')

        return True


class KwApplyClaimSettlementInherit(models.Model):
    _inherit = "kw_advance_claim_settlement"

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.depends('petty_cash_id')
    @api.multi
    def _compute_btn_access(self):
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'approve' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state in ['grant', 'release'] \
                        and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True

    def post_journal_entry(self):
        for rec in self:
            rec_partner = get_partner(self, rec.empl_id)
            line_id_vals = []

            for r in rec.claim_bill_line_ids:
                if r.claim_type_id.expense_account_id:
                    line_id_vals.append([0, 0, {
                        'account_id': r.claim_type_id.expense_account_id.id if r.claim_type_id.expense_account_id else False,
                        'partner_id': rec_partner.id if rec_partner else False,
                        'department_id': rec.empl_id.department_id.id,
                        'debit': r.amount,
                    }])

            # Petty cash advance credit transaction
            petty_cash_account = self.env['kw_advance_claim_accounting_configuration'].sudo().search(
                [('code', '=', 'pca')]).account_id
            if petty_cash_account:
                line_id_vals.append([0, 0, {
                    'account_id': petty_cash_account.id,
                    'partner_id': rec_partner.id if rec_partner else False,
                    'department_id': rec.empl_id.department_id.id,
                    'credit': rec.advance_amt,
                }])

            # Employee to pay organisation
            if rec.net_total < 0:
                line_id_vals.append([0, 0, {
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'credit': abs(rec.net_total),
                }])

            # Organisation to pay Employee
            else:
                line_id_vals.append([0, 0, {
                    'account_id': rec.journal_id.default_debit_account_id.id,
                    'debit': rec.net_total,
                }])

            # Setting sequence code of Journal Entry
            if rec.journal_id:
                seq_code = set_journal_sequence_code(self, rec.journal_id)

                # Creating journal entry
                account_move_id = self.env['account.move'].sudo().create({
                    'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
                    'date': date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': f'{rec.empl_id.name} - Claim Settlement',
                    'line_ids': line_id_vals,
                })
                rec.write({'state':'post','account_move_id': account_move_id.id})
                self.env.user.notify_success(message='Journal entry has been created!')

        return True


class ClaimTypeInherit(models.Model):
    _inherit = "kw_advance_claim_type"

    expense_account_id = fields.Many2one('account.account', 'Expense Account')


class AccountingConfiguration(models.Model):
    _name = "kw_advance_claim_accounting_configuration"

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
    account_id = fields.Many2one('account.account', 'Account')

    @api.constrains('name', 'code')
    def check_constrains(self):
        for rec in self:
            record = self.env['kw_advance_claim_accounting_configuration'].sudo().search(
                [('name', '=', rec.name), ('code', '=', rec.code)]) - self
            if record:
                raise ValidationError(f'{rec.name} with code {rec.code} already exists.')


class kw_adv_sal_release_remark_wiz(models.TransientModel):
    _inherit = 'kw_advance_sal_release_remark_wiz'

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.multi
    def release_salary_advance(self):
        record = super(kw_adv_sal_release_remark_wiz, self).release_salary_advance()
        self.sal_adv_id.write({
            'journal_id': self.journal_id.id,
        })
        self.sal_adv_id.post_journal_entry()
        return record


class kw_adv_petty_cash_release_remark_wizard(models.TransientModel):
    _inherit = 'kw_advance_petty_cash_release_remark_wizard'

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.multi
    def release_petty_cash(self):
        record = super(kw_adv_petty_cash_release_remark_wizard, self).release_petty_cash()
        self.petty_cash_id.write({
            'journal_id': self.journal_id.id,
        })
        self.petty_cash_id.post_journal_entry()
        return record


class kw_adv_claim_release_remark_wiz(models.TransientModel):
    _inherit = 'kw_advance_claim_release_remark_wiz'

    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.multi
    def release_claim(self):
        record = super(kw_adv_claim_release_remark_wiz, self).release_claim()
        self.claim_record_id.write({
            'journal_id': self.journal_id.id,
        })
        self.claim_record_id.post_journal_entry()
        return record
