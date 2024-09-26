from odoo import models, fields ,  api


class TourTravelAdditionalExpenses(models.Model):
    _name = "kw_tour_travel_additional_expense_details"
    _description = "Tour Travel Additional"
    _rec_name = "additional_expense"


    tour_id = fields.Many2one('kw_tour')
    settlement_id = fields.Many2one('kw_tour_settlement')
    additional_expense = fields.Char('Additional Expenses', required=True)
    amount = fields.Float("Amount", required=True)
    document = fields.Binary("Upload Document", required=True)
    document_name = fields.Char("File Name")
    currency_id = fields.Many2one("res.currency", "Currency", required=True)
    remarks = fields.Text('Valid Reason', required=True)
