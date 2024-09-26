from odoo import fields, models,api

class AccountConfigSetting(models.TransientModel):

    _inherit = "res.config.settings"

    module_account_branch_company = fields.Boolean(string='Branch In Accounting')
    module_account_voucher_branch_company = fields.Boolean(string='Branch In Account Voucher')
    module_sale_branch_company = fields.Boolean(string='Branch In Sale')
    module_purchase_branch_company = fields.Boolean(string='Branch In Purchase')
    module_stock_branch_company = fields.Boolean(string='Branch In Stock')
    module_sequence_branch_company = fields.Boolean(string='Branch In Sequence ')
    module_sequence_account_branch_company = fields.Boolean(string='Branch In Account Sequence ')
    module_chart_of_account_branch_company = fields.Boolean(string='Branch In Chart Of Account')
    module_mass_payment_branch = fields.Boolean(string='Branch In Mass Payment')