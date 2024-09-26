from odoo import models, fields, api


class TourTravelTicketLog(models.Model):
    _name = "kw_tour_travel_ticket_cost_log"
    _description = "Tour Travel Cost Log"

    ticket_id = fields.Many2one("kw_tour_travel_ticket", "Tour Travel ticket", required=True, ondelete='cascade')
    booking_date = fields.Date("Booking Date", required=True)
    travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode", required=True)
    currency_id = fields.Many2one("res.currency", "Currency", required=True)
    cost = fields.Integer("Ticket Cost", required=True,track_visibility='always')
    tour_id = fields.Many2one("kw_tour", "Tour", required=True, ondelete='cascade')
    ticket_status = fields.Selection(string='Tikcet Status',
                              selection=[('Confirm', 'Confirm'),('Cancel', 'Cancel')])
    # travel_ticket_cost_ids = fields.One2many(related='tour_id.action_log_ids', string='Action Logs')
    