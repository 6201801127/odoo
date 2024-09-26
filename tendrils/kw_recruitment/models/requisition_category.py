# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
import re
from odoo import api, fields, models
from odoo import tools, _


class RequisitionCategories(models.Model):
    _name = "kw_recruitment_requisition_categories"
    _description = "Resource Requisition Categories."

    # #####------------------------Fields----------------------######

    name = fields.Char(string="Name", size=25, required=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of requisition.")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        result = super(RequisitionCategories, self).create(values)
        self.env.user.notify_success("Recruitment requisition Categories created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(RequisitionCategories, self).write(values)
        self.env.user.notify_success("Recruitment requisition Categories updated successfully.")
        return result

    @api.constrains('name')
    def validate_name(self):
        record = self.env['kw_recruitment_requisition_categories'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The requisition categories {self.name} already exists.")

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True