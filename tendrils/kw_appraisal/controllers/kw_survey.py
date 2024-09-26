import json
import logging
import werkzeug
from datetime import datetime,timedelta
from math import ceil
import pytz
from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class kw_survey(http.Controller):    
    
    # HELPER METHODS #
    def kw_check_bad_cases(self, survey, token=None):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # In case of auth required, block public user
        if survey.auth_required and request.env.user._is_public():
            return request.render("kw_appraisal.survey_auth_required", {'survey': survey, 'token': token})

        # In case of non open surveys
        if survey.stage_id.closed:
            return request.render("kw_appraisal.survey_notopen")

        # If there is no pages
        if not survey.page_ids:
            return request.render("survey.nopages", {'survey': survey})

        # Everything seems to be ok
        return None

    def kw_check_deadline(self, user_input):
        '''Prevent opening of the survey if the deadline has turned out

        ! This will NOT disallow access to users who have already partially filled the survey !'''
        deadline = user_input.deadline
        if deadline:
            dt_deadline = fields.Datetime.from_string(deadline)
            # print(dt_deadline)
            dt_now = datetime.now(pytz.timezone('Asia/Calcutta'))
            current_dt = dt_now.strftime("%Y-%m-%d")
            if str(current_dt) > str(dt_deadline):  # survey is not open anymore
                return request.render("kw_appraisal.survey_notopen")
        return None
    
    def get_goal_datas(self,user_input,self_employee_id,emp_id,UserInput,survey,token):
        ## previous year
        appr_id = request.env['hr.appraisal'].sudo().search([('id','=',user_input.appraisal_id.id)])
        goal_datas = request.env['kw_appraisal_goal'].sudo().search(['&',('appraisal_period','=',user_input.appraisal_id.appraisal_year_rel.id-1),('employee_id','=',emp_id.id)])
        goal_data_vals = []
        for prev_goals in goal_datas:
            goal_data_vals.append(prev_goals)
        
        ## Current year            
        goal_datas = request.env['kw_appraisal_goal'].sudo().search(['&',('appraisal_period','=',user_input.appraisal_id.appraisal_year_rel.id),('employee_id','=',emp_id.id)])
        current_goal_data_vals = []
        for curr_goals in goal_datas:
            current_goal_data_vals.append(curr_goals)
      
        kra_data = request.env['kw_appraisal_kra'].sudo().search(['&',('appraisal_period','=',user_input.appraisal_id.appraisal_year_rel.id),('employee_id','=',emp_id.id)],limit=1)    
        data = {'user_input':user_input,'KRA':kra_data,'manager_record':appr_id.lm_input_id,'collaborator_record':appr_id.ulm_input_id,'emp_id':emp_id,'goal_data_vals':goal_data_vals,'current_goal_data_vals':current_goal_data_vals,'empl_id':self_employee_id,'survey': survey, 'page': None, 'token': user_input.token,'survey_id':survey.id,'appraisal_year':user_input.appraisal_id.appraisal_year_rel.id,'employee_name':user_input.appraisal_id.emp_id.id}
        return data  
        
    
    @http.route(['/kw/survey/start/<model("survey.survey"):survey>',
                 '/kw/survey/start/<model("survey.survey"):survey>/<string:token>'],type='http', auth='public', website=True)
    def kw_start_survey(self, survey, token=None, **post):
        UserInput = request.env['survey.user_input']
        # appraisal_record = request.env['hr.appraisal']
        # user_input_line = request.env['survey.user_input_line']
        if 'empl_id' in request.session:
            self_employee_id = request.session['empl_id']
        else:
            return request.render("kw_appraisal.survey_auth_required")
        # print(self_employee_id)
        emp_id = request.env['hr.employee'].sudo().search([('id','=',self_employee_id)])
        if not token:
            vals = {'survey_id': survey.id}
            if not request.env.user._is_public():
                vals['partner_id'] = request.env.user.partner_id.id
            user_input = UserInput.create(vals)
        else:
            user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
            if not user_input:
                return request.render("kw_appraisal.error", {'survey': survey})
        
        # Do not open expired survey
        # errpage = self.kw_check_deadline(user_input)
        # if errpage:
        #     return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = self.get_goal_datas(user_input,self_employee_id,emp_id,UserInput,survey,token)
            return request.render('kw_appraisal.kw_goal_template',data)
        elif user_input.state == 'skip':
            ## previous year
            data = self.get_goal_datas(user_input,self_employee_id,emp_id,UserInput,survey,token)
            return request.render('kw_appraisal.kw_goal_template',data)
        elif user_input.state == 'done':
            data={}
            menu_id = user_input.appraisal_id.env.ref("kw_appraisal.menu_hr_appraisal_root").id
            if user_input.appraisal_id.emp_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'self':menu_id})
            elif user_input.appraisal_id.hr_manager_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'lm':menu_id})
            elif user_input.appraisal_id.hr_collaborator_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'ulm':menu_id})
            data.update({'survey': survey,'token': token,'user_input': user_input})    
            return request.render('kw_appraisal.kw_sfinished',data)
            # return request.redirect('/kw/survey/fill/%s/%s' % (survey.id, user_input.token)+f"?empl_id={post['empl_id']}")
        
    
    # Survey displaying
    @http.route(['/kw/survey/fill/<model("survey.survey"):survey>/<string:token>',
                 '/kw/survey/fill/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def kw_fill_survey(self, survey, token, prev=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']
        appraisal_record = request.env['hr.appraisal']
        user_input_line = request.env['survey.user_input_line']
        
        # print(post['empl_id'],'Employee id is in fill')
        if 'empl_id' in request.session:
            self_employee_id = request.session['empl_id']
        else:
            return request.render("kw_appraisal.survey_auth_required")
        finished_vals =[]
        
        # Controls if the survey can be displayed
        # errpage = self.kw_check_bad_cases(survey)
        # if errpage:
        #     return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        appr_id = user_input.appraisal_id
        if not user_input:  # Invalid token
            return request.render("kw_appraisal.error", {'survey': survey})

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        # errpage = self.kw_check_deadline(user_input)
        # if errpage:
        #     return errpage
        

        # Select the right page
        if user_input.state == 'new':  
            # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            
            self_employee = request.env['hr.employee'].search([('id','=',self_employee_id)])
            deg = ''
            if self_employee.job_id:
                deg = request.env['hr.job'].sudo().search([('id','=',self_employee.job_id.id)]).name
                # deg = self_employee.job_id.name
            else:
                deg = 'None'
            employee_det = str(self_employee.name+' '+'('+deg+')')
            
            new_lm_vals = []
            new_self_vals = []
            data={}
            if appr_id.state.name == 'Self':
                pass
            elif appr_id.state.name == 'LM':
                ##self data
                if appr_id.self_input_id.sudo().state == "done":
                    input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.self_input_id.id)])
                    for record in input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_self_vals.append(record)
                    data.update({'values':new_self_vals})
            elif appr_id.state.name == 'ULM':
                ## self data
                if appr_id.self_input_id.sudo().state == "done":
                    input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.self_input_id.id)])
                    for record in input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_self_vals.append(record)
                    data.update({'values':new_self_vals})
                ## LM data
                if appr_id.lm_input_id.sudo().state == "done":
                    lm_input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.lm_input_id.id)])
                    for record in lm_input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_lm_vals.append(record)
                    data.update({'lm_values':new_lm_vals})
                        
            data.update({'user_input':user_input,'employee_det':employee_det,'empl_id':self_employee_id,'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token,'training_percentage':appr_id.training_percentage,'planned_training_hours':appr_id.planned_training_hours,'achieved_duration':appr_id.achieved_duration})
            if last:
                data.update({'last': True})
            finished_vals.append(data)
            return request.render('kw_appraisal.surveys', data)
        elif user_input.state == 'done':  # Display success message
            # print(finished_vals," Inside done")
            data={}
            menu_id = user_input.appraisal_id.env.ref("kw_appraisal.menu_hr_appraisal_root").id
            if user_input.appraisal_id.emp_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'self':menu_id})
            elif user_input.appraisal_id.hr_manager_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'lm':menu_id})
            elif user_input.appraisal_id.hr_collaborator_id.user_id.partner_id.id == request.env.user.partner_id.id:
                data.update({'ulm':menu_id})
            data.update({'survey': survey,'token': token,'user_input': user_input,'finished_vals':finished_vals,'training_percentage':appr_id.training_percentage,'planned_training_hours':appr_id.planned_training_hours,'achieved_duration':appr_id.achieved_duration}) 
               
            return request.render('kw_appraisal.kw_sfinished',data)
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)
            # print(page," Pages in skip state")
            ## Finding Self's record
            self_employee = request.env['hr.employee'].search([('id','=',self_employee_id)])
            deg = ''
            if self_employee.job_id:
                deg = request.env['hr.job'].sudo().search([('id','=',self_employee.job_id.id)]).name
                # deg = self_employee.job_id.name
            else:
                deg = 'None'
            employee_det = str(self_employee.name+' '+'('+deg+')')
            new_lm_vals = []
            new_self_vals = []
            ulm_vals=[]
            data={}
            
            if user_input.appraisal_id.state.name == 'Self':
                pass
            elif user_input.appraisal_id.state.name == 'LM':
                ##self data
                if appr_id.self_input_id.sudo().state == "done":
                    input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.self_input_id.id)])
                    for record in input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_self_vals.append(record)
                    data.update({'values':new_self_vals})
                
                if appr_id.ulm_input_id.sudo().state == "done":
                    ulm_input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.ulm_input_id.id)])
                    for record in ulm_input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                ulm_vals.append(record)
                    data.update({'ulm_vals':ulm_vals})
            elif user_input.appraisal_id.state.name == 'ULM':
                ## self data
                
                if appr_id.self_input_id.sudo().state == "done":
                    input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.self_input_id.id)])
                    for record in input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_self_vals.append(record)
                    data.update({'values':new_self_vals})
                ## LM data
                if appr_id.lm_input_id.sudo().state == "done":
                    lm_input_line_data = user_input_line.sudo().search([('user_input_id','=',appr_id.lm_input_id.id)])
                    for record in lm_input_line_data:
                        if page!=None:
                            if record.question_id.page_id.id == page.id:
                                new_lm_vals.append(record)
                    data.update({'lm_values':new_lm_vals})
                    
            if not page:
                
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)
            data.update({'user_input':user_input,'employee_det':employee_det,'empl_id':self_employee_id,'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token,'training_percentage':appr_id.training_percentage,'planned_training_hours':appr_id.planned_training_hours,'achieved_duration':appr_id.achieved_duration})
            if last:
                data.update({'last': True})
            finished_vals.append(data)
            return request.render('kw_appraisal.surveys', data)
        else:
            return request.render("kw_appraisal.error", {'survey': survey})

    # AJAX prefilling of a survey
    @http.route(['/kw/survey/prefill/<model("survey.survey"):survey>/<string:token>',
                 '/kw/survey/prefill/<model("survey.survey"):survey>/<string:token>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def kw_prefill(self, survey, token, page=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        # Fetch previous answers
        if page:
            previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token), ('page_id', '=', page.id)])
        else:
            previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token)])
        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            if not answer.skipped:
                # answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                answer_value = None
                # answer_value1 = None
                if answer.answer_type == 'suggestion' and not answer.value_suggested_row:
                    answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                    answer_value = answer.value_suggested.id
                    if answer_value:
                        ret.setdefault(answer_tag, []).append(answer_value)
                if answer.answer_type == 'number' and not answer.value_suggested_row:
                    answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                    answer_value = answer.value_number
                    if answer_value:
                        ret.setdefault(answer_tag, []).append(answer_value)
                if answer.question_id.type != 'textbox':
                    answer_tag = "%s_%s_%s_%s" % (answer.survey_id.id, answer.page_id.id, answer.question_id.id,'comment')
                    answer_value = answer.value_text
                    if answer_value:
                        ret.setdefault(answer_tag, []).append(answer_value)
                if answer.answer_type == 'textbox':
                    answer_tag = "%s_%s_%s" % (answer.survey_id.id, answer.page_id.id,'comment')
                    answer_value = answer.value_text
                    if answer_value:
                        ret.setdefault(answer_tag, []).append(answer_value)
                if answer.question_id.type == 'textbox':
                    answer_tag = "%s_%s_%s_%s" % (answer.survey_id.id, answer.page_id.id, answer.question_id.id,'comment')
                    answer_value = answer.value_text
                    if answer_value:
                        ret.setdefault(answer_tag, []).append(answer_value)
        return json.dumps(ret, default=str)

    # AJAX submission of a page
    @http.route(['/kw/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def kw_submit(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])
       
        user_inputs = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
        errors = {}
        ret = {}
        if user_inputs.state != 'done':
            if post['ulm_vals'] and post['lm_values']:
                for question in questions:
                    answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                    errors.update(question.validate_question(post, answer_tag))
            else:
                if len(errors):
                    # Return errors messages to webpage
                    ret['errors'] = errors
                else:
                    # Store answers into database
                    try:
                        user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
                    except KeyError:  # Invalid token
                        return request.render("kw_appraisal.error", {'survey': survey})
                    user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID
                    for question in questions:
                        answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                        request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)
                    
                    go_back = post['button_submit'] == 'previous'
                    back_draft = post['button_submit'] == 'save_and_back'
                    send_reassessment = post['button_submit'] == 'reassessment'
                    approve_survey = post['button_submit'] == 'approve'
                    final_approve_survey = post['button_submit'] == 'final_approve'
                    if back_draft:
                        # print('save and back')
                        vals = {'state': 'skip'}
                        user_input.sudo(user=user_id).write(vals)
                    else:
                        next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
                        vals = {'last_displayed_page_id': page_id}
                        if next_page is None and not go_back:
                            vals.update({'state': 'done'})
                            emp = user_input.appraisal_id.emp_id
                            rec = request.env['hr.appraisal'].sudo().search([])
                            for record in rec:
                                if record.id == user_input.appraisal_id.id:
                                    # new_state = record.state.sequence+1
                                    if emp.user_id.partner_id.id == request.env.user.partner_id.id:
                                        if user_input.appraisal_id.state.sequence == 2:
                                            new_state = user_input.appraisal_id.state =3
                                            record.state = new_state
                                    if user_input.appraisal_id.hr_manager_id.user_id.partner_id.id == request.env.user.partner_id.id:
                                        if user_input.appraisal_id.state.sequence == 3:
                                            new_state = user_input.appraisal_id.state =4
                                            record.state = new_state
                                    if user_input.appraisal_id.hr_collaborator_id.user_id.partner_id.id == request.env.user.partner_id.id:
                                        if user_input.appraisal_id.state.sequence == 4:
                                            new_state = user_input.appraisal_id.state =5
                                            record.state = new_state
                                    if record.state.sequence == 3:
                                        template = request.env.ref('kw_appraisal.kw_self_to_lm_email_template')
                                        request.env['mail.template'].browse(template.id).sudo().send_mail(user_input.appraisal_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                                        
                                    elif record.state.sequence == 4:
                                        if not emp.parent_id.parent_id.parent_id.id:
                                            # print("ULM of LM not found===========")
                                            state = request.env['hr.appraisal.stages'].search([('sequence','=',5)])
                                            record.state = state.sequence
                                        else:
                                            # print("ULM of LM Found================")
                                            new_state = record.state.sequence
                                            record.state = new_state
                                            template = request.env.ref('kw_appraisal.kw_lm_to_ulm_email_template')
                                            request.env['mail.template'].browse(template.id).sudo().send_mail(user_input.appraisal_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                                        if not emp.parent_id.parent_id.id:
                                            seq = request.env['hr.appraisal.stages'].search([('sequence','=',5)])
                                            record.state = seq.id

                            if send_reassessment:
                                emp_rec = request.env['hr.appraisal'].sudo().search([])
                                for emp in emp_rec:
                                    emp_id = emp.emp_id.id
                                previous_state = int(user_input.appraisal_id.state.sequence)
                                current_state = user_input.appraisal_id.state = previous_state - 2
                                manager_id = user_input.appraisal_id.hr_manager_id
                                if user_input.appraisal_id.lm_input_id.sudo().state == 'done':
                                    user_input.appraisal_id.lm_input_id.sudo().state = 'skip'
                                    user_input.appraisal_id.lm_input_id.sudo().last_displayed_page_id = 0
                                    user_input.appraisal_id.reassessment = True
                                    template = request.env.ref('kw_appraisal.kw_reassessment_email_template')
                                    request.env['mail.template'].browse(template.id).sudo().send_mail(user_input.appraisal_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")


                            if approve_survey:
                                previous_state = int(user_input.appraisal_id.state.sequence)
                                current_state = user_input.appraisal_id.state = previous_state 
                            else:
                                pass
                            if final_approve_survey:
                                user_input.appraisal_id.reassessment = False
                                previous_state = int(user_input.appraisal_id.state.sequence)
                                current_state = user_input.appraisal_id.state = previous_state + 1

                                template = request.env.ref('kw_appraisal.kw_final_approve_email_template')
                                request.env['mail.template'].browse(template.id).sudo().send_mail(user_input.appraisal_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                            else:
                                pass
                        else:
                            vals.update({'state': 'skip'})
                        user_input.sudo(user=user_id).write(vals)
                    if back_draft:
                        pass                                           
                    else:
                        ret['redirect'] = '/kw/survey/fill/%s/%s' % (survey.id, post['token'])
                    if go_back:
                        ret['redirect'] = '/kw/survey/fill/%s/%s' % (survey.id, post['token']+'/prev')
        if user_inputs.state == 'done':
            ret['redirect'] = '/kw/survey/start/%s/%s' % (survey.id, post['token'])            
        return json.dumps(ret)
    
    
    @http.route(['/kw/survey/results/<model("survey.survey"):survey>',
                 '/kw/survey/results/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def kw_print_survey(self, survey, token=None, **post):
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']
        appraisal_record = request.env['hr.appraisal']
        user_input_line = request.env['survey.user_input_line']
        Employee_record = request.env['hr.employee']
        users = request.env['res.users']
        user_input = UserInput.sudo().search([('token','=',token)])
        # print(user_input.partner_id)
        if 'empl_id' in request.session:
            self_employee_id = request.session['empl_id']
        else:
            self_employee_id = user_input.appraisal_id.emp_id.id if user_input and user_input.appraisal_id else False
            
        self_employee = Employee_record.sudo().search([('id','=',self_employee_id)])
        deg = ''
        if self_employee and self_employee.job_id.name:
            deg = self_employee.job_id.name
        else:
            deg = 'None'
        employee_det = str(self_employee.name+' '+'('+deg+')')
        goal_datas = self.get_goal_datas(user_input,self_employee_id,self_employee,UserInput,survey,token)
        employee_data_vals = []
        manager_inputs_vals = []
        collaborator_input_vals = []
        appraisal_id = appraisal_record.sudo().search([('id','=',user_input.appraisal_id.id)])
        for employee in appraisal_id.emp_id:
            employee_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.self_input_id.id)],limit=1)
            employee_input_line = user_input_line.sudo().search([('user_input_id','=',employee_data.id)])
            for employee_inputs in employee_input_line:
                employee_data_vals.append(employee_inputs)
        for hr_managers in appraisal_id.hr_manager_id:
            hr_managers_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.lm_input_id.id)],limit=1)
            hr_manager_input_line = user_input_line.sudo().search([('user_input_id','=',hr_managers_data.id)])
            for manager_inputs in hr_manager_input_line:
                manager_inputs_vals.append(manager_inputs)
        for hr_collaborators in appraisal_id.hr_collaborator_id:
            hr_collaborators_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.ulm_input_id.id)],limit=1)
            hr_collaborators_input_line = user_input_line.sudo().search([('user_input_id','=',hr_collaborators_data.id)])
            for collaborator_inputs in hr_collaborators_input_line:
                collaborator_input_vals.append(collaborator_inputs)
        if user_input.state == 'done' and not user_input.appraisal_id.state.sequence == 5 and not user_input.appraisal_id.state.sequence == 6:
            return request.render('kw_appraisal.kw_survey_print',
                                      {
                                        'prev_goal':goal_datas['goal_data_vals'],
                                        'current_goal':goal_datas['current_goal_data_vals'],
                                        'user_input':user_input,
                                        'survey': survey,
                                        'token': token,
                                        'page_nr': 0,
                                        'employee_data_vals':employee_data_vals,
                                        'manager_inputs_vals':manager_inputs_vals,
                                        'collaborator_input_vals':collaborator_input_vals,
                                        'self_employee_id':employee_det,
                                        'training_percentage':appraisal_id.training_percentage,'planned_training_hours':appraisal_id.planned_training_hours,'achieved_duration':appraisal_id.achieved_duration})
        elif user_input.state == 'done' and user_input.appraisal_id.state.sequence == 5 or user_input.appraisal_id.state.sequence == 6:
            return request.render('kw_appraisal.kw_survey_final_result',
                                      {
                                        'prev_goal':goal_datas['goal_data_vals'],
                                        'current_goal':goal_datas['current_goal_data_vals'],
                                        'user_input':user_input,
                                        'survey': survey,
                                        'token': token,
                                        'score':user_input.appraisal_id.score,
                                        'page_nr': 0,
                                        'employee_data_vals':employee_data_vals,
                                        'manager_inputs_vals':manager_inputs_vals,
                                        'collaborator_input_vals':collaborator_input_vals,
                                        'self_employee_id':employee_det,
                                        'training_percentage':appraisal_id.training_percentage,'planned_training_hours':appraisal_id.planned_training_hours,'achieved_duration':appraisal_id.achieved_duration})
        else:
            return request.render('kw_appraisal.no_result_found',{'survey': survey,'self_employee_id':employee_det})
    @http.route(['/kw/appraisal/results/<model("survey.survey"):survey>',
                 '/kw/appraisal/results/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def kw_print_appraisal(self, survey, token=None, **post):
        
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']
        appraisal_record = request.env['hr.appraisal']
        user_input_line = request.env['survey.user_input_line']
        Employee_record = request.env['hr.employee']
        users = request.env['res.users']
        user_input = UserInput.sudo().search([('token','=',token)])
        # print(user_input.partner_id)
        if 'empl_id' in request.session:
            self_employee_id = request.session['empl_id']
        else:
            self_employee_id = user_input.appraisal_id.emp_id.id if user_input and user_input.appraisal_id else False
            
        self_employee = Employee_record.sudo().search([('id','=',self_employee_id)])
        deg = ''
        if self_employee and self_employee.job_id.name:
            deg = self_employee.job_id.name
        else:
            deg = 'None'
        employee_det = str(self_employee.name+' '+'('+deg+')')
        goal_datas = self.get_goal_datas(user_input,self_employee_id,self_employee,UserInput,survey,token)
        employee_data_vals = []
        manager_inputs_vals = []
        collaborator_input_vals = []
        appraisal_id = appraisal_record.sudo().search([('id','=',user_input.appraisal_id.id)])
        for employee in appraisal_id.emp_id:
            employee_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.self_input_id.id)],limit=1)
            employee_input_line = user_input_line.sudo().search([('user_input_id','=',employee_data.id)])
            for employee_inputs in employee_input_line:
                employee_data_vals.append(employee_inputs)
        for hr_managers in appraisal_id.hr_manager_id:
            hr_managers_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.lm_input_id.id)],limit=1)
            hr_manager_input_line = user_input_line.sudo().search([('user_input_id','=',hr_managers_data.id)])
            for manager_inputs in hr_manager_input_line:
                manager_inputs_vals.append(manager_inputs)
        for hr_collaborators in appraisal_id.hr_collaborator_id:
            hr_collaborators_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.ulm_input_id.id)],limit=1)
            hr_collaborators_input_line = user_input_line.sudo().search([('user_input_id','=',hr_collaborators_data.id)])
            for collaborator_inputs in hr_collaborators_input_line:
                collaborator_input_vals.append(collaborator_inputs)
        
        if user_input.state == 'done' and user_input.appraisal_id.state.sequence == 5 or user_input.appraisal_id.state.sequence == 6:
            return request.render('kw_appraisal.kw_survey_final_result',
                                      {
                                        'prev_goal':goal_datas['goal_data_vals'],
                                        'current_goal':goal_datas['current_goal_data_vals'],
                                        'user_input':user_input,
                                        'survey': survey,
                                        'token': token,
                                        'score':user_input.appraisal_id.score,
                                        'page_nr': 0,
                                        'employee_data_vals':employee_data_vals,
                                        'manager_inputs_vals':manager_inputs_vals,
                                        'collaborator_input_vals':collaborator_input_vals,
                                        'self_employee_id':employee_det,
                                        'training_percentage':appraisal_id.training_percentage,'planned_training_hours':appraisal_id.planned_training_hours,'achieved_duration':appraisal_id.achieved_duration})
        else:
            return request.render('kw_appraisal.no_result_found',{'survey': survey,'self_employee_id':employee_det})
            
    @http.route(['/kw/goal/submit/'],type='http',methods=['POST'], auth='public', website=True)
    def kw_goal(self,**post):
        pass
        

    @http.route(['/kw/survey/back/<model("survey.survey"):survey>'], type='json', methods=['POST'], auth='public', website=True)
    def kw_back(self, survey, **kw):
        # print(kw['prevs'])
        post = kw['kw_survey_form']
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])
        ret={}
        errors = {}
        if post['ulm_vals'] and post['lm_values']:
            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                errors.update(question.validate_question(post, answer_tag))
        else:
            if len(errors):
                ret['errors'] = errors
            else:
                try:
                    user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
                except KeyError:  # Invalid token
                    return request.render("kw_appraisal.error", {'survey': survey})
                user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

                for question in questions:
                    answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                    request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)
                
                vals = {'state': 'skip','last_displayed_page_id':0}
                user_input.sudo(user=user_id).write(vals)
                if kw['prevs'] != 'prevs':
                    if not post['lm_values'] and not post['ulm_vals'] and not post['values']:
                        ret['redirect'] = 'self'
                    elif post['values'] and not post['lm_values'] and not post['ulm_vals']:
                        ret['redirect'] = 'lm'                        
                    elif not post['ulm_vals'] and post['values'] and post['lm_values']:
                        ret['redirect'] = 'ulm'                        
                    elif post['values'] and not post['lm_values'] and post['ulm_vals']:
                        ret['redirect'] = 'lm_reassign'                                            
                else:
                    ret['redirect'] = 'prevs'
                    ret['survey_id'] = survey.id
                    ret['token'] = user_input.token
        return ret
    
    @http.route(['/kw/survey/score/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def kw_score_survey(self, survey, token=None, **post):
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']
        appraisal_record = request.env['hr.appraisal']
        user_input_line = request.env['survey.user_input_line']
        Employee_record = request.env['hr.employee']
        users = request.env['res.users']
        
        if 'empl_id' in request.session:
            self_employee_id = request.session['empl_id']
        else:
            return request.render("kw_appraisal.survey_auth_required")
        self_employee = Employee_record.sudo().search([('id','=',self_employee_id)])
        deg = ''
        if self_employee.job_id.name:
            deg = self_employee.job_id.name
        else:
            deg = 'None'
        employee_det = str(self_employee.name+' '+'('+deg+')')
        
        user_input = UserInput.sudo().search([('token','=',token)], limit=1)
        if not user_input:
                return request.render("kw_appraisal.error", {'survey': survey})
        employee_data_vals = []
        manager_inputs_vals = []
        collaborator_input_vals = []
        appraisal_id = appraisal_record.sudo().search([('id','=',user_input.appraisal_id.id)])
        value = 0
        for employee in appraisal_id.emp_id:
            employee_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.self_input_id.id)],limit=1)
            employee_input_line = user_input_line.sudo().search([('user_input_id','=',employee_data.id)])
            for employee_inputs in employee_input_line:
                value += int(employee_inputs.quizz_mark)
                employee_data_vals.append(employee_inputs)
        for hr_managers in appraisal_id.hr_manager_id:
            hr_managers_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.lm_input_id.id)],limit=1)
            hr_manager_input_line = user_input_line.sudo().search([('user_input_id','=',hr_managers_data.id)])
            for manager_inputs in hr_manager_input_line:
                manager_inputs_vals.append(manager_inputs)
                
        for hr_collaborators in appraisal_id.hr_collaborator_id:
            hr_collaborators_data = UserInput.sudo().search(['&',('state','=','done'),('id','=',appraisal_id.ulm_input_id.id)],limit=1)
            hr_collaborators_input_line = user_input_line.sudo().search([('user_input_id','=',hr_collaborators_data.id)])
            for collaborator_inputs in hr_collaborators_input_line:
                collaborator_input_vals.append(collaborator_inputs)
                
        if user_input.state == 'done' and not user_input.appraisal_id.state.sequence == 5:
            return request.render('kw_appraisal.kw_survey_score',
                                      {'survey': survey,
                                       'token': token,
                                       'page_nr': 0,
                                       'employee_data_vals':employee_data_vals,
                                       'manager_inputs_vals':manager_inputs_vals,
                                       'collaborator_input_vals':collaborator_input_vals,
                                       'self_employee_id':employee_det})
        elif user_input.state == 'done' and user_input.appraisal_id.state.sequence == 5:
            return request.render('kw_appraisal.kw_survey_score',
                                      {'survey': survey,
                                       'token': token,
                                       'page_nr': 0,
                                       'employee_data_vals':employee_data_vals,
                                       'manager_inputs_vals':manager_inputs_vals,
                                       'collaborator_input_vals':collaborator_input_vals,
                                       'self_employee_id':employee_det})
        else:
            return request.render('kw_appraisal.no_result_found',{'survey': survey,'self_employee_id':employee_det})
            
       