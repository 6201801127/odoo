# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourancillaryExpense(models.Model):
    _name = "kw_tour_ancillary_expenses"
    _description = "Tour City Ancillary"

    name = fields.Char("Ancillary", required=True)
    no_of_days = fields.Integer('Applicable (Days)', required=True, default=0)
    description = fields.Text("Description")

    @api.constrains('name')
    def validate_kw_tour_ancillary_expenses(self):
        regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for ancillary in self:
            if regex.search(ancillary.name) != None:
                raise ValidationError(
                    "Special characters are not allowed in Ancillary expense.")
            record = self.env['kw_tour_ancillary_expenses'].search([]) - ancillary
            for info in record:
                if info.name.lower() == ancillary.name.lower():
                    raise ValidationError(
                        f"The ancillary expense {ancillary.name} already exists.Please try another one.")

    @api.model
    def create(self, values):
        result = super(TourancillaryExpense, self).create(values)
        self.env.user.notify_success("Ancillary expense created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourancillaryExpense, self).write(values)
        self.env.user.notify_success("Ancillary expense(s) updated successfully.")
        return result
