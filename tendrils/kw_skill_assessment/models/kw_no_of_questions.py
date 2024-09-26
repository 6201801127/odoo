# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Kw_no_of_questions(models.Model):
    _name = 'kw_skill_no_of_questions'
    _description = "A model to hold no. of questions"
    _rec_name = 'question_type'

    question_type = fields.Many2one('kw_skill_question_weightage', string="Question Type", required=True)
    no_of_question = fields.Integer(string="Number Of Question", default=1, required=True)
    quest_config = fields.Many2one('kw_skill_question_set_config')
