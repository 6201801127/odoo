from odoo import models, fields ,  api


class TourTravelPrerequisite(models.Model):
    _name = "kw_tour_travel_prerequisite_details"
    _description = "Tour Travel Prerequisite"
    _rec_name = "travel_prerequisite_id"


    tour_id = fields.Many2one('kw_tour')
    settlement_id = fields.Many2one('kw_tour_settlement')
    travel_prerequisite_id = fields.Many2one("kw_tour_travel_prerequisite", "Travel Prerequisite", required=True)
    amount = fields.Float("Amount", required=True)
    document = fields.Binary("Upload Document")
    document_name = fields.Char("File Name")
    currency_id = fields.Many2one("res.currency", "Currency", required=True)
