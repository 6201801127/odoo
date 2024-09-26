# -*- coding: utf-8 -*-
# Commit History
# Model Added 10 june 2021(Gouranga Kala)

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LocationType(models.Model):
    _name = "location.type"
    _description = "Location Type"
    _order = "name asc"

    name = fields.Char("Location")
    description = fields.Text("Description")