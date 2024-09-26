from odoo import models, fields


class AdvacneActionLog(models.Model):
    _name = 'kw_tour_advance_given_log'
    _description = "Tour Advance Given Log"
    _rec_name = "tour_id"

    tour_id = fields.Many2one('kw_tour', 'Apply Tour', required=True, ondelete="cascade")

    requested_inr = fields.Float("Amount Requested(Domestic)")
    old_amount_inr = fields.Float("Previous Amount(Domestic)")
    disbursed_amount_inr = fields.Float("Amount Disbursed(Domestic)")
    new_amount_inr = fields.Float("Total Amount Disbursed(Domestic)")
    currency_domestic_id = fields.Many2one('res.currency')

    requested_usd = fields.Float("Amount Requested(USD)")
    old_amount_usd = fields.Float("Previous Amount(USD)")
    disbursed_amount_usd = fields.Float("Amount Disbursed(USD)")
    new_amount_usd = fields.Float("Total Amount Disbursed(USD)")
    currency_international_id = fields.Many2one('res.currency')

    exchange_rate = fields.Float("Exchange Rate")
