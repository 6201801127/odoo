# -*- coding: utf-8 -*-
import bs4 as bs
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_question_bank_master(models.Model):
    _name = 'kw_skill_question_bank_master'
    _description = "A master model to group of questions."
    _rec_name = 'name'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Question Set Name", track_visibility='onchange')
    type = fields.Selection(string='Assessment Type',
                            selection=[('skill', 'Skill'), ('training', 'Training'),('Induction', 'Induction')], default="skill", required=True,
                            track_visibility='onchange')
    skill_types = fields.Many2one('kw_skill_type_master', string="Skill Category", required=True,
                                  track_visibility='onchange')
    skill = fields.Many2one('kw_skill_master', string="Skill", required=True, track_visibility='onchange')
    total_no_of_questions = fields.Integer(compute='count_questions', string="Total No of Questions", readonly=True,
                                           track_visibility='onchange')
    questions = fields.One2many('kw_skill_question_bank', 'quesbank_rel', string="Questions", required=True,
                                track_visibility='onchange')
    simple_questions = fields.Integer(string="Simple Questions", compute="count_questions")
    average_questions = fields.Integer(string="Average Questions", compute="count_questions")
    complex_questions = fields.Integer(string="Complex Questions", compute="count_questions")

    @api.depends('questions')
    def count_questions(self):
        for record in self:
            record.total_no_of_questions = len(record.questions)
            simple_count = self.env['kw_skill_question_bank'].search_count(
                [('quesbank_rel', '=', record.id), ('difficulty_level.code', '=', 'simple')])
            record.simple_questions = simple_count or 0

            average_count = self.env['kw_skill_question_bank'].search_count(
                [('quesbank_rel', '=', record.id), ('difficulty_level.code', '=', 'average')])
            record.average_questions = average_count or 0

            complex_count = self.env['kw_skill_question_bank'].search_count(
                [('quesbank_rel', '=', record.id), ('difficulty_level.code', '=', 'complex')])
            record.complex_questions = complex_count or 0

    @api.onchange('skill_types')
    def show_skills(self):
        skills_id = self.skill_types.id
        if self.skill and self.skill.skill_type.id != skills_id:
            self.skill = False
        return {'domain': {'skill': ([('skill_type', '=', skills_id)])}}

    @api.constrains('skill_types', 'skill', 'type','name')
    def check_duplicates(self):
        record = self.env['kw_skill_question_bank_master'].sudo().search([('type', '=', 'skill')]) - self
        for data in record:
            for rec in self:
                if rec.type == 'skill':
                    if data.type == 'skill' and data.skill_types == rec.skill_types and data.skill == rec.skill and data.name == rec.name:
                        raise ValidationError(f"{rec.name} for {rec.skill.name} is already exists.")

    @api.constrains('questions')
    def _check_question(self):
        for record in self:
            if len(record.questions) < 1:
                raise ValidationError("Please add at least one question.")
            for q in record.questions:
                if len((bs.BeautifulSoup(q.question, features="lxml")).text.strip()) == 0:
                    raise ValidationError('Question cannot be Empty')
                elif len((bs.BeautifulSoup(q.option_a, features="lxml")).text.strip()) == 0:
                    raise ValidationError('Option A cannot be Empty')
                elif len((bs.BeautifulSoup(q.option_b, features="lxml")).text.strip()) == 0:
                    raise ValidationError('Option B cannot be Empty')
                elif len((bs.BeautifulSoup(q.option_c, features="lxml")).text.strip()) == 0:
                    raise ValidationError('Option C cannot be Empty')
                elif len((bs.BeautifulSoup(q.option_d, features="lxml")).text.strip()) == 0:
                    raise ValidationError('Option D cannot be Empty')
                # elif len((bs.BeautifulSoup(q.justification, features="lxml")).text.strip()) == 0:
                #     raise ValidationError('Answer Justification cannot be Empty')

    @api.model
    def create(self, vals):
        new_record = super(kw_question_bank_master, self).create(vals)
        self.env.user.notify_success(message='Question bank created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_question_bank_master, self).write(vals)
        self.env.user.notify_success(message='Question bank updated successfully.')
        return res
