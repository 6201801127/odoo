import datetime
from datetime import timedelta
from odoo import models, fields, api


class ApplicantMeeting(models.TransientModel):
    _name = 'kw_applicant_meeting'
    _description = "Wizard: Quick create multiple meeting for multiple applicants"

    def _default_active_ids(self):
        return self.env['hr.applicant'].browse(self._context.get('active_ids'))

    applicant_ids = fields.Many2many('hr.applicant', string="Applicants", default=_default_active_ids)
    partner_ids = fields.Many2many('res.partner', string='Attendees', domain=[["user_ids", "!=", False]],
                                   default=lambda self: self.env.user.partner_id, required=True)
    survey_id = fields.Many2one('survey.survey', string="Survey", readonly=False,
                                domain="[('survey_type.code', '=', 'recr')]")
    start_datetime = fields.Datetime('Starting at', required=True)
    duration = fields.Float('Duration', required=True)
    location = fields.Char(string='Location', )

    @api.multi
    def schedule_meeting(self):
        calendar = self.env['calendar.event']
        for applicant in self.applicant_ids:
            calendar.create({
                'name': applicant.name,
                'applicant_id': applicant.id,
                'location': self.location if self.location else False,
                'partner_ids': [[6, False, self.partner_ids.ids]],
                'start': self.start_datetime,
                'stop': self.start_datetime + timedelta(hours=self.duration),
                'duration': self.duration,
                'survey_id': self.survey_id.id,
            })
        self.env.user.notify_success("Meeting scheduled")
