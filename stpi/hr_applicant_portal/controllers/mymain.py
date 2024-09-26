# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from ast import literal_eval
from collections import OrderedDict
from operator import itemgetter
from odoo import http
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from odoo.http import request, content_disposition
# from odoo.tools import image_process, groupby as groupbyelem
from odoo.tools.translate import _
import json, sys, base64, pytz
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary



class HrPortalRecruitment(http.Controller):
    @http.route([
        '/create/jobs/application',
    ], type='http', auth="public", website=True)
    def jobs(self, **post):
        # values = self.get_values()
        post['titles'] = request.env['res.partner.title'].sudo().search_read([], ['id', 'name'])
        post['advertisement_ids'] = request.env['advertisement.line'].sudo().search([('allowed_category_id.state', '=', 'active')])
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
        # post = {'line_type_id_1': '1', 'category_id': '15', 'blood_group': 'b+', 'zip_1': '250001', 'date_end_1': '2019-02-02', 'name': 'Rajneta', 'addreess_rec': '1', 'ref_name_1': 'TEst', 'description_1': 'CSE', 'ref_phone_1': '9865321470', 'position_1': 'O2b', 'organization_1': 'Software Developer', 'aadhar_no': '145236521452', 'ufile': <FileStorage: '' ('application/octet-stream')>, 'employeement_rec': '1', 'personal_email': 'goelarpit1997@gmail.com', 'job_id': '9', 'country_id': '104', 'title': '8', 'street2_1': 'Site-4 Industrial Area, Sahibabad', 'pan_no': 'ABCDE1234F', 'is_out_talent': 'on', 'dob': '2001-01-01', 'education_line_rec': '0', 'country_id_1': '104', 'to_date_1': '2021-02-01', 'city_1': 'Ghaziabad', 'from_date_1': '2020-02-02', 'street_1': 'A-16/29, Site-4 Industrial Area, Sahibabad', 'date_start_1': '2015-02-02', 'is_fail': 'on', 'advertisement_line_id': '21', 'specialization_1': 'CSE', 'address_type_id_1': 'permanent_add', 'name_1': 'B.tech', 'gende': 'male', 'is_difficulty_subject': 'on', 'ref_position_1': 'Test', 'state_id_1': '610', 'religion_id': '8'}
        name = ""
        if post.get('fname'):
            name += post.get('fname')
            post.pop('fname')
        if post.get('mname'):
            name += ' ' + post.get('mname')
            post.pop('mname')
        if post.get('lname'):
            name += ' ' + post.get('lname')
            post.pop('lname')
        post.update({'name': name})
        post.update({'profile_image': base64.b64encode(post.get('ufile').read()) if post.get('ufile') else False})
        post.pop('ufile')
        post.update({'signature': base64.b64encode(post.get('signature').read()) if post.get('signature') else False})
        post.update({'other_documents': base64.b64encode(post.get('other_documents').read()) if post.get('other_documents') else False})
        post.update({'advertisement_line_id': int(post.get('advertisement_line_id')) if post.get('advertisement_line_id') else False})
        post.update({'job_id': literal_eval(post.get('job_id')) if post.get('job_id') else False})
        address_id = self.slicedict(post, 'street_')
        from_date_id = self.slicedict(post, 'from_date_')
        edducation_id = self.slicedict(post, 'date_start_')
        address_rec, operation_rec, education_rec = [], [], []
        for item in address_id.keys():
            address_dic = {}
            rec = int(item.split('_')[1])
            if post.get('address_type_id_{}'.format(rec)):
                address_dic.update({'address_type': post.pop('address_type_id_{}'.format(rec))})
            if post.get('street_{}'.format(rec)):
                address_dic.update({'street': post.pop('street_{}'.format(rec))})
            if post.get('street2_{}'.format(rec)):
                address_dic.update({'street2': post.pop('street2_{}'.format(rec))})
            if post.get('city_{}'.format(rec)):
                address_dic.update({'city': post.pop('city_{}'.format(rec))})
            if post.get('state_id_{}'.format(rec)):
                address_dic.update({'state_id': int(post.pop('state_id_{}'.format(rec)))})
            if post.get('country_id_{}'.format(rec)):
                address_dic.update({'country_id': int(post.pop('country_id_{}'.format(rec)))})
            if post.get('zip_{}'.format(rec)):
                address_dic.update({'zip': post.pop('zip_{}'.format(rec))})
            if 'isCorrespondence_{}'.format(rec) in post and post.get('isCorrespondence_{}'.format(rec)):
                address_dic.update({'is_correspondence_address': bool(post.pop('isCorrespondence_{}'.format(rec)))})
            if address_dic:
                address_rec.append(address_dic)
        for item in from_date_id.keys():
            operations_dic = {}
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
            # print(">>>>line_type_id_1,>>>>>>>>>>>>>>", post)
            # print(">>>>line_type_id_1,>>>>>>>>>>>>>>", rec, post.get('line_type_id_{}'.format(rec)))
            if post.get('line_type_id_{}'.format(rec)):
                operations_dic.update({'line_type_id': int(post.pop('line_type_id_{}'.format(rec)))})
            if post.get('date_start_{}'.format(rec)):
                operations_dic.update({'date_start': post.pop('date_start_{}'.format(rec))})
            if post.get('date_end_{}'.format(rec)):
                operations_dic.update({'date_end': post.pop('date_end_{}'.format(rec))})
            if post.get('description_{}'.format(rec)):
                operations_dic.update({'description': post.pop('description_{}'.format(rec))})
            if post.get('name_{}'.format(rec)):
                operations_dic.update({'name': post.pop('name_{}'.format(rec))})
            if post.get('specialization_{}'.format(rec)):
                operations_dic.update({'specialization': post.pop('specialization_{}'.format(rec))})
            if operations_dic:
                education_rec.append(operations_dic)
        print("\naddress_rec>>>>>>>>>>>>>>>>", address_rec)
        print("\nperation_rec>>>>>>>>>>>>>>>>", operation_rec)
        print("\neducation_rec>>>>>>>>>>>>>>>>", education_rec)
        print('\n====================post===================', post)
        # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
        applicant_id = request.env['hr.applicant'].sudo().create(post)
        print('====================app===================', applicant_id.id)
        if address_rec or operation_rec or education_rec:
            try:
                if address_rec:
                    applicant_id.write({'address_ids': [(0, 0, f) for f in address_rec]})
                if education_rec:
                    applicant_id.write({'resume_line_applicant_ids': [(0, 0, f) for f in education_rec]})
                if operation_rec:
                    applicant_id.write({'prev_occu_ids': [(0, 0, f) for f in operation_rec]})
                print(">>>>>>>>>>>>>>>>>>", applicant_id.prev_occu_ids)
            except (AccessError, MissingError, ValidationError) as e:
                raise UserError(_(e))
        return request.redirect('/thank/you?id=%s&ref_no=%s' %(applicant_id.id, applicant_id.applicant_ref_id))

    @http.route(['/thank/you'],type='http', auth='public', website=True)
    def thankyou(self, **post):
        return request.render("hr_applicant_portal.thankyou", post)

    @http.route(['/get/type'],type='json', auth='public', website=True)
    def GetType(self, **post):
        line_type_ids = request.env['hr.resume.line.type'].sudo().search_read([], ['id', 'name'])
        state_ids = request.env['res.country.state'].sudo().search_read([], ['id', 'name'])
        country_ids = request.env['res.country'].sudo().search_read([], ['id', 'name'])
        address_type_ids = request.env['applicant.address']._fields['address_type']._description_selection(request.env)
        return {'line_type_ids': line_type_ids,
                'state_ids': state_ids,
                'country_ids': country_ids,
                'address_type_ids': address_type_ids,
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

    @http.route(['/getAdvertisementName'],type='http', auth='public', website=True)
    def getAdvertisementName(self, **kw):
        if kw.get('category_ids'):
            category_id = request.env['employee.category'].sudo().search([('name', 'ilike', 'GEN')], limit=1)
            # print("***********************", category_id.name, category_id)
            # institute_id = request.env['res.branch'].sudo().search([('id', '=', int(kw.get('institute_id')))])
            advertisement_ids = request.env['advertisement.line'].sudo().search(
                [('category_id', 'in', (int(kw.get('category_ids')), category_id.id))
                 ])
            result = []
            print('=================================id===============================', advertisement_ids)
            if advertisement_ids:
                for advertisement_id in advertisement_ids:
                    result.append((advertisement_id.id, advertisement_id.name))
                return json.dumps(dict(result=result))
        else:
            return False

    @http.route(['/getJobName'],type='http', auth='public', website=True)
    def getJobName(self, **kw):
        if kw.get('advertisement_ids'):
            # institute_id = request.env['res.branch'].sudo().search([('id', '=', int(kw.get('institute_id')))])
            job_id = request.env['advertisement.line'].sudo().search(
                [('id', '=', int(kw.get('advertisement_ids'))),
                 ])
            result = []
            print('=================================id===============================', job_id)
            if job_id:
                for course in job_id:
                    result.append((course.job_id.id, course.job_id.name))
                return json.dumps(dict(result=result))
        else:
            return False

    @http.route(['/print/hr/application/<int:applicant_id>'],type='http', auth='public', website=True)
    def print_application(self, applicant_id, **kw):
        if applicant_id:
            pdf = request.env.ref('hr_applicant_portal.applicant_id').sudo().render_qweb_pdf([applicant_id])[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)), ('Content-Disposition', content_disposition('Applicant Form.pdf'))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/')

