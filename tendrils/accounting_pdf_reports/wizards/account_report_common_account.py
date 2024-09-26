# -*- coding: utf-8 -*-
"""
This module contains a transient model for generating common account reports in Odoo.

It includes functionalities for defining transient models using fields, models, and APIs provided by Odoo.

Author: [Your Name]
Date: [Current Date]
"""


from odoo import api, fields, models


class AccountCommonAccountReport(models.TransientModel):
    """
    This transient model represents a wizard for generating common account reports in Odoo.
    """
    _name = 'account.common.account.report'
    _description = 'Account Common Account Report'
    _inherit = "account.common.report"

    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts', required=True, default='movement')

    @api.multi
    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        return data
