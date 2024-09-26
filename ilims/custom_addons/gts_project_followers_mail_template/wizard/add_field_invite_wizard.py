from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    # recipient_ids = fields.Char() #to be removed
    stakeholder_ids = fields.Many2many('res.partner', 'stakeholder_partner_rel', string='Recipients Allowed')

    @api.model
    def default_get(self, fields):
        rec = super(Invite, self).default_get(fields)
        if rec.get('res_model') == 'partner.contract':
            partner_list = []
            contract = self.env['partner.contract'].search([('id', '=', rec.get('res_id'))], limit=1)
            if contract and contract.related_project.stakeholder_ids:
                for lines in contract.related_project.stakeholder_ids:
                    if lines.status is True:
                        partner_list.append(lines.partner_id.id)
            rec['stakeholder_ids'] = [(6, 0, [record for record in partner_list])]
        elif rec.get('res_model') in ['project.task', 'qc.inspection', 'acceptance.inspection', 'change.request',
                                      'support.ticket', 'crossovered.budget']:
            partner_list = []
            record = self.env[rec.get('res_model')].search([('id', '=', rec.get('res_id'))], limit=1)
            if record and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True:
                        partner_list.append(lines.partner_id.id)
            rec['stakeholder_ids'] = [(6, 0, [record for record in partner_list])]
        elif rec.get('res_model') == 'project.project':
            partner_list = []
            record = self.env['project.project'].search([('id', '=', rec.get('res_id'))], limit=1)
            if record and record.stakeholder_ids:
                for lines in record.stakeholder_ids:
                    if lines.status is True:
                        partner_list.append(lines.partner_id.id)
            rec['stakeholder_ids'] = [(6, 0, [record for record in partner_list])]
        elif rec.get('res_model') in ['sale.order', 'purchase.order']:
            partner_list = []
            record = self.env[rec.get('res_model')].search([('id', '=', rec.get('res_id'))], limit=1)
            if record:
                project = self.env['project.project'].search(
                    [('analytic_account_id', '=', record.analytic_account_id.id)], limit=1)
                if project and project.stakeholder_ids:
                    for lines in project.stakeholder_ids:
                        if lines.status is True:
                            partner_list.append(lines.partner_id.id)
            rec['stakeholder_ids'] = [(6, 0, [record for record in partner_list])]
        elif rec.get('res_model') == 'account.move':
            partner_list = []
            record = self.env['account.move'].search([('id', '=', rec.get('res_id'))], limit=1)
            if record:
                project = self.env['project.project'].search(
                    [('analytic_account_id', '=', record.analytic_account_id.id)], limit=1)
                if project and project.stakeholder_ids:
                    for lines in project.stakeholder_ids:
                        if lines.status is True:
                            partner_list.append(lines.partner_id.id)
            rec['stakeholder_ids'] = [(6, 0, [record for record in partner_list])]
        else:
            rec['stakeholder_ids'] = [(6, 0, self.env['res.partner'].search([('type', '!=', 'private')]).ids)]
        return rec

    def add_followers(self):
        if not self.env.user.email:
            raise UserError(_("Unable to post message, please configure the sender's email address."))
        email_from = self.env.user.email_formatted
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_partners = wizard.partner_ids - document.sudo().message_partner_ids
            new_channels = wizard.channel_ids - document.message_channel_ids
            document.message_subscribe(new_partners.ids, new_channels.ids)

            model_name = self.env['ir.model']._get(wizard.res_model).display_name
            # send an email if option checked and if a message exists (do not send void emails)
            if wizard.send_mail and wizard.message and not wizard.message == '<br>':  # when deleting the message, cleditor keeps a <br>
                message = self.env['mail.mail'].create({
                    'subject': _('Invitation to follow %(document_model)s: %(document_name)s',
                                 document_model=model_name, document_name=document.display_name),
                    'body': wizard.message,
                    'record_name': document.display_name,
                    'email_from': email_from,
                    'reply_to': email_from,
                    'model': wizard.res_model,
                    'res_id': wizard.res_id,
                    'no_auto_thread': True,
                    'add_sign': True,
                    'auto_delete': False,
                })
                partners_data = []
                recipient_data = self.env['mail.followers']._get_recipient_data(document, 'comment', False,
                                                                                pids=new_partners.ids)
                for pid, cid, active, pshare, ctype, notif, groups in recipient_data:
                    pdata = {'id': pid, 'share': pshare, 'active': active, 'notif': 'email', 'groups': groups or []}
                    if not pshare and notif:  # has an user and is not shared, is therefore user
                        partners_data.append(dict(pdata, type='user'))
                    elif pshare and notif:  # has an user and is shared, is therefore portal
                        partners_data.append(dict(pdata, type='portal'))
                    else:  # has no user, is therefore customer
                        partners_data.append(dict(pdata, type='customer'))

                document._notify_record_by_email(message, {'partners': partners_data, 'channels': []},
                                                 send_after_commit=False)
                # in case of failure, the web client must know the message was
                # deleted to discard the related failure notification
                self.env['bus.bus'].sendone(
                    (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
                    {'type': 'deletion', 'message_ids': message.ids}
                )
                message.unlink()
        return {'type': 'ir.actions.act_window_close'}
