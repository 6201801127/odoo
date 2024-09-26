from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_late_entry_reason_wizard(models.TransientModel):
    _name = 'kw_late_entry_reason_wizard'
    _description = ' Late Entry Reason Wizard'


    late_entries_id = fields.Many2one('kw_daily_employee_attendance', default=lambda self: self.env.context.get('current_late_entry_id'))
    late_entry_reason = fields.Text("Late Entry Reason")

    @api.multi
    def submit_reason(self):
        self.late_entries_id.write({
            'late_entry_reason':self.late_entry_reason,
            'le_state':'1'
        })
        template = self.env.ref('kw_hr_attendance.kw_late_entry_apply_email_template')
        self.env['mail.template'].browse(template.id).send_mail(self.late_entries_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
