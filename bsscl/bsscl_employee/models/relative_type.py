from odoo import models, fields

class RelativeType(models.Model):
    _name = 'relative.type'
    _description = 'Relative Type'

    name = fields.Char('Name')
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')])