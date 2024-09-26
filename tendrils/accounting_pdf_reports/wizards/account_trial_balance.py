# -*- coding: utf-8 -*-
"""
This module contains a transient model for generating trial balance reports in Odoo.

It includes functionalities for defining transient models using fields, models, and APIs provided by Odoo.

"""
from odoo import fields, models


class AccountBalanceReport(models.TransientModel):
    """
    This transient model represents a wizard for generating trial balance reports in Odoo.
    """
    _inherit = "account.common.account.report"
    _name = 'account.balance.report'
    _description = 'Trial Balance Report'

    journal_ids = fields.Many2many('account.journal', 'account_balance_report_journal_rel', 'account_id', 'journal_id', string='Journals', required=True, default=[])

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('accounting_pdf_reports.action_report_trial_balance').report_action(records, data=data)
