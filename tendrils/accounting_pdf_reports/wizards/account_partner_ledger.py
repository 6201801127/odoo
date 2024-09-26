# -*- coding: utf-8 -*-
"""
This module contains a transient model for managing partner ledger reports in Odoo.

It includes functionalities for defining transient models using fields and models.

Author: [Your Name]
Date: [Current Date]
"""

from odoo import fields, models, _


class AccountPartnerLedger(models.TransientModel):
    """
    This transient model represents the partner ledger for accounts.
    It provides a temporary storage mechanism for partner ledger data
    during certain operations or computations, typically used for
    generating reports or performing analyses involving partner accounts.
    """
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').report_action(self, data=data)
