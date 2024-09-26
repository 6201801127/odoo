from odoo import models, fields, api
import random
import secrets


class kw_answer_child(models.Model):
    _name = 'kw_skill_answer_child'
    _description = "A model to create the Answer child Table"
    _rec_name = "ques_id"

    ans_id = fields.Many2one('kw_skill_answer_master', string="Answer Id")
    ques_id = fields.Many2one('kw_skill_question_bank', string="Question Id")
    question = fields.Html(string='Question', related='ques_id.question', readonly=True, store=True)
    justification = fields.Html(string='Justification', related='ques_id.justification', readonly=True, store=True)

    selected_option = fields.Char(string="User Option")
    correct_option = fields.Char(string="Correct Option")
    difficulty_id = fields.Integer(string="Difficulty Id")  # Simple Id,Average Id,Complex Id
    weightage = fields.Integer(string="Question Weightage")
    mark_obtained = fields.Integer(string="Mark Obtained", store=True, compute='get_mark', readonly=True)
    # flag = fields.Boolean("String", compute="get_value")
    selected_answer = fields.Html(string="Selected Answer", compute="get_selected_answer")
    correct_answer = fields.Html(string="Correct Answer", compute="get_correct_answer")

    @api.depends('selected_option', 'correct_option')
    def get_mark(self):
        for record in self:
            if str(record.correct_option).lower() == str(record.selected_option).lower():
                question_id = self.env['kw_skill_question_bank'].sudo().search([('id', '=', record.ques_id.id)])
                weightage_id = question_id.difficulty_level.id
                weightage = self.env['kw_skill_question_weightage'].sudo().search([('id', '=', weightage_id)])
                record.mark_obtained = weightage.weightage
                # m = self.env['kw_skill_answer_master'].sudo().search([('id','=',record.ans_id.id)])
                # mark_ob = m.total_mark_obtained + record.mark_obtained
                # self.env['kw_skill_answer_master'].sudo().write({'total_mark_obtained': 1})

                # master_record.write({'total_mark_obtained': ans})
                # print(weightage.weightage)
            else:
                record.mark_obtained = 0

    # def get_value(self):
    #     for record in self:
    #         if record.selected_option == record.correct_option:
    #             record.flag = True

    def get_selected_answer(self):
        for record in self:
            sel_ans = self.env['kw_skill_question_bank'].sudo().search([('id', '=', record.ques_id.id)])
            if record.selected_option == 'A':
                record.selected_answer = sel_ans.option_a
            elif record.selected_option == 'B':
                record.selected_answer = sel_ans.option_b
            elif record.selected_option == 'C':
                record.selected_answer = sel_ans.option_c
            elif record.selected_option == 'D':
                record.selected_answer = sel_ans.option_d

    def get_correct_answer(self):
        for record in self:
            sel_ans = self.env['kw_skill_question_bank'].sudo().search([('id', '=', record.ques_id.id)])
            if record.correct_option == 'A':
                record.correct_answer = sel_ans.option_a
            elif record.correct_option == 'B':
                record.correct_answer = sel_ans.option_b
            elif record.correct_option == 'C':
                record.correct_answer = sel_ans.option_c
            elif record.correct_option == 'D':
                record.correct_answer = sel_ans.option_d

    @api.model
    def change_current_qid(self, args):
        curr_ques_id = args.get('current_qid', False)
        master_ans_id = args.get('master_answer_id', False)
        # print("master_ans_id >> ", master_ans_id, curr_ques_id)
        # fetch_answers = self.env['kw_skill_answer_child'].sudo().search([('ans_id','=',int(master_ans_id))])
        # for f in fetch_answers:
        #     if f.selected_option != False:
        #         f.write({'selected_option': False})
        #         print(f.selected_option)
        fetch_questions = self.env['kw_skill_answer_child'].sudo().search(
            ['&', ('ans_id', '=', int(master_ans_id)), ('ques_id', '=', int(curr_ques_id))])
        # print("fetch_questions >> ", fetch_questions)
        # print("self.ans_id.set_config_id.assessment_type >1111111111111111111111111111111111111111> ", self,self.ans_id, self.ans_id.set_config_id, self.ans_id.set_config_id.assessment_type,type(self.ans_id.set_config_id.assessment_type))

        result = None
        if fetch_questions:
            ques_ids = []
            update_ques_det = []
            ques_diff_id = fetch_questions.difficulty_id
            # print(update_ques_det,"update_ques_det==============================>>>>>>>>>>>>>>>>>>>>>&&&&&&&&&&&&&&&&&")
            skill_answer_master = self.env['kw_skill_answer_master'].sudo().search([('id', '=', master_ans_id)])
            sk_id = skill_answer_master.skill_id
            set_config_id = skill_answer_master.set_config_id
            # print("sk_id >>> ", sk_id, set_config_id)
            skill_id = sk_id.id
            fetch_all_questions = self.env['kw_skill_answer_child'].sudo().search(
                ['&', ('ans_id', '=', int(master_ans_id)), ('difficulty_id', '=', ques_diff_id)])
            # print("fetch_all_questions >>> ", fetch_all_questions)
            for record in fetch_all_questions:
                ques_ids.append(record.ques_id.id)
            # print("ques_ids <<<<>>>> ", ques_ids)
            # print(set_config_id.assessment_type,skill_id,"set_config_id.assessment_type===>>>>>11111111111111>>>>>>>>")
            if set_config_id.assessment_type == 'training':
                question_bank_master_id_training = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('id', '=', set_config_id.question_bank_id.id), ('skill', '=', sk_id.id),
                     ('type', '=', 'training')])
                # print("question_bank_master_id_training >> ", question_bank_master_id_training)
                question_bank_child_record_training = self.env['kw_skill_question_bank'].sudo().search(
                    ['&', ('quesbank_rel', '=', question_bank_master_id_training.id),
                     ('difficulty_level', '=', ques_diff_id)])
                # print("question_bank_child_record_training >> ", question_bank_child_record_training)
                for rec in question_bank_child_record_training:
                    if rec.id not in ques_ids:
                        update_ques_det.append(rec.id)
                        # dfghjk
            else:
                # print("self.ans_id.set_config_id.assessment_type >1111111111111111111111111111111111111111> ", self, self.ans_id, self.ans_id.set_config_id, self.ans_id.set_config_id.assessment_type,type(self.ans_id.set_config_id.assessment_type))
                # print(set_config_id,set_config_id.sudo().question_bank_id.id,sk_id.id,"set_config_id.question_bank_id.id============------->>>>>>>>>>>>>..")
                question_bank_master_id_skill = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', sk_id.id), ('type', '=', 'skill')])
                # ('id', '=', set_config_id.question_bank_id.id), 
                # print(question_bank_master_id_skill,"question_bank_master_id_skill=====================>>>>>>>>>")
                question_bank_child_record_skill = self.env['kw_skill_question_bank'].sudo().search(
                    ['&', ('quesbank_rel', '=', question_bank_master_id_skill.id),
                     ('difficulty_level', '=', ques_diff_id)])
                # print(question_bank_child_record_skill,"question_bank_child_record_skill============>>>>>>>last")
                for rec in question_bank_child_record_skill:
                    if rec.id not in ques_ids:
                        update_ques_det.append(rec.id)
            # print(update_ques_det,"update_ques_det============")

            random_question = random.sample(update_ques_det, 1)
            # random_question = secrets.sample(update_ques_det, 1)
            random_ques_details = self.env['kw_skill_question_bank'].sudo().search([('id', 'in', random_question)])
            # print("random_ques_details >> ", random_ques_details)
            
            fetch_questions.write({'ques_id': random_ques_details.id,
                                   'question': random_ques_details.question,
                                   'justification': random_ques_details.justification,
                                   'correct_option': random_ques_details.correct_ans,
                                   'selected_option': False})
            result = [random_ques_details.id, random_ques_details.question, random_ques_details.option_a,
                      random_ques_details.option_b, random_ques_details.option_c, random_ques_details.option_d]
        return result
