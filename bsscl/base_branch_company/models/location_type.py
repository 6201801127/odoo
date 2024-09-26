# -*- coding: utf-8 -*-
from odoo import fields, models

class LocationType(models.Model):
    _name = "location.type"
    _description = "Location Type"
    _order = "name asc"

    name = fields.Char("Location")
    description = fields.Text("Description")