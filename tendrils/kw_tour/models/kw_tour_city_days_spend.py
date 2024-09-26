from odoo import models, fields


class TourCityDaysSpend(models.Model):
    _name = 'kw_tour_city_days_spend'
    _description = "Tour City wise Days Spend"

    tour_id = fields.Many2one("kw_tour", required=True, ondelete='cascade')
    city_id = fields.Many2one("kw_tour_city", "Place Of Expense", required=True)
    actual_no = fields.Integer('Actual No. Of Days', required=True, default=0)
    no_of_nights = fields.Integer('No. Of Days', required=True, default=0)
