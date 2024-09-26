from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class EducationalMaster(models.Model):
    _name = 'kw_eq_educational_qualification_master'
    _description = 'Educational Master'

    name = fields.Char()