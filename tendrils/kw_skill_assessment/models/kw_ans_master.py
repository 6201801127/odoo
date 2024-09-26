from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import time
from datetime import date
from odoo.http import request
from ast import literal_eval


class kw_answer_master(models.Model):
    _name = 'kw_skill_answer_master'
    _description = "Skill Assessment"
    _rec_name = 'user_id'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', string="User")
    skill_id = fields.Many2one('kw_skill_master', string="Skill")
    skill_type_id = fields.Many2one('kw_skill_type_master', string="Skill Type")
    total_mark = fields.Integer(string="Total Mark")
    total_mark_obtained = fields.Integer(string="Total Marks Obtained")
    percentage_scored = fields.Float(string="Percentage Scored")
    created_date = fields.Date(string="Created Date")
    time_taken = fields.Char(string="Time Taken")
    total_number_questions = fields.Integer(string="Total Number of Questions")
    total_attempted = fields.Integer(string="Total Attempted")
    total_mark_reviews = fields.Integer(string="Total Mark Reviews")
    count_tab_change = fields.Integer(string="Total No of Change the tab")
    total_correct_answer = fields.Integer(string="Total Correct Answer")
    # designation_name = fields.Char(compute="_get_designation",string="Get Designation Name")
    duration = fields.Char(compute="_get_duration", string="Test Duration")
    time_taken_duration = fields.Char(compute="_test_time_taken", string="Test Time Taken")
    test_name = fields.Char(compute="_get_test_name", string="Test Name")
    emp_rel = fields.Many2one('hr.employee', string="Employee Relationship")
    emp_id = fields.Integer(string="Employee Id", related='emp_rel.id')
    employee_code = fields.Char(string="Employee Code", compute="get_emp_code", )
    emp_desg = fields.Char(string="Employee Designation", related='emp_rel.job_id.name')
    emp_date_of_joining = fields.Date(string="Date of Joining", related='emp_rel.date_of_joining')
    
    set_config_id = fields.Many2one('kw_skill_question_set_config', string="Set Configuration Id")
    status = fields.Char(string="Test Status")
    score_id = fields.Many2one('kw_skill_score_master', string="Score Id")
    test_start_time = fields.Char(string="Test Start Time")
    strip_percentage = fields.Char(string="Strip Percentage", compute="_strip_percentage")

    child_ids = fields.One2many('kw_skill_answer_child', 'ans_id', string="Child Ids")

    def get_emp_code(self):
        for record in self:
            employee_id = self.env['hr.employee'].search([('id', '=', record.emp_rel.id)])
            # print(employee_id.emp_code)
            record.employee_code = employee_id.emp_code

    @api.model
    def save_answer(self, args):
        set_id = args.get('skill_set_id', False)
        uid = args.get('uid', False)
        q_id = args.get('qid', False)
        ans = args.get('ans', False)
        ans_masterid = args.get('answer_id', False)
        int_ans_masterid = int(ans_masterid)

        if set_id:
            skill_id = self.env['kw_skill_question_set_config'].browse(int(set_id))
            s_typ = skill_id.skill_types
            s_id = skill_id.skill
            t_mark = skill_id.total_marks
            answer = self.env["kw_skill_answer_master"].sudo().search([('id', '=', int_ans_masterid)])
            if len(answer) > 0:
                if answer.status == 'Initiated':
                    answer.write({'status': 'Started'})
                record1 = self.env['kw_skill_answer_child'].sudo().search(
                    ['&', ('ans_id', '=', answer.id), ('ques_id', '=', int(q_id))])
                if len(record1) > 0:
                    record1.write({'selected_option': ans})

                # else:
                #     correct_answer = self.env['kw_skill_question_bank'].sudo().search([('id', '=', q_id)])
                #     self.env['kw_skill_answer_child'].sudo().create({'ans_id':answer.id, 'ques_id': q_id , 'selected_option': ans,'correct_option': correct_answer.correct_ans})

            # else:
            #     master_record = self.env['kw_skill_answer_master'].sudo().create({'user_id': uid, 'skill_id': s_id.id, 'skill_type_id': s_typ.id,'total_mark': t_mark,'created_date':date.today()})
            #     ans_master_id =master_record.id
            #     correct_answer = self.env['kw_skill_question_bank'].sudo().search([('id', '=', q_id)])
            #     self.env['kw_skill_answer_child'].sudo().create({'ans_id':ans_master_id, 'ques_id': q_id , 'selected_option': ans,'correct_option': correct_answer.correct_ans})

    @api.model
    def calculate_marks(self, args):
        set_id = args.get('skill_set_id', False)
        uid = args.get('uid', False)
        startTime = args.get('startTime', False)
        timegap = args.get('timetaken', False)
        no_tab_change = args.get('tab_change_no', False)
        answer_masterid = args.get('master_answer_id', False)
        mark_reviews = args.get('mark_reviews', False)

        if answer_masterid:
            skill_id = self.env['kw_skill_question_set_config'].browse(int(set_id))
            s_typ = skill_id.skill_types
            s_id = skill_id.skill
            total_Questions = skill_id.total_questions
            total_correct_answer = 0
            total_marks = 0
            total_attempted = 0
            answer = self.env["kw_skill_answer_master"].sudo().search([('id', '=', answer_masterid)])
            child_record = self.env["kw_skill_answer_child"].sudo().search([('ans_id', '=', answer.id)])

            # print(total_Questions +  'Total Questions')
            # total_unattempted = total_Questions - total_attempted
            for record in child_record:
                total_marks += record.mark_obtained
                if record.selected_option:
                    total_attempted += 1
                if record.selected_option == record.correct_option:
                    total_correct_answer += 1
            # print(total_correct_answer) 
            # print(total_attempted)

            answer.write({'total_mark_obtained': total_marks,
                          'time_taken': timegap,
                          'total_number_questions': total_Questions,
                          'total_attempted': total_attempted,
                          'total_correct_answer': total_correct_answer,
                          'count_tab_change': no_tab_change,
                          'total_mark_reviews': mark_reviews})
            if total_marks > 0:
                percentage = (total_marks / answer.total_mark) * 100
                answer.write({'percentage_scored': percentage, 'status': 'Completed'})
            else:
                answer.write({'percentage_scored': 0, 'status': 'Completed'})
            score_record = self.env["kw_skill_score_master"].sudo().search([])
            for s in score_record:
                if s.min_value < answer.percentage_scored < s.max_value:
                    answer.write({'score_id': s.id})
                elif answer.percentage_scored == s.min_value:
                    answer.write({'score_id': s.id})
                elif answer.percentage_scored == 100 and s.max_value == 100:
                    answer.write({'score_id': s.id})

    @api.multi
    def _get_duration(self):
        for record in self:
            duration = self.env['kw_skill_question_set_config'].sudo().search([('id', '=', record.set_config_id.id)])
            record.duration = f"{round(int(duration.duration) / 3600, 2)} hour(s)"

    @api.model
    def _test_time_taken(self):
        for record in self:
            if record.time_taken and str.isdigit(record.time_taken):
                record.time_taken_duration = self.convert(int(record.time_taken))
            else:
                record.time_taken_duration = record.time_taken

    @api.multi
    def _get_test_name(self):
        for record in self:
            test = self.env['kw_skill_question_set_config'].sudo().search([('id', '=', record.set_config_id.id)])
            record.test_name = test.name

    @api.multi
    def view_details(self):
        self.ensure_one()
        form_view_id = self.env.ref("kw_skill_assessment.kw_view_test_details_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_skill_answer_master',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
        }
        # model_obj = self.env['ir.model.data']
        # res_id = self.id
        # data_id = model_obj._get_id('kw_skill_assessment', 'kw_view_test_details_action_window')
        # view_ids = model_obj.browse(data_id).res_id
        # return {
        #     'name':self.skill_id.name,
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_skill_answer_master',
        #     'view_id' :view_ids,
        #     'view_mode': 'tree,form',
        #     'view_type': 'form',
        #     'target': 'self',
        #     'domain':[('id','=',self.id)],
        # }

        # res = self.env['ir.actions.act_window'].for_xml_id('kw_skill_assessment', 'kw_view_test_details_action_window')
        # res['domain'] = [('id', '=', self.id)]
        # return res

    @api.multi
    def unlink(self):
        for record in self:
            child_record = self.env['kw_skill_answer_child'].sudo().search([('ans_id', '=', record.id)])
            if len(child_record) > 0:
                raise ValidationError("Selected record cannot be Deleted")

    @api.model
    def _strip_percentage(self):
        for record in self:
            s = str(format(record.percentage_scored, '.2f'))
            z = s.rstrip('0').rstrip('.') if '.' in s else s
            record.strip_percentage = z + "%"

    def convert(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0 and minutes == 0:
            return "%dh" % hour
        elif minutes > 0 and hour > 0:
            return "%dh %dm" % (hour, minutes)
        elif minutes > 0 and hour == 0:
            return "%dm" % minutes
        else:
            return "%ds" % seconds

    @api.model
    def _calculate_skill_mark(self):
        ans_master_record = self.env['kw_skill_answer_master'].sudo().search([])
        if not len(ans_master_record) == 0:
            for records in ans_master_record:
                total_correct_answer = 0
                total_marks = 0
                total_attempted = 0
                create_date = records.create_date
                test_duration = int(
                    self.env['kw_skill_question_set_config'].sudo().browse(records.set_config_id.id).duration)
                no_questions = self.env['kw_skill_question_set_config'].sudo().browse(
                    records.set_config_id.id).total_questions
                final_duration = create_date + datetime.timedelta(seconds=test_duration)
                current_time = datetime.datetime.now()
                if final_duration < current_time and records.status != "Completed":
                    child_last_updated_record = self.env['kw_skill_answer_child'].sudo().search(
                        [('ans_id', '=', records.id)], order="write_date desc", limit=1)
                    duration = child_last_updated_record.write_date - create_date
                    if str(duration).find(',') == -1:
                        x = time.strptime(str(duration).split('.')[0], '%H:%M:%S')
                        y = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
                    else:
                        a = str(duration)[str(duration).find(',') + 2:]
                        x = time.strptime(a.split('.')[0], '%H:%M:%S')
                        y = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                    child_record = self.env["kw_skill_answer_child"].sudo().search([('ans_id', '=', records.id)])
                    for rec in child_record:
                        total_marks += rec.mark_obtained
                        if rec.selected_option:
                            total_attempted += 1
                        if rec.selected_option == rec.correct_option:
                            total_correct_answer += 1

                    records.write({'time_taken': int(y),
                                   'total_mark_obtained': total_marks,
                                   'total_attempted': total_attempted,
                                   'total_correct_answer': total_correct_answer,
                                   'total_number_questions': no_questions})
                    if total_marks > 0:
                        percentage = (total_marks / records.total_mark) * 100
                        records.write({'percentage_scored': percentage, 'status': 'Completed'})
                    else:
                        records.write({'percentage_scored': 0, 'status': 'Completed'})

    @api.multi
    def get_manager_groups_users_email(self):
        # print("called")
        # group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_manager')
        manager_email = ""
        manager_employee_ids = literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('kw_skill_assessment.skill_manager_emp_name'))
        # print(manager_employee_ids)

        # if manager_employee_ids:
        manager_emp = self.env['hr.employee'].browse(manager_employee_ids)
        return manager_emp and ','.join(manager_emp.mapped('work_email')) or ''
