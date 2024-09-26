from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions,_
import math


class update_score_wizard(models.TransientModel):
    _name='update_score_wizard'
    _description = 'Update score wizard'

    def _get_default_appraisal(self):
        datas = self.env['hr.appraisal'].browse(self.env.context.get('active_ids'))
        return datas

    appr = fields.Many2many('hr.appraisal',readonly=1, default=_get_default_appraisal)

    @api.multi
    def update_score_lm_ulm(self):
        for record in self.appr:
            try:
                if record.state.sequence in [4,5,6]:
                    total_score = 0
                    questions = 0.0
                    number = 0
                    numeric_total = 0
                    for records in record.hr_manager_id:
                        if record.lm_input_id:
                            user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',record.lm_input_id.id),('user_input_id.state','=','done')])
                        else:
                            user_input = self.env['survey.user_input'].search(['&','&',('appraisal_id', '=', record.id),('partner_id','=',records.user_id.partner_id.id),('state', '=', 'done')])
                            user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',user_input.id)])
                        if len(user_input_line):
                            for lines in user_input_line:
                                if record.ulm_input_id:
                                    self.env.cr.execute(f"SELECT CEIL(SUM(individual_average)) AS final_average FROM (SELECT CEIL(SUM(quizz_mark) / COUNT(DISTINCT question_id) / 2) AS individual_average FROM survey_user_input_line WHERE user_input_id IN ({record.lm_input_id.id}, {record.ulm_input_id.id}) AND answer_type = 'suggestion'  GROUP BY question_id ) AS subquery")
                                    score_dict = self._cr.dictfetchall()
                                    total_score = score_dict[0]['final_average']
                                    self.env.cr.execute(f"SELECT SUM(individual_average) AS final_average FROM (SELECT CEIL(SUM(value_number) / COUNT(DISTINCT question_id)) / 2 AS individual_average FROM survey_user_input_line WHERE user_input_id IN ({record.lm_input_id.id}, {record.ulm_input_id.id}) AND answer_type = 'number'  GROUP BY question_id ) AS subquery")
                                    number_score = self._cr.dictfetchall()
                                    number = number_score[0]['final_average']
                                else:
                                    total_score += lines.quizz_mark
                                    number += lines.value_number
                                for quest_ids in lines.question_id:
                                    if quest_ids.type == 'simple_choice':
                                        for labels in quest_ids:
                                            questions += max(float(marks.quizz_mark) for marks in labels.labels_ids)
                                    if quest_ids.type == 'numerical_box':
                                        numeric_total += quest_ids.validation_max_float_value
                    if questions !=0:
                        score = (total_score/questions)*100
                        record.score = '%.3f'%(score)
                    if record.training_include == False:
                        record.training_score = 100
                    else:
                        record.training_score = math.ceil(record.training_percentage)
                    
                    if numeric_total > 0:
                        
                        record.write({
                        'kra_score': (number / numeric_total) * 100,
                        'score_calculation':'lm_ulm'
                        
                    })
                    record._count_final_score()
                    self.env.user.notify_info(message='Updated Successfully.')
                else:
                    record.write({
                        'total_score':0.0,
                    })
                    self.env.user.notify_warning(message='Appraisal state must be in Complete/Publish')
                    
            except Exception as e:
                # print("Error during update score appraisal ",str(e))
                continue
    @api.multi
    def update_score_lm(self):
        for record in self.appr:
            try:
                if record.state.sequence in [4,5,6]:
                    total_score = 0
                    questions = 0.0
                    number = 0
                    numeric_total = 0
                    for records in record.hr_manager_id:
                        if record.lm_input_id:
                            user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',record.lm_input_id.id),('user_input_id.state','=','done')])
                        else:
                            user_input = self.env['survey.user_input'].search(['&','&',('appraisal_id', '=', record.id),('partner_id','=',records.user_id.partner_id.id),('state', '=', 'done')])
                            user_input_line = self.env['survey.user_input_line'].search([('user_input_id','=',user_input.id)])
                        if len(user_input_line):
                            for lines in user_input_line:
                                total_score += lines.quizz_mark
                                number += lines.value_number
                                for quest_ids in lines.question_id:
                                    if quest_ids.type == 'simple_choice':
                                        for labels in quest_ids:
                                            questions += max(float(marks.quizz_mark) for marks in labels.labels_ids)
                                    if quest_ids.type == 'numerical_box':
                                        numeric_total += quest_ids.validation_max_float_value
                    if questions !=0:
                        score = (total_score/questions)*100
                        record.score = '%.3f'%(score)
                    if record.training_include == False:
                        record.training_score = 100
                    else:
                        record.training_score = math.ceil(record.training_percentage)
                    if numeric_total > 0:
                        print('number,numeric_total=======================',number,numeric_total)
                        record.write({
                        'kra_score': (number / numeric_total) * 100,
                        'score_calculation':'lm'
                        
                    })
                    record._count_final_score()
                    self.env.user.notify_info(message='Updated Successfully.')
                else:
                    record.write({
                        'total_score':0.0
                    })
                    self.env.user.notify_warning(message='Appraisal state must be in Complete/Publish')
                    
            except Exception as e:
                continue