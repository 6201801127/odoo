from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingNotifyAssessment(models.TransientModel):
    _name = 'kw_training_notify_assessment'
    _description = "Wizard: send assessment notification mail to participants"

    def _default_active_id(self):
        return self.env['kw_training_assessment'].browse(self._context.get('active_id'))

    def _default_employee_id(self):
        uid = self.env.user.id
        return self.env['hr.employee'].sudo().search([('user_id','=',uid)],limit=1)

    assessment_id = fields.Many2one(
        'kw_training_assessment', string="Assessment", default=_default_active_id)
    employee_ids = fields.Many2many("hr.employee",string="CC:",default=_default_employee_id)

    @api.multi
    def send_assessment_notification_mail(self):
        training = self.assessment_id.training_id
        
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

        template = self.env.ref('kw_training.training_assessment_notification_mail')

        template.with_context(participants=participant_emails,cc_emails=cc_emails).send_mail(self.assessment_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Assessment mail sent successfully.")

        return True