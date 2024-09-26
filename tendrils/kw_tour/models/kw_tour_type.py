# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourType(models.Model):
    _name = "kw_tour_type"
    _description = "Tour Type"
    _order = "sequence asc"

    name = fields.Char('Name', required=True)
    code = fields.Char("Code", required=True)
    sequence = fields.Integer("sequence")

    @api.constrains('name')
    def validate_tour_type(self):
        # regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for tour_type in self:
            # if regex.search(tour_type.name) != None:
            #     raise ValidationError("Special characters are not allowed in tour type.")

            record = self.env['kw_tour_type'].search([]) - tour_type
            for info in record:
                if info.name.lower() == tour_type.name.lower():
                    raise ValidationError("This Tour type \"" + tour_type.name + "\" already exists.")

    @api.model
    def create(self, values):
        result = super(TourType, self).create(values)
        self.env.user.notify_success("Tour type created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourType, self).write(values)
        self.env.user.notify_success("Tour type updated successfully.")
        return result



class TourTypeNew(models.Model):
    _name = "kw_tour_type_new"
    _description = "Tour Type New"

    name = fields.Char('Name', required=True)
    code = fields.Char("Code", required=True)
