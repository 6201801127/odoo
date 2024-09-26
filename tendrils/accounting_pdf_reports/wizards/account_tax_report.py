# -*- coding: utf-8 -*-
"""
This module contains a transient model for generating tax reports in Odoo.

It includes functionalities for defining transient models using models provided by Odoo.

Author: [Your Name]
Date: [Current Date]
"""

from odoo import models


class AccountTaxReport(models.TransientModel):
    """
    This transient model represents a wizard for generating tax reports in Odoo.
    """
    _inherit = "account.common.report"
    _name = 'account.tax.report'
    _description = 'Tax Report'

    def _print_report(self, data):
        return self.env.ref('accounting_pdf_reports.action_report_account_tax').report_action(self, data=data)
