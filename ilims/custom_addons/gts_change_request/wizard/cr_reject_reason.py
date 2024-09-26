from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class RejectCRWizard(models.TransientModel):
    _name = 'reject.cr.wizard'

    rejection_reason = fields.Text('Rejection Reason')
    cr_id = fields.Many2one('change.request', 'CR')

    @api.model
    def default_get(self, fields):
        res = super(RejectCRWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['cr_id'] = self.env.context.get('active_id')
        return res

    def button_reject(self):
        if self.env.context.get('active_id'):
            change_request = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))])
            if change_request:
                change_request.update({
                    'closure_rejected_reason': self.rejection_reason,
                    'cr_closure_rejected_by': self.env.uid,
                    'is_request_to_close': False,
                    'is_closure_rejected': True
                })
                user_list, requested_by, notification_ids = '', '', []
                if change_request.cr_closure_requested_by:
                    requested_by += change_request.cr_closure_requested_by.partner_id.email + "," \
                                    or change_request.cr_closure_requested_by.login + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': change_request.cr_closure_requested_by.partner_id.id,
                        'notification_type': 'inbox'
                    }))
                if change_request.requested_by:
                    requested_by += change_request.requested_by.email + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': change_request.requested_by.id,
                        'notification_type': 'inbox'
                    }))
                if change_request.project_id.user_id:
                    notification_ids.append((0, 0, {
                        'res_partner_id': change_request.project_id.user_id.partner_id.id,
                        'notification_type': 'inbox'}))
                if change_request.project_id.program_manager_id:
                    notification_ids.append((0, 0, {
                        'res_partner_id': change_request.project_id.program_manager_id.partner_id.id,
                        'notification_type': 'inbox'}))
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action_id = self.env.ref('gts_change_request.action_change_request_view').id
                params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (change_request.id, action_id)
                cr_url = str(params)
                template = self.env.ref('gts_change_request.request_cr_rejected_email')
                if template:
                    values = template.generate_email(change_request.id,
                                                     ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = requested_by
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    # values['email_cc'] = user_list
                    values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                activity = self.env['mail.activity'].search(
                    [('res_id', '=', change_request.id), ('res_model', '=', 'change.request'),
                     ('activity_type_id', '=',
                      self.env.ref('gts_change_request.requested_to_close_change_request').id)])
                message = 'Change Request has been Rejected by ' + str(self.env.user.name) + ' for following reason.\n' \
                          + 'Rejection Reason: ' + str(self.rejection_reason)
                for rec in activity:
                    rec._action_done(feedback=message, attachment_ids=False)
                change_request.message_post(body="Change Request Closure has been Rejected by " + str(self.env.user.name),
                                  message_type='notification', author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids, notify_by_email=False)
