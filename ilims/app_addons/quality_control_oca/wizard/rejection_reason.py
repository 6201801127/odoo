from odoo import api, fields, models


class RejectQualityWizard(models.TransientModel):
    _name = 'reject.quality.wizard'

    rejection_reason = fields.Text('Rejection Reason')
    qc_inspection_id = fields.Many2one('qc.inspection', 'Acceptance')

    @api.model
    def default_get(self, fields):
        res = super(RejectQualityWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['qc_inspection_id'] = self.env.context.get('active_id')
        return res

    def button_reject(self):
        if self.qc_inspection_id:
            self.qc_inspection_id.update({
                'rejection_reason': self.rejection_reason,
                'quality_rejected_by': self.env.uid,
            })
            user_list, notification_ids = "", []
            if self.qc_inspection_id.quality_requested_by.id == self.qc_inspection_id.user.id:
                user_list += self.qc_inspection_id.user.partner_id.email + ", " \
                             or self.qc_inspection_id.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.qc_inspection_id.user.partner_id.id,
                    'notification_type': 'inbox'}))
            else:
                user_list += self.qc_inspection_id.user.partner_id.email + ", " \
                             or self.qc_inspection_id.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.qc_inspection_id.user.partner_id.id,
                    'notification_type': 'inbox'}))
                user_list += self.qc_inspection_id.quality_requested_by.partner_id.email + ", "\
                             or self.qc_inspection_id.quality_requested_by.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.qc_inspection_id.quality_requested_by.partner_id.id,
                    'notification_type': 'inbox'}))
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('quality_control_oca.qc_inspection_form_view').id
            params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (
                self.qc_inspection_id.id, action_id)
            inspection_url = str(params)
            template = self.env.ref('quality_control_oca.quality_rejected_mail')
            if template:
                values = template.generate_email(self.qc_inspection_id.id,
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
                [('res_id', '=', self.qc_inspection_id.id), ('res_model', '=', 'qc.inspection'),
                 ('activity_type_id', '=',
                  self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id)])
            message = 'Quality Inspection is Rejected by ' + str(self.env.user.name) + '\n Rejection Reason: ' + str(
                self.rejection_reason)
            if activity:
                for rec in activity:
                    rec._action_done(feedback=message)
            self.qc_inspection_id.message_post(body="Quality Inspection Approved",
                              message_type='notification', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
            self.qc_inspection_id.write({'state': 'rejected'})
