from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta

class OverallRate(models.Model):
    _name = 'overall.rate'
    _description = 'Overall Rate'

    from_int = fields.Integer('From')
    to_int = fields.Integer('To')
    name = fields.Char('Name')
