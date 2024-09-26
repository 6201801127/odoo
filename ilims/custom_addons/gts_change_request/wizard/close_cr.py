from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class CloseCRWizard(models.TransientModel):
    _name = 'close.cr.wizard'

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
                        if user and user.has_group('gts_change_request.group_cr_close_approval_access'):
                            users_list.append(user.id)
        return [('id', 'in', users_list)]

    user_id = fields.Many2one('res.users', 'Select Approver', domain=lambda self: self._get_users_list_domain())
    closure_reason = fields.Text('Reason to Close CR')
    closure_due_date = fields.Date('Closure Due Date')
    cr_id = fields.Many2one('change.request', 'CR')
    reminder_days = fields.Integer('Activity Reminder')

    @api.model
    def default_get(self, fields):
        res = super(CloseCRWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['cr_id'] = self.env.context.get('active_id')
        return res

    def button_close(self):
        if self.closure_due_date < datetime.now().date():
            raise UserError(_("Closure Due Date cannot be less then today's date!"))
        if self.env.context.get('active_id'):
            change_request = self.env['change.request'].search([('id', '=', self.env.context.get('active_id'))])
            if change_request:
                change_request.update({
                    'closure_reason': self.closure_reason,
                    'cr_closure_requested_by': self.user_id.id,
                    'closure_due_date': self.closure_due_date,
                    'is_request_to_close': True,
                    'is_closure_rejected': False,
                    'close_activity_reminder_days': self.reminder_days
                })
                user_cc = ''
                if change_request.requested_by.id != self.env.user.partner_id.id:
                    user_cc += change_request.requested_by.email
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action_id = self.env.ref('gts_change_request.action_change_request_view').id
                params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (change_request.id, action_id)
                cr_url = str(params)
                template = self.env.ref('gts_change_request.request_to_close_cr_email')
                if template:
                    values = template.generate_email(change_request.id,
                                                     ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
                    values['email_to'] = self.user_id.partner_id.email or self.user_id.login
                    values['email_from'] = self.env.user.partner_id.email
                    values['email_cc'] = user_cc
                    values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                activity_dict = {
                    'res_model': 'change.request',
                    'res_model_id': self.env.ref('gts_change_request.model_change_request').id,
                    'res_id': change_request.id,
                    'activity_type_id': self.env.ref(
                        'gts_change_request.requested_to_close_change_request').id,
                    'date_deadline': self.closure_due_date,
                    'summary': 'Requested to Close for the following reason.\n' + 'Closure Reason: ' + str(
                        self.closure_reason),
                    'user_id': self.user_id.id
                }
                self.env['mail.activity'].create(activity_dict)
