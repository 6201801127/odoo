from odoo import models, fields, api, _ 

class TravelBooking(models.Model):
    _name = "travel.booking"
    _description = "Tour Travel Booking"

    tour_id = fields.Many2one(comodel_name="bsscl.tour", string="Tour")
    settlement_id = fields.Many2one(comodel_name="tour.settlement", string="Tour Settlement")
    travel_mode = fields.Selection(selection =[('1','By aeroplane'),('2','By bus'),('3','By train'),('4','By Taxi'),('5','Others')])
    other_travel_mode = fields.Char(string="Other Travel Mode")
    travel_from = fields.Char(string="Travel From")
    travel_to = fields.Char(string="Travel To")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')
    travel_cost = fields.Float(string="Travel Cost")
    amount_total = fields.Float(string="Total")
    # travel_doc = fields.Binary()