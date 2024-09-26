from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
import re
from datetime import date, datetime,timedelta
from dateutil import relativedelta
from kw_utility_tools import kw_validations
from odoo import http
from math import ceil
from math import floor
from odoo.http import request
import base64
from odoo.tools.mimetypes import guess_mimetype


class EmployeeCVProfile(models.Model):
    _name = "kw_emp_cv_profile"
    _description = "Employee Cv Profile Details"
    _rec_name = "emp_id"


    emp_cv_prfl_id = fields.Many2one('kw_emp_profile', string="Employee Profile Id")
    emp_id = fields.Many2one('hr.employee', string="Employee")
    emp_cv_info_ids = fields.One2many(related='emp_cv_prfl_id.cv_info_details_ids', string='CV Info')
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='pending')
    cv_info_boolean = fields.Boolean(string='Check CV Info')
    department = fields.Char(related='emp_cv_prfl_id.department_name', string="Department")
    designation = fields.Char(related='emp_cv_prfl_id.job_position', string='Designation')
    employee_code = fields.Char(related='emp_cv_prfl_id.employee_code', string='Employee Code')
    email_id = fields.Char(related='emp_cv_prfl_id.work_email_id', string='Work Email')
    profile_cv_info_ids = fields.One2many(related='emp_cv_prfl_id.cv_info_details_ids', string='CV Info')
    work_email_id = fields.Char(string="Work Email", size=100)
    
    
    name = fields.Char(string='Employee')
    
    @api.model
    def create(self, vals):
        emp_rec = super(EmployeeCVProfile, self).create(vals)
        profile = self.env['kw_emp_profile'].search([('id', '=', emp_rec.emp_cv_prfl_id.id)])
        for rec in emp_rec:
            cv_inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_cv_change_request_email_template')
            if rec.cv_info_boolean is True:
                above_m8_grade = ['M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5']
                if rec.emp_cv_prfl_id.emp_id.grade.name in above_m8_grade:
                    if rec.emp_cv_prfl_id.emp_id.parent_id :
                        # send mail to parent
                        hr_emails = rec.emp_cv_prfl_id.emp_id.parent_id.work_email
                        action_taken_by = rec.emp_cv_prfl_id.emp_id.parent_id.name
                        from_mail = emp_rec.emp_cv_prfl_id.emp_id.work_email
                        action_id = self.env.ref('kw_emp_profile.profile_new_cv_approval_action').id
                        cv_inform_template.with_context(email=hr_emails,from_mail=from_mail, view_id=action_id, rec_id=rec.id, by=action_taken_by).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    empl =  rec.emp_cv_prfl_id.emp_id
                    result = rec.check_higher_authority_send_mail(empl, above_m8_grade)
                    hr_emails = result.work_email
                    action_taken_by = result.name
                    action_id = self.env.ref('kw_emp_profile.profile_new_cv_approval_action').id
                    cv_inform_template.with_context(email=hr_emails, view_id=action_id, rec_id=rec.id, by=action_taken_by).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        if emp_rec.cv_info_boolean == True:
            # profile.write({'cv_sts': True})
            self.env.cr.execute(f"update kw_emp_profile set cv_sts=true where id = {profile.id}")
            
    
    
    def check_higher_authority_send_mail(self, employee_id, above_m8_grade):
        current_employee = employee_id.parent_id
        while current_employee:
            if current_employee.grade.name in above_m8_grade:
                if current_employee.user_id.id == self.env.uid:
                    return current_employee
                return current_employee
            current_employee = current_employee.parent_id
        return employee_id.parent_id
    
    def check_higher_authority(self, employee_id, above_m8_grade, rec, found_parent=False):
        profile_lst = []
        new_data = self.env['kw_emp_cv_profile'].sudo().search([
            ('emp_cv_prfl_id', '=', rec.id),
            ('cv_info_boolean', '=', True),
            ('state', '=', 'pending')
        ])
        if employee_id.parent_id and not found_parent:
            if employee_id.parent_id.grade.name in above_m8_grade:
                found_parent = True
                if employee_id.parent_id.user_id.id == self.env.uid:
                    for new in new_data:
                        profile_lst.append(new.id)
                    return profile_lst
            else:
                return self.check_higher_authority(employee_id.parent_id, above_m8_grade, rec, found_parent)
        return profile_lst
    
    
    
    def redirect_cv_details_page(self):
        profile_lst = []
        login_user = self.env.user
        profile = self.env['kw_emp_profile'].sudo().search([('cv_sts', '=', True)])
        above_m8_grade = ['M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5']

        for rec in profile:
            if rec.emp_id.active == True:
                new_data = self.env['kw_emp_cv_profile'].sudo().search([('emp_cv_prfl_id', '=', rec.id), ('cv_info_boolean', '=', True), ('state', '=', 'pending')])
                if rec.emp_id.grade.name in above_m8_grade:
                    if rec.emp_id.parent_id and rec.emp_id.parent_id in login_user.employee_ids:
                        for new in new_data:
                            profile_lst.append(new.id)
                else:
                    result = self.check_higher_authority(rec.emp_id, above_m8_grade, rec)
                    if result: 
                        profile_lst.extend(result)

        # form_view_id = self.env.ref('kw_emp_profile.kw_emp_profile_new_data_cv_view_form').id
        tree_view_id = self.env.ref('kw_emp_profile.kw_emp_profile_new_cv_view_tree').id
        action =  {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_emp_cv_profile',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'target': 'self',
            'domain': [('id', 'in', profile_lst)],
        }
        return action
    
    @api.multi
    def cv_take_action(self):
        view_id = self.env.ref(
            'kw_emp_profile.kw_emp_profile_new_cv_view_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_emp_cv_profile',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            # 'domain': [('id', '=', self.id)],
        }
        
    def btn_approve_by_authority(self):
        for record in self:
            record.state = 'approved'
            emp_cv_lst = []
            pfl_cv_lst = []
            pfl_new_cv_lst = []
            for res in record.emp_cv_info_ids:
                emp_cv_lst.append(res.id)
            for rec in record.profile_cv_info_ids:
                if rec.emp_cv_info_id:
                    pfl_cv_lst.append(rec.emp_cv_info_id.id)
                else:
                    pfl_new_cv_lst.append(rec.id)

            for items in pfl_cv_lst:
                if items in emp_cv_lst:
                    profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('emp_cv_info_id', '=', int(items))])
                    emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                    emp_cv_rec.update({
                        'project_of': profile_cv_rec.project_of,
                        'project_name': profile_cv_rec.project_name,
                        # 'project_id':profile_cv_rec.project_id.id,
                        'location': profile_cv_rec.location,
                        'start_month_year': profile_cv_rec.start_month_year,
                        'end_month_year': profile_cv_rec.end_month_year,
                        'project_feature': profile_cv_rec.project_feature,
                        'role': profile_cv_rec.role,
                        'responsibility_activity': profile_cv_rec.responsibility_activity,
                        'client_name': profile_cv_rec.client_name,
                        'compute_project': profile_cv_rec.compute_project,
                        'organization_id': profile_cv_rec.organization_id.id,
                        'activity': profile_cv_rec.activity,
                        'other_activity': profile_cv_rec.other_activity,
                        'emp_project_id': profile_cv_rec.emp_project_id.id,
                    })
            for items in emp_cv_lst:
                if items not in pfl_cv_lst:
                    emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])
                    emp_cv_rec.unlink()

            for items in pfl_new_cv_lst:
                profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('id', '=', int(items))])
                
                
                emp_cv_rec = record.sudo().emp_cv_prfl_id.sudo().emp_id.cv_info_details_ids.sudo().create({
                    'project_of': profile_cv_rec.project_of,
                    'project_name': profile_cv_rec.project_name,
                    # 'project_id':profile_cv_rec.project_id.id,
                    'location': profile_cv_rec.location,
                    'start_month_year': profile_cv_rec.start_month_year,
                    'end_month_year': profile_cv_rec.end_month_year,
                    'project_feature': profile_cv_rec.project_feature,
                    'role': profile_cv_rec.role,
                    'responsibility_activity': profile_cv_rec.responsibility_activity,
                    'client_name': profile_cv_rec.client_name,
                    'compute_project': profile_cv_rec.compute_project,
                    'organization_id': profile_cv_rec.organization_id.id,
                    'activity': profile_cv_rec.activity,
                    'other_activity': profile_cv_rec.other_activity,
                    'emp_id': record.emp_cv_prfl_id.sudo().emp_id.id,
                    'emp_project_id': profile_cv_rec.emp_project_id.id,

                })
                profile_cv_rec.update({'emp_cv_info_id': emp_cv_rec.id})
            value ={}
            if record.cv_info_boolean == True:
                value = {'cv_sts': False}
            profile = self.env['kw_emp_profile'].sudo().search([('id', '=', record.emp_cv_prfl_id.id)])
            profile.update(value)
            
            inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_cv_approve_request_email_template')
            if inform_template:
                hr_emails = record.emp_cv_prfl_id.sudo().emp_id.sudo().work_email
                action_taken_by = self.env.user.employee_ids.name
                inform_template.with_context(email= hr_emails, action_taken_by=action_taken_by,
                                            email_from=self.env.user.employee_ids.work_email).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    def button_reject_cv(self):
        for record in self:
            value = {}
            record.state = 'rejected'
            emp_cv_lst = []
            pfl_cv_lst = []
            pfl_new_cv_lst = []
            for res in record.emp_cv_info_ids:
                emp_cv_lst.append(res.id)
            for rec in record.profile_cv_info_ids:
                if rec.emp_cv_info_id:
                    pfl_cv_lst.append(rec.emp_cv_info_id.id)
                else:
                    pfl_new_cv_lst.append(rec.id)

            for items in emp_cv_lst:
                if items in pfl_cv_lst:
                    profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search(
                        [('emp_cv_info_id', '=', int(items))])
                    emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                    profile_cv_rec.update({
                        'project_of': emp_cv_rec.project_of,
                        'project_name': emp_cv_rec.project_name,
                        # 'project_id':emp_cv_rec.project_id.id,
                        'location': emp_cv_rec.location,
                        'start_month_year': emp_cv_rec.start_month_year,
                        'end_month_year': emp_cv_rec.end_month_year,
                        'project_feature': emp_cv_rec.project_feature,
                        'role': emp_cv_rec.role,
                        'responsibility_activity': emp_cv_rec.responsibility_activity,
                        'client_name': emp_cv_rec.client_name,
                        'compute_project': emp_cv_rec.compute_project,
                        'organization_id': emp_cv_rec.organization_id.id,
                        'activity': emp_cv_rec.activity,
                        'other_activity': emp_cv_rec.other_activity,
                        'emp_project_id': emp_cv_rec.emp_project_id.id,
                    })
            for items in pfl_new_cv_lst:
                if items not in pfl_cv_lst:
                    profile_cv_rec = self.env['kw_emp_profile_cv_info'].sudo().search([('id', '=', int(items))])
                    profile_cv_rec.unlink()

            for items in emp_cv_lst:
                if items not in pfl_cv_lst:
                    emp_cv_rec = self.env['kw_emp_cv_info'].sudo().search([('id', '=', int(items))])

                    profile_cv_rec = record.emp_cv_prfl_id.cv_info_details_ids.create({
                        'project_of': emp_cv_rec.project_of,
                        'project_name': emp_cv_rec.project_name,
                        # 'project_id':emp_cv_rec.project_id.id,
                        'location': emp_cv_rec.location,
                        'start_month_year': emp_cv_rec.start_month_year,
                        'end_month_year': emp_cv_rec.end_month_year,
                        'project_feature': emp_cv_rec.project_feature,
                        'role': emp_cv_rec.role,
                        'responsibility_activity': emp_cv_rec.responsibility_activity,
                        'client_name': emp_cv_rec.client_name,
                        'compute_project': emp_cv_rec.compute_project,
                        'organization_id': emp_cv_rec.organization_id.id,
                        'activity': emp_cv_rec.activity,
                        'other_activity': emp_cv_rec.other_activity,
                        'emp_cv_info_id': emp_cv_rec.id,
                        'emp_project_id': emp_cv_rec.emp_project_id.id,
                    })
                    profile_cv_rec.update({'emp_id': record.emp_cv_prfl_id.id})
            if record.cv_info_boolean == True:
                value = {'cv_sts': False}
            profile = self.env['kw_emp_profile'].sudo().search([('id', '=', record.emp_cv_prfl_id.id)])
            profile.update(value)
            inform_template = self.env.ref('kw_emp_profile.kw_emp_profile_cv_reject_request_email_template')
            if inform_template:
                hr_emails = record.emp_cv_prfl_id.sudo().emp_id.sudo().work_email
                action_taken_by = self.env.user.employee_ids.name
                inform_template.with_context(email= hr_emails, action_taken_by=action_taken_by,
                        email_from=self.env.user.employee_ids.work_email).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        
