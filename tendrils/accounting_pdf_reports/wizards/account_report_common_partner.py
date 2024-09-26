# -*- coding: utf-8 -*-
"""
This module contains a transient model for managing common partner reports in Odoo.

It includes functionalities for defining transient models using fields and models.

Author: [Your Name]
Date: [Current Date]
"""

from odoo import fields, models


class AccountingCommonPartnerReport(models.TransientModel):
    """
    This transient model represents a wizard for generating common partner reports in Odoo.
    """
    _name = 'account.common.partner.report'
    _description = 'Account Common Partner Report'
    _inherit = "account.common.report"

    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        return data
