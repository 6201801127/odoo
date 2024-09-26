from odoo import models, fields, api, tools


class kw_skill_user(models.Model):
    _name = 'kw_skill_user'
    _description = "A model to view User wise Total Test"
    _rec_name = 'user_id'

    user_id = fields.Many2one('kw_skill_answer_master')

    # employee_name = fields.Char(string="Employee Name")
    # skill = fields.Char(string="Skill")
    # test_date = fields.Date(string="Test Date")
    # total_questions =  fields.Integer(string="Total Questions")
    # total_attempted =  fields.Integer(string="Total Attempted")
    # total_unattempted = fields.Integer(string="Total Unattempted")
    # correct_answer = fields.Integer(string="Correct Answer")
    # total_mark = fields.Integer(string="Total Mark")
    # mark_obtained = fields.Integer(string="Mark Obtained")
    # percentage = fields.Float(string="Percentage")
