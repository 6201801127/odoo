from odoo import api, fields, models


class RejectAcceptanceWizard(models.TransientModel):
    _name = 'reject.acceptance.wizard'

    rejection_reason = fields.Text('Rejection Reason')
    acceptance_id = fields.Many2one('acceptance.inspection', 'Acceptance')

    @api.model
    def default_get(self, fields):
        res = super(RejectAcceptanceWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['acceptance_id'] = self.env.context.get('active_id')
        return res

    def button_reject(self):
        if self.acceptance_id:
            self.acceptance_id.update({
                'rejection_reason': self.rejection_reason,
                'acceptance_rejected_by': self.env.uid,
            })
            user_list, notification_ids = "", []
            if self.acceptance_id.acceptance_requested_by:
                user_list += self.acceptance_id.acceptance_requested_by.partner_id.email + ", " \
                             or self.acceptance_id.acceptance_requested_by.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.acceptance_id.acceptance_requested_by.partner_id.id,
                    'notification_type': 'inbox'}))
            if self.acceptance_id.user:
                user_list += self.acceptance_id.user.partner_id.email + ", " or self.acceptance_id.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.acceptance_id.user.partner_id.id,
                    'notification_type': 'inbox'}))
            action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
            params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (
                self.acceptance_id.id, action_id)
            inspection_url = str(params)
            template = self.env.ref('gts_acceptance_management.acceptance_rejected_mail')
            if template:
                values = template.generate_email(self.acceptance_id.id,
                                                 ['subject', 'email_to', 'email_from', 'body_html'])
                values['email_to'] = user_list
                values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
            activity = self.env['mail.activity'].search(
                [('res_id', '=', self.acceptance_id.id), ('res_model', '=', 'acceptance.inspection'),
                 ('activity_type_id', '=',
                  self.env.ref('gts_acceptance_management.acceptance_requested_for_approval').id)])
            message = 'Acceptance is Rejected by ' + str(self.env.user.name) + '\n Rejection Reason: ' + str(
                self.rejection_reason)
            if activity:
                for rec in activity:
                    rec._action_done(feedback=message)
            self.acceptance_id.message_post(body="Acceptance has Not Accepted",
                              message_type='notification', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
            self.acceptance_id.write({'state': 'failed'})
