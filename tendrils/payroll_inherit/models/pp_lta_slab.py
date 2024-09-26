from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class PPTalab(models.Model):
    _name = 'pp_lta_slab'
    _description = 'PP And LTA Slab'
    
    
    ctc_from = fields.Float(string="CTC From")
    ctc_to = fields.Float(string="CTC To")
    pp = fields.Float(string='PP')
    lta = fields.Float(string='LTA')
