# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations


class HrApplicant(models.Model):
    _name = "kw_survey_type"
    _description = "Adds a type for each surveys."

    name = fields.Char("Title", required=True)
    code = fields.Char("Code", required=True)

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_survey_type'].sudo().search([]) - self
        # for record in self:
        for data in existing:
            if data.name and data.name.lower() == self.name.lower():
                raise ValidationError(
                    f"The name {self.name} is already exists.")
            if data.code and data.code.lower() == self.code.lower():
                raise ValidationError(
                    f"The code {self.code} is already exists.")


class Kw_Survey_type(models.Model):
    _inherit = "survey.survey"

    # #----------- Additional fields----------------
    survey_type = fields.Many2one(string='Survey Type', comodel_name='kw_survey_type', required=True )
