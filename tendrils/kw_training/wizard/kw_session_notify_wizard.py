from odoo import models, fields, api
from odoo.exceptions import  ValidationError

class TrainingNotifySession(models.TransientModel):
    _name = 'kw_training_notify_session'
    _description = "Wizard: send notification mail to participants"

    def _default_active_ids(self):
        return self.env['kw_training_schedule'].browse(self._context.get('active_ids'))

    def _default_employee_id(self):
        uid = self.env.user.id
        return self.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)

    schedule_ids = fields.Many2many('kw_training_schedule', string="Sessions", default=_default_active_ids)
    employee_ids = fields.Many2many("hr.employee", string="CC:", default=_default_employee_id)

    @api.multi
    def send_notification_mail(self):
        training = self.schedule_ids.mapped('training_id')

        if len(training) >1:
            raise ValidationError("Please select session(s) of a single training.")

        participant_emails = ''
        cc_emails = ''
        cc_employees = self.env['hr.employee']

        if self.employee_ids:
            cc_employees |= self.employee_ids

        if training.plan_ids:
            if training.plan_ids[0].participant_ids:
                participant_emails = ','.join(training.plan_ids[0].participant_ids.mapped('work_email'))
                cc_employees |= training.plan_ids[0].participant_ids.mapped('parent_id')
            if training.plan_ids[0].internal_user_ids:
                cc_employees |= training.plan_ids[0].internal_user_ids

        if cc_employees:
            cc_emails =  ','.join(cc_employees.mapped('work_email'))

        template = self.env.ref('kw_training.training_session_notification_mail')

        template.with_context(participants=participant_emails, cc_emails=cc_emails,
                              session_ids=self.schedule_ids).send_mail(training.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        self.env.user.notify_success("Notification mail sent successfully.")
