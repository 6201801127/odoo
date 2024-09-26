
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InductionScore(models.Model):
    _name = "kw_induction_score"
    _description = "Kwantify Training Score"
    _rec_name = "assessment_id"

    assessment_id = fields.Many2one(
        'kw_employee_induction_assessment', string="Assessment",ondelete='cascade')
    # training_id = fields.Many2one(related="assessment_id.training_id",
    #                               string="Training",)
    full_marks = fields.Integer(string="Assessment Mark", related='assessment_id.marks')
    ind_score_detail_ids = fields.One2many(
        "induction_assessment_emp_score_details", "score_id", string="Participant")

    
    @api.model
    def create(self, values):
        result = super(InductionScore, self).create(values)
        if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_employee_induction_assessment':
            assessment = self.env['kw_employee_induction_assessment'].browse(
                self._context['active_id'])
            if not assessment.score_id:
                assessment.score_id = result.id
        return result







class InductionScoreDetails(models.Model):
    _name = 'induction_assessment_emp_score_details'
    _description = "Kwantify Onboarding Induction Score Details"
    _rec_name = "score_id"

    score_id        = fields.Many2one("kw_induction_score", string='Score',ondelete="cascade")
    # training_id     = fields.Many2one(related="score_id.training_id")
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
    