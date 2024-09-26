# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError

class MassMailing(models.Model):
    _inherit = "mail.mass_mailing"


    @api.multi
    def action_view_clicked(self):
        model_name = self.env['ir.model']._get('link.tracker').display_name
        return {
            'name': model_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'link.tracker',
            'domain': [('mass_mailing_id.id', '=', self.id)],
            'context': dict(self._context, create=False)
        }

    @api.onchange('mass_mailing_campaign_id')
    def _onchange_mass_mailing_campaign_id(self):
        if self.mass_mailing_campaign_id:
            dic = {'campaign_id': self.mass_mailing_campaign_id.campaign_id,
                    'source_id': self.mass_mailing_campaign_id.source_id,
                    'medium_id': self.mass_mailing_campaign_id.medium_id,
                    'name': False}
            self.update(dic)

    # @api.multi
    # def onchange(self, values, field_name, field_onchange):
    #     res = super(MassMailing,self).onchange(values, field_name, field_onchange)
    #     print(values, field_name, field_onchange)
    #     print("res",res)
    #     return res
class MailMassMailingContact(models.Model):
    _inherit = "mail.mass_mailing.contact"

    opened = fields.Boolean(string='Opened',compute="_compute_mail_statistics",
                             help='The contact has chosen not to receive mails anymore from this list')
    received = fields.Boolean(string='Received',compute="_compute_mail_statistics",
                             help='The contact has chosen not to receive mails anymore from this list')
    clicked = fields.Boolean(string='Clicked',compute="_compute_mail_statistics",
                             help='The contact has chosen not to receive mails anymore from this list')
    @api.multi
    def _compute_mail_statistics(self):
        statistics = self.env['mail.mail.statistics'].sudo()
        for contact in self:
            contact.opened = bool(statistics.search_count([('res_id','=',contact.id),('opened','!=',False)]))
            contact.received = bool(statistics.search_count([('res_id','=',contact.id),('sent','!=',False),('bounced','=',False)]))
            contact.clicked = bool(statistics.search_count([('res_id','=',contact.id),('clicked','!=',False)]))



    @api.constrains('email')
    def validate_email(self):
        if self.email:
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email) != None:
                raise ValidationError(f'Email is invalid for : {self.email}')
        for record in self:
            if record.email:
                records = self.env['mail.mass_mailing.contact'].search(
                    [('email', '=', record.email)]) - self
                if records:
                    raise ValidationError("This email id is already existing.")
