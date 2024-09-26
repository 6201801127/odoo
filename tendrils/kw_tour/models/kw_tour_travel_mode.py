from odoo import models, fields


class TourTravelMode(models.Model):
    _name = "kw_tour_travel_mode"
    _description = "Tour Travel Mode"

    name = fields.Char("Mode", required=True)
    code = fields.Char("Code")
