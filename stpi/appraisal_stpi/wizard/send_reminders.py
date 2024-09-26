from odoo import api, fields, models,_


class SendTdsReminder(models.TransientModel):
    _name = 'send.tds.reminder'
    _description = 'Send Reminder'



    def send_reminder_action_button(self):
        id_dec = self.env['hr.declaration'].search([('state', 'in', ['draft','to_approve','approved'])])
        for rec in id_dec:
            template_id = rec.env.ref('tds.email_template_tds').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
