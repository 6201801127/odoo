from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class RejectContractWizard(models.TransientModel):
    _name = 'reject.contract.wizard'

    rejection_reason = fields.Text('Rejection Reason')

    def button_reject(self):
        if self.env.context.get('active_id'):
            contract = self.env['partner.contract'].search([('id', '=', self.env.context.get('active_id'))])
            if contract:
                contract.update({
                    'rejection_reason': self.rejection_reason,
                    'contract_rejected_by': self.env.uid,
                })
                history_dict = {
                    'contract_id': contract.id,
                    'rejected_by': self.env.uid,
                    'reason': self.rejection_reason
                }
                self.env['contract.rejection.history'].create(history_dict)
                users_obj = self.env['res.users']
                user_list, notification_ids = '', []
                for user in users_obj.search([]):
                    if user.has_group('contract.group_contract_approver'):
                        if user.partner_id.email:
                            user_list += user.partner_id.email + ","
                        else:
                            user_list += user.login + ","
                        notification_ids.append((0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'}))
                if contract.closure_requested_by:
                    user_list += contract.closure_requested_by.partner_id.email or contract.closure_requested_by.login
                    notification_ids.append((0, 0, {
                        'res_partner_id': contract.closure_requested_by.partner_id.id,
                        'notification_type': 'inbox'}))
                action_id = self.env.ref('contract.view_partner_contract_form').id
                params = "web#id=%s&view_type=form&model=partner.contract&action=%s" % (contract.id, action_id)
                contract_url = str(params)
                template = self.env.ref('contract.rejected_email_template_contract')
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
                                                              self.env.ref('contract.contract_ask_for_approval').id)])
                message = "Contract Rejected by " + str(
                    contract.contract_rejected_by.name) + " for following reason.\n" + "Rejection Reason: " + str(
                    contract.rejection_reason)
                for rec in activity:
                    rec._action_done(feedback=message, attachment_ids=False)
                contract.message_post(body="Contract has been Rejected by " + str(self.env.user.name),
                                      message_type='notification', author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids, notify_by_email=False)
                contract.write({'state': 'rejected'})
