from odoo import models, fields, api

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export'),
            ('deductor','Registered Business - Deductor'),
            ('regular_deductor','Regular & Deductor')], string="GST Treatment")