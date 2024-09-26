from odoo import models,api,fields


class TourtravelExpenseDetails(models.Model):
    _name = 'kw_tour_travel_expense_details'
    _description = "Tour Travel Expense Details"

    tour_id = fields.Many2one(string='Tour', comodel_name='kw_tour', ondelete='cascade', )
    tour_others_id = fields.Many2one(string='Tour Others', comodel_name='kw_tour_others', ondelete='cascade')
    expense_id = fields.Many2one(string='Expense', comodel_name='kw_tour_expense_type', ondelete='restrict')
    no_of_days = fields.Integer(string="No. of days")
    no_of_employee = fields.Integer('No. Of Employee')
    amount_domestic = fields.Float(string='Amount in Domestic', )
    amount_international = fields.Float(string='Amount in International')
    # user_input_amount_domestic = fields.Float(string='Amount in INR For User', )
    # user_input_amount_international = fields.Float(string='Amount in USD For User')
    no_of_night_inr = fields.Integer(string='No. Of Days For Domestic')
    no_of_night_usd = fields.Integer(string='No. Of Days For International')
    tour_csg_id = fields.Many2one('kw_group_tour_csg')
    currency_domestic = fields.Many2one('res.currency', string="Currency Domestic")
    currency_international = fields.Many2one('res.currency', string="Currency International")

  