# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_meeting_amenity_master(models.Model):
    _name = 'kw_meeting_amenity_master'
    _description = 'Amenities'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Amenity name already exists !')
    ]

    @api.constrains('name')
    def validate_amenity_name(self):
        if re.match("^[0-9a-zA-Z/\s\-.]+$", self.name) == None:
            raise ValidationError("Please enter a valid name format.")

    @api.model
    def create(self, vals):
        new_record = super(kw_meeting_amenity_master, self).create(vals)
        self.env.user.notify_success(message='Amenity created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_meeting_amenity_master, self).write(vals)
        self.env.user.notify_success(message='Amenity updated successfully.')
        return res
