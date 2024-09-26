from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class RejectContractCloseWizard(models.TransientModel):
    _name = 'reject.contract.close.wizard'

    rejection_reason = fields.Text('Rejection Reason')

    def button_reject(self):
        if self.env.context.get('active_id'):
            contract = self.env['partner.contract'].search([('id', '=', self.env.context.get('active_id'))])
            if contract:
                contract.update({
                    'closure_rejection_reason': self.rejection_reason,
                    'closure_rejected_by': self.env.uid,
                    'is_request_to_close': False,
                    'is_rejected': True
                })
                user_list, notification_ids = '', []
                if contract.closure_requested_by:
                    if contract.closure_requested_by.partner_id.email:
                        user_list += contract.closure_requested_by.partner_id.email + ","
                    else:
                        user_list += contract.closure_requested_by.login + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': contract.closure_requested_by.partner_id.id,
                        'notification_type': 'inbox'}))
                if contract.related_project.user_id:
                    if contract.related_project.user_id.id != contract.closure_requested_by.id:
                        if contract.related_project.user_id.partner_id.email:
                            user_list += contract.related_project.user_id.partner_id.email + ","
                        else:
                            user_list += contract.related_project.user_id.login + ","
                        notification_ids.append((0, 0, {
                            'res_partner_id': contract.related_project.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                if contract.message_follower_ids:
                    for followers in contract.message_follower_ids:
                        if followers.partner_id.email not in user_list:
                            if followers.partner_id.email:
                                user_list += followers.partner_id.email + ","
                            notification_ids.append((0, 0, {
                                'res_partner_id': followers.partner_id.id,
                                'notification_type': 'inbox'}))
                action_id = self.env.ref('contract.view_partner_contract_form').id
                params = "web#id=%s&view_type=form&model=partner.contract&action=%s" % (contract.id, action_id)
                contract_url = str(params)
                template = self.env.ref('contract.request_contract_rejected_email')
                if template:
                    values = template.generate_email(contract.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                activity = self.env['mail.activity'].search([('res_id', '=', contract.id),
                                                             ('res_model', '=', 'partner.contract'),
                                                             ('activity_type_id', '=',
                                                              self.env.ref(
                                                                  'contract.contract_requested_to_close').id)])
                message = "Contract Requested to Close has been Rejected by " + str(
                    contract.closure_rejected_by.name) + " for following reason.\n" + "Rejection Reason: " + str(
                    self.rejection_reason)
                for rec in activity:
                    rec._action_done(feedback=message, attachment_ids=False)
                contract.message_post(body="Contract Requested to Close has been Rejected by " + str(contract.closure_rejected_by.name),
                                      message_type='notification', author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids, notify_by_email=False)
