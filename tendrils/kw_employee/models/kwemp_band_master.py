# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.exceptions import ValidationError


class kwemp_band_master(models.Model):
    _name = 'kwemp_band_master'
    _description = "Employment Band"

    name = fields.Char(string="Band", required=True, size=50)
    description = fields.Text(string="Description", )
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of records.")
    active = fields.Boolean('Active', default=True)
    send_consolidated_mail = fields.Boolean(string="Send Consolidated Email",
                                            help="It is for consolidated mail send check")

    @api.constrains('name', )
    def validate_organization_type(self):
        record = self.env['kwemp_band_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The band \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_band_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='Employee Band created successfully.')
        else:
            self.env.user.notify_danger(message='Employee Band creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_band_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Band updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Band updation failed.')
        return res
