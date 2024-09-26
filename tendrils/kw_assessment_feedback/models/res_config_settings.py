# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from ast import literal_eval


class ResConfigSettingsAFeedBack(models.TransientModel):
    _inherit = 'res.config.settings'

    assessment_ids = fields.Many2many('hr.employee','kw_asfeedback_employee_rel','employee_id','canteen_id',)
    probation_assessment_start_date=fields.Integer('Start Day')
    probation_assessment_end_date=fields.Integer('End Day')
    
    
    def set_values(self):
        res = super(ResConfigSettingsAFeedBack, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_assessment_feedback.assessment_ids', self.assessment_ids.ids)
        param = self.env['ir.config_parameter'].sudo()
        
        param.set_param('kw_assessment_feedback.probation_assessment_start_date', self.probation_assessment_start_date or 0)
        param.set_param('kw_assessment_feedback.probation_assessment_end_date', self.probation_assessment_end_date or 0)
        
        
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsAFeedBack, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        assessment_ids = self.env['ir.config_parameter'].sudo().get_param('kw_assessment_feedback.assessment_ids')
        lines = False
        if assessment_ids != False:
            lines = [(6, 0, literal_eval(assessment_ids))]
        res.update(
            assessment_ids=lines,
            probation_assessment_start_date=int(param.get_param('kw_assessment_feedback.probation_assessment_start_date')),
            probation_assessment_end_date=int(param.get_param('kw_assessment_feedback.probation_assessment_end_date'))
            
        )
        return res