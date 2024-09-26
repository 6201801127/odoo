import base64
from odoo import models, fields, api


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    feedback_url = fields.Text(string='Evaluators', compute="_compute_feedback_url", store=False)

    def _compute_feedback_url(self):
        token = self.env['survey.user_input'].sudo().search([('meeting_id', '=', self.event_id.id), ('partner_id', '=', self.partner_id.id),
                                                             ('survey_id', '=', self.event_id.survey_id.id)])
        # print(token)
        trail = "/%s" % token.token if token.token else ""
        survey_url = self.env['survey.survey'].sudo().search([('id', '=', self.event_id.survey_id.id)]).recruitment_survey_url
        self.feedback_url = "%s%s" % (survey_url if survey_url else "", trail)
        # print(self.feedback_url)
        return True

    @api.multi
    def _send_mail_to_attendees(self, template_xmlid, force_send=True):
        res = False
        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        # get ics file for all meetings
        ics_files = self.mapped('event_id')._get_ics_file()

        # prepare rendering context for mail template
        colors = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }
        rendering_context = dict(self._context)
        rendering_context.update({
            'color': colors,
            'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
            'dbname': self._cr.dbname,
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
        })
        invitation_template = invitation_template.with_context(rendering_context)

        # send email with attachments
        mails_to_send = self.env['mail.mail']
        for attendee in self:
            if attendee.email or attendee.partner_id.email:
                # FIXME: is ics_file text or bytes?
                ics_file = ics_files.get(attendee.event_id.id)
                mail_id = invitation_template.send_mail(attendee.id, notif_layout='mail.mail_notification_light')

                vals = {}
                if ics_file:
                    vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                      'mimetype': 'text/calendar',
                                                      'datas_fname': 'invitation.ics',
                                                      'datas': base64.b64encode(ics_file)})]
                # We don't want to have the mail in the chatter while in queue!
                vals['model'] = None
                vals['res_id'] = False
                current_mail = self.env['mail.mail'].browse(mail_id)
                current_mail.mail_message_id.write(vals)
                mails_to_send |= current_mail

        if force_send and mails_to_send:
            res = mails_to_send.send()

        return res
