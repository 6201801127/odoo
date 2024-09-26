# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from ast import literal_eval
from collections import OrderedDict
from operator import itemgetter
from odoo import http
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from odoo.http import request
# from odoo.tools import image_process, groupby as groupbyelem
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary



class HrPortalRecruitment(http.Controller):
    @http.route([
        '/create/jobs/application',
    ], type='http', auth="public", website=True)
    def jobs(self, **post):
        # values = self.get_values()
        post['titles'] = request.env['res.partner.title'].sudo().search_read([], ['id', 'name'])
        post['advertisement_ids'] = request.env['hr.requisition.application'].sudo().search([('state', '=', 'active')])
        print("svsdvdvsdvsdvsdvsdv", post.get('advertisement_ids'))
        post['job_ids'] = request.env['hr.job'].sudo().search([])
        post['category_ids'] = request.env['employee.category'].sudo().search([])
        post['religion_ids'] = request.env['employee.religion'].sudo().search([])
        post['country_ids'] = request.env['res.country'].sudo().search([])
        post['blood_group'] = request.env['hr.applicant']._fields['blood_group']._description_selection(request.env)
        # post['genders'] = values.get('genders')
        # post['school_ids'] = values.get('school_ids')
        # post['default_id'] = request.env['res.country'].sudo().search([('code', '=', 'SA')], limit=1)
        # post['student_position'] = values.get('student_position')
        # post['states'] = values.get('states')
        # post['is_parent_died'] = values.get('is_parent_died')
        # post['datepicker'] = 1
        return request.render("hr_applicant_portal.apply4jobs", post, {})

    def slicedict(self, d, s):
        return {k: v for k, v in d.items() if k.startswith(s)}

    @http.route(['/Apply/jobs'], type='http', auth="public", website=True)
    def ApplyJobs(self, **post):
        # try:
        post.update({'job_id': literal_eval(post.get('job_id'))})
        from_date_id = self.slicedict(post, 'from_date_')
        edducation_id = self.slicedict(post, 'date_start_')
        operation_rec, education_rec = [], []
        for item in from_date_id.keys():
            operations_dic = {}
            print(">>>>>>>>>>>>>>>>>>", item.split('_')[1])
            rec = int(item.split('_')[2])
            if post.get('from_date_{}'.format(rec)):
                operations_dic.update({'from_date': post.pop('from_date_{}'.format(rec))})
            if post.get('to_date_{}'.format(rec)):
                operations_dic.update({'to_date': post.pop('to_date_{}'.format(rec))})
            if post.get('position_{}'.format(rec)):
                operations_dic.update({'position': post.pop('position_{}'.format(rec))})
            if post.get('organization_{}'.format(rec)):
                operations_dic.update({'organization': post.pop('organization_{}'.format(rec))})
            if post.get('ref_name_{}'.format(rec)):
                operations_dic.update({'ref_name': post.pop('ref_name_{}'.format(rec))})
            if post.get('ref_position_{}'.format(rec)):
                operations_dic.update({'ref_position': post.pop('ref_position_{}'.format(rec))})
            if post.get('ref_phone_{}'.format(rec)):
                operations_dic.update({'ref_phone': post.pop('ref_phone_{}'.format(rec))})
            if operations_dic:
                operation_rec.append(operations_dic)
        for item in edducation_id.keys():
            operations_dic = {}
            rec = int(item.split('_')[2])
            print(">>>>line_type_id_1,>>>>>>>>>>>>>>", post)
            print(">>>>line_type_id_1,>>>>>>>>>>>>>>", rec, post.get('line_type_id_{}'.format(rec)))
            if post.get('line_type_id_{}'.format(rec)):
                operations_dic.update({'line_type_id': int(post.pop('line_type_id_{}'.format(rec)))})
            if post.get('date_start_{}'.format(rec)):
                operations_dic.update({'date_start': post.pop('date_start_{}'.format(rec))})
            if post.get('date_end_{}'.format(rec)):
                operations_dic.update({'date_end': post.pop('date_end_{}'.format(rec))})
            if post.get('description_{}'.format(rec)):
                operations_dic.update({'description': post.pop('description_{}'.format(rec))})
            if post.get('name_{}'.format(rec)):
                operations_dic.update({'title': post.pop('name_{}'.format(rec))})
            if post.get('specialization_{}'.format(rec)):
                operations_dic.update({'specialization': post.pop('specialization_{}'.format(rec))})
            if operations_dic:
                education_rec.append(operations_dic)
        print(">>>>>>>>>>>>>>>>", education_rec)
        print('====================post===================', post)
        applicant_id = request.env['hr.applicant'].sudo().create(post)
        print('====================app===================', applicant_id.id)
        if operation_rec or education_rec:
            try:
                if education_rec:
                    applicant_id.write({'resume_line_applicant_ids': [(0, 0, f) for f in education_rec]})
                if operation_rec:
                    applicant_id.write({'prev_occu_ids': [(0, 0, f) for f in operation_rec]})
                print(">>>>>>>>>>>>>>>>>>", applicant_id.prev_occu_ids)
            except (AccessError, MissingError, ValidationError) as e:
                raise UserError(_(e))
        return request.redirect('/thank/you')

    @http.route(['/thank/you'],type='http', auth='public', website=True)
    def thankyou(self, **post):
        return request.render("hr_applicant_portal.thankyou", {})

    @http.route(['/get/type'],type='json', auth='public', website=True)
    def GetType(self, **post):
        line_type_ids = request.env['hr.resume.line.type'].sudo().search_read([], ['id', 'name'])
        state_ids = request.env['res.country.state'].sudo().search_read([], ['id', 'name'])
        country_ids = request.env['res.country'].sudo().search_read([], ['id', 'name'])
        return {'line_type_ids': line_type_ids,
                'state_ids': state_ids,
                'country_ids': country_ids
                }
        # admission = request.env['admission.admission'].sudo()
        # redirect = ("/my/admissions")
        # try:
        #     admission_sudo = self._document_check_access('admission.admission', admission_id, access_token=access_token)
        #     values = self.get_values(admission_sudo)
        # except Exception as e:
        #     return request.redirect("%s?error_e=%s" % (redirect, (tools.ustr(e))))

        # values.update(self._admission_get_page_view_values(admission_sudo, access_token, **kw))
        # post = values
        # post['datepicker'] = 1
        # return request.render("sync_ems_admission_website.apply4admission", post, {})
