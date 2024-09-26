from odoo import models, tools, fields, api, _

class AccessType(models.Model):
    _name = 'access.type'
    _description = "Access Type"

    name = fields.Char("Access")
