from odoo import api, fields, models, _


class ChangeRequestCategory(models.Model):
    _name = 'cr.category'

    name = fields.Char('Name', track_visibility='always')
