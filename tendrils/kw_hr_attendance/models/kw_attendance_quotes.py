from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceQuotes(models.Model):
    _name = 'kw_attendance_quotes'
    _description = 'Attendance Quotes'
    _order = 'name asc'

    name = fields.Text(string="Quote", required=True)
    sunday = fields.Boolean(string='Sunday')
    monday = fields.Boolean(string='Monday')
    tuesday = fields.Boolean(string='Tuesday')
    wednesday = fields.Boolean(string='Wednesday')
    thursday = fields.Boolean(string='Thursday')
    friday = fields.Boolean(string='Friday')
    saturday = fields.Boolean(string='Saturday')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.constrains('name')
    def _check_quote_size(self):
        for quote in self:
            if len(quote.name) > 500:
                raise ValidationError('Number of characters must be within 500')

    @api.constrains('from_date', 'to_date')
    def _validate_date(self):
        for quote in self:
            if (quote.from_date and quote.to_date) and (quote.from_date > quote.to_date):
                raise ValidationError("To date should be greater than from date.")
