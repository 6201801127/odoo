# -*- coding: utf-8 -*-
from datetime import date
import datetime
from time import strptime

from requests import request
from odoo import http
from odoo.http import request
import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import base64


class KwOnboardingInductionFeedback(http.Controller):
    @http.route('/employee-view-feedback', type='http', auth='public', website=True,csrf=False)
    def employee_feedback_view_page(self,**args):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            assessment_check = request.env['kw_onboard_induction_emp_tagged'].search([
                                                            ('emp_ids', 'in', employee_id.id),
                                                            ('start_date', '<=', datetime.datetime.now().date())
                                                        ])
            if assessment_check.exists():
                return http.request.render('kw_onboarding_induction_feedback.employee_onboard_assessment_form_view')
       
    @http.route('/employee-view-feedback-submit',type='http',auth='public',website=True)
    def employee_assessment_feedback_submit(self,**post):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            assessment_check = request.env['kw_onboard_induction_emp_tagged'].search([
                                                            ('emp_ids', 'in', employee_id.id),
                                                            ('start_date', '<=', datetime.datetime.now().date())
                                                        ])
            if assessment_check.exists():
                view_id = http.request.env.ref('kw_onboarding_induction_feedback.kw_onboarding_feedback_form').id
                action_id = http.request.env.ref("kw_onboarding_induction_feedback.onboarding_induction_feedback_action_window").id
                menu_id = http.request.env.ref('kw_onboarding_induction_feedback.onboarding_feedback_menu_root').id
                request.session['skip_assessment'] = True
                return http.request.redirect(
                    '/web#id=%s&view_type=tree&action=%s&model=kw_onboarding_feedback&view_id=%s' % (employee_id.id,action_id,view_id))

    @http.route('/employee-view-feedback-skip',type='http',auth='public',website=True)
    def employee_assessment_feedback_skip(self,**post):
        request.session['skip_assessment'] = True
        return request.redirect('/web')
    
    
    @http.route('/get-induction_assessment-of-employee', auth='public', type='http', website=True, csrf=False)
    def get_checklist_report(self, **args):
        emp_rec = request.env.user.employee_ids
        if emp_rec:
            employee_id = emp_rec[0]
            skips_check= 0
            emp_induction_log = request.env['kw_employee_induction_assessment'].sudo().search([('emp_id', '=', employee_id.id)])
            for record in emp_induction_log: 
                # print("emp_induction_log=============================",emp_induction_log)
                if record.exists():
                    skips_check += record.skips_check
                else:
                    skips_check = 0
                return http.request.render('kw_onboarding_induction_feedback.employee_induction_assessment_view', {'emp_name': employee_id.name,
                                                                                   'skips_check': skips_check})
        else:
            http.request.session['skip_induction'] = True
        return http.request.redirect('/web')
    # @http.route('/employee-induction_assessment-skip', auth='user', website=True, csrf=False)
    # def skip_induction(self, **kw):
    #     emp_rec = request.env.user.employee_ids
    #     if emp_rec:
    #         http.request.session['skip_induction'] = True
    #         return http.request.redirect('/web')




