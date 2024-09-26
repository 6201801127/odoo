from odoo import models, fields, api


class kw_my_skill(models.Model):
    _name = 'kw_skill_my_skill'
    _description = "A model to view the my skill"
    _rec_name = 'res_skill'

    res_skill = fields.Many2one('kw_skill_question_set_config', string="Skill", required=True)

    skill_duration = fields.Char(string="Duration", size=100, readonly='1', store='true', compute='auto_fill')

    skill_completed_in = fields.Char(string="Completed In", size=100, compute='auto_fill')
    skill_total_questions = fields.Integer(string="Total Questions", readonly='1', store='true', compute='auto_fill')
    skill_correct_answer = fields.Integer(string="Correct Answer")
    user_id = fields.Char(string="User ID", readonly='1', store='true', compute='auto_fill')
    percentage = fields.Float(string="Percentage", compute='total_percentage', readonly=True, )

    @api.depends('skill_correct_answer', 'skill_total_questions')
    def total_percentage(self):
        for record in self:
            if record.skill_total_questions > 0:
                record.percentage = (record.skill_correct_answer / record.skill_total_questions) * 100

    @api.multi
    @api.depends('res_skill')
    def auto_fill(self):
        for record in self:
            for data in record.res_skill:
                record.skill_total_questions = int(data.total_questions)
                record.user_id = str(self.env.user.name_get()[0][1])
                record.skill_completed_in = data.duration
                if data.duration == '30':
                    record.skill_duration = data.duration + ' Minute'
                else:
                    record.skill_duration = data.duration + ' Hours'
