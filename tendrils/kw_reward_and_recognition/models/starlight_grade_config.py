import re

from urllib3 import Retry
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class StarlightGradeConfiguration(models.Model):
    _name = "kw_starlight_grade_configuration"
    _description = "Starlight Grade Configuration"



    grade_ids = fields.Many2many('kwemp_grade_master', 'kw_starlight_grade_configuration_grade_master',
                                 'kw_starlight_grade_config_id',
                                 'grade_id', string='Grade', required=True)

    
    @api.model
    def default_get(self, fields):
        res = super(StarlightGradeConfiguration, self).default_get(fields)
        grade_data = self.env['kw_starlight_grade_configuration'].sudo().search([])
        if len(grade_data) >= 1:
            raise ValidationError('You cannot create multiple Records.')
        return res