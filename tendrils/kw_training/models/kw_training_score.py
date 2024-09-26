# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingScore(models.Model):
    _name = "kw_training_score"
    _description = "Kwantify Training Score"
    _rec_name = "assessment_id"

    assessment_id = fields.Many2one(
        'kw_training_assessment', string="Assessment",ondelete='cascade')
    training_id = fields.Many2one(related="assessment_id.training_id",
                                  string="Training",)
    full_marks = fields.Integer(string="Assessment Mark", related='assessment_id.marks')
    score_detail_ids = fields.One2many(
        "kw_training_score_details", "score_id", string="Participant")

    
    @api.model
    def create(self, values):
        result = super(TrainingScore, self).create(values)
        if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_training_assessment':
            assessment = self.env['kw_training_assessment'].browse(
                self._context['active_id'])
            if not assessment.score_id:
                assessment.score_id = result.id
        return result