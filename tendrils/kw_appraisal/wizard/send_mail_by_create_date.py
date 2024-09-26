from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class Sendmail(models.TransientModel):
    _name           = 'send_mail_by_create_date'
    _description    = "Send Mail Wizard"
    
    created_date = fields.Date()
    
    
    def send_email_appraisal_fillup(self):
        if self.created_date:
            start_datetime = datetime.combine(self.created_date, datetime.min.time())
            end_datetime = datetime.combine(self.created_date, datetime.max.time())
            # Search for HR appraisal records created within the specified date
            appraisal_recs = self.env['hr.appraisal'].search([('create_date', '>=', start_datetime),('create_date', '<=', end_datetime),('kw_ids', '=', self.env.context.get('active_id'))])
            for record in appraisal_recs:
                try:
                    if appraisal_recs:
                        mail_template    = self.env.ref('kw_appraisal.kw_employee_appraisal_draft_email_template')
                        mail_template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                except Exception as e:
                    pass
            return True