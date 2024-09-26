from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class nhif_master(models.Model):
    _name = 'nhif_master'
    _description = 'NHIF Master'
    
    
    gross_from = fields.Float()
    gross_to = fields.Float()
    nhif = fields.Float("NHIF")