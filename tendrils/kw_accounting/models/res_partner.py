from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_payable_code = fields.Char(string="Ledger Payable Code",related="property_account_payable_id.code")
    property_account_payable_name = fields.Char(string="Ledger Payable Name",related="property_account_payable_id.name")
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    property_account_receivable_code = fields.Char(string="Ledger Receivable Code",related="property_account_receivable_id.code")
    property_account_receivable_name = fields.Char(string="Ledger Receivable Name",related="property_account_receivable_id.name")
    
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

    vendor_state = fields.Selection([('draft','Draft'),
        ('applied', 'Applied'),
        ('approved', 'Approved')],default='draft',string="Vendor Status", help="Ensure the state of a vendor.")


    @api.onchange('property_account_receivable_id')
    def _onchange_property_account_receivable_id(self):
        if self.property_account_receivable_id:
            existing_partner = self.env['res.partner'].search([('property_account_receivable_id', '=', self.property_account_receivable_id.id)])
            print("existing_partner", existing_partner)
            if existing_partner and existing_partner != self:
                raise ValidationError("This account receivable is already assigned to another partner!")

    @api.onchange('property_account_payable_id')
    def _onchange_property_account_payable_id(self):
        if self.property_account_payable_id:
            existing_partner = self.env['res.partner'].search([('property_account_payable_id', '=', self.property_account_payable_id.id)])
            print("existing_partner", existing_partner)
            if existing_partner and existing_partner != self:
                raise ValidationError("This account payable is already assigned to another partner!")


    @api.multi
    def apply_for_vendor(self):
        self.vendor_state='applied'

        notify_emp = self.env.ref('account.group_account_manager').users
        mail_to = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
        template_id = self.env.ref('kw_inventory.kw_vendor_created_mail_template')
        template_id.with_context(mail_to=mail_to).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("New Vendor Created Successfully")

    @api.multi
    def approve_vendor(self):
        self.vendor_state='approved'
        self.env.user.notify_success("Vendor Approved Successfully")

class kw_res_partner_bank(models.Model):
    _inherit = "res.partner.bank"

    ifsc_code = fields.Char(related='bank_id.bic')
    addr = fields.Char(related="bank_id.street2")