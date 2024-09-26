import json
import logging
import werkzeug
from datetime import datetime
from math import ceil,modf
import pytz
from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import ustr
from odoo.addons.http_routing.models.ir_http import slug
import collections 

_logger = logging.getLogger(__name__)
class kw_assessment_feedback(http.Controller):

    @http.route(['/kw/feedback/goal/<model("kw_feedback_final_config"):feedback_details>/<string:token>'],type='http', auth='user', website=True)
    def kw_feedback_goal(self, feedback_details, token=None, **post):
        weightage_record = request.env['kw_feedback_weightage_master'].sudo().search([])
        period_date = feedback_details.feedback_details_id.period_id.period_date

        map_resource_id = feedback_details.feedback_details_id.period_id.map_resource_id
        periods = map_resource_id.mapped('period_ids').sorted(key=lambda r: r.period_date)
        # periods = request.env['kw_feedback_map_resources'].sudo().search([
        #     ('map_resource_id','=',feedback_details.feedback_details_id.id)
        # ])
        # print(periods)
        
        ## current 
        c_year = period_date.year
        c_month = period_date.month
        # print(c_year ,'-',c_month)

        ## next 
        n_year = period_date.year
        n_month = period_date.month + 1
        if n_month > 12:
            n_month = n_month - 12
            n_year = n_year + 1

        # print(n_month ,'-',n_year)
        goal_data = request.env['kw_feedback_goal_and_milestone'].sudo().search([
            ('emp_id','=',feedback_details.assessee_id.id),
            ('year','=',str(c_year)),
            ('months','=',str(c_month))
        ],limit=1)
        
        next_period = periods.filtered(lambda res:res.period_date.month == n_month and res.period_date.year == n_year)
        # print(next_period)
        next_period_goal = []
        if next_period:
            next_period_goal = request.env['kw_feedback_goal_and_milestone'].sudo().search([
                ('emp_id','=',feedback_details.assessee_id.id),
                ('year','=',str(n_year)),
                ('months','=',str(n_month))
            ],limit=1)   
        
        data={'feedback':feedback_details,'feedback_id':feedback_details.id,'token':token,'goal':goal_data,'weightage':weightage_record,'next_period_goal':next_period_goal,'next_period':True if next_period else False}
        return request.render('kw_assessment_feedback.kw_feedback_goal_template',data)

    @http.route(['/kw/feedback/goal/submit/'],type='http',methods=['POST'], auth='user', website=True)
    def kw_feedback_goal_submit(self,**post):
        pass

    @http.route(['/kw/feedback/begin/<model("kw_feedback_final_config"):feedback_details>/<string:token>'],type='http', auth='user', website=True)
    def kw_feedback_begin(self, feedback_details, token=None, **post):
        weightage_record = request.env['kw_feedback_weightage_master'].sudo().search([])
        
        if feedback_details.feedback_status not in ['4','5','6']:
            if feedback_details.feedback_status == '1':
                feedback_details.write({'feedback_status':'2'})

            user_input = request.env['survey.user_input'].sudo().search([('token', '=', token)], limit=1)
            if user_input.state == 'new':
                user_input.write({
                    'state':'skip'
                })
            feedback_details.feedback_details_id._get_final_status()
                
            data={'feedback':feedback_details,'token':token,'weightage':weightage_record}
            return request.render('kw_assessment_feedback.kw_feedback_form',data)
        else:
            return request.render('kw_assessment_feedback.kw_feedback_thanks_page')
    
    

    @http.route(['/kw/feedback/prefill/<model("kw_feedback_final_config"):feedback_details>/<string:token>'],type='http', auth='user', website=True)
    def kw_feedback_prefill(self, feedback_details, token=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token)])

        positive_remark = "%s_%s" % (feedback_details.id, 'positive_remark')
        weak_remark = "%s_%s" % (feedback_details.id, 'weakareas_remark')
        suggestion_remark = "%s_%s" % (feedback_details.id, 'suggestions_remark')

        positive_remark_value = None
        weak_remark_value = None
        suggestion_remark_value = None

        if feedback_details.positive_remark:
            positive_remark_value = feedback_details.positive_remark

        if positive_remark_value:
            ret.setdefault(positive_remark, []).append(positive_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No positive remark has been found for feedback %s" % positive_remark)

        if feedback_details.weak_remark:
            weak_remark_value = feedback_details.weak_remark

        if weak_remark_value:
            ret.setdefault(weak_remark, []).append(weak_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No weak remark has been found for feedback %s" % weak_remark)

        if feedback_details.improve_remark:
            suggestion_remark_value = feedback_details.improve_remark

        if suggestion_remark_value:
            ret.setdefault(suggestion_remark, []).append(suggestion_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No suggestion remark has been found for feedback %s" % suggestion_remark)
            
        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            if not answer.skipped:
                answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                
                answer_value = None

                if answer.answer_type == 'free_text':
                    answer_value = answer.value_free_text
                elif answer.answer_type == 'text' and answer.question_id.type == 'textbox':
                    answer_value = answer.value_text
                elif answer.answer_type == 'text' and answer.question_id.type != 'textbox':
                    # here come comment answers for matrices, simple choice and multiple choice
                    answer_tag = "%s_%s" % (answer_tag, 'comment')
                    answer_value = answer.value_text
                elif answer.answer_type == 'number':
                    answer_value = str(answer.value_number)
                elif answer.answer_type == 'date':
                    answer_value = fields.Date.to_string(answer.value_date)
                elif answer.answer_type == 'suggestion' and not answer.value_suggested_row:
                    answer_value = answer.value_suggested.id
                elif answer.answer_type == 'suggestion' and answer.value_suggested_row:
                    answer_tag = "%s_%s" % (answer_tag, answer.value_suggested_row.id)
                    answer_value = answer.value_suggested.id
        
                if answer_value:
                    ret.setdefault(answer_tag, []).append(answer_value)
                else:
                    _logger.warning("[Assessment Feedback] No answer has been found for question %s" % answer_tag)

        return json.dumps(ret, default=str)

    @http.route(['/kw/feedback/back/<model("kw_feedback_final_config"):feedback_details>/<string:token>'], type='json', methods=['POST'], auth='user', website=True)
    def kw_feedback_back(self,feedback_details, token, **kw):
        final_remark = str(feedback_details.id)+'_final_remark'
        post = kw['kw_feedback_form']
        ret={}
        self.get_feedback_details(feedback_details,token,post)
        if kw['prevs'] == 'prevs':
            feedback_details.write({'feedback_status':'2','final_remark':post[final_remark]})  
            ret['redirect'] = 'prevs'
        return ret

    @http.route(['/kw/feedback/results/<model("kw_feedback_final_config"):feedback_details>/<string:token>'],type='http', auth='user', website=True)
    def kw_feedback_results(self, feedback_details, token=None, **post):
        if feedback_details.feedback_status not in ['0','1','2']:
            data={'feedback':feedback_details,'token':token}
            return request.render('kw_assessment_feedback.kw_feedback_view_form',data)
        else:
            return "Not Published"

    @http.route(['/kw/feedback/submit/<model("kw_feedback_final_config"):feedback_details>'],type='http',methods=['POST'], auth='user', website=True)
    def kw_feedback_finish(self, feedback_details, **post):
        _logger.debug('Incoming data: %s', post)
        user_input_line = request.env['survey.user_input_line']
        # Answer validation
        errors = {}
        for page in feedback_details.survey_id.page_ids:
            for question in page.question_ids:
                answer_tag = "%s_%s_%s" % (feedback_details.survey_id.id, page.id, question.id)
                errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
                user_id = request.env.user.id or SUPERUSER_ID
            except KeyError:
                return request.render("kw_assessment_feedback.kw_feedback_no_open_template")
            
            for page in feedback_details.survey_id.page_ids:
                for question in page.question_ids:
                    answer_tag = "%s_%s_%s" % (feedback_details.survey_id.id, page.id, question.id)
                    user_input_line.sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)
                    input_line = user_input_line.search([('user_input_id','=',user_input.id),('question_id','=',question.id),('survey_id','=',question.survey_id.id)])
                    
            user_input.write({
                'state':'done'
            })
            positive_remark = "%s_%s" % (feedback_details.id, 'positive_remark')
            weak_remark = "%s_%s" % (feedback_details.id, 'weakareas_remark')
            suggestion_remark = "%s_%s" % (feedback_details.id, 'suggestions_remark')

            feedback_details.write({
                'feedback_status':'3',
                'positive_remark':post[positive_remark] if positive_remark in post else False,
                'weak_remark':post[weak_remark] if weak_remark in post else False,
                'improve_remark':post[suggestion_remark] if suggestion_remark in post else False,
                })
            feedback_details.controller_count_score()
            feedback_details.feedback_details_id._get_compiled_remarks()
            feedback_details.feedback_details_id._get_final_status()

            ret['redirect'] = '/kw/feedback/thank_you/%s' % (slug(feedback_details))
        return json.dumps(ret)

    @http.route(['/kw/feedback/thank_you/<model("kw_feedback_final_config"):feedback_details>'],type='http', auth='user', website=True)
    def kw_feedback_thank_you(self, feedback_details, **kw):
        if feedback_details.feedback_status in ['3','4','5','6']:
            return request.render('kw_assessment_feedback.kw_feedback_thanks_page')
        else:
            return "Not Published"

    @http.route(['/kw/feedback/final_feedback/<model("kw_feedback_details"):feedback_details>'],type='http', auth='user', website=True)
    def kw_final_feedback(self, feedback_details, **kw):
        if feedback_details.feedback_status in ['3','4','5','6']:
            UserInputLine = request.env['survey.user_input_line']
            previous_answers = UserInputLine.sudo().search([('user_input_id', 'in', [input_ids.user_input_id.id for input_ids in feedback_details.feedback_final_config_id])])
            return request.render('kw_assessment_feedback.kw_final_feedback_view_form',{'feedback':feedback_details})

    @http.route(['/kw/feedback/final_feedback_prefill/<model("kw_feedback_details"):feedback_details>'],type="http",auth="user",website=True)
    def kw_final_feedback_prefill(self, feedback_details,**args):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}
        previous_answers = UserInputLine.sudo().search([('user_input_id', 'in', [input_ids.user_input_id.id for input_ids in feedback_details.feedback_final_config_id])])

        positive_remark = "%s_%s" % (feedback_details.id, 'positive_remark')
        weak_remark = "%s_%s" % (feedback_details.id, 'weakareas_remark')
        suggestion_remark = "%s_%s" % (feedback_details.id, 'suggestions_remark')

        positive_remark_value = None
        weak_remark_value = None
        suggestion_remark_value = None

        if feedback_details.positive_area:
            positive_remark_value = feedback_details.positive_area

        if positive_remark_value:
            ret.setdefault(positive_remark, []).append(positive_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No positive remark has been found for feedback %s" % positive_remark)

        if feedback_details.weak_area:
            weak_remark_value = feedback_details.weak_area

        if weak_remark_value:
            ret.setdefault(weak_remark, []).append(weak_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No weak remark has been found for feedback %s" % weak_remark)

        if feedback_details.suggestion_remark:
            suggestion_remark_value = feedback_details.suggestion_remark

        if suggestion_remark_value:
            ret.setdefault(suggestion_remark, []).append(suggestion_remark_value)
        else:
            _logger.warning("[Assessment Feedback] No suggestion remark has been found for feedback %s" % suggestion_remark)
            
        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            
            answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
            
            answer_value = None

            if answer.answer_type == 'free_text':
                answer_value = answer.value_free_text
            elif answer.answer_type == 'text' and answer.question_id.type == 'textbox':
                answer_value = answer.value_text
            elif answer.answer_type == 'text' and answer.question_id.type != 'textbox':
                # here come comment answers for matrices, simple choice and multiple choice
                answer_tag = "%s_%s" % (answer_tag, 'comment')
                answer_value = answer.value_text
            elif answer.answer_type == 'number':
                answer_value = str(answer.value_number /len(feedback_details.feedback_final_config_id))
            elif answer.answer_type == 'date':
                answer_value = fields.Date.to_string(answer.value_date)
            elif answer.answer_type == 'suggestion' and not answer.value_suggested_row:
                answer_value = answer.value_suggested.id
            elif answer.answer_type == 'suggestion' and answer.value_suggested_row:
                answer_tag = "%s_%s" % (answer_tag, answer.value_suggested_row.id)
                answer_value = answer.value_suggested.id
    
            if answer_value and answer_tag not in ret:
                ret.setdefault(answer_tag, []).append(answer_value)
            elif answer_value and answer_tag in ret:
                ret[answer_tag] = [str('%.1f' %(float(ret[answer_tag][0]) + float(answer_value)))]
            else:
                _logger.warning("[Assessment Feedback] No answer has been found for question %s" % answer_tag)
            
            if answer.page_id.id in ret:
                ret[answer.page_id.id] = [str('%.1f' %(float(ret[answer.page_id.id][0]) + float(answer_value)))]
            else:
                ret.setdefault(answer.page_id.id, []).append(answer_value)

        return json.dumps(ret, default=str)

    @http.route('/assessment_feedback/weightage_score', auth='user', type='json')
    def assessment_weightage_score(self):
        weightage_master = request.env['kw_feedback_weightage_master'].search([],order="from_range")
        
        return {
            'html': request.env.ref('kw_assessment_feedback.weightage_score_view').render({
                'weightage_master': weightage_master,
            })
        }
        