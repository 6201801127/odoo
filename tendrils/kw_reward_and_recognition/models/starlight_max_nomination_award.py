import re

from urllib3 import Retry
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class StarlightMaxNominationAward(models.Model):
    _name = "starlight_max_nomination_award"
    _description = "Starlight Grade Configuration"

    division_ids = fields.Many2many('kw_division_config', 'starlight_max_nomination_award_grade_master',
                                    'starlight_max_nomination_award_id',
                                    'div_id', string='Division', required=True)
    nomination_count = fields.Integer(string="Max Nomination")
    award_count = fields.Integer(string="Max Award")

    @api.constrains('division_ids')
    def _check_division_ids(self):
        max_nomination_award_data = self.env['starlight_max_nomination_award'].sudo().search([]) - self
        for rec in max_nomination_award_data:
            type_data =  set(self.division_ids.mapped('type'))
            if len(type_data) > 1:
                raise ValidationError('Divisions Type should be unique.You cannot add SBU divisions with Non-SBU divisions.')
            for div in self.division_ids:
                if div.id in rec.division_ids.ids:
                    raise ValidationError('Duplicate Divisions are restricted.')
