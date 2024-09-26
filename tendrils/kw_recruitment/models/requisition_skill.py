# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
import re
from odoo import api, fields, models
from odoo import tools, _


class RequisitionSkills(models.Model):
    _name = "kw_recruitment_requisition_skills"
    _description = "Resource Requisition Skills."

    # #####------------------------Fields----------------------######

    name = fields.Char(string="Name", size=25, required=True)
    category_id = fields.Many2one('kw_recruitment_requisition_categories', required=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of requisition.")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        result = super(RequisitionSkills, self).create(values)
        self.env.user.notify_success("Recruitment Requisition skills created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(RequisitionSkills, self).write(values)
        self.env.user.notify_success("Recruitment Requisition skills updated successfully.")
        return result

    @api.constrains('name')
    def validate_name(self):
        record = self.env['kw_recruitment_requisition_skills'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower() and info.category_id.id==self.category_id.id:
                raise ValidationError(f"The requisition skills {self.name} already exists.")