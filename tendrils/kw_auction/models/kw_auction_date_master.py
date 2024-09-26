from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date


class KwAuctionDateMaster(models.Model):
    _name = 'kw_auction_date_master'
    _rec_name = 'complete_name'

    date_from = fields.Date(string = 'Date From')
    date_to = fields.Date(string = 'Date To')
    complete_name = fields.Char(string='Complete Name', compute='_compute_concatenated_dates', store=True)


    @api.depends('date_from', 'date_to')
    def _compute_concatenated_dates(self):
        for record in self:
            concatenated_date = ''
            if record.date_from and record.date_to:
                concatenated_date = str(record.date_from) + ' to ' + str(record.date_to)
            record.complete_name = concatenated_date


    @api.model
    def create(self, vals):
        existing_record = self.env['kw_auction_date_master'].search([], limit=1)
        if existing_record:
            raise ValidationError("Only one record is allowed.")
        return super(KwAuctionDateMaster, self).create(vals)
    

    @api.constrains('date_from', 'date_to')
    def check_date_range(self):
        if self.date_from and self.date_to:
            if self.date_to < date.today():
                raise ValidationError("Date To must be greater than or equal to today's date.")
            if self.date_from > self.date_to:
                raise ValidationError("Date To must be greater then or equal to Date From")
           
            
    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(('You cannot duplicate a record.'))
    
    @api.multi
    def unlink(self):
        raise UserError('You have no access to delete this record.')