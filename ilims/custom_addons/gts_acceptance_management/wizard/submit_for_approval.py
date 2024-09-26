from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class AcceptanceApprovalWizard(models.TransientModel):
    _name = 'acceptance.approval.wizard'

    def _get_users_list_domain(self):
        user_obj = self.env['res.users'].search([])
        users_list = []
        active_id = self.env.context.get('active_id')
        if active_id:
            acceptance = self.env['acceptance.inspection'].search([('id', '=', active_id)], limit=1)
            if acceptance:
                for lines in acceptance.project_id.stakeholder_ids:
                    if lines.status is True:
                        user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user and user.has_group('gts_groups.group_acceptance_management_can_approve'):
                            users_list.append(user.id)
                print('user_list =', users_list)
        return [('id', 'in', users_list)]

    user_id = fields.Many2one('res.users', 'Select Approver', domain=lambda self: self._get_users_list_domain())
    approval_due_date = fields.Date('Approval Due Date')
    acceptance_id = fields.Many2one('acceptance.inspection', 'Acceptance')
    reminder_days = fields.Integer('Activity Reminder')

    @api.model
    def default_get(self, fields):
        rec = super(AcceptanceApprovalWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            acceptance = self.env['acceptance.inspection'].search([('id', '=', active_id)])
            if acceptance:
                for line in acceptance.inspection_lines:
                    if not line.criteria_status:
                        raise UserError(_("You should provide status for all the criteria line!"))
                #     if line.question_type != "qualitative" and not line.uom_id:
                #         raise UserError(
                #             _("You should provide a unit of measure for quantitative acceptance."))
                rec['acceptance_id'] = acceptance.id
        return rec

    def ask_for_approval(self):
        if self.approval_due_date:
            if self.approval_due_date < datetime.now().date():
                raise UserError(_("Approval Date cannot be less then today's date!"))
        if self.acceptance_id:
            self.acceptance_id.due_date = self.approval_due_date
        user_list_from, user_list_cc = "", ""
        if self.acceptance_id.user.id == self.env.user.id:
            user_list_from += self.acceptance_id.user.partner_id.email + ", " or self.acceptance_id.user.login + ", "
        else:
            user_list_from += self.env.user.partner_id.email + ", " or self.env.user.login + ", "
            user_list_cc += self.acceptance_id.user.partner_id.email + ", " or self.acceptance_id.user.login + ", "
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template_id = self.env.ref('gts_acceptance_management.acceptance_submit_for_approval')
        action_id = self.env.ref('gts_acceptance_management.acceptance_inspection_form_view').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (
            self.acceptance_id.id, action_id)
        inspection_url = str(params)
        if template_id:
            values = template_id.generate_email(self.acceptance_id.id,
                                                ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
            values['email_to'] = self.user_id.partner_id.email or self.user_id.login
            values['email_from'] = user_list_from
            values['email_cc'] = user_list_cc
            values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity_dict = {
            'res_model': 'acceptance.inspection',
            'res_model_id': self.env.ref('gts_acceptance_management.model_acceptance_inspection').id,
            'res_id': self.acceptance_id.id,
            'activity_type_id': self.env.ref('gts_acceptance_management.acceptance_requested_for_approval').id,
            'date_deadline': self.approval_due_date,
            'summary': 'Request to Approve the Acceptance',
            'user_id': self.user_id.id
        }
        self.env['mail.activity'].create(activity_dict)
        self.acceptance_id.write({'acceptance_requested_by': self.env.user.id, 'state': 'waiting_for_approval',
                                  'activity_reminder_days': self.reminder_days})
