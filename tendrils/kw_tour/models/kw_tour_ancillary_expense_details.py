from odoo import api, fields, models


class TourAncillaryExpense(models.Model):
    _name = "kw_tour_ancillary_expense_details"
    _description = "Tour Ancillary Expenses"
    _rec_name = "ancillary_expense_id"

    tour_id = fields.Many2one('kw_tour', required=True, ondelete="cascade")
    ancillary_expense_id = fields.Many2one("kw_tour_ancillary_expenses", "Ancillary Head", required=True)
    amount = fields.Float("Amount", required=True, )
    description = fields.Text("Description")
    currency_id = fields.Many2one("res.currency", "Currency", required=True)

