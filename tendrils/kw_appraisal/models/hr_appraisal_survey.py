# -*- coding: utf-8 -*-

from odoo import models, fields


class SurveyInput(models.Model):
    _inherit = 'survey.user_input'

    appraisal_id = fields.Many2one('hr.appraisal', string="Appraisal ID")
