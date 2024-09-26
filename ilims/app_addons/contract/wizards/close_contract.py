from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class CloseContractWizard(models.TransientModel):
    _name = 'close.contract.wizard'

    def _get_project_stakeholders(self):
        users_obj = self.env['res.users']
        if self.env.context.get('active_id'):
            stakeholder_list, users_list,  = [], []
            contract = self.env['partner.contract'].browse(self.env.context.get('active_id'))
            if contract and contract.related_project and contract.related_project.stakeholder_ids:
                for lines in contract.related_project.stakeholder_ids:
                    if lines.status is True and lines.partner_id:
                        stakeholder_list.append(lines.partner_id.id)
                if stakeholder_list:
                    users = users_obj.search([('partner_id', 'in', stakeholder_list),
                                              ('groups_id', 'in',
                                               self.env.ref('contract.group_contract_close_approval_access').id)])
                    if users:
                        for user in users:
                            users_list.append(user.id)
            return [('id', 'in', users_list)]

    stakeholder_id = fields.Many2one('res.users', 'Approver', domain=lambda self: self._get_project_stakeholders())
    closure_due_date = fields.Date('Closure Due Date')
    closure_reason = fields.Text('Closure Reason')
    reminder_days = fields.Integer('Activity Reminder')

    def button_close(self):
        if self.closure_due_date < datetime.now().date():
            raise UserError(_("Closure Due Date cannot be less then today's date!"))
        if self.env.context.get('active_id'):
            contract = self.env['partner.contract'].search([('id', '=', self.env.context.get('active_id'))])
            if contract:
                contract.update({
                    'closure_reason': self.closure_reason,
                    'closure_requested_by': self.env.uid,
                    'closure_due_date': self.closure_due_date,
                    'is_request_to_close': True,
                    'close_activity_reminder_days': self.reminder_days
                })
                users_obj = self.env['res.users']
                user_list = ''
                for user in users_obj.search([]):
                    if user.has_group('contract.group_contract_close_approval_access'):
                        user_list += user.login + ","
                action_id = self.env.ref('contract.view_partner_contract_form').id
                params = "web#id=%s&view_type=form&model=partner.contract&action=%s" % (contract.id, action_id)
                contract_url = str(params)
                template = self.env.ref('contract.request_to_close_contract_email')
                if template:
                    values = template.generate_email(contract.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = self.stakeholder_id.login
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                # for user in users_obj.search([]):
                #     if user.has_group('contract.group_contract_close_approval_access'):
                if self.stakeholder_id:
                    activity_dict = {
                        'res_model': 'partner.contract',
                        'res_model_id': self.env.ref('contract.model_partner_contract').id,
                        'res_id': contract.id,
                        'activity_type_id': self.env.ref('contract.contract_requested_to_close').id,
                        'date_deadline': self.closure_due_date,
                        'summary': 'Request to Close Contract',
                        'user_id': self.stakeholder_id.id
                    }
                    self.env['mail.activity'].create(activity_dict)
                    contract.message_post(partner_ids=[self.stakeholder_id.partner_id.id],
                                          body="Dear " + str(self.stakeholder_id.name) + " A new request for contract ("
                                               + str(contract.subject) + ") closing approval assigned to you.",
                                          message_type='email', email_from=contract.related_project.outgoing_email)
