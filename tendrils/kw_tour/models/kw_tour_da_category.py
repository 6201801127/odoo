# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourDaCategory(models.Model):
    _name = "kw_tour_da_category"
    _description = "Tour DA Category"

    name = fields.Char('DA Category', required=True)
    percentage = fields.Integer('Percentage', required=True)

    @api.model
    def create(self, values):
        result = super(TourDaCategory, self).create(values)
        self.env.user.notify_success("Tour DA category created successfully.")
        return result

    @api.constrains('name')
    def validate_da_category(self):
        regex = re.compile(r"[@_!#$%^&*|<>?/\}{~:]")
        for da_category in self:
            if regex.search(da_category.name) != None:
                raise ValidationError(
                    "Special characters are not allowed in DA category.")
            record = self.env['kw_tour_da_category'].search([]) - da_category
            for info in record:
                if info.name.lower() == da_category.name.lower():
                    raise ValidationError(f"DA Category {da_category.name} already exists.")

    @api.multi
    def write(self, values):
        result = super(TourDaCategory, self).write(values)
        self.env.user.notify_success("Tour DA category updated successfully.")
        return result

    @api.multi
    def name_get(self):
        result = [(record.id, f'{record.name} ({record.percentage} % of DA)') for record in self]
        return result

    @api.constrains('percentage')
    def _check_da_percentage(self):
        for da_category in self:
            if not 0 <= da_category.percentage <= 100:
                raise ValidationError("Percentage should be between 0 to 100.")
