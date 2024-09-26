from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class CRSubmitApproval(models.TransientModel):
    _name = 'cr.approval.wizard'

    def _get_users_list_domain(self):
        user_obj = self.env['res.users'].search([])
        users_list = []
        active_id = self.env.context.get('active_id')
        if active_id:
            cr = self.env['change.request'].search([('id', '=', active_id)], limit=1)
            if cr:
                for lines in cr.project_id.stakeholder_ids:
                    if lines.status is True:
                        user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user and user.has_group('gts_change_request.group_cr_approval_access'):
                            users_list.append(user.id)
        return [('id', 'in', users_list)]

    user_id = fields.Many2one('res.users', 'Select Approver', domain=lambda self: self._get_users_list_domain())
    approval_due_date = fields.Date('Approval Due Date')
    reminder_days = fields.Integer('Activity Reminder')

    def ask_for_approval(self):
        if self.approval_due_date:
            if self.approval_due_date < datetime.now().date():
                raise UserError(_("Approval Date cannot be less then today's date!"))
        cr = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))], limit=1)
        if cr:
            cr.approval_due_date = self.approval_due_date
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            template_id = self.env.ref('gts_change_request.change_request_submit_for_approval')
            action_id = self.env.ref('gts_change_request.view_change_request_form').id
            params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (cr.id, action_id)
            cr_url = str(params)
            if template_id:
                values = template_id.generate_email(cr.id, ['subject', 'email_to', 'email_from', 'body_html'])
                values['email_to'] = self.user_id.partner_id.email or self.user_id.login
                values['email_from'] = cr.requested_by.email
                values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
            activity_dict = {
                'res_model': 'change.request',
                'res_model_id': self.env.ref('gts_change_request.model_change_request').id,
                'res_id': cr.id,
                'activity_type_id': self.env.ref('gts_change_request.approve_change_request').id,
                'date_deadline': self.approval_due_date,
                'summary': 'Request to Approve the Contract',
                'user_id': self.user_id.id
            }
            self.env['mail.activity'].create(activity_dict)
            cr.write({'state': 'waiting_for_approval', 'activity_reminder_days': self.reminder_days})
