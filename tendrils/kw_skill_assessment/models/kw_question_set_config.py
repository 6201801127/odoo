import werkzeug
import random
import math
# from dateutil import relativedelta
from datetime import date, datetime, timedelta

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
import secrets


class kw_question_set_config(models.Model):
    _name = 'kw_skill_question_set_config'
    _description = "Skill Assessment"
    _rec_name = 'name'

    name = fields.Char("Name", required=True)
    skill_types = fields.Many2one('kw_skill_type_master', string="Skill Type", required=True)
    skill = fields.Many2one('kw_skill_master', string="Skill", required=True)
    dept = fields.Many2many('hr.department', string="Department", domain=[
        ('parent_id', "=", False)], required=True)
    applicable_candidate = fields.Selection(string="Applicable Candidates",
                                            selection=[('1', 'All'), ('2', 'Designation Specific'),
                                                       ('3', 'Individual'), ('4', 'Experience')], default='1',
                                            required=True)
    select_deg = fields.Many2many('hr.job', 'kw_skill_job_quest_rel', 'job_id', 'quest_id',
                                  string="Select Designation", )
    select_individual = fields.Many2many('hr.employee', 'kw_skill_emp_quest_rel', 'emp_id', 'quest_id',
                                         string="Select Employee")
    frequency = fields.Selection(string="Frequency",
                                 selection=[('n', 'Any time'), ('o', 'Once'), ('m', 'Monthly'),
                                            ('q', 'Quarterly'), ('h', 'Half-Yearly'),
                                            ('t', 'Twice a Year'), ('y', 'Yearly')], default='y', required=True)

    interval = fields.Selection(string="Interval (in months)",
                                selection=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                                           ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11')])

    add_questions = fields.One2many("kw_skill_no_of_questions", 'quest_config', string="Questions")
    duration = fields.Selection(string="Duration", required=True,
                                selection=[('900', '15 mins'), ('1800', '30 mins'), ('2700', '45 mins'),
                                           ('3600', '1 hour'),
                                           ('5400', '1 hour 30 mins'), ('7200', '2 hours'),
                                           ('10800', '3 hours')])
    total_questions = fields.Integer(string="Total Questions", store=True, compute='total_no_questions', readonly=True)
    total_marks = fields.Integer(string="Total Marks", store=True, compute='total_no_questions', readonly=True)

    set_config_id_readonly = fields.Boolean(compute="readonly_question_set", default=False, )

    designation_id = fields.Boolean(compute="_get_designation", string="Designation Id", default=False)
    question_type = fields.Boolean(compute="_get_no_of_questions", string="question Type", default=False)
    frequency_val = fields.Boolean(compute="_validate_frequency", string="Frequency Validation", default=False)
    fiscal_year = fields.Char(compute="_get_fiscal_year", string="Fiscal Year")
    fiscal_year_last_date = fields.Char(compute="_get_fiscal_year", string="Fiscal Year End Date")
    instruction = fields.Html(string='Instruction', required=True,
                              default="<h2><center> Welcome to your Skill Assessment portal !!</center> </h2><br />\
            You are eligible to appear this skill assessment twice in a year. Your 2nd chance to appear the test will be valid only after 3 months of 1st attempt.<br />\
            This assessment consists of multiple choice questions.<br />\
            There is No negative marking for wrong answer/s.<br /><br />\
            <table border='1px' cellpadding='5' cellspacing='5'>\
            <tr>\
            <th>Question Type </th>\
            <th>Mark per correct Answer</th>\
            <th>Total Questions</th>\
            <tr> <td> Simple </td>\
            <td> 1 </td>\
            <td> 20 </td> </tr>\
            <tr><td>Average</td>\
            <td>3</td>\
            <td>10</td></tr>\
            <td>Complex</td>\
            <td>5</td>\
            <td>5</td></tr>\
            </table>\
                <br />\
            <h5> Total Mark: 75 </h5>\
            <h5> Total Duration: 1hour </h5> \
            <h5> Guideline: </h5><br />\
            ·         Select only one correct answer out of 4 options.<br />\
            ·         Don’t click “Refresh” or “Back” button in URL.<br />\
            ·         Don’t shift/open to any other browser. Switching to other browser will reset your selected Question/answer.<br />\
            ·         Please click on “mark for review” for the answers you are not sure.<br />\
            ·         Status of your attempt is mentioned at left review pane with color codes.<br />\
            ·         The “End Test” option is available on last question page only.<br />\
            ·         Referring answers from any print or electronic media or discussing with others are strictly prohibited during the assessment.")
    expected_duration = fields.Char('Expected Duration', compute='_compute_duration', store=True)
    exam_given_count = fields.Integer(compute="get_no_of_test_given")

    experience_id = fields.Many2one(string='Experience', comodel_name='kw_skill_experience_master',
                                    ondelete='restrict', )
    active = fields.Boolean(string='Status', default=False,
                            help="The active field allows you to hide the test without removing it.")
    state = fields.Selection(string="State", selection=[('1', 'Draft'), ('2', 'Published')], required=True, default='1')

    assessment_type = fields.Selection(selection=[('skill', 'Skill'), ('training', 'Training'),('Induction','Induction')],
                                       string="Assessment Type", default="skill", required=True)
    start_on = fields.Datetime(string="Start Date")
    expire_on = fields.Datetime(string="Expire Date")
    question_bank_id = fields.Many2one('kw_skill_question_bank_master', 'Question Set')
    mail_note = fields.Text(string="Note", )
    eligible_tests = fields.Boolean(string="Eligible Tests", compute="get_eligible_tests", search='_value_search')
    simple_questions = fields.Integer(string="Simple Questions", compute="get_no_of_difficulty_level_questions")
    average_questions = fields.Integer(string="Average Questions", compute="get_no_of_difficulty_level_questions")
    complex_questions = fields.Integer(string="Complex Questions", compute="get_no_of_difficulty_level_questions")

    @api.onchange("frequency", "interval")
    def compute_mail_note(self):
        if self.frequency:
            note = f"You can appear the test {dict(self._fields['frequency'].selection).get(self.frequency)} and update your annual skill ratings."
            if self.frequency == 'n':
                self.mail_note = note
            elif self.frequency == 'o':
                self.mail_note = note
            elif self.frequency == 'm':
                self.mail_note = note
            elif self.frequency == 'q':
                self.mail_note = note
            elif self.frequency == 'h':
                self.mail_note = note
            elif self.frequency == 't' and self.interval:
                if self.interval == '0' or self.interval == '1':
                    self.mail_note = f"{note}\nThe second test will be activated only after {dict(self._fields['interval'].selection).get(self.interval)} month of 1st appearance. "

                else:
                    self.mail_note = f"{note}\nThe second test will be activated only after {dict(self._fields['interval'].selection).get(self.interval)} months of 1st appearance. "
            elif self.frequency == 'y':
                self.mail_note = note
            else:
                self.mail_note = False

    @api.onchange('question_bank_id')
    def set_questions(self):
        self.add_questions = False
        if self.question_bank_id and self.question_bank_id.questions:
            weightage_read_group = self.env['kw_skill_question_bank'].read_group(
                [('id', 'in', self.question_bank_id.questions.ids)], ['difficulty_level', 'question'],
                ['difficulty_level'])
            weightage_count = [(0, 0, {'question_type': data['difficulty_level'][0],
                                       'no_of_question': data['difficulty_level_count']}) for data in
                               weightage_read_group]
            self.add_questions = weightage_count

    @api.onchange('skill')
    def get_no_of_difficulty_level_questions(self):
        self.simple_questions = False
        self.average_questions = False
        self.complex_questions = False
        qm_id = self.env['kw_skill_question_bank_master'].sudo().search(
            [('skill', '=', self.skill.id), ('type', '=', 'skill')])
        # print(qm_id)
        simple_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'simple')])
        self.simple_questions = simple_count or 0

        average_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'average')])
        self.average_questions = average_count or 0

        complex_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'complex')])
        self.complex_questions = complex_count or 0
    
    @api.onchange('skill')
    def get_no_of_difficulty_level_ind_questions(self):
        # print("call skill onchange=======================================================")
        self.simple_questions = False
        self.average_questions = False
        self.complex_questions = False
        # print("in false condition-----------------------")
        qm_id = self.env['kw_skill_question_bank_master'].sudo().search(
            [('skill', '=', self.skill.id), ('type', '=', 'Induction')])
        # print(qm_id)
        simple_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'simple')])
        self.simple_questions = simple_count or 0
        # print(" self.simple_questions ========", self.simple_questions )

        average_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'average')])
        self.average_questions = average_count or 0
        # print(" self.average_questions ========", self.average_questions )

        complex_count = self.env['kw_skill_question_bank'].search_count(
            [('quesbank_rel', '=', qm_id.id), ('difficulty_level.code', '=', 'complex')])
        self.complex_questions = complex_count or 0

    @api.model
    def get_no_of_test_given(self):
        for record in self:
            total_test = self.env['kw_skill_answer_master'].search_count([('set_config_id', '=', record.id)])
            record.exam_given_count = total_test or 0

    def _get_fiscal_year(self):
        for record in self:
            current_date = datetime.now().date()
            record.fiscal_year = self.env['account.fiscalyear'].sudo().search(
                [('date_start', '<=', current_date), ('date_stop', '>=', current_date)], limit=1).name
            record.fiscal_year_last_date = self.env['account.fiscalyear'].sudo().search(
                [('date_start', '<=', current_date), ('date_stop', '>=', current_date)], limit=1).date_stop

    # @api.constrains('start_on', 'expire_on')
    # def training_validation(self):
    #     for record in self:
    #         if record.assessment_type == 'training':
    #             if record.start_on >= record.expire_on:
    #                 raise ValidationError("Expire date should be grater than start date.")
    #             elif record.start_on < datetime.today():
    #                 raise ValidationError("Start date must be greater or equal to today.")
    #             else:
    #                 return True

    @api.onchange('dept', 'applicable_candidate')
    def show_designations(self):
        self.select_deg = False
        dept_child_ids = self._get_all_child_department(self.dept)
        dept_child_ids += self.dept
        return {'domain': {
            'select_deg': (['|', ('department_id', 'in', dept_child_ids.ids), ('department_id', '=', False)]),
            'select_individual': ([('department_id', 'in', dept_child_ids.ids)])}}

    # @api.onchange('dept', 'applicable_candidate')
    # def show_individual_employee(self):
    #     if not self.dept:
    #         self.select_individual = False
    #     elif self.dept and not self.select_individual:
    #         ''' check if selected employee  are from the selected department, if so then don't remove the employee,
    #         if a department is removed then remove the employees. '''
    #         dept_child_ids = self._get_all_child_department(self.dept)
    #         dept_child_ids += self.dept
    #         print(dept_child_ids.ids, ' >> ', self.dept.ids)
    #         employees = self.env['hr.employee'].sudo().search([("department_id", "in", dept_child_ids.ids)])
    #         # # employees = self.select_individual.filtered(lambda rec: rec.department_id.id in self._get_all_child_department(self.dept))
    #         # print('employees : ', employees)
    #         if employees:
    #             self.select_individual = [[6, False, employees.ids]]
    #     return {'domain': {'select_individual': ([('department_id', 'in', self.dept.ids)])}}

    @api.depends('add_questions')
    def _compute_duration(self):
        for record in self:
            expected_duration = 0
            t_delta = ''
            for question in record.add_questions:
                expected_duration += question.question_type.duration * question.no_of_question
                t_delta = str(timedelta(seconds=expected_duration))
            if len(t_delta) > 0:
                record.expected_duration = t_delta

    @api.onchange('skill_types')
    def show_skills(self):
        if self.skill_types:
            skill_id = self.skill_types.id
            if self.skill and self.skill.skill_type.id != skill_id:
                self.skill = False
            return {'domain': {'skill': ([('skill_type', '=', skill_id)])}}

    @api.depends('add_questions')
    def total_no_questions(self):
        for record in self:
            total_quest = 0
            total_marks = 0
            for question in record.add_questions:
                total_quest += question.no_of_question
                total_marks += question.question_type.weightage * question.no_of_question
            record.total_questions = total_quest
            record.total_marks = total_marks

    @api.constrains('add_questions', 'skill')
    def validate_add_question(self):
        qtypes = []
        for rec in self:
            if len(rec.add_questions) < 1:
                raise ValidationError("Please add at least one question.")
            if rec.assessment_type == 'training':
                qm_training = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('id', '=', rec.question_bank_id.id), ('skill', '=', rec.skill.id), ('type', '=', 'training')])
                for questions in rec.add_questions:
                    qc_training = self.env['kw_skill_question_bank'].sudo().search(
                        [('quesbank_rel', '=', qm_training.id), ('difficulty_level', '=', questions.question_type.id)])
                    if questions.no_of_question > len(qc_training):
                        raise ValidationError(
                            f"Question bank does not contain {questions.no_of_question} no of {questions.question_type.name} Questions for this Skill.")
                    if questions.question_type.name not in qtypes:
                        qtypes.append(questions.question_type.name)
                    else:
                        raise ValidationError(f"The question type {questions.question_type.name} is exists.")
            elif rec.assessment_type == 'Induction':
                qm = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', rec.skill.id), ('type', '=', 'Induction')])
                for questions in rec.add_questions:
                    qc = self.env['kw_skill_question_bank'].sudo().search(
                        [('quesbank_rel', '=', qm.id), ('difficulty_level', '=', questions.question_type.id)])
                    if questions.no_of_question > len(qc):
                        raise ValidationError(
                            f"Question bank does not contain {questions.no_of_question} no of {questions.question_type.name} Questions for this Skill.")
                    if questions.question_type.name not in qtypes:
                        qtypes.append(questions.question_type.name)
                    else:
                        raise ValidationError(f"The question type {questions.question_type.name} is exists.")
                
            else:
                qm = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', rec.skill.id), ('type', '=', 'skill')])
                for questions in rec.add_questions:
                    qc = self.env['kw_skill_question_bank'].sudo().search(
                        [('quesbank_rel', '=', qm.id), ('difficulty_level', '=', questions.question_type.id)])
                    if questions.no_of_question > len(qc):
                        raise ValidationError(
                            f"Question bank does not contain {questions.no_of_question} no of {questions.question_type.name} Questions for this Skill.")
                    if questions.question_type.name not in qtypes:
                        qtypes.append(questions.question_type.name)
                    else:
                        raise ValidationError(f"The question type {questions.question_type.name} is exists.")

    @api.constrains('select_deg', 'select_individual', 'experience_id')
    def validate_applicable_candidate(self):
        for record in self:
            if record.applicable_candidate == '2' and not len(record.select_deg) > 0:
                raise ValidationError("Please select Designation")
            if record.applicable_candidate == '3' and not len(record.select_individual) > 0:
                # print("in validation============================")
                raise ValidationError("Please select Employee")
            if record.applicable_candidate == '4' and not len(record.experience_id) > 0:
                raise ValidationError("Please select Experience")

    @api.onchange('applicable_candidate')
    def clear_applicable_candidate(self):
        for record in self:
            if record.applicable_candidate == '2':  # designation
                record.select_individual = False
                record.experience_id = False
            elif record.applicable_candidate == '3':  # individual
                record.select_deg = False
                record.experience_id = False
            elif record.applicable_candidate == '4':  # experience
                record.select_individual = False
                record.select_deg = False
            else:  # all
                record.select_individual = False
                record.select_deg = False
                record.experience_id = False

    def take_test(self, extra_params=False):
        '''
        Parameter : extra_params : Dict to receive the parameters
        '''
        # form_view_id = self.env.ref("kw_skill_assessment.kw_question_set_config_form_view_view").id
        # skill_name = self.skill.name
        # # total_duration = self.duration
        # # questions = self.total_questions
        # # print(f'Total question is {self.total_questions}')

        # return {
        #     'name': skill_name + ' Test',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_skill_question_set_config',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'res_id': self.id,
        #     'view_id': form_view_id,
        #     'target': 'new',
        #     'domain': [('id', '=', self.id)]
        #     # 'context': { 'skill': skill_name, } ,
        #     # 'flags': {'mode': 'readonly',"toolbar":False }
        # }

        url = f"/test-instruction/{slug(self)}"
        if extra_params:
            url += f'?message={extra_params}'
        return {
            'type': 'ir.actions.act_url',
            'name': 'Test Instruction',
            'target': 'self',
            'url': url,
        }

    @api.multi
    def readonly_question_set(self):
        answer_master_record = self.env['kw_skill_answer_master'].search([('set_config_id', '=', self.id)])
        if answer_master_record:
            self.set_config_id_readonly = True
        else:
            self.set_config_id_readonly = False

    @api.multi
    def start_test(self):
        # context = self._context
        current_uid = self._uid
        # desg_name = ''
        user = self.env['res.users'].sudo().browse(current_uid).name
        if 'master_id' in request.session:
            request.session.pop('master_id')
        # request.session['master_id'] = 'hello'
        # skill_name = self.skill.name
        # skill_type_id = self.skill_types.id
        # skill_id = self.skill.id
        q_set_id = self.id

        url = f"/take_test?userid={current_uid}&ques_set_id={q_set_id}"

        return {
            'type': 'ir.actions.act_url',
            'name': 'Take Test',
            'target': 'self',
            'url': url,

            # 'context': { 'skill': skill_name, }
        }

    @api.model
    def question_set(self, set):
        ids = []
        set_id = set.id
        skill_type_id = set.skill_types.id
        skill_id = set.skill.id
        no_total_questions = set.total_questions
        add_questions = set.add_questions
        # print(set, set_id,no_total_questions,add_questions,skill_id,"===============skill_id========1st ========")
        for record in add_questions:
            no_of_category_questions = record.no_of_question
            name_of_category_questions = record.question_type
            # print(self,self.assessment_type,"==========self1>>>>>>>>>>>>>>>======assessment_type")
            if self.assessment_type == 'training':
                no_qid = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('id', '=', self.question_bank_id.id), ('skill', '=', skill_id), ('type', '=', 'training')])
                find_ques = self.env['kw_skill_question_bank'].sudo().search(
                    [('quesbank_rel', '=', no_qid.id), ('difficulty_level', '=', name_of_category_questions.id)])
                random_questions = random.sample(find_ques, no_of_category_questions)
                # random_questions = secrets.sample(find_ques, no_of_category_questions)
                for qrt in random_questions:
                    ids.append(qrt.id)
            elif self.assessment_type == 'Induction':
                no_qid = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', skill_id), ('type', '=', 'Induction')])
                find_ques = self.env['kw_skill_question_bank'].sudo().search(
                    [('quesbank_rel', '=', no_qid.id), ('difficulty_level', '=', name_of_category_questions.id)])
                random_questions = random.sample(find_ques, no_of_category_questions)
                # random_questions = secrets.sample(find_ques, no_of_category_questions)
                for qrt in random_questions:
                    ids.append(qrt.id)
            else:
                no_qid = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', skill_id), ('type', '=', 'skill')])
                find_ques = self.env['kw_skill_question_bank'].sudo().search(
                    [('quesbank_rel', '=', no_qid.id), ('difficulty_level', '=', name_of_category_questions.id)])
                # print(find_ques,no_of_category_questions,"no_of_category_questions >>>>>>>>>>>>>11111111111>>>>>>>>>")
                random_questions = random.sample(find_ques, no_of_category_questions)
                # random_questions = secrets.sample(find_ques, no_of_category_questions)
                # print(find_ques,no_of_category_questions,"no_of_category_questions >>>>>>>>>>>>>22222222222222222>>>>>>>>>")

                for qrt in random_questions:
                    ids.append(qrt.id)
        return ids

        # questions = self.env['kw_skill_question_bank_master'].search(
        #     [('skill', '=', skill_id), ('skill_types', '=', skill_t http.request.redirectid)]).questions
        # # # questions_weightage_ids = self.env['kw_skill_question_weightage'].search([])
        # # # for weigtage_ids in questions_weightage_ids:button
        # for i in questions:
        #     if len(ids) != no_total_questions:
        #         ids.append(i.id)
        #     else:
        #         break
        # return ids

    @api.model
    def get_questions(self, args):
        answer_master = args.get('answer_id', False)
        start_time = args.get('time_start', False)
        matching = 1
        answer_record = self.env['kw_skill_answer_master'].sudo().search(
            [('id', '=', answer_master)])
        if len(answer_record) > 0:
            if not answer_record.test_start_time:
                answer_record.write({'test_start_time': start_time})
            if answer_record.test_start_time != start_time:
                matching = 0

        if 'master_id' in request.session:
            m_id = request.session['master_id']
            check_id = self.env['kw_skill_answer_master'].search(['&', ('id', '=', m_id), ('status', '=', 'completed')])
            if len(check_id) > 0:
                valid = 0
            else:
                valid = 1

        ques_id = args.get('questionid', False)
        skillsetid = args.get('skillset_id', False)
        # skill_record = self.env['kw_skill_question_set_config'].sudo().search([('id', '=', skillsetid)])
        skill_record = self.env['kw_skill_question_set_config'].sudo().browse(skillsetid)
        # print(skill_record,"skill_record========================================")

        record = self.env['kw_skill_question_bank'].search(
            [('id', '=', ques_id)])
        for question_record in record:
            pass
            # question = question_record.justification
            # print(question)
        return [question_record.question, question_record.option_a, question_record.option_b, question_record.option_c,
                question_record.option_d, valid, matching]

        # uid = self._uid
        # master_record = self.env['kw_skill_answer_master'].sudo().create({'user_id': uid, 'skill_id': skill_record.skill.id, 'skill_type_id': skill_record.skill_types.id,'created_date':date.today()})
        # for question_record in record:
        # self.env['kw_skill_answer_child'].sudo().create({'ans_id':master_record.id, 'ques_id': question_record.id,'correct_option': question_record.correct_ans})

        # return [question_record.question, question_record.option_a, question_record.option_b, question_record.option_c, question_record.option_d,master_record.id]
        # # print(question_record.id)days()

    def publish_test(self):
        template = self.env.ref("kw_skill_assessment.kw_skill_configuration_email_template")
        if template:
            for rec in self:
                rec.write({'active': True, 'state': '2'})
                dept_child_ids = self._get_all_child_department(rec.dept)
                dept_child_ids += rec.dept
                # print("rec.assessment_type====================",rec.assessment_type)
                if rec.assessment_type == 'skill' :
                    subject = f"Skill Assessment added for %s" % rec.name
                    body = template.body_html

                    if rec.applicable_candidate == "1":
                        """# all employees of the department"""
                        emp_record = self.env['hr.employee'].sudo().search(
                            [("department_id", "in", dept_child_ids.ids)])
                        for record in emp_record:
                            extra_params = {'email_to': record.work_email, 'username': record.name}
                            template.with_context(extra_params).send_mail(rec.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
                    elif rec.applicable_candidate == "2":
                        """# for designation specific"""
                        emp_record1 = self.env['hr.employee'].sudo().search([('job_id', 'in', rec.select_deg.ids)])
                        for record in emp_record1:
                            extra_params = {'email_to': record.work_email, 'username': record.name}
                            template.with_context(extra_params).send_mail(rec.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
                    elif rec.applicable_candidate == "3":
                        """# for individual employees"""
                        emp_record2 = self.env['hr.employee'].sudo().search([('id', 'in', rec.select_individual.ids)])
                        for record in emp_record2:
                            extra_params = {'email_to': record.work_email, 'username': record.name}
                            template.with_context(extra_params).send_mail(rec.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")

                    elif rec.applicable_candidate == "4":
                        """# for experience specific"""
                        emp_record3 = self.env['hr.employee'].sudo().search(
                            [('department_id', 'in', dept_child_ids.ids)])
                        # print(emp_record3)
                        for record in emp_record3:
                            total_months = 0
                            if record.date_of_joining:
                                total_months += (datetime.today().year - record.date_of_joining.year) * 12 + (
                                        datetime.today().month - record.date_of_joining.month)
                            if record.work_experience_ids:
                                for exp_data in record.work_experience_ids:
                                    total_months += (exp_data.effective_to.year - exp_data.effective_from.year) * 12 + (
                                            exp_data.effective_to.month - exp_data.effective_from.month)
                            total_experience_years = math.floor(total_months / 12)
                            exp_record = self.env['kw_skill_experience_master'].sudo().search(
                                [('id', '=', rec.experience_id.id)])
                            if exp_record.min_exp <= total_experience_years <= exp_record.max_exp:
                                extra_params = {'email_to': record.work_email, 'username': record.name}
                                template.with_context(extra_params).send_mail(rec.id,
                                                                              notif_layout="kwantify_theme.csm_mail_notification_light")
                if rec.assessment_type == 'skill':
                    self.env.user.notify_success(message='Question set published successfully.')
                elif rec.assessment_type == 'Induction':
                    self.env.user.notify_success(message='Induction Assessment published successfully.')
                else:
                    self.env.user.notify_success(message='Training Assessment published successfully.')

    def unpublish_test(self):
        for record in self:
            record.write({'active': False, 'state': '1'})

    @api.model
    def create(self, vals):
        new_record = super(kw_question_set_config, self).create(vals)
        if new_record.assessment_type == 'skill':
            self.env.user.notify_success(message='Question set created successfully.')
        else:
            self.env.user.notify_success(message='Training assessment set created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_question_set_config, self).write(vals)
        # if vals.get('active') == False:
        #     self.write({'state':'1'})
        # if vals.get('active') == True:
        #     self.write({'state':'2'})
        # self.env.user.notify_success(message='Question set updated successfully.')
        return res

    def _get_all_child_department(self, dept_ids):
        child_recs = dept_ids.mapped('child_ids')
        if child_recs:
            return child_recs | self._get_all_child_department(child_recs)
        else:
            return child_recs

    @api.multi
    def _get_designation(self):
        uid = self.env.user.id
        record = self.env['hr.employee'].sudo().search([('user_id', '=', uid)])
        for rec in self:
            # all_child_ids = self._get_all_child_department(rec.dept)
            # print(all_child_ids)
            # print(record.department_id,rec.dept.ids)
            if record.department_id.id in rec.dept.ids:
                # print("true")
                if rec.applicable_candidate == '1':
                    rec.designation_id = True
                elif rec.applicable_candidate == '2':
                    if record.job_id.id in rec.select_deg.ids:
                        rec.designation_id = True
                elif rec.applicable_candidate == '3':
                    for ind in rec.select_individual:
                        for r in record:
                            if r.id == ind.id:
                                rec.designation_id = True
                elif rec.applicable_candidate == "4":
                    total_months = 0
                    if record.date_of_joining:
                        total_months += (datetime.today().year - record.date_of_joining.year) * 12 + (
                                datetime.today().month - record.date_of_joining.month)
                    if record.work_experience_ids:
                        for exp_data in record.work_experience_ids:
                            total_months += (exp_data.effective_to.year - exp_data.effective_from.year) * 12 + (
                                    exp_data.effective_to.month - exp_data.effective_from.month)
                    # print("Difference is %s months " % (total_months))
                    total_experience_years = math.floor(total_months / 12)
                    # print("Difference is %s years " % (total_experience_years))
                    exp_record = self.env['kw_skill_experience_master'].sudo().search(
                        [('id', '=', rec.experience_id.id)])
                    # print(exp_record.min_exp, ' >> ', total_experience_years, ' >> ', exp_record.max_exp)
                    if exp_record.min_exp <= total_experience_years <= exp_record.max_exp:
                        rec.designation_id = True

    @api.multi
    def _get_no_of_questions(self):
        for rec in self:
            qList = []
            if rec.assessment_type == 'training':
                # print(rec.question_bank_id.id)
                qm = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('id', '=', rec.question_bank_id.id), ('skill', '=', rec.skill.id), ('type', '=', 'training')])
                for questions in rec.add_questions:
                    qc = self.env['kw_skill_question_bank'].sudo().search(
                        [('quesbank_rel', '=', qm.id), ('difficulty_level', '=', questions.question_type.id)])
                    if questions.no_of_question <= len(qc):
                        qList.append(1)
                    else:
                        qList.append(0)
                if 0 not in qList:
                    rec.question_type = True
                else:
                    rec.question_type = False
            else:
                # print(rec.question_bank_id.id)
                qm = self.env['kw_skill_question_bank_master'].sudo().search(
                    [('skill', '=', rec.skill.id), ('type', '=', 'skill')])
                for questions in rec.add_questions:
                    qc = self.env['kw_skill_question_bank'].sudo().search(
                        [('quesbank_rel', '=', qm.id), ('difficulty_level', '=', questions.question_type.id)])
                    if questions.no_of_question <= len(qc):
                        qList.append(1)
                    else:
                        qList.append(0)
                if 0 not in qList:
                    rec.question_type = True
                else:
                    rec.question_type = False

    @api.multi
    def _validate_frequency(self):
        dict_freq = {'y': 365 * 24, 'h': 180 * 24, 'q': 90 * 24, 'm': 30 * 24}
        for record in self:
            frequency = record.frequency
            curr_date = datetime.now()
            data = self.env['kw_skill_answer_master'].sudo().search(
                ['&', ('user_id', '=', self._uid), ('set_config_id', '=', record.id)], order="create_date desc",
                limit=1)
            if len(data) > 0:
                date_gap = abs(curr_date - data.create_date).total_seconds() / 3600.0
                # print(f"date_gap for {record.skill.name} is {date_gap}")
                if frequency == 'o':
                    record.frequency_val = False
                elif frequency == 'n':
                    record.frequency_val = True
                elif frequency == 't':
                    yr = self.env['kw_skill_answer_master'].sudo().search(
                        ['&', ('user_id', '=', self._uid), ('set_config_id', '=', record.id)])
                    for rc in yr:
                        if rc.create_date + timedelta(int(record.interval) * 365 / 12) < datetime.now():
                            record.frequency_val = True
                        else:
                            record.frequency_val = False
                else:
                    if date_gap <= dict_freq[frequency]:
                        record.frequency_val = False
                    else:
                        record.frequency_val = True
            else:
                record.frequency_val = True
            # print(record.frequency_val)

    def get_eligible_tests(self):
        for record in self:
            if record.id == 72:
                # print(record.question_type,record.frequency_val,record.designation_id,record.id,"------------------>>>>>>>>>>>>1>>>>>>>>>>.record.designation_id")
                pass
            
            if record.question_type == True and record.frequency_val == True and record.designation_id == True:
                # print(record.question_type,record.frequency_val,record.designation_id,"===========>>>>>>>>>>>>>>>>>>>>>record.designation_id")
                record.eligible_tests = True,
            else:
                record.eligible_tests = False
            # print(record.eligible_tests)

    @api.multi
    def _value_search(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.eligible_tests is True)
        # print(recs)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        else:
            return [('id', 'in', [])]

    @api.multi
    def unlink(self):
        for record in self:
            if record.set_config_id_readonly == True:
                raise ValidationError(
                    'You cannot delete Question set.\n Because Some employee has been already given the test.')
            record.active = False
        return True
