from odoo import fields, models, api,_
from odoo.exceptions import ValidationError
from datetime import datetime


class UpdateAdvertisement(models.TransientModel):
    _name = 'update.advertisement'
    _description = 'Update Advertisement'

    last_date = fields.Date('Last Date')
    advertisement_id = fields.Many2one('hr.requisition.application', invisible=1)



    def update_last_date(self):
        if self.last_date:
            if self.advertisement_id.start_date and self.advertisement_id.start_date < self.last_date:
                self.advertisement_id.last_date = self.last_date
        else:
            raise ValidationError(
                _('Advertisement start date must be less than last date'))

