from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class CalendarEventType(models.Model):
    _inherit = "calendar.event.type"
    _order = "name asc"

    max_meeting_hour = fields.Float(string='Maximum Allowed Meeting Hour',)
    code = fields.Char('Code')
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    prefix = fields.Char('Prefix')
    color = fields.Integer(string='Color Index', default=5)
    enable_tracking = fields.Boolean(string="Enable Tracking", default=False)

    # meetings = fields.Many2many(
    #     comodel_name='calendar.event',
    #     relation='meeting_category_rel',
    #     column1='type_id',
    #     column2='event_id',
    #     string='Meetings',
    #     readonly=True)

    # count_meetings  = fields.Integer(compute='_compute_count_meetings',  string="Count Meetings")

    # ----------------------------------------------------------
    # Read 
    # ----------------------------------------------------------

    # @api.depends('meetings')
    # def _compute_count_meetings(self):
    #     for record in self:
    #         record.count_meetings = len(record.meetings)

    @api.constrains('name')
    def validate_name(self):
        if re.match("^[a-zA-Z/\s\-,().]+$", self.name) == None:
            raise ValidationError("Please enter a valid name format.")

    @api.constrains('max_meeting_hour')
    def validate_max_hour(self):
        if self.max_meeting_hour > 14:
            raise ValidationError("Meeting maximum hour should not be greater than 14 hrs.")

    @api.model
    def create(self, vals):
        new_record = super(CalendarEventType, self).create(vals)
        self.env.user.notify_success(message='Event Type created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(CalendarEventType, self).write(vals)
        self.env.user.notify_success(message='Event Type updated successfully.')
        return res

