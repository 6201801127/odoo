# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from .tour_models import set_journal_sequence_code, get_partner
from odoo.exceptions import ValidationError


class KwSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    account_debit = fields.Many2one('account.account', 'Debit Account')
    account_credit = fields.Many2one('account.account', 'Credit Account')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')


class KwSalarySlipInherit(models.Model):
    _inherit = 'hr.payslip'

    date = fields.Date('Date Account')
    journal_id = fields.Many2one('account.journal', 'Salary Journal')
    move_id = fields.Many2one('account.move', 'Accounting Entry')

    def action_payslip_confirm(self):
        salary_journal = self.env['ir.config_parameter'].sudo().get_param('hr_payroll.default_salary_journal')
        if salary_journal:
            for rec in self:
                if rec.state == 'draft':
                    rec.journal_id = int(salary_journal)
                    rec.action_payslip_done()
        else:
            raise ValidationError('Please set Salary Journal in Configuration => Settings')


    def action_payslip_done(self):
        for rec in self:

            rec_partner = get_partner(self, rec.employee_id)
            line_id_vals = []
            total_amount = 0

            if rec.journal_id:
                cred_total, debt_total = 0, 0
                for line_id in rec.line_ids:
                    if line_id.category_id.code == 'DED' and line_id.salary_rule_id.account_credit:
                        line_id_vals.append([0, 0, {
                            'account_id': line_id.salary_rule_id.account_credit.id,
                            'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                                line_id.salary_rule_id.analytic_account_id else False,
                            'name': line_id.name,
                            'credit': abs(line_id.total),
                        }])
                        debt_total += abs(line_id.total)
                    else:
                        if line_id.salary_rule_id.account_debit:
                            line_id_vals.append([0, 0, {
                                'account_id': line_id.salary_rule_id.account_debit.id,
                                'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                                    line_id.salary_rule_id.analytic_account_id else False,
                                'name': line_id.name,
                                'debit': line_id.total,
                            }])
                            cred_total += line_id.total

                if cred_total > debt_total:
                    line_id_vals.append([0, 0, {
                        'account_id': rec.journal_id.default_debit_account_id.id,
                        'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                            line_id.salary_rule_id.analytic_account_id else False,
                        'name': 'Adjustment Entry',
                        'credit': cred_total - debt_total,
                    }])
                else:
                    line_id_vals.append([0, 0, {
                        'account_id': rec.journal_id.default_credit_account_id.id,
                        'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                            line_id.salary_rule_id.analytic_account_id else False,
                        'name': 'Adjustment Entry',
                        'debit': debt_total - cred_total,
                    }])

                        # if line_id.code == 'NET':
                        #     for r in range(2):
                        #         if r == 0:
                        #             line_id_vals.append([0, 0, {
                        #                 'account_id': line_id.salary_rule_id.account_debit.id,
                        #                 'partner_id': rec_partner.id if rec_partner else False,
                        #                 'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                        #                     line_id.salary_rule_id.analytic_account_id else False,
                        #                 'department_id': rec.employee_id.department_id.id,
                        #                 'name': line_id.name,
                        #                 'debit': line_id.total,
                        #             }])
                        #         else:
                        #             line_id_vals.append([0, 0, {
                        #                 'account_id': line_id.salary_rule_id.account_credit.id,
                        #                 'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                        #                     line_id.salary_rule_id.analytic_account_id else False,
                        #                 'name': line_id.name,
                        #                 'credit': line_id.total,
                        #             }])
                        # else:
                        #     for r in range(2):
                        #         if r == 0:
                        #             line_id_vals.append([0, 0, {
                        #                 'account_id': line_id.salary_rule_id.account_debit.id,
                        #                 'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                        #                     line_id.salary_rule_id.analytic_account_id else False,
                        #                 'name': line_id.name,
                        #                 'debit': line_id.total,
                        #             }])
                        #         else:
                        #             line_id_vals.append([0, 0, {
                        #                 'account_id': line_id.salary_rule_id.account_credit.id,
                        #                 'analytic_account_id': line_id.salary_rule_id.analytic_account_id.id if \
                        #                     line_id.salary_rule_id.analytic_account_id else False,
                        #                 'name': line_id.name,
                        #                 'credit': line_id.total,
                        #             }])

                seq_code = set_journal_sequence_code(self, rec.journal_id)

                # Creating journal entry
                account_move_id = self.env['account.move'].sudo().create({
                    'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
                    'date': rec.date if rec.date else date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': rec.number,
                    'line_ids': line_id_vals,
                })
                rec.move_id = account_move_id.id
                self.env.user.notify_success(message='Journal entry has been created!')

            else:
                raise ValidationError('Please give salary journal!')
        res = super().action_payslip_done()

        return res
