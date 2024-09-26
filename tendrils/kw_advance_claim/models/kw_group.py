from odoo import models, fields, api


class kw_group(models.Model):
    _name = 'kw_advance_group'
    _description = 'Kw Group'

    name = fields.Char(string="Group", required=True, track_visibility='onchange')
