from odoo import models,api

class QuestionBankMaster(models.Model):
    _inherit = "kw_skill_question_bank_master"

    @api.model
    def create(self, values):
        result = super(QuestionBankMaster, self).create(values)
        if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_training_assessment':
            assessment = self.env['kw_training_assessment'].browse(self._context['active_id'])
            if not assessment.question_bank_id:
                assessment.question_bank_id = result.id
        return result