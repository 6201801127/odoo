from odoo import models, api


class kw_question_set_config_training(models.Model):
    _inherit = 'kw_skill_question_set_config'

    @api.multi
    def view_employeewise_answer(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_training', 'kw_user_trainingtest_report_action_window')
        res['domain'] = [('set_config_id', '=', self.id)]
        return res

    @api.multi
    def view_assessment_answer(self):
        assessment_given = self.env['kw_skill_answer_master'].search(
            [('user_id', '=', self._uid), ('set_config_id', '=', self.id)], limit=1)
        view_id = self.env.ref('kw_skill_assessment.kw_question_user_report_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_skill_answer_master',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'res_id': assessment_given.id,
            'target': 'self',
            'flags': {"toolbar": False}
        }

    @api.model
    def create(self, values):
        values['active'] = True
        values['state'] = '2'
        result = super(kw_question_set_config_training, self).create(values)
        if ('active_model' in self._context
                and 'active_id' in self._context and self._context['active_model'] == 'kw_training_assessment'):
            assessment = self.env['kw_training_assessment'].browse(self._context['active_id'])
            if not assessment.assessment_id:
                assessment.assessment_id = result.id
        return result
