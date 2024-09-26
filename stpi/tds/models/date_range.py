from odoo import models, fields, api, _

class DateRange(models.Model):
    _inherit='date.range'

    tds = fields.Boolean(string='TDS')