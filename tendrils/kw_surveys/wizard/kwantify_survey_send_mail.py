from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions, _


class kwantify_survey_send_mail(models.TransientModel):
    _name = 'kwantify_survey_send_mail'
    _description = 'mail Survey wizard'

    def _get_default_kwantify_survey(self):
        datas = self.env['kw_surveys'].browse(self.env.context.get('active_ids'))
        return datas

    surveys = fields.Many2many('kw_surveys', readonly=1, default=_get_default_kwantify_survey)

    @api.multi
    def send_mail_survey(self):
        current_emp_email = self.env.user.employee_ids[-1].work_email

        survey_details = self.surveys.mapped('survey_details_id').filtered(lambda r: r.state in ['1', '2'])

        template = self.env.ref('kw_surveys.kwantify_surveys_email_template')

        for details in survey_details:
            subject = details.kw_surveys_id.email_subject_line
            body = details.kw_surveys_id.email_body
            template.with_context(user_email=current_emp_email, kw_email_body=body, kw_subject_line=subject).send_mail(
                details.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Mail Sent Successfully.")
        return {'type': 'ir.actions.act_window_close'}
