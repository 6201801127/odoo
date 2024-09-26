# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
import re
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class JobCategory(models.Model):
    _name = "kw_job_category"
    _description = "Employee category for job."

    # #####------------------------Fields----------------------######

    name = fields.Char(string="Job Category", required=True, size=100)
    active = fields.Boolean(string="Active",default=True)

    @api.constrains('name')
    def validate_category(self):
        if re.match(r"^[a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError(
                "Invalid Job Categry! Please provide a valid Job Categry.")
        

        record = self.env['kw_job_category'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The job category {self.name} already exists.")
    
    @api.model
    def create(self, values):
        result = super(JobCategory, self).create(values)
        self.env.user.notify_success("Job category created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(JobCategory, self).write(values)
        self.env.user.notify_success("Job category updated successfully.")
        return result
    
    @api.multi
    def unlink(self):
        result = super(JobCategory, self).unlink()
        self.env.user.notify_success("Job category deleted successfully.")
        return result
    
    
    
   
