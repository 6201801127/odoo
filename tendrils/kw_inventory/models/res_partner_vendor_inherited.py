from odoo import api, fields, models


class RespartnerInheritedForVendor(models.Model):
    _inherit = "res.partner"

    vendor_state = fields.Selection([('draft','Draft'),
        ('applied', 'Applied'),
        ('approved', 'Approved')],default='draft',string="State", help="Ensure the state of a vendor.", statusbar_visible=True)


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

