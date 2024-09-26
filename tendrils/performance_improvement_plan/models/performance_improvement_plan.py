# -*- coding: utf-8 -*-

from datetime import date
import base64
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.kw_utility_tools import kw_validations, kw_whatsapp_integration


class PerformanceImprovementPlan(models.Model):
    _name = 'performance_improvement_plan'
    _description = 'Performance Improvement Plan Process'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    reference = fields.Char(string="Reference No", track_visibility='always')
    raised_by = fields.Many2one('hr.employee', 'Raised By', default=lambda self: self.env.user.employee_ids[0:1],
                                track_visibility='always')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, track_visibility='always')
    designation_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id",
                                     track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    track_visibility='always')
    division_id = fields.Many2one('hr.department', string="Division", related="employee_id.division",
                                  track_visibility='always')
    emp_sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU", compute="get_emp_sbu", track_visibility='always')
    project_id = fields.Many2one('project.project', string='Project', store=True,
                                 track_visibility='always')
    project_code = fields.Char(string='Project Code', compute='_compute_project_code')
    performance_reason = fields.Many2many('pip_reason_issue_config', 'pip_reason_rel', 'pip_config_id', 'reason_id',
                                          string="Reason for Performance Issue",domain="[('status_active','=',True)]",
                                          required=True, track_visibility='always')

    remarks_pm = fields.Text('Describe the Reason (PM/Reviewer)', track_visibility='always')
    remarks = fields.Text('Describe the Reason (Practice/Division head/HOD)', track_visibility='always')
    suggestion_pm = fields.Selection(string='Suggestion (PM/Reviewer)', selection=[('move_to_pip', 'Move to PIP'),
                                                                                   ('discuss',
                                                                                    'Discussion with higher authority (SBU/Reviewer)')],
                                     track_visibility='onchange', default='move_to_pip')
    suggestion = fields.Selection(string='Suggestion (Practice/Division head)',
                                  selection=[('move_to_pip', 'Move to PIP'),
                                             ('discuss', 'Discussion with higher authority (SBU/Reviewer)')],
                                  track_visibility='onchange', default='move_to_pip')
    status = fields.Selection([('Draft', 'Draft'), ('Applied', 'PIP Raised'),
                               ('Recommend PIP', 'Counselling Recommended'),('Recommend Training', 'Training Recommended'), ('Closed', 'Closed')
                               ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange',
                              default='Draft')
    approve_remarks = fields.Text(string="Remarks", track_visibility='always', size=1000)
    # documents_pm = fields.Binary(string=u'Upload Relevant Document', attachment=True, )
    documents_pm_doc = fields.One2many('document_upload', 'ref_id', string='Relevant Documents', attachment=True)
    file_name = fields.Char(string='Document Name')
    suggestion_reviewer_sbu = fields.Selection(string="Recommend Action",
                                               selection=[('RP', 'Recommend Counselling'),('RT','Recommend Training')],
                                               track_visibility='onchange')
    suggestion_reviewer = fields.Selection(string="Recommend Action", selection=[('RP', 'Recommend Counselling'),('RT','Recommend Training')],
                                           track_visibility='onchange')
    add_skill = fields.Many2one('kw_skill_master',string="Skill",domain="[('skill_type.skill_type','in',['Technical','Non-Technical'])]")
    target_date = fields.Date(string="Target Date")
    date_of_action = fields.Date(string="Approve Date", track_visibility='always')
    applied_date = fields.Date(string="Applied Date", track_visibility='always')
    pending_at = fields.Many2one("hr.employee", string="Pending at", track_visibility='always')
    pending_at_txt = fields.Char(string="Pending At", compute="_compute_pending_at")
    approved_by_txt = fields.Char(string="Approved By", compute="_compute_pending_at")
    approved_user_id = fields.Many2one("hr.employee", string="Approved By")

    check_pm = fields.Boolean(string="Check PM", compute="_compute_check_forward", store=False)
    check_sbu = fields.Boolean(string="Check SBU", compute="_compute_check_forward", store=False)
    check_user = fields.Boolean(string="Check User")
    check_hod = fields.Boolean(string="Check HOD", compute="_compute_check_forward", store=False)
    check_division_head = fields.Boolean(string="Check Division", compute="_compute_check_forward", store=False)
    check_pratice_head = fields.Boolean(string="Check Practice", compute="_compute_check_forward", store=False)
    check_reviewer = fields.Boolean(string="Reviewer", compute="_compute_check_forward", store=False)
    rcm_group = fields.Boolean(string="RCM Check", compute="_compute_check_forward", store=False)
    hide_request_for = fields.Boolean(string="Hide Request for", compute="_compute_check_forward", store=False)
    check_hr = fields.Boolean(string="HR check", compute="_compute_check_forward", store=False)
    request_for = fields.Selection(string="Request For",
                                   selection=[('Project', 'Project'), ('SBU_employee', 'Employee')],
                                   track_visibility='onchange')
    suggestion_hod_sbu = fields.Text(string="Remarks/Suggestion for improvement", track_visibility='onchange')
    show_add_skill = fields.Boolean(string="show skill ")
    show_target_date = fields.Boolean(string="show date ")

    @api.onchange('suggestion_reviewer_sbu', 'suggestion_reviewer')
    def _onchange_suggestion_reviewer(self):
        if self.suggestion_reviewer_sbu == 'RT' or self.suggestion_reviewer == 'RT':
            self.show_add_skill = True
            self.show_target_date = True
            self.add_skill = False  
            self.target_date = False  
        else:
            self.add_skill = False
            self.target_date = False
            self.show_add_skill = False
            self.show_target_date = False

    # @api.depends('suggestion_reviewer_sbu', 'suggestion_reviewer')
    # def _compute_field_visibility(self):
    #     for rec in self:
    #         rec.show_add_skill = rec.suggestion_reviewer_sbu == 'RT' or rec.suggestion_reviewer == 'RT'
    #         rec.show_target_date = rec.show_add_skill


    # @api.onchange('show_add_skill', 'show_target_date')
    # def _onchange_show_fields(self):
    #     self.add_skill = False if not self.show_add_skill else self.add_skill
    #     self.target_date = False if not self.show_target_date else self.target_date


    @api.depends('employee_id')
    def get_emp_sbu(self):
        if self.employee_id and self.employee_id.sbu_type == 'sbu':
            self.emp_sbu_master_id = self.employee_id.sbu_master_id

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        # self.onchange_project()
        return super(PerformanceImprovementPlan, self).read(fields, load=load)
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.status in ['Recommend PIP','Closed'] :
                raise ValidationError('You Can\'t be deleted as PIP Process already take action. ')
            elif rec.create_uid.id != self.env.user.id:
                raise ValidationError('You Can\'t be deleted. ')
            res = super(PerformanceImprovementPlan, rec).unlink()
        return res

    # @api.model
    # def create(self, vals):
    #     record = super(PerformanceImprovementPlan, self).create(vals)
    #     ref_id_user = self.env.ref('performance_improvement_plan.group_pip_module_user').id
    #     data_user = self.env['res.groups'].sudo().search([('id', '=', ref_id_user)])
    #     for rec in record.employee_id:
    #         data_user.users = [(4, rec.user_id.id)]
    #     return record

    @api.model
    def create(self, vals):
        existing_pip = self.search(
            [('employee_id', '=', vals.get('employee_id')), ('status', 'in', ['Draft', 'Applied', 'Recommend PIP','Recommend Training'])],
            limit=1)
        if existing_pip:
            raise ValidationError("A PIP has already been raised for this employee.You can't create another one.")
        new_pip = super(PerformanceImprovementPlan, self).create(vals)
        return new_pip

    @api.constrains('request_for')
    def _check_request_for(self):
        if not self.request_for:
            if self.check_reviewer and self.check_pm:
                raise ValidationError("Please Check the Request For.")

    @api.constrains('documents_pm_doc')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf', 'application/zip',
                             'application/msword', 'application/vnd.ms-excel',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        max_file_size_mb = 2.0
        if self.documents_pm_doc:
            for docs in self.documents_pm_doc:
                mimetype = guess_mimetype(base64.b64decode(docs.documents))
                if not docs.documents:
                    raise ValidationError("Document data is missing.")
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError(_("Unsupported file format! Allowed file formats are .docs, .xls, .zip, .pptx and .pdf."))
                elif ((len(docs.documents) * 3 / 4) / 1024) / 1024 > max_file_size_mb:
                    raise ValidationError(_("Maximum file size should be less than {} MB.".format(max_file_size_mb)))
                kw_validations.validate_file_mimetype(docs.documents, allowed_file_list)
                kw_validations.validate_file_size(docs.documents, 2)
        else:
            raise ValidationError("At least one document is required in Upload Relevant Documents.")

    @api.depends('pending_at', 'status', 'approved_user_id')
    def _compute_pending_at(self):
        for rec in self:
            if rec.status == 'Recommend PIP':
                rec.pending_at = False
                rec.pending_at_txt = 'HR'

            elif rec.status == 'Recommend Training':
                rec.pending_at = False
                rec.pending_at_txt = 'L&K'

            elif rec.status == 'Closed':
                rec.pending_at = False
                rec.pending_at_txt = '---'

            elif rec.status == 'Forward':
                rec.pending_at = False
                rec.pending_at_txt = 'HR'
            else:
                rec.pending_at_txt = rec.pending_at.name if rec.pending_at else ''

            rec.approved_by_txt = rec.approved_user_id.display_name if rec.approved_user_id else ''

    @api.depends('raised_by')
    def _compute_check_forward(self):
        ses_employee = self.env.user.employee_ids
        for rec in self:
            sbu_record = self.env['kw_sbu_master'].sudo().search(
                [('type', '=', 'sbu'), ('representative_id', '=', ses_employee.id)])
            department_rec = self.env['hr.department'].sudo().search(
                [('manager_id', '=', ses_employee.id),
                 ('dept_type.code', 'in', ['department', 'division', 'section'])])
            project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee.id)])
            department_codes = department_rec.filtered(lambda x: x.code != '' and x.code is not False).mapped('code')
            # print('department_rec.mapped >>> ', department_rec, department_codes,self.env.user,ses_employee, ses_employee.name, ses_employee.department_id.code, ses_employee.department_id.name)

            if (department_rec.exists() and 'BSS' not in department_codes
                    and ses_employee.department_id.code != 'BSS'):
                rec.request_for = 'SBU_employee'
                rec.hide_request_for = True

            if sbu_record.exists():
                rec.check_sbu = True
            # elif self.env.user.has_group('kw_resource_management.group_budget_manager'):
            #     rec.rcm_group = True
            elif department_rec.exists() and 'department' in department_rec.mapped('dept_type.code'):
                rec.check_hod = True
            elif department_rec.exists() and 'division' in department_rec.mapped('dept_type.code'):
                rec.check_division_head = True
            elif department_rec.exists() and 'section' in department_rec.mapped('dept_type.code'):
                rec.check_pratice_head = True
            elif self.env.user.has_group('performance_improvement_plan.group_pip_hr_user'):
                rec.check_hr = True
            elif self.env.user.has_group('kw_resource_management.group_sbu_reviewer'):
                project_rec = self.env['project.project'].sudo().search([('reviewer_id.id', '=', ses_employee.id)])
                if project_rec.exists():
                    rec.check_reviewer = True
            elif project_rec.exists():
                rec.check_pm = True
            else:
                child_ids = self.env['hr.employee'].sudo().search(
                    [('id', 'child_of', ses_employee.id), ('employement_type.code', 'not in', ['O']),
                     ('id', '!=', ses_employee.id)])
                # print('child_ids >>>>> ', child_ids)
                if child_ids.exists():
                    rec.request_for = 'SBU_employee'
                    rec.hide_request_for = True

    @api.onchange('raised_by', 'project_id', 'request_for')
    def onchange_project(self):
        empl_id = self.env['hr.employee']
        raised_by_id = self.raised_by.id
        ses_user = self.env.user
        ses_employee_id = self.env.user.employee_ids
        if not ses_employee_id:
            ses_employee_id = empl_id.search([('user_id', '=', ses_user.id)])
        # print('ses_employee_id >> ', ses_user, ses_employee_id)
        emp_domain = [('grade_id.id', '=', ses_employee_id.grade.id)]
        if ses_employee_id.emp_band:
            emp_domain += [('band_id.id', '=', ses_employee_id.emp_band.id)]
        emp_grade = self.env['kwemp_grade'].sudo().search(emp_domain, limit=1)
        # print('emp_grade.sort_no >>> ', emp_grade.sort_no, emp_domain)
        employee_id_list = self.env['hr_employee_info'].sudo().search(
            [('sort_no', '<=', emp_grade.sort_no), ('employement_type.code', '!=', 'O')]).mapped('id')

        # raise by SBU
        domain = [('id', 'in', [])]
        employee_ids = [('id', 'in', [])]
        init_domain = {'domain': {'employee_id': [('id', 'in', [])], 'project_id': [('id', 'in', [])], }}

        sbu_record = self.env['kw_sbu_master'].sudo().search(
            [('representative_id', '=', ses_employee_id.id), ('type', '=', 'sbu')])
        if self.raised_by and sbu_record.exists():
            # raised by SBU
            if not self.request_for:
                return init_domain
            elif self.request_for == 'SBU_employee':
                # employee_ids = empl_id.search(
                #     ['|', ('id', 'child_of', ses_employee_id.id), ('id', 'in', employee_id_list),
                #      ('sbu_master_id', '=', sbu_record.id),
                #      ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id)])
                # employee_ids = [('id', 'in', employee_ids.ids), ('id', '!=', ses_employee_id.id)]
                employee_ids = ['|', ('id', 'child_of', ses_employee_id.id), ('id', 'in', employee_id_list),
                                ('sbu_master_id', '=', sbu_record.id),
                                ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id)]
                self.project_id = False
                self.project_code = False
                self.employee_id = False
            elif self.request_for == 'Project':
                project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee_id.id)])
                project_ids = project_rec.ids if project_rec else []
                project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                    [('project_id', '=', self.project_id.id)])
                employee_ids = [('id', 'in', project_member_ids.mapped('emp_id').ids), ('id', '!=', ses_employee_id.id)]
                domain = [('id', 'in', project_ids)]
                self.employee_id = False
            # print('1 > >> >>> ', domain, employee_ids)
            return {'domain': {'project_id': domain, 'employee_id': employee_ids}}

        # raise by project reviewer
        if ses_user.has_group('kw_resource_management.group_sbu_reviewer'):
            project_rec = self.env['project.project'].sudo().search([('reviewer_id.id', '=', ses_employee_id.id)])
            # print("project reviewer project_rec >>>>>>>>>>>>>>> ", project_rec)
            # self.check_reviewer = True
            if project_rec.exists():
                project_ids = project_rec.ids if project_rec else []
                project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                    [('project_id', '=', self.project_id.id)])
                employee_ids = [('id', 'in', project_member_ids.mapped('emp_id').ids), ('id', '!=', ses_employee_id.id)]
                return {'domain': {'project_id': [('id', 'in', project_ids)], 'employee_id': employee_ids}}

        # raise by hod
        department_rec = self.env['hr.department'].sudo().search([('manager_id', '=', ses_employee_id.id)])
        # print('department_rec >>>> ', department_rec, self.request_for)
        if department_rec.exists():
            for dept in department_rec:
                # print('department_rec 2 >>>> ', dept.dept_type.code, dept.name, employee_id_list)
                if dept.dept_type.code == 'department':
                    # print("in if>>>>>>>>>>>>>>>>>>>>>>>>> department >>>>>>>>>>>")
                    # self.check_hod = True
                    if not self.request_for:
                        return init_domain
                    elif self.request_for == 'SBU_employee':
                        self.employee_id = False
                        self.project_id = False
                        # emp_rec = empl_id.sudo().search(
                        #     ['|', ('id', 'child_of', ses_employee_id.id),
                        #      '&', ('id', 'in', employee_id_list), ('department_id', '=', dept.id),
                        #      ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id)])
                        # employee_ids = [('id', 'in', emp_rec.ids)]
                        employee_ids = ['|', ('id', 'child_of', ses_employee_id.id),
                                        '&', ('id', 'in', employee_id_list), ('department_id', '=', dept.id),
                                        ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id)]
                        self.project_id = False
                        self.project_code = False
                    elif self.request_for == 'Project':
                        self.employee_id = False
                        project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee_id.id)])
                        project_ids = project_rec.ids if project_rec else []
                        project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                            [('project_id', '=', self.project_id.id), ('emp_id', '!=', ses_employee_id.id)])
                        if project_member_ids:
                            employee_ids = [('id', 'in', project_member_ids.mapped('emp_id').ids)]
                        else:
                            employee_ids = [('id', 'in', [])]
                        domain = [('id', 'in', project_ids)]
                    # print('dept >>>>> ', domain, employee_ids)
                    return {'domain': {'employee_id': employee_ids, 'project_id': domain}}

                # raise by division head
                elif dept.dept_type.code == 'division':
                    # print("in if>>>>>>>>>>>>>>>>>>>>>>>>>division>>>>>>>>>>>",dept)
                    # self.check_division_head = True
                    if not self.request_for:
                        return init_domain
                    elif self.request_for == 'SBU_employee':
                        self.employee_id = False
                        self.project_id = False
                        # emp_rec = empl_id.sudo().search(
                        #     ['|', ('id', 'child_of', ses_employee_id.id),
                        #      '&', ('id', 'in', employee_id_list), ('division', '=', dept.id),
                        #      ('id', '!=', ses_employee_id.id), ('employement_type.code', '!=', 'O')])
                        # print('emp_rec >>> ', emp_rec)
                        # employee_ids = [('id', 'in', emp_rec.ids)]
                        employee_ids = ['|', ('id', 'child_of', ses_employee_id.id),
                                        '&', ('id', 'in', employee_id_list), ('division', '=', dept.id),
                                        ('id', '!=', ses_employee_id.id), ('employement_type.code', '!=', 'O')]
                    elif self.request_for == 'Project':
                        self.employee_id = False
                        project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee_id.id)])
                        project_ids = project_rec.ids if project_rec else []
                        project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                            [('project_id', '=', self.project_id.id), ('emp_id', '!=', ses_employee_id.id)])
                        employee_ids = project_member_ids.mapped('emp_id').ids
                        domain = [('id', 'in', project_ids)]
                        employee_ids = [('id', 'in', employee_ids)]
                    # print('division > >> >>> ', domain, employee_ids)
                    return {'domain': {'employee_id': employee_ids, 'project_id': domain}}

                # raise by practice head
                elif dept.dept_type.code == 'section':
                    # print("in if>>>>>>>>>>>>>>>>>>>>>>>>>section>>>>>>>>>>>")
                    # self.check_pratice_head = True
                    if not self.request_for:
                        return init_domain
                    elif self.request_for == 'SBU_employee':
                        self.employee_id = False
                        self.project_id = False
                        self.project_code = False
                        # emp_rec = empl_id.sudo().search(
                        #     ['|', ('id', 'child_of', ses_employee_id.id),
                        #      '&', ('id', 'in', employee_id_list), ('section', '=', dept.id),
                        #      ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id), ])
                        # employee_ids = [rec.id for rec in emp_rec]
                        employee_domain = ['|', ('id', 'child_of', ses_employee_id.id),
                                           '&', ('id', 'in', employee_id_list), ('section', '=', dept.id),
                                           ('employement_type.code', '!=', 'O'), ('id', '!=', ses_employee_id.id), ]
                    elif self.request_for == 'Project':
                        self.employee_id = False
                        project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee_id.id)])
                        project_ids = project_rec.ids if project_rec else []
                        project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                            [('project_id', '=', self.project_id.id), ('emp_id', '!=', ses_employee_id.id)])
                        employee_domain = [('id', 'in', project_member_ids.mapped('emp_id').ids)]
                        domain = [('id', 'in', project_ids)]
                    # print('section > >> >>> ', domain, employee_ids)
                    return {'domain': {'employee_id': employee_domain, 'project_id': domain, }}

        # raise by PM
        project_rec = self.env['project.project'].sudo().search([('emp_id', '=', ses_employee_id.id)])
        if self.raised_by and project_rec.exists():
            # self.check_pm = True
            if not self.project_id:
                self.employee_id = []  # Set Many2one field to False (empty tuple)
            project_ids = project_rec.ids if project_rec else []
            project_member_ids = self.env['kw_project_resource_tagging'].sudo().search(
                [('project_id', '=', self.project_id.id)])
            employee_ids = [('id', 'in', project_member_ids.mapped('emp_id').ids), ('id', '!=', ses_employee_id.id)]
            return {'domain': {'project_id': [('id', 'in', project_ids)], 'employee_id': employee_ids}}

        child_ids = self.env['hr.employee'].sudo().search(
            [('id', 'child_of', ses_employee_id.id), ('employement_type.code', 'not in', ['O']), ('id', '!=', ses_employee_id.id)])
        # print('child_ids >>>>> ', child_ids)
        if child_ids.exists():
            emp_domain = [('id', 'child_of', ses_employee_id.id), ('employement_type.code', 'not in', ['O']),
                          ('id', '!=', ses_employee_id.id)]
            return {'domain': {'employee_id': emp_domain, 'project_id': [('id', 'in', [])], }}

        return init_domain

    @api.depends('project_id')
    def _compute_project_code(self):
        for rec in self:
            if rec.project_id:
                rec.project_code = rec.project_id.code
            else:
                rec.project_code = False

    def send_to_approve(self):
        self.applied_date = date.today()
        existing_sequences = self.env['ir.sequence.date_range'].search(
            [('sequence_id.code', '=', 'PIP'), ('date_from', '<=', self.applied_date),
             ('date_to', '>=', self.applied_date)])
        sequence = existing_sequences.sequence_id
        pip_sequence = sequence.next_by_id() or '/'
        fiscal_year_part = existing_sequences.prefix.split('/')[-1]
        pip_code = 'PIP/{}/{}'.format(fiscal_year_part, pip_sequence.split('/')[-1])
        self.reference = pip_code

        ref_id_user = self.env.ref('performance_improvement_plan.group_pip_module_user')
        if self.employee_id:
            ref_id_user.sudo().write({'users': [(4, self.employee_id.user_id.id)]})

        for rec in self:
            existing_pip = self.search(
                [('employee_id', '=', rec.employee_id.id), ('status', 'in', ['Applied', 'Draft', 'Recommend PIP'])],
                limit=1)
            if existing_pip and rec.id != existing_pip.id:
                raise ValidationError("A PIP has already been raised for this employee.You can't create another one.")
        #    sbu applied
        template_obj = self.env.ref('performance_improvement_plan.email_template_for_approve_pip')
        pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
        hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
        # print('self.check_sbu >>> ', self.check_sbu)
        # print('self.check_reviewer >>> ',  self.check_reviewer)
        # print('self.check_hod >>> ', self.check_hod)
        # print('self.check_division_head >>> ', self.check_division_head,)
        # print('self.check_pratice_head >>> ', self.check_pm)
        # print('self.check_pm >>> ', self.check_pm)

        if self.check_sbu is True:
            # print("in sbu=======================")

            self.write({'status': 'Recommend PIP',
                        'approved_user_id': self.env.user.employee_ids.id,
                        'suggestion_reviewer_sbu': 'RP',
                        'date_of_action': date.today()})
            manager_emp_notify_user = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            email_to = ','.join(manager_emp_hr.mapped('work_email')) or ''

            mail_emp_cc = []
            mail_cc = []
            if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
                mail_cc.append(self.employee_id.parent_id.work_email)

            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_emp_cc.extend(manager_emp_notify_user.mapped('work_email'))
            mail_cc.extend(manager_emp_notify_user.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) + ',' + (self.env.user.employee_ids.work_email)
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Recommended for Counselling",
                    mail_for='Approved',
                    email_to=email_to,
                    mail_cc=','.join(set(mail_emp_cc)),
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.employee_id.display_name
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Initiated",
                    mail_for='to_user',
                    email_to=self.employee_id.work_email,
                    mail_cc=cc_mail,
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.employee_id.name
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")
        #  reviewer applied   
        elif self.check_reviewer is True:
            # print("in reviewer==========",self.employee_id.sbu_master_id.representative_id.id)
            self.write({'pending_at': self.employee_id.sbu_master_id.representative_id.id,
                        'status': 'Applied'})

            email_to = self.employee_id.sbu_master_id.representative_id.work_email
            manager_emp_notify = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            mail_cc = []
            if self.env.user.employee_ids.work_email:
                mail_cc.append(self.env.user.employee_ids.work_email)

            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_cc.extend(manager_emp_notify.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) or ''

            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Raised",
                    mail_for='Reviewer_Applied',
                    email_to=email_to,
                    mail_cc=cc_mail,
                    name=self.employee_id.sbu_master_id.representative_id.name,
                    remarks=self.remarks_pm,
                    email_from=self.env.user.employee_ids.work_email,
                    user_name=self.employee_id.display_name,
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")
            # HOD Applied
        elif self.check_hod is True:
            # print("in hod========")

            self.write({'status': 'Recommend PIP',
                        'approved_user_id': self.env.user.employee_ids.id,
                        'suggestion_reviewer': 'RP',
                        'date_of_action': date.today()})
            manager_emp_notify_user = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            email_to = ','.join(manager_emp_hr.mapped('work_email')) or ''

            mail_emp_cc = []
            mail_cc = []
            if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
                mail_cc.append(self.employee_id.parent_id.work_email)

            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_emp_cc.extend(manager_emp_notify_user.mapped('work_email'))
            mail_cc.extend(manager_emp_notify_user.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) + ',' + (self.env.user.employee_ids.work_email)
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Recommended for Counselling",
                    mail_for='Approved',
                    email_to=email_to,
                    mail_cc=','.join(set(mail_emp_cc)),
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.employee_id.name
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Initiated",
                    mail_for='to_user',
                    email_to=self.employee_id.work_email,
                    mail_cc=cc_mail,
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.employee_id.name
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")

        # division head OR RA applied for NON-SBU user
        elif (self.check_division_head is True
              or (not self.employee_id.sbu_master_id or self.employee_id.sbu_master_id.type != 'sbu')):
            # print("====================in division==========", self.employee_id.department_id.manager_id.id)
            self.write({'pending_at': self.employee_id.department_id.manager_id.id,
                        'status': 'Applied', })

            email_to = self.employee_id.department_id.manager_id.work_email
            manager_emp_notify = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            mail_cc = []
            # if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
            #     mail_cc.append(self.employee_id.parent_id.work_email)
            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_cc.extend(manager_emp_notify.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) or ''
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Raised",
                    mail_for='Applied_div',
                    email_to=email_to,
                    email_from=self.env.user.employee_ids.work_email,
                    mail_cc=cc_mail,
                    name=self.employee_id.department_id.manager_id.name,
                    user_name=self.employee_id.display_name,
                    remarks=self.remarks
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")
            # practice head
        elif self.check_pratice_head is True:
            # print("====================in practice==========",self.employee_id.department_id.manager_id.id)

            self.write({'pending_at': self.employee_id.department_id.manager_id.id,
                        'status': 'Applied'})

            email_to = self.employee_id.department_id.manager_id.work_email
            manager_emp_notify = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            mail_cc = []
            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_cc.extend(manager_emp_notify.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) or ''
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Raised",
                    mail_for='Applied_pra',
                    email_to=email_to,
                    mail_cc=cc_mail,
                    user_name=self.employee_id.name,
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.employee_id.department_id.manager_id.name,
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")

        # pm applied OR RA applied for SBU employee
        elif (self.check_pm is True
              or (self.employee_id.sbu_master_id and self.employee_id.sbu_master_id.type == 'sbu')):
            # print("====================in practice==========", self.employee_id.sbu_master_id.representative_id.id)
            # rec.check_pm = True
            self.write({'pending_at': self.employee_id.sbu_master_id.representative_id.id,
                        'status': 'Applied'})

            email_to = self.employee_id.sbu_master_id.representative_id.work_email
            manager_emp_notify = self.env['hr.employee'].sudo().search(
                [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
            manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
            mail_cc = []
            if self.employee_id.department_id.manager_id.work_email:
                mail_cc.append(self.employee_id.department_id.manager_id.work_email)
            mail_cc.extend(manager_emp_notify.mapped('work_email'))
            mail_cc.extend(manager_emp_hr.mapped('work_email'))
            cc_mail = ','.join(set(mail_cc)) or ''
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Raised",
                    mail_for='Applied',
                    email_to=email_to,
                    email_from=self.env.user.employee_ids.work_email,
                    mail_cc=cc_mail,
                    name=self.employee_id.sbu_master_id.representative_id.name,
                    user_name=self.employee_id.display_name,
                    remarks=self.remarks_pm,
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Mail Sent Successfully.")
        # else:
        #     # for SBU user
        #     if self.employee_id.sbu_master_id.type == 'sbu':

            # recommendation for training
            
    def take_action_pip(self):
        form_view_id = self.env.ref("performance_improvement_plan.performance_improvement_plan_takeaction_form").id
        return {
                'type': 'ir.actions.act_window',
                'name': 'Take Action',
                'res_model': 'performance_improvement_plan',
                'res_id' : self.id,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'self',
                'flags': {'mode': 'edit'}
                }
      
    def send_to_hod(self):
        if self.suggestion_reviewer:
            if self.suggestion_reviewer == 'RP':
                form_view_id = self.env.ref("performance_improvement_plan.remarks_approver_view_pip_form").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'res_model': 'kw_pip_remark_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                }

            elif self.suggestion_reviewer == 'RT':
                form_view_id = self.env.ref("performance_improvement_plan.remarks_approver_view_pip_training_recommend_form").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'res_model': 'kw_pip_remark_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                }
                
            # else:
            #     view_id = self.env.ref("performance_improvement_plan.remarks_approver_close_view_pip_form").id
            #     return {
            #         'type': 'ir.actions.act_window',
            #         'name': 'Confirm',
            #         'res_model': 'kw_pip_remark_wizard',
            #         'view_mode': 'form',
            #         'view_type': 'form',
            #         'view_id': view_id,
            #         'target': 'new',
            #     }
        else:
            raise ValidationError("Please give's Remark.")

    def send_to_rcm(self):
        form_view_id = self.env.ref("performance_improvement_plan.remarks_approver_view_pip_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'res_model': 'kw_pip_remark_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def forward_to_HR(self):
        if self.suggestion_reviewer_sbu:
            if self.suggestion_reviewer_sbu == 'RP':
                form_view_id = self.env.ref("performance_improvement_plan.remarks_approver_view_pip_form").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'res_model': 'kw_pip_remark_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                }

           
            elif self.suggestion_reviewer_sbu == 'RT':
                form_view_id = self.env.ref("performance_improvement_plan.remarks_approver_view_pip_training_recommend_form").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'res_model': 'kw_pip_remark_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                }
                
            # else:
            #     view_id = self.env.ref("performance_improvement_plan.remarks_approver_close_view_pip_form").id
            #     return {
            #         'type': 'ir.actions.act_window',
            #         'name': 'Confirm',
            #         'res_model': 'kw_pip_remark_wizard',
            #         'view_mode': 'form',
            #         'view_type': 'form',
            #         'view_id': view_id,
            #         'target': 'new',
            #     }
        else:
            raise ValidationError("Please give SBU Remark.")
        
        
    def button_emp_pip_details(self):
        form_view_id = self.env.ref('performance_improvement_plan.kw_pip_feedback_hr_view_feedback_form_view').id
        record = self.env['kw_pip_counselling_details'].sudo().search([('assessee_id', '=', self.employee_id.id), ('pip_ref_id', '=', self.id)])
        return {
            'name': "Counselling Details",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'res_model': 'kw_pip_counselling_details',
            'type': 'ir.actions.act_window',
            'res_id': record.id,
            'domain': [],
            'context': {'create': False, 'edit': False, 'delete': False,},
        }


class DocumentUpload(models.Model):
    _name = 'document_upload'
    _description = 'document_upload'

    ref_id = fields.Many2one('performance_improvement_plan')
    documents = fields.Binary(string=u'Document', attachment=True)
    file_name = fields.Char(string='Document Name')
