# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.exceptions import ValidationError


class kwemp_grade_master(models.Model):
    _name = 'kwemp_grade_master'
    _description = "Employment Grades Master"

    name = fields.Char(string="Grade", required=True, size=50)
    description = fields.Text(string="Description")
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of records.")
    has_band = fields.Boolean(string="Has Band", default=True, help="Marks specific Grade contains Bands.")
    active = fields.Boolean('Active', default=True)
    send_consolidated_mail = fields.Boolean(string="Send Consolidated Email",
                                            help="It is for consolidated mail send check")

    @api.constrains('name', )
    def validate_grade_band_type(self):
        record = self.env['kwemp_grade_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The grade \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_grade_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='Employee Grade created successfully.')
        else:
            self.env.user.notify_danger(message='Employee Grade creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_grade_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Grade updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Grade updation failed.')
        return res
