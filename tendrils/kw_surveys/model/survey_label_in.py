from odoo import fields, models, api


class SurveyLabelInherit(models.Model):
    _inherit = "survey.label"

    is_correct = fields.Boolean('Is a correct answer')
