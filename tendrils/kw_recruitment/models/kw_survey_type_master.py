# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations


# class HrApplicant(models.Model):
#     _name = "kw_survey_type"
#     _description = "Survey Type"
#
#     name = fields.Char("Title", required=True)
#     code = fields.Char("Code", required=True)
#
#     @api.constrains('name')
#     def check_duplicate(self):
#         existing = self.env['kw_survey_type'].sudo().search([]) - self
#         for record in self:
#             for data in existing:
#                 if record.name.lower() == data.name.lower():
#                     raise ValidationError(
#                         f"The name {record.name} is already exists.")
#                 if record.code.lower() == data.code.lower():
#                     raise ValidationError(
#                         f"The code {record.code} is already exists.")
