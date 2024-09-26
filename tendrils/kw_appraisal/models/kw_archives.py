from odoo import models, fields, api
from odoo.exceptions import  ValidationError


class kw_archives_year(models.Model):
    _name = 'kw_archives_year'
    _description = 'Archive year'
    _rec_name    = 'kw_period_id'

    kw_period_id = fields.Integer(string='kw period id')
    period_no = fields.Integer(string='Period Number')
    year = fields.Char(string='Year')