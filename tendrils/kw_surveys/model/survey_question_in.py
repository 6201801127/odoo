# -*- coding: utf-8 -*-
from odoo import api, fields, models


class kwSurveyQuestion(models.Model):
    _inherit = "survey.question"

    question = fields.Text('Question Name', required=True, translate=True)

    # Conditional display
    is_conditional = fields.Boolean(
        string='Conditional Display', copy=False, help="""If checked, this question will be displayed only 
        if the specified conditional answer have been selected in a previous question""")
    triggering_question_id = fields.Many2one(
        'survey.question', string="Triggering Question", copy=False, compute="_compute_triggering_question_id",
        store=True, readonly=False, help="Question containing the triggering answer to display the current question.",
        domain="""[('survey_id', '=', survey_id),
                 '&', ('question_type', 'in', ['simple_choice', 'multiple_choice']),
                 '|',
                     ('sequence', '<', sequence),
                     '&', ('sequence', '=', sequence), ('id', '<', id)]""")

    triggering_answer_id = fields.Many2one(
        'survey.question.answer', string="Triggering Answer", copy=False, compute="_compute_triggering_answer_id",
        store=True, readonly=False, help="Answer that will trigger the display of the current question.",
        domain="[('question_id', '=', triggering_question_id)]")

    @api.depends('is_conditional')
    def _compute_triggering_question_id(self):
        """ Used as an 'onchange' : Reset the triggering question if user uncheck 'Conditional Display'
            Avoid CacheMiss : set the value to False if the value is not set yet."""
        for question in self:
            if not question.is_conditional or question.triggering_question_id is None:
                question.triggering_question_id = False

    @api.depends('is_conditional')
    def _compute_triggering_question_id(self):
        """ Used as an 'onchange' : Reset the triggering question if user uncheck 'Conditional Display'
            Avoid CacheMiss : set the value to False if the value is not set yet."""
        for question in self:
            if not question.is_conditional or question.triggering_question_id is None:
                question.triggering_question_id = False

    @api.depends('triggering_question_id')
    def _compute_triggering_answer_id(self):
        """ Used as an 'onchange' : Reset the triggering answer if user unset or change the triggering question
            or uncheck 'Conditional Display'.
            Avoid CacheMiss : set the value to False if the value is not set yet."""
        for question in self:
            if not question.triggering_question_id \
                    or question.triggering_question_id != question.triggering_answer_id.question_id \
                    or question.triggering_answer_id is None:
                question.triggering_answer_id = False

    @api.onchange('labels_ids')
    def onchange_labels_ids(self):
        for label in self.labels_ids:
            # print('label >> ', label.id, label.is_correct)
            pass
