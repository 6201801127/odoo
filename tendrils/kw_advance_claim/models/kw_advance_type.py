from odoo import models, fields, api


class kw_advance_type(models.Model):
    _name = 'kw_advance_type'
    _description = 'Advance Type'

    name = fields.Char(string='Advance Type', required=True)
    alias = fields.Char(string='Alias', required=True)
