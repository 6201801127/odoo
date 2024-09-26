# -*- coding: utf-8 -*-
import random
import bs4 as bs
import datetime
import time
import itertools
from datetime import date
from odoo import http
from odoo.http import request
from odoo.http import request
from collections import Counter


def emp_count(rec, id):
    temp = []
    for t in rec:
        if t[3] not in temp and id == t[0]:
            temp.append(t[3])
    return len(temp)


def percent_count(rec, id):
    count = emp_count(rec, id)
    if count > 0:
        score_count = 0
        temp = []
        for t in rec:
            if id == t[0]:
                score_count += t[5]
        return score_count / count


def fail(rec, id):
    count = emp_count(rec, id)
    if count > 0:
        pass


class kw_assessment(http.Controller):
    @http.route('/take_test', auth="public", website=True)
    def take_test(self, **args):
        # import pdb
        # pdb.set_trace()
        if http.request.session.uid is None:
            return http.request.redirect('/web')

        if 'userid' in args:
            infodict = dict()

            # user_id = args['userid']
            user_id = http.request.session['uid']
            # print(user_id,"user_id============================")
            set_id = int(args['ques_set_id'])
            # print(set_id,"set id===================",type(set_id))
            # skill_set = http.request.env['kw_skill_question_set_config'].sudo().search([('id', '=', set_id)])
            skill_set = http.request.env['kw_skill_question_set_config'].sudo().browse(set_id)
            # print("skill_set >>> ", skill_set, skill_set2)
            # sdkjfsdfjsdf
            infodict['skill_set'] = skill_set
            emp_record = http.request.env['hr.employee'].search([('user_id', '=', user_id)])
            infodict['employee'] = emp_record
            infodict['questions'] = http.request.env['kw_skill_question_set_config'].sudo().browse(set_id).question_set(skill_set)
            # print("infodict >>> ", infodict)
            # asasa
            # soup = http.request.env['kw_skill_question_set_config'].search([('id', '=', set_id)]).instruction
            if skill_set.instruction:
                soup = skill_set.instruction
                infodict['ques_instruction'] = (bs.BeautifulSoup(soup)).text
            else:
                infodict['ques_instruction'] = 'NA'

            if skill_set.applicable_candidate == '1':
                pass
            if skill_set.applicable_candidate == '2':
                emp = http.request.env['hr.employee'].search([('user_id', '=', user_id)])
                mylst = []
                for deg in skill_set.select_deg:
                    mylst.append(deg.id)
                for r in emp:
                    if r.job_id.id not in mylst:
                        return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
            if skill_set.applicable_candidate == '3':
                lyst = []
                for ind in skill_set.select_individual:
                    lyst.append(ind.user_id.id)
                if user_id not in lyst:
                    return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')

            dict_freq = {'y': 365 * 24, 'h': 180 * 24, 'q': 90 * 24, 'm': 30 * 24}
            frequency = skill_set.frequency
            assessment_type = skill_set.assessment_type
            curr_date = datetime.datetime.now()
            data = http.request.env['kw_skill_answer_master'].sudo().search(
                ['&', ('user_id', '=', user_id), ('set_config_id', '=', skill_set.id)], order="create_date desc",
                limit=1)
            if len(data) > 0:
                date_gap = abs(curr_date - data.create_date).total_seconds() / 3600.0
                if frequency == 'o' and assessment_type != "Induction":
                    return http.request.redirect(
                        '/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                if frequency == 'o' and assessment_type == "Induction" and skill_set.induction_code != 'POSH':
                    return http.request.redirect(
                        '/web#action=kw_onboarding_induction_feedback.action_kw_induction_assessment_user_readonly_act_window&model=kw_employee_induction_assessment&view_type=kanban')
                if frequency == 'o' and assessment_type == "Induction" and skill_set.induction_code == 'POSH':
                    return http.request.redirect(
                        '/web#action=kw_onboarding_induction_feedback.action_posh_induction_user_readonly_act_window&model=kw_employee_posh_induction_details&view_type=kanban')
                if frequency == 't':
                    a = []
                    yr = http.request.env['kw_skill_answer_master'].sudo().search(
                        ['&', ('user_id', '=', user_id), ('set_config_id', '=', skill_set.id)])
                    for rc in yr:
                        if rc.create_date.year == curr_date.year:
                            a.append(rc.id)
                    if len(a) >= 2:
                        return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                if frequency in dict_freq and date_gap <= dict_freq[frequency]:
                    return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')

            answer_freq = http.request.env['kw_skill_answer_master'].search(
                ['&', '&', '&', ('user_id', '=', user_id), ('set_config_id', '=', skill_set.id),
                 ('status', '!=', 'Completed'), ('created_date', '=', date.today())], order="create_date desc", limit=1)
            if not len(answer_freq) == 0:
                # for re in answer_freq:
                create_date = answer_freq.create_date
                test_duration = int(http.request.env['kw_skill_question_set_config'].sudo().browse(answer_freq.set_config_id.id).duration)
                final_duration = create_date + datetime.timedelta(seconds=test_duration)
                current_time = datetime.datetime.now()
                if final_duration > current_time and answer_freq.status != "Completed":
                    return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                if final_duration < current_time and answer_freq.status == "Completed":
                    if skill_set.applicable_candidate == '1':
                        pass
                    if skill_set.applicable_candidate == '2':
                        emp = http.request.env['hr.employee'].search([('user_id', '=', user_id)])
                        mylst = []
                        for deg in skill_set.select_deg:
                            mylst.append(deg.id)
                        for r in emp:
                            if r.job_id.id not in mylst:
                                return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                    if skill_set.applicable_candidate == '3':
                        lyst = []
                        for ind in skill_set.select_individual:
                            lyst.append(ind.user_id.id)
                        if user_id not in lyst:
                            return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')

                    dict_freq = {'y': 365 * 24, 'h': 180 * 24, 'q': 90 * 24, 'm': 30 * 24}
                    frequency = skill_set.frequency
                    curr_date = datetime.datetime.now()
                    data = http.request.env['kw_skill_answer_master'].sudo().search(
                        ['&', ('user_id', '=', user_id), ('set_config_id', '=', skill_set.id)],
                        order="create_date desc", limit=1)
                    if len(data) > 0:
                        date_gap = abs(curr_date - data.create_date).total_seconds() / 3600.0
                        if frequency == 'o':
                            return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                        if frequency == 't':
                            a = []
                            yr = http.request.env['kw_skill_answer_master'].sudo().search(
                                ['&', ('user_id', '=', user_id), ('set_config_id', '=', skill_set.id)])
                            for rc in yr:
                                if rc.create_date.year == curr_date.year:
                                    a.append(rc.id)
                            if len(a) >= 2:
                                return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')
                        if frequency in dict_freq and date_gap <= dict_freq[frequency]:
                            return http.request.redirect('/web#action=kw_skill_assessment.kw_my_skill_action_window&model=kw_skill_answer_master&view_type=kanban')

            child_ids = []
            for i in infodict['questions']:
                c_ans = http.request.env['kw_skill_question_bank'].sudo().search([('id', '=', i)])
                weightage = http.request.env['kw_skill_question_weightage'].sudo().search([('id', '=', c_ans.difficulty_level.id)])
                child_ids.append([0, 0, {'ques_id': i,
                                         'correct_option': c_ans.correct_ans,
                                         'difficulty_id': c_ans.difficulty_level,
                                         'weightage': weightage.weightage}])
            master_record = http.request.env['kw_skill_answer_master'].sudo().create({
                'user_id': user_id,
                'skill_id': skill_set.skill.id,
                'skill_type_id': skill_set.skill_types.id,
                'total_mark': skill_set.total_marks,
                'created_date': date.today(),
                'emp_rel': emp_record.id,
                'status': 'Initiated',
                'set_config_id': skill_set.id,
                'child_ids': child_ids})
            template = http.request.env.ref("kw_skill_assessment.kw_skill_email_template")
            if template and skill_set.assessment_type == 'skill':
                template.send_mail(master_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            infodict['answer_master_id'] = master_record.id
            http.request.session['master_id'] = master_record.id
            return http.request.render('kw_skill_assessment.kw_skill_assessment_test', infodict)
        else:
            return http.request.redirect('/web')

    @http.route('/skill-employee-report', type='json', auth="user", website=True)
    def skill_employee_report(self, **args):

        dept = []
        departments = http.request.env['hr.department'].sudo().search([])
        for record in departments:
            dept.append({'id': record.id, 'name': record.name})

        stm = []
        skill_type_master = http.request.env['kw_skill_type_master'].sudo().search([])
        for record in skill_type_master:
            stm.append({'id': record.id, 'name': record.skill_type})

        sm = []
        skill_master = http.request.env['kw_skill_master'].sudo().search([])
        for rec in skill_master:
            sm.append({'id': rec.id, 'name': rec.name, 'skill_type': rec.skill_type.id})

        count_child_id = []
        for record in skill_type_master:
            child_id_length = http.request.env['kw_skill_master'].sudo().search([('skill_type.id', '=', record.id)])
            count_child_id.append(len(child_id_length))

        emp = http.request.env['hr.employee'].sudo().search([])
        all_answer_data = http.request.env['kw_skill_answer_master'].sudo().search([])
        percentage = []
        for record in all_answer_data:
            percentage.append(record.percentage_scored)
        emp_skill_answer_data = all_answer_data.mapped(lambda r: r.user_id)
        # question_set_assessment_type = all_answer_data.filtered(lambda r: r.set_config_id.assessment_type == "skill")
        # print(question_set_assessment_type)
        emp_skill_data = []
        for employee in emp:
            # if question_set_assessment_type.set_config_id.assessment_type == 'skill':
            if emp_skill_answer_data:
                skill_answer_master_data = {}
                skill_answer_master_data['emp_name'] = employee.name
                skill_answer_master_data['emp_code'] = employee.emp_code
                skill_answer_master_data['designation'] = employee.job_id.name
                sum = 0
                color = ''
                for skill_master_data in skill_master:
                    filter_emp_answer_data = all_answer_data.filtered(
                        lambda r: r.user_id == employee.user_id and r.skill_id.id == skill_master_data.id and r.set_config_id.assessment_type == "skill")
                    percentage_sc = 0
                    if filter_emp_answer_data:
                        maxm = max([record.id for record in filter_emp_answer_data])
                        for total_mark in filter_emp_answer_data:
                            if total_mark.id == maxm:
                                percentage_sc = float("%.2f" % total_mark.percentage_scored)
                                # print(percentage_sc)
                                if round(percentage_sc) <= 40:
                                    color = "Red"
                                elif 41 <= round(percentage_sc) <= 70:
                                    color = "Orange"
                                else:
                                    color = "Green"

                                t_mark = total_mark.total_mark_obtained
                                sum = sum + t_mark
                    skill_answer_master_data[skill_master_data.name] = (color if filter_emp_answer_data else 'No')
                    skill_answer_master_data[skill_master_data.id] = (percentage_sc if filter_emp_answer_data else 'No')
                skill_answer_master_data['sum_skill_mark'] = sum
                emp_skill_data.append(skill_answer_master_data)
        infodict = dict(department=dept, skill_type=stm, count_child=count_child_id, skill_master=sm,
                        emp_scores=emp_skill_data)
        return infodict

    @http.route('/result', type='http', auth="user", website=True)
    def skill_result(self, **args):
        answer_masterid = args.get('answer_master_id', False)
        # print(answer_masterid,"answer_masterid============================")
        infodict = dict()
        infodict['weightage_type'] = {}
        infodict['total'] = {}
        user_id = http.request.session['uid']
        infodict['employee'] = http.request.env['hr.employee'].search([('user_id', '=', user_id)])
        # print(infodict['employee'],"infodict['employee']==================================================")
        skill_answer_master = http.request.env['kw_skill_answer_master'].search([('id', '=', answer_masterid)])
        set_config_id = skill_answer_master.set_config_id
        infodict['answer_record'] = skill_answer_master
        # print(infodict['answer_record'],"infodict['answer_record']==========")
        weightage_records = http.request.env['kw_skill_question_weightage'].search([])
        alloted_duration = http.request.env['kw_skill_question_set_config'].search(
            [('id', '=', infodict['answer_record'].set_config_id.id)]).duration
        infodict['alloted_time'] = self.convert(int(alloted_duration))

        if infodict['answer_record'].time_taken and str.isdigit(infodict['answer_record'].time_taken):
            infodict['time_taken'] = self.convert(int(infodict['answer_record'].time_taken))
            # infodict['time_taken'] = time.strftime("%Hhr %Mmin %Ssec", time.gmtime(int(infodict['answer_record'].time_taken)))
        else:
            infodict['time_taken'] = time.strftime("%Hhr %Mmin %Ssec", time.gmtime(infodict['answer_record'].time_taken))

        total_questions = 0
        total_correct_answer = 0
        for c in weightage_records:
            sec_mark = 0
            correct_answer = 0
            no_ques = 0
            child_rec = http.request.env['kw_skill_answer_child'].search(
                ['&', ('ans_id', '=', int(answer_masterid)), ('difficulty_id', '=', c.id)])
            if len(child_rec) > 0:
                for record in child_rec:
                    sec_mark += record.mark_obtained
                    if record.selected_option == record.correct_option:
                        correct_answer += 1
                quest_config_rec = http.request.env['kw_skill_question_set_config'].search(
                    [('id', '=', infodict['answer_record'].set_config_id.id)]).add_questions
                for q in quest_config_rec:
                    if q.question_type.id == c.id:
                        no_ques = q.no_of_question
                total_questions += no_ques
                total_correct_answer += correct_answer
                infodict['weightage_type'].update({c.name: [no_ques, correct_answer, sec_mark]})
        infodict['total_ques'] = total_questions
        infodict['total_correct_ans'] = total_correct_answer
        if set_config_id.assessment_type == "Induction" and set_config_id.induction_code != 'POSH':
            record_emp = http.request.env['kw_employee_induction_assessment'].sudo().search([('assessment_id','=',set_config_id.id)])
            template = request.env.ref("kw_onboarding_induction_feedback.kw_induction_assessment_result_email_template")
            if record_emp :
                users = request.env['res.users'].sudo().search([])
                manager = users.filtered(lambda user: user.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_notify_manager') == True)
                manager_name = ','.join(manager.mapped('name')) if manager else ''
                email_to = ','.join(manager.mapped('email'))  if manager else ''
                if template:
                    assessment_name = set_config_id.name
                    emp_name = request.env.user.employee_ids.name
                    email_from=request.env.user.employee_ids.work_email
                    template.with_context(email_from = email_from,email_to=email_to,emp_name=emp_name,assessment=assessment_name,manager_name=manager_name).send_mail(record_emp.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                request.env.user.notify_success("Notified to manager successfully.")
        elif set_config_id.assessment_type == "Induction" and set_config_id.induction_code == 'POSH':
            template = request.env.ref("kw_onboarding_induction_feedback.kw_induction_posh_assessment_result_email_template")
            posh_induction = http.request.env['kw_employee_posh_induction_details'].sudo().search([('assessment_id','=',set_config_id.id)])
            posh_induction.write({'induction_complete':True,'complete_date':date.today(),'status_induction':'Complete'})
            
            if template:
                assessment_name = set_config_id.name
                emp_name = request.env.user.employee_ids.name
                email_to=request.env.user.employee_ids.work_email
                email_from = posh_induction.posh_assign_user.work_email
                template.with_context(email_from = email_from,email_to=email_to,emp_name=emp_name,assessment=assessment_name).send_mail(posh_induction.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            request.env.user.notify_success("Notified to Employee successfully.")
        return http.request.render('kw_skill_assessment.kw_skill_result', infodict)

    @http.route('/test-instruction/<model("kw_skill_question_set_config"):question_set>', type='http', auth="user",
                website=True)
    def test_instruction(self, question_set, **args):
        # print(args)
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        question_dict = {'question_set': question_set}
        if 'message' in args:
            question_dict['message'] = args['message']
        return http.request.render('kw_skill_assessment.kw_skill_assessment_index2', question_dict)

    # def convert_to_string(self, seconds):
    #     min, sec = divmod(seconds, 60) 
    #     hour, min = divmod(min, 60) 
    #     if hour > 0:
    #         return "%dhr %02dmin %02dsec" % (hour, min, sec) 
    #     elif min > 0:
    #         return "%02dmin %02dsec" % (min, sec) 
    #     else:
    #         return "%02dsec" % (sec)

    def convert(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0 and minutes == 0:
            return "%dh" % (hour)
        elif minutes > 0 and hour > 0:
            return "%dh %dm" % (hour, minutes)
        elif minutes > 0 and hour == 0:
            return "%dm" % (minutes)
        else:
            return "%ds" % (seconds)

    @http.route('/skill-stack-report', type='json', auth="user", website=True)
    def skill_stack_report(self, **args):
        query = "SELECT gm.id AS gm_id, gm.name AS gm_name, a.id AS a_id, a.user_id AS a_user_id, a.skill_id AS a_skill_id, a.percentage_scored AS a_percentage_scored\
                FROM kw_skill_group_master gm\
                JOIN kw_skill_group_master_kw_skill_master_rel gmr ON gm.id=gmr.kw_skill_group_master_id\
                JOIN kw_skill_master sm ON sm.id=gmr.kw_skill_master_id\
                JOIN kw_skill_answer_master a ON a.skill_id=sm.id\
                WHERE a.id in (SELECT id FROM (select row_number() over(partition by user_id, skill_id order by id desc) as sl_no, * FROM kw_skill_answer_master) adt where sl_no=1)"
        request.cr.execute(query)
        data = request.cr.fetchall()
        sgm = []
        sgm_record = http.request.env['kw_skill_group_master'].sudo().search([])
        for record in sgm_record:
            sgm.append({'id': record.id,
                        'name': record.name,
                        'skills': [r.name for r in record.skills],
                        'emp_count': emp_count(data, record.id),
                        'percentage': percent_count(data, record.id)})
        infodict = dict(skill_group=sgm)
        return infodict

    @http.route('/skill-report', type='json', auth="user", website=True)
    def skill_report(self, **args):

        query = """
            with sam as 
                (
                SELECT skill_id, sum(case when percentage_scored < 40 then 1 else 0 end) as fail, COUNT(a.ID) AS TOTAL
                , json_agg(json_build_object
                ('Name',e.name, 'Emp Code',e.emp_code, 
                'Designation',(select name from hr_job where id = e.job_id), 
                'Department',(select name from hr_department where id = e.department_id),
                'Score',(SELECT TRUNC(percentage_scored::NUMERIC,2)) )) as total_users
                    
                , sum(case when percentage_scored between 41 and 70 then 1 else 0 end) as average
                , sum(case when percentage_scored > 71 then 1 else 0 end) as good
                , avg(percentage_scored) as percentage_scored
                , json_agg(case when percentage_scored < 40 then json_build_object
                    ('Name',e.name, 'Emp Code',e.emp_code, 
                    'Designation',(select name from hr_job where id = e.job_id), 
                    'Department',(select name from hr_department where id = e.department_id),
                    'Score',(select TRUNC(percentage_scored::NUMERIC,2)) ) end) as fail_user
                ,json_agg(case when percentage_scored between 41 and 70 
                    then json_build_object
                    ('Name',e.name, 'Emp Code',e.emp_code, 
                    'Designation',(select name from hr_job where id = e.job_id), 
                    'Department',(select name from hr_department where id = e.department_id),
                    'Score',(select TRUNC(percentage_scored::NUMERIC,2)) ) end) as average_user
                , json_agg(case when percentage_scored > 71 then json_build_object
                    ('Name',e.name, 'Emp Code',e.emp_code, 
                    'Designation',(select name from hr_job where id = e.job_id), 
                    'Department',(select name from hr_department where id = e.department_id),
                    'Score',(select TRUNC(percentage_scored::NUMERIC,2)) ) end) as good_user
                FROM kw_skill_answer_master a
                INNER JOIN hr_employee as e on e.user_id = a.user_id
                WHERE a.id in (select id from 
                (SELECT row_number() over(partition by user_id,skill_id order by id desc) as sl_no, * FROM kw_skill_answer_master 
                WHERE set_config_id in 
                (SELECT id from kw_skill_question_set_config WHERE assessment_type = 'skill')
                ) adt where sl_no=1) group by skill_id)
                
                SELECT sm.id,sm.name
                ,COALESCE(total,0) AS total
                , COALESCE(fail, 0) AS fail
                , COALESCE(average, 0) AS average
                , COALESCE(good, 0) AS good
                , COALESCE(round( CAST(sam.percentage_scored as numeric), 2), 0) AS percentage_scored
                , COALESCE(sam.good_user, '[]') AS good_users
                , COALESCE(sam.average_user, '[]') AS average_user
                , COALESCE(sam.fail_user , '[]') AS fail_user
                , COALESCE(sam.total_users , '[]') AS total_users
                from kw_skill_master sm
                
                LEFT join sam on sm.id = sam.skill_id order by total desc,sm.name
        """
        request.cr.execute(query)
        data = request.cr.fetchall()
        total_emp = sum([i[2] for i in data])
        sk = []
        for record in data:
            sk.append(
                {'id': record[0],
                 'name': record[1],
                 'emp_count': record[2],
                 'emp_percent': round((record[2] / total_emp) * 100, 2) if record[2] != 0 else 0,
                 'fail': record[3],
                 'average': record[4],
                 'good': record[5],
                 'percentage': record[6],
                 'good_users': record[7],
                 'average_users': record[8],
                 'fail_users': record[9],
                 'total_users': record[10]})
        infodict = dict(sk_master=sk)
        return infodict

    @http.route('/core_skill-report', type='json', auth="user", website=True)
    def core_skill_report(self, **args):

        query = """
             select id,name,COALESCE(core_resource_strength,0) as core_resource_strength,
             COALESCE(resource_with_knowledge,0) as resource_with_knowledge,fail,average,good,percentage_scored,good_users,
             average_users,fail_users,COALESCE(core_resource_strength_users, '[]') as core_resource_strength_users,
             COALESCE(resource_with_knowledge_users, '[]') as resource_with_knowledge_users from
            (select * from
            (with sam as 
                (
                select skill_id, sum(case when percentage_scored < 40 then 1 else 0 end) as fail, COUNT(a.user_id) AS TOTAL
                , sum(case when percentage_scored between 41 and 70 then 1 else 0 end) as average
                , sum(case when percentage_scored > 71 then 1 else 0 end) as good
                , avg(percentage_scored) as percentage_scored
					
				, json_agg(case when percentage_scored < 40 then json_build_object
				('Name',a.name, 'Emp Code',a.emp_code, 
				 'Designation',(select name from hr_job where id = a.job_id), 
				 'Department',(select name from hr_department where id = a.department_id),
				 'Score',(select TRUNC(percentage_scored::NUMERIC,2))) end) as fail_user	
				,json_agg(case when percentage_scored between 41 and 70 
				then json_build_object
				('Name',a.name, 'Emp Code',a.emp_code, 
				 'Designation',(select name from hr_job where id = a.job_id), 
				 'Department',(select name from hr_department where id = a.department_id),
				 'Score', (select TRUNC(percentage_scored::NUMERIC,2))) end) as average_user
				,json_agg(case when percentage_scored > 71 then json_build_object
				('Name',a.name, 'Emp Code',a.emp_code, 
				 'Designation',(select name from hr_job where id = a.job_id), 
				 'Department',(select name from hr_department where id = a.department_id),
				 'Score',(select TRUNC(percentage_scored::NUMERIC,2))) end) as good_user
					
                from (select h.user_id,s.skill_id,s.percentage_scored,h.name,h.emp_code,h.job_id,h.department_id from hr_employee as h
            join kw_skill_answer_master as s on s.user_id=h.user_id and h.primary_skill_id=s.skill_id where h.active is true) a
                where a.user_id in (select user_id from
                (select row_number() over(partition by user_id,skill_id order by id desc) as sl_no, * from kw_skill_answer_master 
                where set_config_id in 
                (select id from kw_skill_question_set_config where assessment_type = 'skill')
                ) adt where sl_no=1) group by skill_id)

            select sm.id,sm.name
            ,COALESCE(TOTAL,0) as TOTAL
            , COALESCE(fail, 0) as fail
            , COALESCE(average, 0) as average
            , COALESCE(good, 0) as good
            , COALESCE(round( CAST(sam.percentage_scored as numeric), 2), 0) as percentage_scored
			, COALESCE(sam.fail_user, '[]') as fail_users
			, COALESCE(sam.good_user, '[]') as good_users
			, COALESCE(sam.average_user, '[]') as average_users 
            from kw_skill_master sm
            LEFT join sam on sm.id = sam.skill_id) as p
            Left outer join
            (SELECT COALESCE(primary_skill_id,0) as primary_skill_id,COUNT(*) AS "core_resource_strength"
			 ,json_agg(json_build_object
				('Name',a.name, 'Emp Code',a.emp_code, 
				 'Designation',(select name from hr_job where id = a.job_id), 
				 'Department',(select name from hr_department where id = a.department_id))) as core_resource_strength_users
					
            FROM hr_employee as a LEFT JOIN kw_skill_master on a.primary_skill_id = kw_skill_master.id where a.active is true
            GROUP BY primary_skill_id) as q
            on p.id=q.primary_skill_id) as x
            Left outer join
            (SELECT COALESCE(skill_id,0) as skill_id,COUNT(distinct a.user_id) AS "resource_with_knowledge"
			 ,json_agg(json_build_object
				('Name',a.name, 'Emp Code',a.emp_code, 
				 'Designation',(select name from hr_job where id = a.job_id), 
				 'Department',(select name from hr_department where id = a.department_id),
				 'Score',(select TRUNC(kw_skill_answer_master.percentage_scored::NUMERIC,2)) )) as resource_with_knowledge_users
            from kw_skill_answer_master 
            join hr_employee as a on kw_skill_answer_master.skill_id=a.primary_skill_id and kw_skill_answer_master.user_id=a.user_id 
            where a.active is true
            GROUP BY kw_skill_answer_master.skill_id) as y
            on x.id=y.skill_id
            """

        request.cr.execute(query)
        data = request.cr.fetchall()
        sk = []
        for record in data:
            sk.append(
                {'id': record[0],
                 'name': record[1],
                 'total_emp_count': record[2],
                 'emp_count': record[3],
                 'emp_percent': round((record[3] / record[2]) * 100, 2) if record[2] != 0 else 0,
                 'fail': record[4],
                 'average': record[5],
                 'good': record[6],
                 'percentage': record[7],
                 'good_users': record[8],
                 'average_users': record[9],
                 'fail_users': record[10],
                 'core_resource_strength_users': record[11],
                 'resource_with_knowledge_users': ([dict(t) for t in {tuple(d.items()) for d in record[12]}])})
        infodict = dict(sk_master=sk)
        return infodict

    @http.route('/skill_status-report', type='json', auth="user", website=True)
    def skill_status_report(self, **args):

        query = """
            select id,name,COALESCE(employee_count,0) as employee_count,COALESCE(appear_employee_count,0) as appear_employee_count,
            total,core_resourse_strength_users,COALESCE(appeared_users,'[]') as core_resourse_appeared_users,total_users from 
            (select id,name,total,employee_count,COALESCE(users,'[]') as core_resourse_strength_users,total_users from
            (with sam as 
            (
                select skill_id, COUNT(a.ID) AS TOTAL,json_agg(json_build_object
            ('Name',e.name, 'Emp Code',e.emp_code, 
                'Designation',(select name from hr_job where id = e.job_id), 
                'Department',(select name from hr_department where id = e.department_id))) as total_users
                from kw_skill_answer_master a
                inner join hr_employee as e on e.user_id = a.user_id 
                where e.active is true and a.id in (select id from 
                (select row_number() over(partition by user_id,skill_id order by id desc) as sl_no, * from kw_skill_answer_master 
                where set_config_id in 
                (select id from kw_skill_question_set_config where assessment_type = 'skill')
                ) adt where sl_no=1) group by skill_id
            )
            select sm.id,sm.name
            ,COALESCE(TOTAL,0) as TOTAL,COALESCE(total_users,'[]') as total_users
            from kw_skill_master sm
            LEFT join sam on sm.id = sam.skill_id) as c

            LEFT OUTER JOIN

            (SELECT COALESCE(primary_skill_id,0) as primary_skill_id,COALESCE(COUNT(*),0) AS "employee_count"
                ,json_agg(json_build_object
            ('Name',e.name, 'Emp Code',e.emp_code, 
                'Designation',(select name from hr_job where id = e.job_id), 
                'Department',(select name from hr_department where id = e.department_id))) as users
                
            FROM hr_employee as e 
            LEFT JOIN kw_skill_master on e.primary_skill_id = kw_skill_master.id 
            WHERE e.active is true 
            GROUP BY primary_skill_id) as b

            ON c.id=b.primary_skill_id) as p

            LEFT OUTER JOIN

            (SELECT COALESCE(skill_id,0) as skill_id,COUNT(distinct e.user_id) AS "appear_employee_count"
                ,json_agg(json_build_object
            ('Name',e.name, 'Emp Code',e.emp_code, 
                'Designation',(select name from hr_job where id = e.job_id), 
                'Department',(select name from hr_department where id = e.department_id))) as appeared_users
            from kw_skill_answer_master 
            join hr_employee as e on kw_skill_answer_master.skill_id=e.primary_skill_id and kw_skill_answer_master.user_id=e.user_id 
            WHERE e.active is true
            GROUP BY kw_skill_answer_master.skill_id) as q

            ON p.id=q.skill_id
            """

        request.cr.execute(query)
        data = request.cr.fetchall()
        sk = []
        for record in data:
            sk.append(
                {'id': record[0],
                 'name': record[1],
                 'total_emp_count': record[2],
                 'appear_emp_count': record[3],
                 'appear_emp_percent': round(((record[3] / record[2]) * 100), 2) if record[2] != 0 else 0,
                 'not_appear_emp_count': record[2] - record[3],
                 'not_appear_emp_percent': round(((record[2] - record[3]) / record[2]) * 100, 2) if record[2] != 0 else 0,
                 'total_appeared': record[4],
                 'core_resourse_strength_users': record[5],
                 'core_resourse_appeared_users': ([dict(t) for t in {tuple(d.items()) for d in record[6]}]),
                 'total_users': record[7],
                 'core_resourse_not_appeared_users': [i for i in record[5] if i not in [dict(t) for t in {tuple(d.items()) for d in record[6]}]]})
        infodict = dict(sk_master=sk)
        return infodict

    @http.route('/users_skill-report', type='json', auth="user", website=True)
    def users_skill_report(self, **args):

        # query = """
        # select emp_id,resource_name,designation,core_skill from
        # (select emp_id,a.user_id,a.name as resource_name,j.name as designation,a.primary_skill_id from
        # (select h.user_id,h.name,h.job_id,h.primary_skill_id,h.id as emp_id from hr_employee as h inner join kw_skill_answer_master as k on h.user_id=k.user_id 
        # and h.primary_skill_id=k.skill_id) as a
        # Left outer join (select id,name from hr_job) as j on a.job_id=j.id) as p
        # left outer join (select id,name as core_skill from kw_skill_master) as ks
        # on p.primary_skill_id=ks.id"""
        # request.cr.execute(query)
        # data = request.cr.fetchall()
        # print(data)
        query = """select a.id as emp_id,a.name as resource_name,a.designation,core_skill from
            (select h.id,h.name,h.job_id,j.name as designation,h.primary_skill_id from hr_employee as h 
            left outer join hr_job as j on  h.job_id=j.id) as a
            left outer join (select id,name as core_skill from kw_skill_master)as ksm
            on a.primary_skill_id=ksm.id"""
        request.cr.execute(query)
        data = request.cr.fetchall()

        query2 = """
        select emp_id,name,aditional_skill,percentage_scored from
        (select * from
        (select h.id as emp_id,user_id,name,kw_skill_master_id from hr_employee as h inner join hr_employee_kw_skill_master_rel as hs
        on h.id=hs.hr_employee_id) as a
        inner join (select user_id,skill_id,percentage_scored from kw_skill_answer_master) as sam
        on a.user_id=sam.user_id and a.kw_skill_master_id=sam.skill_id) as x
        left outer join (select id,name as aditional_skill from kw_skill_master) as ks
        on x.skill_id=ks.id"""
        request.cr.execute(query2)
        data2 = request.cr.fetchall()
        sk = []
         
        for record in data:
            skill_percentage={}
            for rec in data2:
                if record[0] == rec[0]:
                    skill_percentage[rec[2]]=rec[3]
                else:
                    pass
            sk.append(
                {'id': record[0],
                 'name': record[1],
                 'designation': record[2],
                 'core_skill': record[3],
                 'skill1': list(skill_percentage)[0] if len(skill_percentage) != 0 else '-',
                 'percentage1': round(list(skill_percentage.values())[0], 2) if len(skill_percentage) != 0 else '-',
                 'rating1': '-',
                 'skill2': list(skill_percentage)[1] if len(skill_percentage) > 1 else '-',
                 'percentage2': round(list(skill_percentage.values())[1], 2) if len(skill_percentage) > 1 else '-',
                 'rating2': '-',
                 'skill3': list(skill_percentage)[2] if len(skill_percentage) > 2 else '-',
                 'percentage3': round(list(skill_percentage.values())[2], 2) if len(skill_percentage) > 2 else '-',
                 'rating3': '-',
                 'skill4': list(skill_percentage)[3] if len(skill_percentage) > 3 else '-',
                 'percentage4': round(list(skill_percentage.values())[3], 2) if len(skill_percentage) > 3 else '-',
                 'rating4': '-', })
        infodict = dict(sk_master=sk)
        return infodict
