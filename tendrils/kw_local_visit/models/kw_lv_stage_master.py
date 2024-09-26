# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_stage_master(models.Model):
    _name = 'kw_lv_stage_master'
    _description =  "Local visit stage details"

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name')