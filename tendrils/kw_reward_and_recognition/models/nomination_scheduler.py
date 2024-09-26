from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NominationLog(models.Model):
    _name = 'nomination_log'
    _description = 'STARLIGHT '

    send_to = fields.Char(string='To')
    send_from = fields.Char(string='From')
    status = fields.Char(string='Status')
    date = fields.Date(string='Date')
