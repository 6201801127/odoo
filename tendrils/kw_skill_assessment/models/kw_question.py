from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_question_bank(models.Model):
    _name = 'kw_skill_question_bank'
    _description = "A model to group of questions."
    _rec_name = "question"

    def _get_default_level(self):
        return self.env['kw_skill_question_weightage'].search([('code', '=', 'simple')], limit=1)

    difficulty_level = fields.Many2one('kw_skill_question_weightage', string="Difficulty Level",
                                       default=_get_default_level, required=True)

    question = fields.Html(string='Question', required=True)

    option_a = fields.Html(string='Option A', required=True)
    option_b = fields.Html(string='Option B', required=True)
    option_c = fields.Html(string='Option C', required=True)
    option_d = fields.Html(string='Option D', required=True)

    correct_ans = fields.Selection(string="Correct Answer",
                                   selection=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'),
                                              ('D', 'Option D')], required=True)

    justification = fields.Html(string='Answer Justification', )
    quesbank_rel = fields.Many2one('kw_skill_question_bank_master', string='Question bank relation', ondelete='cascade')

    # @api.model
    # def create(self, vals):
    #     new_record = super(kw_question_bank, self).create(vals)
    #     self.env.user.notify_success(message='Question created successfully.')
    #     return new_record

    # @api.multi
    # def write(self, vals):
    #     res = super(kw_question_bank, self).write(vals)
    #     self.env.user.notify_success(message='Question updated successfully.')
    #     return res
