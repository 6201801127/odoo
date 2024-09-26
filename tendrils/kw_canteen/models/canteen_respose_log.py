from odoo import models, fields, api
from datetime import date

class CanteenMealFeedBack(models.Model):
    _name = 'kw_canteen_response_log'
    _description = 'Feedback on canteen Meal'

    request_date=fields.Date("Date",default=date.today())
    request = fields.Text('Request')
    response = fields.Text('Response')
