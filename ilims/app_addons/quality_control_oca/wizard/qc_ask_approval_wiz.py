from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class QualityMailWizard(models.TransientModel):
    _name = 'quality.mail.wizard'

    def _get_users_list_domain(self):
        user_obj = self.env['res.users'].search([])
        users_list = []
        active_id = self.env.context.get('active_id')
        if active_id:
            quality_inspection = self.env['qc.inspection'].search([('id', '=', active_id)], limit=1)
            if quality_inspection:
                for lines in quality_inspection.project_id.stakeholder_ids:
                    if lines.status is True:
                        user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user and user.has_group('gts_groups.group_quality_management_can_approve'):
                            users_list.append(user.id)
        return [('id', 'in', users_list)]

    user_id = fields.Many2one('res.users', 'Select Approver', domain=lambda self: self._get_users_list_domain())
    approval_due_date = fields.Date('Approval Due Date')
    qc_inspection_id = fields.Many2one('qc.inspection', 'Quality Inspection')
    reminder_days = fields.Integer('Activity Reminder')

    @api.model
    def default_get(self, fields_list):
        rec = super(QualityMailWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            quality_inspection = self.env['qc.inspection'].search([('id', '=', active_id)], limit=1)
            # for line in quality_inspection.inspection_lines:
            #     if line.question_type == "qualitative" and not line.qualitative_value:
            #         raise UserError(_("You should provide answers for all the qualitative questions!"))
            #     if line.question_type != "qualitative" and not line.uom_id:
            #         raise UserError(
            #             _("You should provide a unit of measure for quantitative questions."))
            rec['qc_inspection_id'] = quality_inspection.id
        return rec

    def ask_for_approval(self):
        if self.approval_due_date:
            if self.approval_due_date < datetime.now().date():
                raise UserError(_("Approval Date cannot be Less than Today's Date"))
        if self.qc_inspection_id:
            self.qc_inspection_id.due_date = self.approval_due_date
        user_list_cc = ""
        if self.qc_inspection_id.user.id != self.env.user.id:
            user_list_cc += self.qc_inspection_id.user.partner_id.email + ", " \
                              or self.qc_inspection_id.user.login + ", "
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template_id = self.env.ref('quality_control_oca.quality_test_evaluation_waiting_approval_email')
        action_id = self.env.ref('quality_control_oca.qc_inspection_form_view').id
        params = str(base_url)+ "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (
            self.qc_inspection_id.id, action_id
        )
        inspection_url = str(params)
        if template_id:
            values = template_id.generate_email(self.qc_inspection_id.id,
                                                ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
            values['email_to'] = self.user_id.partner_id.email or self.user_id.login
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['email_cc'] = user_list_cc
            values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity_dict = {
            'res_model': 'qc.inspection',
            'res_model_id': self.env.ref('quality_control_oca.model_qc_inspection').id,
            'res_id': self.qc_inspection_id.id,
            'activity_type_id': self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id,
            'date_deadline': self.approval_due_date,
            'summary': 'Request to Approve the Quality Inspection',
            'user_id': self.user_id.id
        }
        self.env['mail.activity'].create(activity_dict)
        self.qc_inspection_id.write({'quality_requested_by': self.env.uid, 'state': 'waiting',
                                     'activity_reminder_days': self.reminder_days})
