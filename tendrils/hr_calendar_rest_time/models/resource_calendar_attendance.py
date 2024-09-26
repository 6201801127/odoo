# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Resource Calendar Module: Defines the ResourceCalendar class for managing resource calendars in Odoo. Handles scheduling, availability, and working hours of resources. (c) 2020 Creu Blanca, Licensed under AGPL-3.0 or later.
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResourceCalendarAttendance(models.Model):
    """
    Model representing a resource calendar.

    Attributes:
        _inherit (str): Inherited model name.
    """
    _inherit = 'resource.calendar.attendance'
    day_period = fields.Selection([('morning', 'First Half'), ('afternoon', 'Second Half'),('all_day', 'All Day')], required=True, default='morning')
    rest_time = fields.Float(string='Rest Time')

    @api.onchange('rest_time')
    def _onchange_rest_time(self):
        # avoid negative or after midnight
        self.rest_time = min(self.rest_time, 23.99)
        self.rest_time = max(self.rest_time, 0.0)
        # if self.rest_time:
        #     self.day_period = 'all_day'

    @api.constrains('hour_from', 'hour_to', 'rest_time')
    def _check_rest_time(self):
        for record in self:
            if (record.hour_to - record.hour_from < record.rest_time) and not record.calendar_id.cross_shift:
                raise ValidationError(
                    _('Rest time cannot be greater than the interval time')
                )
