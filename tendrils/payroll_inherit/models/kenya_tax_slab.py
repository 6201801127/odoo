from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class KenyaTalab(models.Model):
    _name = 'kenya_tax_slab'
    _description = 'Kenya Tax Slab'
    
    
    amount_from = fields.Float()
    amount_to = fields.Float()
    rate = fields.Float()
