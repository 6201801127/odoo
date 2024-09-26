# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourTravelPrerequisite(models.Model):
    _name = "kw_tour_travel_prerequisite"
    _description = "Tour Travel Prerequisite"

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")

    @api.model
    def create(self, values):
        result = super(TourTravelPrerequisite, self).create(values)
        self.env.user.notify_success("Travel prerequisite created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourTravelPrerequisite, self).write(values)
        self.env.user.notify_success("Travel prerequisite updated successfully.")
        return result
