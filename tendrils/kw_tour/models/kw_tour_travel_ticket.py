from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourTicketDetails(models.Model):
    _name = "kw_tour_travel_ticket"
    _description = "Ticket Details"

    tour_id = fields.Many2one("kw_tour")
    settlement_id = fields.Many2one("kw_tour_settlement")
    booking_date = fields.Date("Booking Date", required=True)
    travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode", required=True)
    cost = fields.Integer("Ticket Cost", required=True,track_visibility='always')
    service_charges = fields.Integer("Service Charges", required=True)
    document = fields.Binary("Upload Document")
    document_name = fields.Char("File Name")
    travel_ticket_cost_ids = fields.One2many(
        'kw_tour_travel_ticket_cost_log', 'tour_id', string="Travel Ticket Cost Logs")
    currency_id = fields.Many2one("res.currency", "Currency", required=True,
                                  )

    @api.model
    def create(self,vals):
        res = super(TourTicketDetails,self).create(vals)
        # print("create called")
        if res and not res.settlement_id:
            res.tour_id.travel_ticket_cost_ids.create({
                'booking_date': res.booking_date,
                'travel_mode_id': res.travel_mode_id.id,
                'currency_id': res.currency_id.id,
                'cost': ((res.cost if res.cost else 0)+(res.service_charges if res.service_charges else 0)),
                'tour_id': res.tour_id.id,
                'ticket_id': res.id,
            })
        return res


    @api.multi
    def write(self,vals):
        res = super(TourTicketDetails,self).write(vals)
        # print("write called")
        if self and not self.settlement_id:
            self.tour_id.travel_ticket_cost_ids.create({
                'booking_date': self.booking_date,
                'travel_mode_id': self.travel_mode_id.id,
                'currency_id': self.currency_id.id,
                'cost': ((self.cost if self.cost else 0) + (self.service_charges if self.service_charges else 0)),
                'tour_id': self.tour_id.id,
                'ticket_id': self.id,
            })
        return res
            
    # @api.multi
    # def unlink(self):
    #     pass