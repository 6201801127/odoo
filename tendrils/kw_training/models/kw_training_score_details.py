# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingScoreDetails(models.Model):
    _name = 'kw_training_score_details'
    _description = "Kwantify Training Score Details"
    _rec_name = "score_id"

    score_id        = fields.Many2one("kw_training_score", string='Score',ondelete="cascade")
    training_id     = fields.Many2one(related="score_id.training_id")
    participant_id  = fields.Many2one("hr.employee", string='Employee',required=True)
    score           = fields.Integer(string='Score', default=0,required=True,size=100)
    percentage      = fields.Float(string="Percentage", default=0.00,required=True,compute='calculate_percentage')
    full_marks      = fields.Integer(related='score_id.full_marks')
    attendance      = fields.Selection([('attended', 'Attended'),('not_attended','Not Attended')],default="attended", required=True)

    @api.constrains('score')
    def check_value(self):
        for rec in self:
            if rec.score > rec.full_marks or rec.score < 0:
                raise ValidationError(f'Enter score between 0-{rec.full_marks}.')


    @api.depends('score','attendance')
    def calculate_percentage(self):
        for detail in self:
            if detail.attendance == 'not_attended':
                detail.score = 0
                detail.percentage = 0.00
            elif detail.attendance == 'attended':
                detail.percentage = round(float((detail.score/detail.full_marks)*100),2)
    