# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
import re
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class Industrytype(models.Model):
    _name = "kw_industry_type"
    _description = "Employee Industry Type for job."

    # #####------------------------Fields----------------------######

    name = fields.Char(string="Functional Area", required=True, size=100)
    active = fields.Boolean(string="Active",default=True)

    @api.constrains('name')
    def validate_industry_type(self):
        if re.match(r"^[a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError(
                "Invalid Industry type Please provide a valid Industry type.")
        

        record = self.env['kw_industry_type'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The Industry type {self.name} already exists.")
    
    @api.model
    def create(self, values):
        result = super(Industrytype, self).create(values)
        self.env.user.notify_success("Industry type created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(Industrytype, self).write(values)
        self.env.user.notify_success("Industry type(s) updated successfully.")
        return result
    
    @api.multi
    def unlink(self):
        result = super(Industrytype, self).unlink()
        self.env.user.notify_success("Industry type(s) deleted successfully.")
        return result
    
    
    
