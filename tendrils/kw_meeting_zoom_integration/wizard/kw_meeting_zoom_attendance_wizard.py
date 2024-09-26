from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions,_
from datetime import date

class kw_meeting_zoom_wizard(models.Model):
    _name='kw_meeting_zoom_wizard'
    _description = 'Meeting Zoom wizard'

    def _get_default_confirm(self):
        datas = self.env['kw_meeting_events'].browse(self.env.context.get('active_ids'))
        return datas

    meeting_events_id = fields.Many2one('kw_meeting_events',string="Meeting Event Id", store=True, readonly=True,required=True)
    duration = fields.Selection(string="Duration",related='meeting_events_id.kw_duration')
    kw_start_meeting_date = fields.Date(string="Start Date",related='meeting_events_id.kw_start_meeting_date')
    kw_start_meeting_time = fields.Selection(string="Start Time",related='meeting_events_id.kw_start_meeting_time')
    # attendee_ids = fields.Many2many('kw_meeting_attendee','kw_meeting_attendee_kw_meeting_zoom_wizard_rel' , ondelete='cascade')
    attendee_ids = fields.One2many('kw_meeting_attendee','attendace_wizard_id',string='Attendees')
