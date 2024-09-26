import pytz
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceGraceTimeLog(models.Model):
    _name = 'kw_attendance_grace_time_log'
    _description = 'Attendance Grace Time Log'

    shift_id = fields.Many2one(comodel_name='resource.calendar', string='Shift')
    grace_time = fields.Float(string='Grace Time')
    effective_from = fields.Date(string="Effective From")
    effective_to = fields.Date(string="Effective To")
