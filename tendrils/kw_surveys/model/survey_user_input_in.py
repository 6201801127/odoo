# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    kw_response_id = fields.Many2one('kw_surveys', string="Feedback ID")
    start_time = fields.Datetime(string="Started On")
    end_time = fields.Datetime(string="End time")
    duration = fields.Integer(string='Duration in (Sec)',compute='_compute_duration',store=True)
  
    @api.depends('start_time','end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration_time=record.end_time-record.start_time
                difference_in_seconds = duration_time.total_seconds()
                record.duration = difference_in_seconds
                # print('durationtime>>>>>',duration_time)


class SurveyUserInputLineInherit(models.Model):
    _inherit = 'survey.user_input_line'

    # scoring
    answer_score = fields.Float('Score')
    answer_is_correct = fields.Boolean('Correct')
