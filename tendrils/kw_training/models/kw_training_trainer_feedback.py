from odoo import models, fields,api
from odoo.exceptions import ValidationError
import bs4 as bs


class TrainingTrainerFeedbackDetails(models.Model):
    _name = 'kw_training_trainer_feedback_details'
    _description = "Trainer Feedback Against Participants"
    _rec_name = 'training_id'


    trainer_feedback_id = fields.Many2one("kw_training_trainer_feedback",string='Feedback',ondelete="cascade")
    participant_id = fields.Many2one("hr.employee",string='Participant',ondelete="cascade")
    designation = fields.Char(string="Designation", related='participant_id.job_id.name')
    department = fields.Char(string="Department", related='participant_id.department_id.name')
    training_id = fields.Many2one("kw_training",string='Training',ondelete="restrict")
    proficiency = fields.Selection(string="Proficiency", required=True, selection=[('Excellent', 'Excellent'), ('Best', 'Best'), ('Better', 'Better'), ('Good', 'Good'), ('Wrost', 'Wrost'), ('Not applicable', 'Not applicable')])
    remark = fields.Text(string="Remark",required=True)
    financial_year = fields.Many2one('account.fiscalyear', "Financial Year")
    course_type_id = fields.Many2one('kw_skill_type_master',string="Course Type")
    course_id = fields.Many2one('kw_skill_master','Course')

class TrainingTrainerFeedback(models.Model):
    _name = 'kw_training_trainer_feedback'
    _description = "Trainer Feedback Against Participants"
    _rec_name = 'training_id'


    course_type_id = fields.Many2one('kw_skill_type_master',string="Course Type",required=True)
    course_id = fields.Many2one('kw_skill_master',string="Course",required=True)
    financial_year = fields.Many2one("account.fiscalyear",string='Financial Year')
    training_id = fields.Many2one("kw_training",string='Training',ondelete="restrict")
    feedback_detail_ids = fields.One2many("kw_training_trainer_feedback_details","trainer_feedback_id",string="Feedbacks")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')


    @api.multi
    def feedback_submit_btn(self):
        for rec in self.feedback_detail_ids:
            if not rec.proficiency:
                raise ValidationError(f"Kindly set proficiency for {rec.participant_id.name}")
            if rec.remark == False or rec.remark == '':
                raise ValidationError(f"Kindly set remark for {rec.participant_id.name}")
        self.state = 'submit' 


             
    