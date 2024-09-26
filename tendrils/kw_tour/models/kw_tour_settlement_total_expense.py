from odoo import models, fields


class TourSettlementTotalExpense(models.Model):
    _name = 'kw_tour_settlement_total_expense'
    _description = "Tour Settlement Total Expense"

    settlement_id = fields.Many2one('kw_tour_settlement', 'Settlement', required=True, ondelete='cascade')
    expense_id = fields.Many2one('kw_tour_expense_type', 'Expense', ondelete='restrict')
    amount_inr = fields.Float(string='Amount(Domestic)')
    domestic_currency_id = fields.Many2one('res_currency')
    amount_usd = fields.Float(string='Amount(USD)')
    international_currency_id = fields.Many2one('res_currency')
    travel_prerequisite_id = fields.Many2one("kw_tour_travel_prerequisite", "Travel Prerequisite")

