# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
import re
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class Qualificationmaster(models.Model):
    _name = "kw_qualification_master"
    _description = "Employee qualification for job."
    _order = "name asc"

    # #####------------------------Fields----------------------######

    name = fields.Char(string="Qualification", required=True, size=100)
    active = fields.Boolean('Active', default=True)
    code = fields.Char(string="Code")
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of qualification.")
    campus_drive = fields.Boolean('Show in Campus Drive')

    @api.constrains('name')
    def validate_qualification(self):
        if re.match(r"^[a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError(
                "Invalid Qualification! Please provide a valid Qualification.")

        record = self.env['kw_qualification_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The qualification {self.name} already exists.")

    @api.multi
    def unlink(self):
        Job = self.env['kw_hr_job_positions']
        obj = Job.search([('qualification', 'in', self.ids)])
        if obj:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        self.env.user.notify_success("Qualification(s) deleted successfully.")
        return super(Qualificationmaster, self).unlink()

    @api.model
    def create(self, values):
        result = super(Qualificationmaster, self).create(values)
        self.env.user.notify_success("Qualification created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(Qualificationmaster, self).write(values)
        self.env.user.notify_success("Qualification(s) updated successfully.")
        return result
