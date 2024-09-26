from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class CRRejectWizard(models.TransientModel):
    _name = 'wizard.cr.reject'

    rejection_reason = fields.Text('Rejection Reason')

    def button_reject(self):
        if self.env.context.get('active_id'):
            cr = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))])
            if cr:
                cr.update({
                    'rejected_reason': self.rejection_reason,
                    'cr_rejected_by': self.env.uid,
                })
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action_id = self.env.ref('gts_change_request.view_change_request_form').id
                params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (cr.id, action_id)
                cr_url = str(params)
                template = self.env.ref('gts_change_request.change_request_rejected_email')
                user_list = ''
                if cr.requested_by.email:
                    user_list += cr.requested_by.email + ", "
                if cr.project_id.user_id:
                    user_list += cr.project_id.user_id.partner_id.email + ", "
                if cr.project_id.program_manager_id:
                    user_list += cr.project_id.program_manager_id.partner_id.email + ", "
                if template:
                    values = template.generate_email(cr.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                activity = self.env['mail.activity'].search([('res_id', '=', cr.id),
                                                             ('res_model', '=', 'change.request'),
                                                             ('activity_type_id', '=',
                                                              self.env.ref('gts_change_request.approve_change_request').id)])
                message = "CR Rejected by " + str(self.env.user.name) + " for following reason.\n" +\
                          "Rejection Reason: " + str(self.rejection_reason)
                for rec in activity:
                    rec._action_done(feedback=message, attachment_ids=False)
                notification_ids = []
                for record in cr:
                    if record.project_id.user_id:
                        notification_ids.append((0, 0, {
                            'res_partner_id': record.project_id.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                    if record.project_id.program_manager_id:
                        notification_ids.append((0, 0, {
                            'res_partner_id': record.project_id.program_manager_id.partner_id.id,
                            'notification_type': 'inbox'}))
                    if record.requested_by:
                        notification_ids.append((0, 0, {
                            'res_partner_id': record.requested_by.id,
                            'notification_type': 'inbox'}))
                cr.message_post(body="Change Request has been Rejected by " + str(self.env.user.name),
                                message_type='notification', author_id=self.env.user.partner_id.id,
                                notification_ids=notification_ids, notify_by_email=False)
                cr.write({'state': 'rejected'})
