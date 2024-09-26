from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class ApprovalEmailWizard(models.TransientModel):
    _name = 'approval.email.wizard'

    def _get_users_list_domain(self):
        user_obj = self.env['res.users'].search([])
        users_list = []
        active_id = self.env.context.get('active_id')
        if active_id:
            contract = self.env['partner.contract'].search([('id', '=', active_id)], limit=1)
            if contract:
                for lines in contract.related_project.stakeholder_ids:
                    if lines.status is True:
                        user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user and user.has_group('contract.group_contract_approver'):
                            users_list.append(user.id)
                print('user_list =', users_list)
        return [('id', 'in', users_list)]

    user_id = fields.Many2one('res.users', 'Select Approver', domain=lambda self: self._get_users_list_domain())
    approval_due_date = fields.Date('Approval Due Date')
    contract_id = fields.Many2one('partner.contract', 'Contract')
    reminder_days = fields.Integer('Activity Reminder')

    @api.model
    def default_get(self, fields):
        rec = super(ApprovalEmailWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            contract = self.env['partner.contract'].search([('id', '=', active_id)])
            if not contract.attach_draft_contract:
                raise ValidationError(_("Please attach Unsigned Contract before sending for Approval!"))
            rec['contract_id'] = contract.id
        return rec

    def ask_for_approval(self):
        if self.approval_due_date:
            if self.approval_due_date < datetime.now().date():
                raise UserError(_("Approval Date cannot be less then today's date!"))
        if self.contract_id:
            self.contract_id.approval_due_date = self.approval_due_date
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template_id = self.env.ref('contract.ask_for_approval_email')
        action_id = self.env.ref('contract.view_partner_contract_form').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=partner.contract&action=%s" % (
            self.contract_id.id, action_id
        )
        contract_url = str(params)
        if template_id:
            values = template_id.generate_email(self.contract_id.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = self.user_id.partner_id.email or self.user_id.login
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity_dict = {
            'res_model': 'partner.contract',
            'res_model_id': self.env.ref('contract.model_partner_contract').id,
            'res_id': self.contract_id.id,
            'activity_type_id': self.env.ref('contract.contract_ask_for_approval').id,
            'date_deadline': self.approval_due_date,
            'summary': 'Request to Approve the Contract',
            'user_id': self.user_id.id
        }
        self.env['mail.activity'].create(activity_dict)
        self.contract_id.message_post(partner_ids=[self.user_id.partner_id.id],
                                      body="Dear " + str(self.user_id.name) + " A new request for contract ("
                                           + str(self.contract_id.subject) + ") approval assigned to you.",
                                      message_type='email', email_from=self.contract_id.related_project.outgoing_email)
        self.contract_id.write({'contract_requested_by': self.env.uid, 'state': 'waiting_for_approval',
                                'activity_reminder_days': self.reminder_days})
