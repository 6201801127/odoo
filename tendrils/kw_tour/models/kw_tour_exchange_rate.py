from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
from datetime import datetime


class TourExchangeRate(models.Model):
    _name = "kw_tour_exchange_rate"
    _description = "Tour Exchange Rate"
    _order = 'date desc'

    date = fields.Date("Date")
    rate = fields.Float("INR Rate")
    kenya_rate = fields.Float("Kenya Rate")
    dubai_rate = fields.Float("Dubai Rate")
    canada_rate = fields.Float("Canada Rate")
    rawanda_rate = fields.Float("Rwanda Rate")

    inr_currency = fields.Many2one('res.currency', string="INR Currency",
                                   default=lambda self: self.env.ref('base.INR'))
    rawanda_currency = fields.Many2one('res.currency', string="Rawanda Currency",
                                       default=lambda self: self.env.ref('base.RWF'))
    kenya_currency = fields.Many2one('res.currency', string="Kenya Currency",
                                     default=lambda self: self.env.ref('base.KES'))
    dubai_currency = fields.Many2one('res.currency', string="Dubai Currency",
                                     default=lambda self: self.env.ref('base.AED'))
    canada_currency = fields.Many2one('res.currency', string="Canada Currency",
                                      default=lambda self: self.env.ref('base.CAD'))

    _sql_constraints = [('date_uniq', 'unique (date)',
                         'Record already exist with same date !')]

    @api.model
    def create(self, values):
        result = super(TourExchangeRate, self).create(values)
        if result.rate <= 0:
            raise ValidationError("Rate cannot be Zero!!")
        self.env.user.notify_success("Exchange Rate created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourExchangeRate, self).write(values)
        if self.rate <= 0:
            raise ValidationError("Rate cannot be Zero!!")
        self.env.user.notify_success("Exchange Rate updated successfully.")
        return result

    @api.model
    def exchange_rate_create(self):
        url = 'https://v6.exchangerate-api.com/v6/8e00f80d0a72c5f255b11b44/latest/USD'
        response = requests.get(url)
        data = response.json()
        if data.get('result') == 'success':
            data_dict = data.get('conversion_rates')
            self.create({
                'date': datetime.now().date(),
                'rate': data_dict.get("INR"),
                'kenya_rate': data_dict.get("KES"),
                'dubai_rate': data_dict.get("AED"),
                'canada_rate': data_dict.get("CAD"),
                'rawanda_rate': data_dict.get("RWF")
            })
