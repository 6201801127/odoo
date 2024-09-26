from odoo import api, fields, models, tools, _


class Signature(models.Model):
    _name = "digital_sign"
    _description = "Digital Signature"
    rec_name = "name"

    name = fields.Char(string="CEO Name")
    digital_signat = fields.Binary(string="Digital Signature")

