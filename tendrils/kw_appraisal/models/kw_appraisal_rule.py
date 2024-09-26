# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.exceptions import  ValidationError


class KwAppraisalRule(models.Model):
    _name           = "kw_appraisal_rule"
    _description    = "Appraisal Rule"
    _rec_name = 'year_id'
    
    year_id = fields.Many2one('kw_assessment_period_master', string='Appraisal Period')
    calculation = fields.Html(translate=True, sanitize_style=True)
    description = fields.Html(translate=True, sanitize_style=True)
