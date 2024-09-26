from odoo import models, fields, api


class mom_mail_wizard(models.TransientModel):
    _name = "mom_mail_wizard"
    _description = "MoM Mail Wizard"

    meeting_id = fields.Many2one('kw_meeting_events', string="Meeting ID")
    draft_mom_content = fields.Html(string='MOM Content')
    meeting_topic = fields.Char(related='meeting_id.name', string="Meeting topic")

    @api.multi
    def send_mom_mail(self):
        template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_draft_mom_zoom')
        if not template:
            template = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_draft_mom')
        template_data = self.env['mail.template'].browse(template.id)
        template_data.send_mail(self.meeting_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
