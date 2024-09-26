import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BusinesscardNotifyemail(models.TransientModel):
    _name = 'kw_visitng_card_notify_mail'
    _description = "Wizard: send business card on mail"

    def _default_active_id(self):
        return self.env['kw_visiting_card_apply'].browse(self.env.context.get('active_id')).id

    def _default_vender_id(self):
        data = self.env['kw_visiting_card_apply'].search([('id', '=', self.env.context.get('active_id', 0))], limit=1)
        return data.vendor_name

    def _default_card_datils(self):
        data = self.env['kw_visiting_card_apply'].search([('id', '=', self.env.context.get('active_id', 0))], limit=1)
        return data.card_details

    card_id = fields.Many2one('kw_visiting_card_apply', string="Card Name", readonly=True, default=_default_active_id)
    vendor_name = fields.Many2one('res.partner', string='Vendor', default=_default_vender_id)
    vendor_email = fields.Char(string='Vendor Email', related='vendor_name.email')
    card_details = fields.Text('Card Details', default=_default_card_datils)

    @api.multi
    def send_print_mail(self):
        # print("send mail called")
        card = self.card_id
        # print(card.state)
        # if not self.vendor_name:
        if card.state.lower() not in ['sent for printing', 'delivered to user']:
            raise ValidationError("Please go to the sent for printing stage after that mail trigger.")
        vendor_name = self.vendor_name.name
        vendor_email = self.vendor_name.email
        manager_group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
        manager_employees = manager_group.users.mapped('employee_ids') or False
        email_ids = manager_employees and ','.join(manager_employees.mapped('work_email')) or ''
        current_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)], limit=1)
        template = self.env.ref('kw_visiting_card.kw_send_for_print_visiting_card_email_template_by_wizard')
        template.with_context(manager_email=email_ids, employee=current_employee, vendor_name=vendor_name,
                              vendor_email=vendor_email).send_mail(card.id, force_send=True,
                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Vendor mail sent successfully.")
        return True

    # border: 1px solid #ccc;
    # padding: 1em;
    # background-color: #ccc;
    # width: 100%;
    # text-align: left;
