from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from datetime import datetime,date

class kw_update_date_wizard(models.TransientModel):
    _name       ='kw_update_date_wizard'
    _description= 'Update Date wizard'

    def _get_default_assessment_feedback(self):
        datas   = self.env['kw_feedback_details'].browse(self.env.context.get('active_ids'))
        return datas

    feedback = fields.Many2many('kw_feedback_details', readonly=1, default=_get_default_assessment_feedback)
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    assessment_date = fields.Date(string='Assessment Date')

    @api.onchange('from_date','to_date','assessment_date')
    def publish_date_validation(self):
        if self.from_date and self.to_date and (self.from_date > self.to_date):
            raise ValidationError('End date must be greater than start date.')
        if self.assessment_date and self.assessment_date < date.today():
            raise ValidationError('Assessment date must be greater than current date.')

    @api.multi
    def update_date(self):
        self.ensure_one()
        if self._context.get('value1'):
            for record in self.feedback:
                if record.feedback_status in ['0', '1', '2']:
                    record.write({
                        'assessment_from_date': self.from_date,
                        'assessment_to_date': self.to_date
                    })
                for rec in record.feedback_final_config_id:
                    template = self.env.ref('kw_assessment_feedback.kw_schedule_periodic_feedback_email_template')
                    if template:
                        template.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Periodic Date Updated Successfully.")

        elif self._context.get('value2'):
            for record in self.feedback:
                if record.feedback_status in ['0', '1', '2']:
                    record.write({
                        'assessment_date': self.assessment_date
                    })
                for rec in record.assessment_tagging_id:
                    template = self.env.ref('kw_assessment_feedback.kw_schedule_probationary_feedback_email_template')
                    if template:
                        template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Final Assessment Date Updated Successfully.")
        else:
            pass

        return {'type': 'ir.actions.act_window_close'}
