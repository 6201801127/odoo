# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime, date, timedelta
from ast import literal_eval
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class kw_eos_checklist(models.Model):
    _inherit = 'kw_eos_checklist'

    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange',
                                    related="applicant_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job Position", track_visibility='onchange',
                             related="applicant_id.job_id")
    division = fields.Many2one('hr.department', string="Division", related="applicant_id.division",
                               track_visibility='onchange')
    section = fields.Many2one('hr.department', string="Practice", related="applicant_id.section",
                              track_visibility='onchange')
    practise = fields.Many2one('hr.department', string="Section", related="applicant_id.practise")
    offboarding_type = fields.Many2one('kw_resignation', string='Offboarding Type', compute="_compute_employee_details",
                                       store=True)
    effective_from = fields.Date(related='offboarding_type.effective_form', string='Effective from')
    last_working_date = fields.Date(related='offboarding_type.last_working_date', string='Last Working Date')
    date_of_joining = fields.Date('Date of Joining', related='offboarding_type.date_of_joining')
    base_branch_id = fields.Many2one('kw_res_branch', related='offboarding_type.base_branch_id')

    state = fields.Selection([('Draft', 'Draft'),
                              ('Applied', 'Applied'),
                              ('Approved', 'Approved'),
                              ('Granted', 'Granted'),
                              ('Rejected', 'Rejected')], default='Draft')
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by")
    approved_by = fields.Many2one('hr.employee', string="Action taken by")

    is_ra = fields.Boolean(string="Is RA?", default=False, compute="_check_ra")
    is_dept_head = fields.Boolean(string="Is RA?", default=False, compute="_check_ra")
    demise_check = fields.Boolean(string="Demise Check", default=False, compute='_compute_demise_check')
    eos_takeaction_check = fields.Boolean(string="Demise Check", default=False, compute='_compute_eos_takeaction_check')

    is_all_checklist_completed = fields.Boolean(string="Is All EOS Checklist Completed ?", default=False,
                                                compute='_compute_checklist_pendings')

    ''' Fields for Tour Module End'''

    tour_apply_pending_for_user = fields.Integer(string="Tour Apply Pending For User", compute='_compute_tour_pendings')
    tour_apply_pending_at_user = fields.Integer(string="Tour Apply Pending At User", compute='_compute_tour_pendings')
    tour_cancellation_pending_for_user = fields.Integer(string="Tour Cancellation Pending For User",
                                                        compute='_compute_tour_pendings')
    tour_cancellation_pending_at_user = fields.Integer(string="Tour Cancellation Pending At User",
                                                       compute='_compute_tour_pendings')
    tour_settlement_details = fields.Char(string="Tour Settlement Details", compute='_compute_tour_pendings')
    tour_advance_pending_at_user = fields.Integer(string="Tour Advance Pending At User",
                                                  compute='_compute_tour_pendings')
    tour_advance_pending_for_user = fields.Integer(string="Tour Advance Pending For User",
                                                   compute='_compute_tour_pendings')
    tour_settlement_pending_at_user = fields.Integer(string="Tour Settlement Pending At User",
                                                     compute='_compute_tour_pendings')
    toursettlement_pending_for_user = fields.Integer(string="Tour Settlement Pending For User",
                                                     compute='_compute_tour_pendings')
    wfh_request_pending_for_user = fields.Integer(string="WFH Request Pending For User",
                                                  compute='_compute_wfh_pendings')
    wfh_request_pending_at_user = fields.Integer(string="WFH Request Pending At User", compute='_compute_wfh_pendings')
    assesment_pending_for_user = fields.Integer(string="WFH Request Pending At User",
                                                compute='_compute_assesment_pendings')
    assesment_pending_at_user = fields.Integer(string="WFH Request Pending At User",
                                               compute='_compute_assesment_pendings')
    assesment_pending_details = fields.Integer(string="WFH Request Pending At User",
                                               compute='_compute_assesment_pendings')

    ''' Fields for Tour Module End '''

    ''' Fields for Advance & Claim Module '''

    # advance_apply_pending_for_user = fields.Integer(string="Salary Advance Apply Pending For User", compute='_compute_advance_pendings')
    # advance_apply_pending_at_user = fields.Integer(string="Salary Advance Apply Pending At User", compute='_compute_advance_pendings')

    ''' Fields for Advance & Claim Module End '''

    ''' Fields For Assets '''
    assets_applied = fields.Integer(string="Assets Applied", compute='_compute_api_fields')
    assets_pending = fields.Integer(string="Assets Pending", compute='_compute_api_fields')
    ''' End Assets Fields '''

    ''' Fields For Leave '''
    leave_applied = fields.Integer(string="Leave Applied", compute='_compute_leave')
    leave_pending = fields.Integer(string="Leave Pending", compute='_compute_leave')

    leave_cancellation_applied = fields.Integer(string="Leave Cancellation Applied", compute='_compute_leave')
    leave_cancellation_pending = fields.Integer(string="Leave Cancellation Pending", compute='_compute_leave')
    ''' End Leave Fields '''

    ''' Fields For Salary Advance '''
    salary_advance_applied = fields.Integer(string="Salary Advance Applied", compute='_compute_api_fields')
    salary_advance_pending = fields.Integer(string="Salary Advance Pending", compute='_compute_api_fields')
    ''' End Salary Advance Fields '''

    ''' Fields For Stationary '''
    stationary_applied = fields.Integer(string="Stationary Applied", compute='_compute_api_fields')
    stationary_pending = fields.Integer(string="Stationary Pending", compute='_compute_api_fields')
    ''' End Stationary Fields '''

    ''' Business Card Fields Start '''
    card_applied = fields.Integer(string="Card Applied", compute='_compute_card_fields')
    card_pending = fields.Integer(string="Card Pending", compute='_compute_card_fields')
    ''' Business Card Fields End '''

    ''' Status Fields From API Start '''
    reg_process_status = fields.Char(string="Offboarding Process", compute='_compute_api_fields')
    kt_process_status = fields.Char(string="KT Process", compute='_compute_api_fields')
    eos_process_status = fields.Char(string="EOS Process", compute='_compute_api_fields')

    ra_details_status = fields.Char(string="RA Details", compute='_compute_api_fields')
    other_action_status = fields.Char(string="Other Action", compute='_compute_api_fields')
    project_task_reporting_status = fields.Char(string="Project Task Reporting", compute='_compute_api_fields')
    task_review_pending_status = fields.Char(string="Task Review Pending", compute='_compute_api_fields')
    active_project_team_member_status = fields.Char(string="Active Project Team Member", compute='_compute_api_fields')
    independent_task_pending_status = fields.Char(string="Independent Task Pending", compute='_compute_api_fields')
    workorder_active_for_user = fields.Integer(string="Workorders", compute='_compute_api_fields')
    workorder_active_at_user = fields.Integer(string="Workorders" ,compute='_compute_api_fields')
    opportunity_active_for_user = fields.Integer(string="opportunitys", compute='_compute_api_fields')
    opportunity_active_at_user = fields.Integer(string="opportunitys" ,compute='_compute_api_fields')
    lead_active_for_user = fields.Integer(string="opportunitys", compute='_compute_api_fields')
    lead_active_at_user = fields.Integer(string="opportunitys" ,compute='_compute_api_fields')


    ''' Status Field From API End '''

    ra_remark = fields.Text(string="Remarks")
    dept_head_remark = fields.Text(string="Remarks")
    is_applicant = fields.Boolean(string="Is Applicant", compute='_compute_applicant_fields', default=True)
    is_manager = fields.Boolean(string="Is Manager", compute='_compute_applicant_fields', default=True)

    att_correction_apply = fields.Integer(string="Attendance Correction Applied", compute='_compute_att_correction')
    att_correction_pending = fields.Integer(string="Attendance Correction Pending", compute='_compute_att_correction')

    att_late_entry_apply = fields.Integer(string="Late Entry Applied", compute='_compute_att_correction')
    att_late_entry_pending = fields.Integer(string="Late Entry Pending", compute='_compute_att_correction')

    att_comp_off_apply = fields.Integer(string="Comp off Applied", compute='_compute_att_correction')
    att_comp_off_pending = fields.Integer(string="Comp off Pending", compute='_compute_att_correction')

    ''' Fields For Petty cash '''
    petty_cash_applied = fields.Integer(string="Salary Advance Applied", compute='_compute_advance_claim')
    petty_cash_pending = fields.Integer(string="Salary Advance Pending", compute='_compute_advance_claim')
    ''' End Salary Petty cash '''
    check_advance = fields.Boolean(string="Check Advance", default=False, compute='_compute_advance_claim')
    ''' Fields For Petty cash '''
    claim_settlement_applied = fields.Integer(string="Salary Advance Applied", compute='_compute_advance_claim')
    claim_settlement_pending = fields.Integer(string="Salary Advance Pending", compute='_compute_advance_claim')
    ''' End Salary Petty cash '''
    check_clearance_existance = fields.Integer(string="Check Clearance", compute='_compute_checklist_pendings')

    @api.multi
    def view_att_correction_pending(self):
        view_id = self.env.ref('kw_hr_attendance.view_kw_employee_take_action_attendance_tree').id
        form_view_id = self.env.ref('kw_hr_attendance.kw_employee_apply_attendance_view_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': "Attendance Request Approval",
            'res_model': 'kw_attendance_request_take_action',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_att_request': True},
            'domain': [('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id), ('state', 'in', ['2'])]
        }
        return action

    @api.multi
    def view_late_entry_pending_details(self):
        # view_id = self.env.ref('kw_hr_attendance.view_late_entry_to_approve_tree').id
        # print('active_idssssssssssss',self._context)
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'name': "Late Entry Approval Requests",
        #     'res_model': 'kw_late_entry_take_action',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'view_id': view_id,
        #     'views': [(view_id, 'tree')],
        #     'target': 'self',
        #     # 'context':{'hr_eos_att_request':True},
        #     'domain' :  [('le_forward_to.user_id','=',self.applicant_id.user_id.id)]
        # }
        # return action
        action_id = self.env.ref('kw_hr_attendance.action_late_entry_approve_requests_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web#action={action_id}&model=kw_late_entry_take_action&view_type=list",
            'target': 'self',
        }

    @api.multi
    def view_comp_off_pending(self):
        view_id = self.env.ref(
            'kw_hr_leave_attendance_integration.view_kw_daily_employee_off_day_entry_take_action_list').id
        action = {
            'type': 'ir.actions.act_window',
            'name': "Take Action",
            'res_model': 'hr.leave.allocation',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            # 'context':{'hr_eos_att_request':True},
            'domain': [('second_approver_id.user_id', '=', self.applicant_id.user_id.id),
                       ('attendance_id', '!=', False), ('state', 'in', ['confirm', 'forward'])]
        }
        return action

    @api.depends('applicant_id')
    def _compute_att_correction(self):
        for eos in self:
            employee = eos.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos.att_correction_apply = self.env['kw_employee_apply_attendance'].sudo().search_count(
                [('employee_id', '=', employee.id), ('state', '=', '2')])
            eos.att_correction_pending = self.env['kw_employee_apply_attendance'].sudo().search_count(
                [('state', 'in', ['2']), ('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id)])
            eos.att_late_entry_apply = self.env['kw_daily_employee_attendance'].sudo().search_count(
                [('employee_id', '=', employee.id), ('check_in_status', '=', '2'), ('le_authority_remark', '=', False),
                 ('late_entry_reason', '!=', False)])
            eos.att_late_entry_pending = self.env['kw_daily_employee_attendance'].sudo().search_count(
                [('employee_id.parent_id', '=', employee.id), ('check_in_status', 'in', ['2', '3']),
                 ('le_authority_remark', '=', False), ('le_state', 'in', ['1', '3'])])
            # eos.att_comp_off_apply = self.env['kw_daily_employee_attendance'].sudo().search_count(
            #     [('check_in', '!=', False), ('check_out', '!=', False),
            #      ('employee_id.user_id', '=', self.applicant_id.user_id.id), ('day_status', 'in', ['2', '4', '5']),
            #      ('state', 'in', ['1', '7', '8'])])
            eos.att_comp_off_apply = self.env['hr.leave.allocation'].sudo().search_count(
                [('employee_id.user_id', '=', employee.user_id.id), ('attendance_id', '!=', False),
                 ('comp_off_allocation', '!=', False), ('state', 'in', ['confirm', 'forward'])])
            eos.att_comp_off_pending = self.env['hr.leave.allocation'].sudo().search_count(
                [('second_approver_id.user_id', '=', self.applicant_id.user_id.id), ('attendance_id', '!=', False),
                 ('state', 'in', ['confirm', 'forward'])])

    @api.depends('applicant_id')
    def _compute_applicant_fields(self):
        for rec in self:
            if rec.applicant_id.user_id.id == self.env.user.id:
                rec.is_applicant = True
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') and rec.eos_apply_for == 'self':
                rec.is_manager = True
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') and rec.eos_apply_for == 'sub':
                rec.is_manager = False

    @api.multi
    def _check_feedback(self):
        for rec in self:
            feedback_status = self.env['employee.exit.interview'].sudo().search(
                [('employee_id', '=', rec.applicant_id.id)])
            if feedback_status:
                rec.is_feedback_submit = True

    is_feedback_submit = fields.Boolean(string="Is feedback Submit?", default=False, compute="_check_feedback")

    """ === View details button for KT Application ======= """

    @api.multi
    def view_kt_details(self):
        view_id = self.env.ref('kw_kt.kw_kt_view_tree').id
        action = {
            'name': 'KT Application',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': [('applicant_id', '=', self.applicant_id.id)]
        }
        return action

    """ === View details button for Tour request details ======= """

    @api.multi
    def tour_request_details(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_take_action_tree').id
        action = {
            'name': 'Tour Request Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': ['|', '&', ('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id),
                       ('state', '=', 'Applied'),
                       '&', ('final_approver_id.user_id', '=', self.applicant_id.user_id.id),
                       ('state', '=', 'Forwarded')],
        }
        return action

    """ === View details button for Tour request details ======= """

    @api.multi
    def tour_advance_pending_details(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_advance_request_take_action_tree').id
        action = {
            'name': 'Tour Advance Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_advance_request',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': [('state', 'in', ['Applied']),
                       ('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id)],
            'context': {'eos_ra_takeaction': True},
        }
        return action

    """ === View details button for Tour request details ======= """

    @api.multi
    def tour_settlement_pending_details(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_settlement_take_action_tree').id
        action = {
            'name': 'Tour Settlement Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_settlement',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': ['|', ('final_approver_id.user_id', '=', self.applicant_id.user_id.id),
                       ('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id),
                       ('state', 'in', ['Applied', 'Forwarded'])
                       ],
            'context': {'eos_ra_takeaction': True},
        }
        return action

    """ === View details button for WFH request details ======= """

    @api.multi
    def wfh_request_pending_details(self):
        view_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_tree').id
        action = {
            'name': 'WFH Request Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_wfh',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id), ('state', '=', 'applied')],
            # 'context': {'eos_ra_takeaction':True},
        }
        return action

    """ === View details button for WFH request details ======= """

    @api.multi
    def assesment_pending_details(self):
        # state 1 = draft, 2 = scheduled
        assesment_pending = self.env['kw_feedback_final_config'].sudo().search(
            [('assessor_id.user_id', '=', self.applicant_id.user_id.id), ('feedback_status', 'in', ['1'])])
        view_id = self.env.ref('kw_assessment_feedback.kw_feedback_add_feedback_kanban_view').id
        action = {
            'name': 'Assessment Feedback Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_feedback_final_config',
            'view_mode': 'kanban',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': [('id', '=', assesment_pending.ids)],
            'context': {'eos_ra_takeaction': True},
        }
        return action

    """ === View details button for Tour cancellation details ======= """

    @api.multi
    def view_tour_cancellation_details(self):
        view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_tree').id
        action = {
            'name': 'Tour Cancellation Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_cancellation',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'domain': [('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id), ('state', '=', 'Applied')],
            'context': {'hr_tour_canceelaion': True}
        }
        return action

    @api.multi
    def view_ra_details(self):
        view_id = self.env.ref('kw_employee.kw_change_ra_relation_view_form').id
        action = {
            'name': 'Change RA',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_change_ra_relation',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            # 'res_id':self.id,
            'context': {'default_reporting_auth_id': self.applicant_id.id, 'default_search_by': 'ra',
                        'eos_ra_change_action': True}
        }
        return action

    """ ==== Submit feedback button method ==== """

    @api.multi
    def view_eos_form(self):
        if self.offboarding_type.offboarding_type.name == 'Termination':
            view_id = self.env.ref('kw_eos.view_termination_employee_exit_interview_form').id
        else:
            view_id = self.env.ref('kw_eos.view_employee_exit_interview_form').id
        action = {
            'name': 'Exit Interview Form',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.exit.interview',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'context': {'default_resignation_id': self.offboarding_type.id,
                        'default_employee_id': self.applicant_id.id},
            # 'res_id':self.id,
            # 'domain' : [('employee_id','=',self.applicant_id.id)]
        }
        return action

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('eos'):
            if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                args += []
            else:
                args += [('applicant_id.user_id', '=', self.env.uid)]
        if self._context.get('eos_report') and not self._context.get('disable_search'):
            if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
                args += [('state', '!=', 'Draft')]
            else:
                args += ['|', '|','|', '&', ('applicant_id.user_id', '=', self.env.uid), ('state', '!=', 'Draft'), '&',
                         ('applicant_id.parent_id.user_id', '=', self.env.uid), ('state', '!=', 'Draft'), '&',
                         '&','&',('applicant_id.sbu_master_id.representative_id','=',False),('applicant_id.department_id.manager_id.user_id', '=', self.env.uid), ('state', '!=', 'Draft'),
                         ('applicant_id.sbu_master_id.representative_id.user_id','=',self.env.uid)]
        return super(kw_eos_checklist, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                     access_rights_uid=access_rights_uid)
        
        

    @api.depends('applicant_id')
    def _compute_demise_check(self):
        for rec in self:
            if rec.offboarding_type.sudo().offboarding_type.name == 'Demise':
                rec.demise_check = True

    @api.depends('applicant_id')
    def _compute_eos_takeaction_check(self):
        if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
            for rec in self:
                if rec.offboarding_type.offboarding_type.name in ['Demise', 'Termination']:
                    rec.eos_takeaction_check = True
        if self.env.user.has_group('kw_employee.group_hr_ra'):
            for rec in self:
                if rec.offboarding_type.offboarding_type.name != 'Demise':
                    rec.eos_takeaction_check = True

    # ===== Compute Employee Details =====
    @api.depends('applicant_id')
    def _compute_employee_details(self):
        for rec in self:
            employee = rec.applicant_id
            offboard_id = self.env['kw_resignation'].sudo().search(
                [('applicant_id', '=', employee.id), ('state', '=', 'grant')])
            # print("offboard_id===",offboard_id)
            # rec.sudo().write({
            #     'job_id':employee.job_id.id if rec.applicant_id.job_id else False,
            #     'division':employee.division.id if rec.applicant_id.division else False,
            #     'section':employee.section.id,
            #     'practise':employee.practise.id,
            #     'offboarding_type':offboard_id.id if offboard_id.offboarding_type else False,
            #     'department_id':employee.department_id.id,
            # })
            rec.offboarding_type = offboard_id.id

    # ==== EOS Reminder ======
    @api.multi
    def action_eos_reminder(self):
        for rec in self:
            eos_record = self.env['kw_resignation'].sudo().search([('applicant_id', '=', rec.applicant_id)])
            reminder_date = eos_record.last_working_date - relativedelta(days=3)
            if eos_record:
                if reminder_date == date.today():
                    # print("Send mail here======>")
                    pass

    @api.model
    def create(self, values):
        res = super(kw_eos_checklist, self).create(values)
        if not values.get('termination_create') or not values.get('demise_create'):
            res.applicant_id = res.applicant_id.id if res.applicant_id else self.env.user.employee_ids.id
        # self.env.user.notify_success("EOS request applied successfully.")

        employee = res.applicant_id if res.applicant_id else self.env.user.employee_ids
        record = self.env['kw_eos_checklist'].search(
            [('applicant_id', '=', employee.id), ('state', '!=', 'Rejected')]) - res
        if record:
            raise ValidationError("You cannot apply for EOS, EOS already been applied.")
        return res

    @api.depends('applicant_id')
    def _compute_card_fields(self):
        for rec in self:
            card_applied_count = 0
            card_pending_count = 0

            card_applied_rec = self.env['kw_visiting_card_apply'].sudo().search_count(
                [('emp_name', '=', rec.applicant_id.id), ('state', 'not in', ['Delivered to User', 'Rejected'])])
            # ===== Card Applied Record ========
            if card_applied_rec:
                card_applied_count = card_applied_rec

            # ====== Card pending record ======
            card_pending_rec = self.env['kw_visiting_card_apply'].sudo().search_count(
                [('emp_name.parent_id', '=', rec.applicant_id.id), ('state', '=', 'Applied')])
            if card_pending_rec:
                card_pending_count = card_pending_rec

            if self.env.user.has_group('kw_visiting_card.group_kw_visiting_card_manager'):
                card_pending_record = self.env['kw_visiting_card_apply'].sudo().search_count(
                    [('state', 'in', ['Approved', 'Granted', 'Sent For Printing', 'Delivered to User'])])
                if card_pending_record:
                    card_pending_count += card_pending_record
            rec.update({'card_applied': card_applied_count,
                        'card_pending': card_pending_count})

    # @api.multi
    # def btn_view_form(self):
    #     view_id = self.env.ref('kw_eos.kw_eos_checklist_view_form').id
    #     action = {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'kw_eos_checklist',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'view_id': view_id,
    #         'target': 'self',
    #         'res_id':self.id,
    #     }
    #     return action

    """Open Salary advance tree view"""

    @api.multi
    def view_salary_advance_details(self):
        user = self.env.user
        # if user.has_group("kw_eos.group_kw_eos_manager"):
        #     domain = ['|',('approver_id','=',self.applicant_id.id),('approved_leave_emp_id.parent_id.user_id','=',self.applicant_id.user_id.id),('status','in',['apply','forward'])]
        # else:
        #     domain = [('action_to_be_taken_by.user_id','=',self.applicant_id.user_id.id),('state','in',['applied','hold','forward'])]
        view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_takeaction_tree').id
        action = {
            'name': "Salary Advance",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_apply_salary_advance',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_leave_cancel': True},
            'domain': [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id),
                       ('state', 'in', ['applied', 'hold', 'forward'])],
        }
        return action

    """Open Petty cash tree view"""

    @api.multi
    def view_petty_cash_details(self):
        user = self.env.user
        # if user.has_group("kw_eos.group_kw_eos_manager"):
        #     domain = ['|',('approver_id','=',self.applicant_id.id),('approved_leave_emp_id.parent_id.user_id','=',self.applicant_id.user_id.id),('status','in',['apply','forward'])]
        # else:
        #     domain = [('action_to_be_taken_by.user_id','=',self.applicant_id.user_id.id),('state','in',['applied','hold','forward'])]
        view_id = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_takeaction_tree').id
        action = {
            'name': "Petty Cash",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_apply_petty_cash',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_leave_cancel': True},
            'domain': [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id),
                       ('state', 'in', ['applied', 'hold', 'forward'])],
        }
        return action

    """Open Claim Settlement tree view"""

    @api.multi
    def view_claim_settlement_details(self):
        user = self.env.user
        # if user.has_group("kw_eos.group_kw_eos_manager"):
        #     domain = ['|',('approver_id','=',self.applicant_id.id),('approved_leave_emp_id.parent_id.user_id','=',self.applicant_id.user_id.id),('status','in',['apply','forward'])]
        # else:
        #     domain = [('action_to_be_taken_by.user_id','=',self.applicant_id.user_id.id),('state','in',['applied','hold','forward'])]
        view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_takeaction_tree').id
        action = {
            'name': "Claim Settlement",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_claim_settlement',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_leave_cancel': True},
            'domain': [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id),
                       ('state', 'in', ['applied', 'hold', 'forward'])],
        }
        return action

    """Open leave cancellation tree view"""

    @api.multi
    def view_leave_cancellation(self):
        user = self.env.user
        if user.has_group("kw_eos.group_kw_eos_manager"):
            domain = ['|', ('approver_id', '=', self.applicant_id.id),
                      ('approved_leave_emp_id.parent_id.user_id', '=', self.applicant_id.user_id.id),
                      ('status', 'in', ['apply', 'forward'])]
        else:
            domain = [('approver_id.user_id', '=', self.applicant_id.user_id.id),
                      ('status', 'not in', ['approve', 'reject'])]
        view_id = self.env.ref('kw_hr_leaves.kw_cancel_leave_approval_list').id
        action = {
            'name': "Leave Cancellation",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_cancel_leave',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_leave_cancel': True},
            'domain': domain
        }
        return action

    @api.multi
    def view_leave_pending(self):
        user = self.env.user
        if user.has_group("kw_eos.group_kw_eos_manager"):
            domain = [('employee_id.parent_id.user_id', '=', self.applicant_id.user_id.id),
                      ('state', 'in', ['confirm', 'hold', 'forward'])]
        else:
            domain = [('second_approver_id.user_id', '=', self.applicant_id.user_id.id),
                      ('state', 'in', ['confirm', 'hold', 'forward'])]
        view_id = self.env.ref('hr_holidays.hr_leave_view_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': "Leave Apply",
            'res_model': 'hr.leave',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'target': 'self',
            'context': {'hr_eos_leave_action': True, 'hr_eos_leave_approver': True},
            'domain': domain
        }
        return action

    @api.multi
    def btn_ra_take_action(self):
        view_id = self.env.ref('kw_eos.eos_take_action_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_eos_checklist',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.id,
        }
        return action

    @api.multi
    def pending_checklist_validation(self):
        raise ValidationError("You cannot apply for EOS as some checklist are still pending.")

    @api.multi
    def forward_to_upper_ra(self):
        # if RA on leave forward to upper RA 
        upper_ra = False
        attendance = self.env['kw_daily_employee_attendance'].search(
            [('employee_id', '=', self.applicant_id.parent_id.id),
             ('attendance_recorded_date', '=', datetime.today().date())])
        if attendance and attendance.status == 'On Leave':
            upper_ra = self.applicant_id.parent_id.parent_id
        return upper_ra

    @api.multi
    def action_eos_submit(self):
        # import pdb
        # pdb.set_trace()
        remark = f'Granted By {self.env.user.employee_ids.name}'
        approved_by = self.env.user.employee_ids
        eos_chklst_log = self.env['kw_eos_checklist_log']
        eos_log = {
            'applicant_id': self.env.user.employee_ids.id,
            'date': self.effective_from,
            'last_working_date': self.last_working_date,
            'eos_id': self.id,
        }
        view_id = False
        form_view_id = False
        employee = self.applicant_id if self.applicant_id else self.env.user.employee_ids
        offboard_rec = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', employee.id), ('state', '=', 'grant')])

        """ Create EOS Clearance record """
        clearance_obj = self.env['hr.employee.clearance'].sudo()
        clearance = clearance_obj.search([('resignation_id', '=', offboard_rec.id)])
        if not clearance.exists():
            clearance = clearance_obj.create({'employee_id': employee.id,
                                              'resignation_id': offboard_rec.id,
                                              'last_day_of_service': offboard_rec.last_working_date,
                                              'hr_unit_date': offboard_rec.last_working_date,
                                              'eos_id': self.id})
        if ((self.env.user.has_group('kw_eos.group_kw_eos_manager')
                or self.env.user.has_group('kw_eos.group_kw_eos_officer'))
                and self.eos_apply_for == 'sub'):
            param = self.env['ir.config_parameter'].sudo()
            hrd_group = literal_eval(param.get_param('kw_eos.notify_cc'))
            email_list = []
            if hrd_group:
                # all_jobs = self.env['hr.job'].browse(hrd_group)
                empls = self.env['hr.employee'].search([('id', 'in', hrd_group), ('active', '=', True)])
                email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')
            if employee.coach_id.work_email and employee.coach_id.active == True:
                email_list += employee.coach_id.work_email
            #     print(email_list)
            # email_list.append(employee.department_id.manager_id.work_email)

            hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list = [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

            cc = email_list and ",".join(email_list) or ''
            """ 1) State changed to Applied
                2) Mail fired to respective authorities
            """
            if self.offboarding_type.offboarding_type.name not in ['Termination', 'Demise']:
                """ Update Eos record """
                upper_ra = self.forward_to_upper_ra()
                self.write({'state': 'Applied',
                            'action_to_be_taken_by': upper_ra.id if upper_ra else employee.parent_id.id})
                """ RA mail EOS applied mail notification """
                eos_log['remark'] = f'Applied By {self.env.user.employee_ids.name}'
                eos_log['state'] = 'Applied'
                """ Create EOS Log record """
                checklist_log = eos_chklst_log.create(eos_log)
                template_obj = self.env.ref('kw_eos_integrations.eos_apply_mail_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc,
                                                                                      mail_to=self.applicant_id.parent_id.work_email,
                                                                                      applicant_name=self.applicant_id.name,
                                                                                      code=self.applicant_id.emp_code,
                                                                                      branch_alias=self.base_branch_id.alias,
                                                                                      department_id=self.department_id.name,
                                                                                      division=self.division.name,
                                                                                      section=self.section.name,
                                                                                      practise=self.practise.name,
                                                                                      job_id=self.job_id.name,
                                                                                      action_taken_by=self.action_to_be_taken_by.name,
                                                                                      last_working_date=datetime.strptime(
                                                                                          str(self.last_working_date),
                                                                                          "%Y-%m-%d").strftime(
                                                                                          "%d-%b-%Y"),
                                                                                      ).send_mail(checklist_log.id,
                                                                                                  notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                  force_send=False)
            else:
                """ 1) State changes to Granted 
                    2) Mail fired to the respective authorities when offboarding_type is Termination or Demise 
                """
                """ Update EOS log """
                eos_log['remark'] = f'Granted By {self.env.user.employee_ids.name}'
                eos_log['state'] = 'Granted'
                """ Create EOS Log record """
                checklist_log = eos_chklst_log.create(eos_log)
                self.action_dept_head_remark_grant(remark, approved_by)
            """ Mail fired to Onboarding(RA,IT,Admin,Finance) and EOS Manager """
            # print("========================",checklist_log,)
            admin_list = []
            admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
            admin_list += admin.filtered(lambda r: r.work_email != False).mapped('work_email')
            admin_lists = admin_list and ",".join(admin_list) or ''
            template_obj = self.env.ref('kw_eos_integrations.clearance_admin_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(to=admin_lists,
                                                                                  applicant_name=self.applicant_id.name,
                                                                                  code=self.applicant_id.emp_code,
                                                                                  branch_alias=self.base_branch_id.alias,
                                                                                  department_id=self.department_id.name,
                                                                                  division=self.division.name,
                                                                                  section=self.section.name,
                                                                                  practise=self.practise.name,
                                                                                  job_id=self.job_id.name,
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(clearance.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)

            it_list = []
            it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
            it_list += it.filtered(lambda r: r.work_email != False).mapped('work_email')
            it_lists = it_list and ",".join(it_list) or ''
            template_obj = self.env.ref('kw_eos_integrations.clearance_it_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(to=it_lists,
                                                                                  applicant_name=self.applicant_id.name,
                                                                                  code=self.applicant_id.emp_code,
                                                                                  branch_alias=self.base_branch_id.alias,
                                                                                  department_id=self.department_id.name,
                                                                                  division=self.division.name,
                                                                                  section=self.section.name,
                                                                                  practise=self.practise.name,
                                                                                  job_id=self.job_id.name,
                                                                                  last_working_date=datetime.strptime(str(self.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(clearance.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)

            account_list = []
            accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
            account_list += accaunt.filtered(lambda r: r.work_email != False).mapped('work_email')
            account_lists = account_list and ",".join(account_list) or ''
            template_obj = self.env.ref('kw_eos_integrations.clearance_account_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(to=account_lists,
                                                                                  applicant_name=self.applicant_id.name,
                                                                                  code=self.applicant_id.emp_code,
                                                                                  branch_alias=self.base_branch_id.alias,
                                                                                  department_id=self.department_id.name,
                                                                                  division=self.division.name,
                                                                                  section=self.section.name,
                                                                                  practise=self.practise.name,
                                                                                  job_id=self.job_id.name,
                                                                                  last_working_date=datetime.strptime(str(self.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(clearance.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)

            manager_list = []
            manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
            manager_list += manager.filtered(lambda r: r.work_email != False).mapped('work_email')
            manager_lists = manager_list and ",".join(manager_list) or ''
            template_obj = self.env.ref('kw_eos_integrations.clearance_manager_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(to=manager_lists,
                                                                                  applicant_name=self.applicant_id.name,
                                                                                  code=self.applicant_id.emp_code,
                                                                                  branch_alias=self.base_branch_id.alias,
                                                                                  department_id=self.department_id.name,
                                                                                  division=self.division.name,
                                                                                  section=self.section.name,
                                                                                  practise=self.practise.name,
                                                                                  job_id=self.job_id.name,
                                                                                  last_working_date=datetime.strptime(str(self.last_working_date), "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(clearance.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)

            upper_ra = self.forward_to_upper_ra()
            ra_email = upper_ra.work_email if upper_ra else self.applicant_id.parent_id.work_email
            template_obj = self.env.ref('kw_eos_integrations.clearance_ra_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(to=ra_email,
                                                                                  applicant_name=self.applicant_id.name,
                                                                                  code=self.applicant_id.emp_code,
                                                                                  branch_alias=self.base_branch_id.alias,
                                                                                  department_id=self.department_id.name,
                                                                                  division=self.division.name,
                                                                                  section=self.section.name,
                                                                                  practise=self.practise.name,
                                                                                  job_id=self.job_id.name,
                                                                                  last_working_date=datetime.strptime(
                                                                                      str(self.last_working_date),
                                                                                      "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                  ).send_mail(clearance.id,
                                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                              force_send=False)
            self.env.user.notify_success("Mail sent successfully.")

            view_id = self.env.ref('kw_eos_integrations.kw_eos_checklist_view_tree').id
            form_view_id = self.env.ref('kw_eos.kw_eos_checklist_view_form').id

            return {
                'name': 'EOS Apply',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'kw_eos_checklist',
                'type': 'ir.actions.act_window',
                'target': 'main',
                'views': [(view_id, 'tree'), (form_view_id, 'form')],
            }
        else:
            # print('employeeemployeeemployeeemployeeemployee',self.applicant_id)
            # employee = self.applicant_id if self.applicant_id else self.env.user.employee_ids
            # record = self.env['kw_eos_checklist'].search([('applicant_id','=',employee.id)])-self
            # if record:
            #     raise ValidationError("You cannot apply for EOS, EOS already been applied.")

            """ for users state changes to Granted and mail fired to the respective authorities """
            if self.offboarding_type.offboarding_type.name == 'Termination':
                view_id = self.env.ref('kw_eos.view_termination_employee_exit_interview_form').id
            else:
                view_id = self.env.ref('kw_eos.view_employee_exit_interview_form').id
            exit_interview = self.env['employee.exit.interview'].sudo().search(
                [('resignation_id', '=', offboard_rec.id), ('employee_id', '=', employee.id)], order='id desc', limit=1)
            # print("exit_interview===",exit_interview)
            action = {
                'name': 'Exit Interview Form',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.exit.interview',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
            }
    
            if exit_interview:
                action['res_id'] = exit_interview.id
            else:
                action['context'] = {'default_resignation_id': self.offboarding_type.id,'default_employee_id': self.applicant_id.id}
            # print("action==",action)
            return action

    @api.multi
    def action_eos_submit_by_hr(self):
        employee = self.applicant_id if self.applicant_id else self.env.user.employee_ids
        self.write({'state': 'Applied', 'action_to_be_taken_by': employee.parent_id.id})
        param = self.env['ir.config_parameter'].sudo()
        hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
        email_list = []
        if hrd_group:
            all_jobs = self.env['hr.job'].browse(hrd_group)
            empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids), ('active', '=', True)])
            email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')
        #     print(email_list)
        # email_list.append(employee.department_id.manager_id.work_email)
        # print(email_list)

        hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
        if hrd_cc_group:
            email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

        cc = email_list and ",".join(email_list) or ''

        template_obj = self.env.ref('kw_eos_integrations.eos_apply_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc).send_mail(self.id,
                                                                                               notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                               force_send=False)

        offboard_rec = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', employee.id), ('state', '=', 'grant')])
        self.env['hr.employee.clearance'].sudo().create({'employee_id': employee.id,
                                                         'resignation_id': offboard_rec.id,
                                                         'last_day_of_service': offboard_rec.last_working_date,
                                                         'hr_unit_date': offboard_rec.last_working_date,
                                                         'eos_id': self.id})

        admin_list = []
        admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
        admin_list += admin.filtered(lambda r: r.work_email != False).mapped('work_email')
        admin_lists = admin_list and ",".join(admin_list) or ''
        template_obj = self.env.ref('kw_eos_integrations.clearance_admin_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(to=admin_lists).send_mail(self.id,
                                                                                                        notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                        force_send=False)

        it_list = []
        it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
        it_list += it.filtered(lambda r: r.work_email != False).mapped('work_email')
        it_lists = it_list and ",".join(it_list) or ''
        template_obj = self.env.ref('kw_eos_integrations.clearance_it_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(to=it_lists).send_mail(self.id,
                                                                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                     force_send=False)

        account_list = []
        accaunt = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
        account_list += accaunt.filtered(lambda r: r.work_email != False).mapped('work_email')
        account_lists = account_list and ",".join(account_list) or ''
        template_obj = self.env.ref('kw_eos_integrations.clearance_account_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(to=account_lists).send_mail(self.id,
                                                                                                          notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                          force_send=False)

        manager_list = []
        manager = self.env.ref('kw_eos.group_kw_eos_manager').mapped('users.employee_ids')
        manager_list += manager.filtered(lambda r: r.work_email != False).mapped('work_email')
        manager_lists = manager_list and ",".join(manager_list) or ''
        template_obj = self.env.ref('kw_eos_integrations.clearance_manager_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(to=manager_lists).send_mail(self.id,
                                                                                                          notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                          force_send=False)

        # ra_list=[]
        # ra_list.append(self.applicant_id.parent_id.work_email)
        # ra_lists=ra_list and ",".join(ra_list) or ''
        ra_email = self.applicant_id.parent_id.work_email
        template_obj = self.env.ref('kw_eos_integrations.clearance_ra_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(to=ra_email).send_mail(self.id,
                                                                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                                     force_send=False)
        self.env.user.notify_success("Mail sent successfully.")

        # template_id = self.env.ref('kw_eos_integrations.eos_apply_mail_template')
        # template_id.send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        # self.env.user.notify_success("Mail sent successfully.")

        action_id = self.env.ref('kw_eos.eos_checklist_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_eos_checklist&view_type=list',
            'target': 'self',
        }

    @api.multi
    def action_eos_approve(self):
        view_id = self.env.ref('kw_eos_integrations.view_eos_ra_approve_remark_form').id
        action = {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_eos_checklist',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_applicant_id': self.applicant_id.id}
        }
        return action

    # ====Reject button ===
    @api.multi
    def action_eos_reject(self):
        self.ra_remark = False
        view_id = self.env.ref('kw_eos_integrations.view_eos_ra_reject_remark_form').id
        action = {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_eos_checklist',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_applicant_id': self.applicant_id.id}
        }
        return action

    # ==== Reject Submit =====
    @api.multi
    def action_ra_remark_reject(self):
        # self.write({'state':'Rejected'})
        employee = self.applicant_id
        if not employee:
            employee = self.env.user.employee_ids
        eos_checklist_rec = self.env['kw_eos_checklist'].sudo().search(
            [('applicant_id', '=', employee.id), ('state', '!=', 'Rejected')])

        eos_checklist_rec.write({'state': 'Rejected',
                                 'ra_remark': self.ra_remark,
                                 'action_to_be_taken_by': False,
                                 'approved_by': eos_checklist_rec.action_to_be_taken_by.id})

        # offboard_rec = self.env['kw_resignation'].sudo().search([('applicant_id','=',employee.id),('state','=','grant')])
        clearance_record = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', employee.id)])
        for rec in clearance_record:
            rec.write({'active': False})

        param = self.env['ir.config_parameter'].sudo()
        hrd_group = literal_eval(param.get_param('kw_eos.notify_cc'))
        email_list = []
        if hrd_group:
            # all_jobs = self.env['hr.job'].browse(hrd_group)
            # empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids),('active','=',True)])
            empls = self.env['hr.employee'].search([('id', 'in', hrd_group), ('active', '=', True)])
            email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')
        email_list.append(self.applicant_id.department_id.manager_id.work_email)
        # it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
        # email_list += it.filtered(lambda r: r.work_email != False).mapped('work_email')
        # admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
        # email_list += admin.filtered(lambda r: r.work_email != False).mapped('work_email')

        hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
        if hrd_cc_group:
            email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

        cc = email_list and ",".join(email_list) or ''
        template_obj = self.env.ref('kw_eos_integrations.eos_reject_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc,
                                                                              mail_to=self.applicant_id.work_email,
                                                                              applicant_name=self.applicant_id.name,
                                                                              code=self.applicant_id.emp_code,
                                                                              branch_alias=self.base_branch_id.alias,
                                                                              department_id=self.department_id.name,
                                                                              division=self.division.name,
                                                                              section=self.section.name,
                                                                              practise=self.practise.name,
                                                                              job_id=self.job_id.name,
                                                                              ra_remark=self.ra_remark,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.last_working_date),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ).send_mail(self.eos_log_ids[0].id,
                                                                                          notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                          force_send=False)
        self.env.user.notify_success("Mail sent successfully.")

        action_id = self.env.ref('kw_eos.eos_take_action_action').id
        eos_chklst_log = self.env['kw_eos_checklist_log']
        eos_log = eos_chklst_log.create({'applicant_id': self.applicant_id.parent_id.id,
                                         'date': self.effective_from,
                                         'state': self.state,
                                         'remark': self.ra_remark,
                                         'last_working_date': self.last_working_date,
                                         'eos_id': self.id,
                                         })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_eos_checklist&view_type=list',
            'target': 'self',
        }

    @api.multi
    def action_ra_remark_approve(self):

        if self.applicant_id.department_id.manager_id.id == self.applicant_id.id or self.applicant_id.id == self.applicant_id.sbu_master_id.representative_id.id:
            self.action_dept_head_remark_grant()
            action_id = self.env.ref('kw_eos.eos_take_action_action').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_eos_checklist&view_type=list',
                'target': 'self',
            }


        else:
            employee = self.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos_checklist_rec = self.env['kw_eos_checklist'].sudo().search(
                [('applicant_id', '=', employee.id), ('state', '!=', 'Rejected')])

            eos_checklist_rec.write({'state': 'Approved',
                                    'ra_remark': self.ra_remark,
                                    'action_to_be_taken_by': employee.sbu_master_id.representative_id.id if employee.sbu_master_id.representative_id else employee.department_id.manager_id.id,
                                    'approved_by': eos_checklist_rec.action_to_be_taken_by.id})
            # print("============================",eos_checklist_rec,eos_checklist_rec.action_to_be_taken_by)

            param = self.env['ir.config_parameter'].sudo()
            hrd_group = literal_eval(param.get_param('kw_eos.notify_cc'))
            email_list = []
            if hrd_group:
                empls = self.env['hr.employee'].search([('id', 'in', hrd_group), ('active', '=', True)])
                email_list += empls.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_list.append(self.applicant_id.department_id.manager_id.work_email)

            hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

            users_data = self.env['res.users'].sudo().search([])
            rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
            rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
            old_cc = email_list and ",".join(email_list) or ''
            cc = rcm_work_email + ',' + old_cc

            template_obj = self.env.ref('kw_eos_integrations.eos_approve_mail_template')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc,
                                                                                mail_to=self.applicant_id.sbu_master_id.representative_id.work_email if self.applicant_id.sbu_master_id.representative_id else self.applicant_id.department_id.manager_id.work_email,
                                                                                applicant_name=self.applicant_id.name,
                                                                                emp_code =self.applicant_id.parent_id.emp_code,
                                                                                code=self.applicant_id.emp_code,
                                                                                branch_alias=self.base_branch_id.alias,
                                                                                department_id=self.department_id.name,
                                                                                division=self.division.name,
                                                                                section=self.section.name,
                                                                                practise=self.practise.name,
                                                                                job_id=self.job_id.name,
                                                                                ra_remark=self.ra_remark,
                                                                                last_working_date=datetime.strptime(
                                                                                    str(self.last_working_date),
                                                                                    "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                                ).send_mail(self.eos_log_ids[0].id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                            force_send=False)
            eos_chklst_log = self.env['kw_eos_checklist_log']
            eos_log = eos_chklst_log.create({
                'applicant_id': self.applicant_id.parent_id.id,
                'date': self.effective_from,
                'state': self.state,
                'remark': self.ra_remark,
                'last_working_date': self.last_working_date,
                'eos_id': self.id,
            })
            self.env.user.notify_success("Mail sent successfully.")

            action_id = self.env.ref('kw_eos.eos_take_action_action').id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=kw_eos_checklist&view_type=list',
                'target': 'self',
            }

    @api.multi
    def action_eos_grant(self):
        view_id = self.env.ref('kw_eos_integrations.view_eos_grant_remark_form').id
        action = {
            'name': "Remarks",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_eos_checklist',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_applicant_id': self.applicant_id.id}
        }
        return action

    @api.multi
    def action_dept_head_remark_grant(self, remark=False, approved_by=False, mail_to=False):
        upper_ra = self.forward_to_upper_ra()
        clearance = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', self.applicant_id.id)],limit=1,order='id desc')
        if clearance and clearance.eos_id.id == self.id:
            # print("eos id matched------")
            clearance.hr_eos_clearance = self.dept_head_remark
        eos_checklist_rec = self.env['kw_eos_checklist'].sudo().search(
            [('applicant_id', '=', self.applicant_id.id), ('state', '!=', 'Rejected')])
        eos_checklist_rec.write({'state': 'Granted',
                                 'dept_head_remark': self.dept_head_remark if self.dept_head_remark else '',
                                 'action_to_be_taken_by': upper_ra.id if upper_ra else False,
                                 'approved_by': approved_by.id if approved_by else self.action_to_be_taken_by.id})

        # if approved_by and not mail_to or self.applicant_id.department_id.manager_id.id == self.env.user.employee_ids.id:
        #     email_list.append(self.applicant_id.parent_id.work_email)
        # if self.applicant_id.coach_id.work_email and self.offboarding_type.name == 'Terminattion':
        #     email_list += self.applicant_id.coach_id.work_email
        users_data = self.env['res.users'].sudo().search([])
        rcm_head = users_data.filtered( lambda user : user.has_group('kw_recruitment.group_rcm_head_user') == True)
        rcm_work_email = ','.join(rcm_head.mapped('employee_ids.work_email'))
        old_cc = self.get_cc(deg_group=True, hrd=True, dept_head=True, account=True, ra=True, f_auth=True, it=True,
                         admin=True, upper_ra=True, other_hrd=True,sbu=True)
        # print("hfhffhghffholddddddddddddddddddd==============",old_cc,rcm_work_email)
        cc =rcm_work_email +','+ old_cc
        template_obj = self.env.ref('kw_eos_integrations.eos_grant_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).with_context(cc=cc,
                                                                              remark="Granted",
                                                                              action_taken_by=approved_by.name if approved_by else self.env.user.employee_ids.name,
                                                                              action_taken_by_code =approved_by.emp_code if approved_by else self.env.user.employee_ids.emp_code,
                                                                              applicant_email=self.applicant_id.work_email if self.applicant_id.work_email else mail_to,
                                                                              applicant_name=self.applicant_id.name,
                                                                              code=self.applicant_id.emp_code,
                                                                               
                                                                              branch_alias=self.base_branch_id.alias,
                                                                              sbu_type=self.applicant_id.sbu_master_id.type if self.applicant_id.sbu_master_id.type else '',
                                                                              sbu=self.applicant_id.sbu_master_id.name if self.applicant_id.sbu_master_id else '',
                                                                              department_id=self.department_id.name,
                                                                              division=self.division.name,
                                                                              section=self.section.name,
                                                                              practise=self.practise.name,
                                                                              job_id=self.job_id.name,
                                                                              action_to_be_taken_by=self.action_to_be_taken_by.name,
                                                                              action_to_be_taken_by_code=self.action_to_be_taken_by.emp_code,
                                                                              last_working_date=datetime.strptime(
                                                                                  str(self.last_working_date),
                                                                                  "%Y-%m-%d").strftime("%d-%b-%Y"),
                                                                              ra_remark=self.ra_remark,
                                                                              dept_head_remark=self.dept_head_remark,
                                                                              ).send_mail(self.eos_log_ids[0].id,
                                                                                          notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                          force_send=False)
        self.env.user.notify_success("Mail sent successfully.")
        if self.applicant_id.department_id.manager_id.id == self.env.user.employee_ids.id or self.applicant_id.id == self.applicant_id.department_id.manager_id.id or self.applicant_id.id == self.applicant_id.sbu_master_id.representative_id.id:
            eos_chklst_log = self.env['kw_eos_checklist_log']
            eos_log = eos_chklst_log.create({'applicant_id': self.env.user.employee_ids.id,
                                             'date': self.effective_from,
                                             'state': self.state,
                                             'remark': self.dept_head_remark if self.dept_head_remark else self.ra_remark,
                                             'last_working_date': self.last_working_date,
                                             'eos_id': self.id,
                                             })

        action_id = self.env.ref('kw_eos.eos_take_action_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_eos_checklist&view_type=list',
            'target': 'self',
        }

    # get cc
    @api.multi
    def get_cc(self, deg_group=False, hrd=False, dept_head=False, reg_record=None, account=False, ra=False,
               f_auth=False, it=False, admin=False, upper_ra=False, other_hrd=False, sbu=False):
        param = self.env['ir.config_parameter'].sudo()
        email_list = []
        employee = self.applicant_id if self.applicant_id else self.env.user.employee_ids
        if ra:
            if reg_record:
                ra_id = reg_record.mapped('applicant_id.parent_id')
                email_list += ra_id and ra_id.work_email and [ra_id.work_email] or []
            else:
                email_list.append(employee.parent_id.work_email)
        if f_auth:
            if reg_record and reg_record.applicant_id.coach_id != reg_record.applicant_id.parent_id and reg_record.applicant_id.coach_id.active == True:
                f_auth_id = reg_record.mapped('applicant_id.coach_id')
                if f_auth_id:
                    email_list += f_auth_id and f_auth_id.work_email and [f_auth_id.work_email] or []
        if account:
            account_emp = self.env.ref('kw_onboarding.group_kw_onboarding_finance').mapped('users.employee_ids')
            email_list += account_emp.filtered(lambda r: r.work_email != False and r.active == True).mapped(
                'work_email')
        if it:
            it = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').mapped('users.employee_ids')
            email_list += it.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
        if admin:
            admin = self.env.ref('kw_onboarding.group_kw_onboarding_admin').mapped('users.employee_ids')
            email_list += admin.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
        if upper_ra:
            # Restrict CEO mail
            upper_upper_ra = employee.parent_id.parent_id.mapped('parent_id')
            if upper_upper_ra and employee.parent_id.parent_id.active == True:
                email_list.append(employee.parent_id.parent_id.work_email)
        """ fetch SBU representative email """
        if sbu:
            sbu_emp = employee.sbu_master_id.representative_id
            if sbu_emp:
                email_list.append(employee.sbu_master_id.representative_id.work_email)
        
        """HRD users"""
        if hrd:
            hrd_group = literal_eval(param.get_param('kw_eos.hrd_ids'))
            if hrd_group:
                empls = self.env['hr.employee'].search([('id', 'in', hrd_group), ('active', '=', True)])
                email_list += empls.filtered(lambda r: r.work_email).mapped('work_email')

        """Notify CC users"""
        if deg_group:
            cc_group = literal_eval(param.get_param('kw_eos.notify_cc'))
            if cc_group:
                # all_jobs = self.env['hr.job'].browse(cc_group)
                # empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids),('active','=',True)])
                empls = self.env['hr.employee'].search([('id', 'in', cc_group), ('active', '=', True)])
                if empls:
                    email_list += [emp.work_email for emp in empls if emp.work_email]

        if hrd or deg_group:
            hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
            if hrd_cc_group:
                email_list += [user.email for user in hrd_cc_group if user.email and isinstance(user.email, str)]

        """department head users"""
        if dept_head:
            if reg_record:
                manager_id = reg_record.mapped('applicant_id.department_id.manager_id')
                email_list += manager_id and manager_id.work_email and [manager_id.work_email] or []
            else:
                email_list.append(employee.department_id.manager_id.work_email)
                if self.state == 'forward' and employee.parent_id.active == True:
                    email_list.append(employee.parent_id.work_email)
        """ other HRD """
        if other_hrd:
            cc_group = literal_eval(param.get_param('kw_eos.new_hrd_ids'))
            if cc_group:
                empls = self.env['hr.employee'].search([('id', 'in', cc_group), ('active', '=', True)])
                if empls:
                    email_list += [emp.work_email for emp in empls if emp.work_email]

        email_list = list(filter(None, email_list))
        email = set(email_list)
        return email and ",".join(email) or ''

        # kt_process_status

    @api.depends('applicant_id')
    def _check_ra(self):
        for record in self:
            if record.applicant_id.parent_id.user_id.id == record.action_to_be_taken_by.user_id.id:
                record.is_ra = True

            if record.applicant_id.department_id.manager_id.user_id.id == record.action_to_be_taken_by.user_id.id or record.applicant_id.sbu_master_id.representative_id.user_id.id == record.action_to_be_taken_by.user_id.id \
                    and record.action_to_be_taken_by.user_id.id == self.env.user.id:
                record.is_dept_head = True

    @api.depends('applicant_id')
    def _compute_api_fields(self):
        demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_eos.module_offboarding_mode_status')
        if demo_mode_enabled:
            pass
        else:
            # res = super(kw_eos_checklist, self).default_get(fields)
            # print("inside api=====================================================")
            parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
            EOSurl = parameterurl + 'ManageEOSDetails'
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            for eos_id in self:
                employee = eos_id.applicant_id
                if not employee:
                    employee = self.env.user.employee_ids

                reg_record = self.env['kw_resignation'].sudo().search(
                    [('applicant_id', '=', employee.id), ('state', '=', 'grant')])
                if reg_record:
                    if reg_record.offboarding_type.name == 'Resignation':
                        reg_process_status = "Resignation Completed"
                    if reg_record.offboarding_type.name == 'Retirement':
                        reg_process_status = "Retirement Completed"
                    if reg_record.offboarding_type.name == 'Contract Closure':
                        reg_process_status = "Contract Closure Completed"
                    if reg_record.offboarding_type.name == 'Demise':
                        reg_process_status = "Demise Completed"
                    if reg_record.offboarding_type.name == 'Termination':
                        reg_process_status = "Termination Completed"
                else:
                    reg_process_status = "Pending"

                """ KT Check """
                # kt_completed_record = self.env['kw_kt_view'].sudo().search(
                #     [('applicant_id', '=', employee.id), ('state', '=', 'Completed')])
                kt_record = self.env['kw_kt_view'].sudo().search(
                    [('applicant_id', '=', employee.id), ('kt_type_id.code', '=', 'reg')])
                if kt_record:
                    if kt_record.state == 'Completed':
                        kt_process_status = "Completed"
                    elif kt_record.state != 'Completed':
                        kt_process_status = "Pending"
                else:
                    kt_process_status = 'Not Required'

                """ Feedback check """
                feedback_status = self.env['employee.exit.interview'].sudo().search(
                    [('employee_id', '=', eos_id.applicant_id.id)])
                if feedback_status:
                    eos_process_status = "Completed"
                else:
                    eos_process_status = "Not Applied"

                """RA check"""
                child_id = self.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
                if child_id:
                    ra_details_status = 'Pending'
                else:
                    ra_details_status = 'Completed'

                user_id = eos_id.applicant_id.kw_id
                if not user_id:
                    user_id = self.env.user.employee_ids.kw_id

                # if eos_apply_for == 'self':
                #     userId = str(self.env.user.employee_ids.kw_id)
                # else:
                #     userId = str(self.applicant_id.kw_id)

                EOSDict = {
                    "userId": user_id
                }
                try:
                    resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)
                except Exception:
                    raise ValidationError("Some error occurred.Please try again later")
                if json_record.get('Userstatus') == '1':
                    pending_advances_for_count = False
                    pending_advances_at_count = False
                    if json_record.get('retEOSActDa'):
                        eos_checklist = json_record.get('retEOSActDa')
                        advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
                        if advance_checklist:
                            for rec in eos_checklist:
                                if rec['Activity_Name'] == "Salary Advance":
                                    salary_advance_applied = int(rec['Applied'])
                                    salary_advance_pendings = int(rec['Pendings'])
                        else:
                            ''' Start Pending For count '''
                            pending_advances_for_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count(
                                [('employee_id', '=', employee.id), ('state', 'not in', ['paid', 'cancel', 'reject'])])
                            ''' End Pending For '''

                            ''' Start Pending At count '''
                            pending_advances_at_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count(
                                [('action_to_be_taken_by', '=', employee.id), ('state', 'in', ['applied', 'forward'])])
                            ''' End Pending At '''

                            # eos_id.update({
                            #     'salary_advance_applied':pending_advances_for_count,
                            #     'salary_advance_pendings':pending_advances_at_count
                            # })

                        for eos in eos_checklist:
                            if eos['Activity_Name'] == "Assets":
                                assets_applied = int(eos['Applied'])
                                assets_pendings = int(eos['Pendings'])

                            # if eos['Activity_Name'] == "Leave Apply":
                            #     leave_applied = int(eos['Applied'])
                            #     leave_pendings = int(eos['Pendings'])

                            # if eos['Activity_Name'] == "Leave Cancellation":
                            #     leave_cancellation_applied = int(eos['Applied'])
                            #     leave_cancellation_pendings = int(eos['Pendings'])

                            # if eos['Activity_Name'] == "Salary Advance":
                            #     salary_advance_applied = int(eos['Applied'])
                            #     salary_advance_pendings = int(eos['Pendings'])

                            if eos['Activity_Name'] == "Stationary":
                                stationary_applied = int(eos['Applied'])
                                stationary_pendings = int(eos['Pendings'])

                            if eos['Activity_Name'] == "Opportunity active":
                                opportunity_active_for_user = int(eos['Applied'])
                                opportunity_active_at_user = int(eos['Pendings'])

                            if eos['Activity_Name'] == "WorkOrder active":
                                workorder_active_for_user = int(eos['Applied'])
                                workorder_active_at_user = int(eos['Pendings'])
                            
                            if eos['Activity_Name'] == "Leads active":
                                lead_active_for_user = int(eos['Applied'])
                                lead_active_at_user = int(eos['Pendings'])

                    if json_record.get('retEOSDa'):
                        eos_all_status = json_record.get('retEOSDa')
                        active_project_member_status, other_action_status, project_task_reporting_status = '', '', ''
                        task_review_pending_status, active_project_team_member, independent_task_pending_status = '', '', ''
                        for eos_status in eos_all_status:
                            # if eos_status['Reason'] == "Resignation Process":
                            #     reg_process_status = eos_status["Status"]
                            # if eos_status['Reason'] == "KT Process":
                            #     kt_process_status = eos_status["Status"]
                            # if eos_status['Reason'] == "EOS Process":
                            #     eos_process_status = eos_status["Status"]

                            if eos_status['Reason'].strip() == "Active Project Team Member".strip():
                                active_project_member_status = eos_status["Status"]
                            # if eos_status['Reason'] == "RA Details":
                            #     ra_details_status = eos_status["Status"]
                            # if eos_status['Reason'] == "Other Action":
                            #     if eos_status["Status"] == "Not Completed":
                            #         other_action_status = "Pending"
                            #     else:
                            #         other_action_status = "Completed"
                            # if eos_status['Reason'] == "Project Task Reporting":
                            #     project_task_reporting_status = eos_status["Status"]
                            if eos_status['Reason'] == "Task Review Pending":
                                if eos_status["Status"] == "Still Project task Review pending":
                                    task_review_pending_status = "Pending"
                                else:
                                    task_review_pending_status = "Completed"
                            if eos_status['Reason'] == "Active Project Team Member":
                                active_project_team_member = eos_status["Status"]
                            # if eos_status['Reason'] == "Independent Task Pending":
                            #     independent_task_pending_status = eos_status["Status"]

                    self.env['kw_eos_log'].sudo().create(
                        {'req_data': EOSDict, 'response_res': json_record, 'type': 'ManageEOSDetails'})

                    eos_id.update({
                        'assets_applied': assets_applied,
                        'assets_pending': assets_pendings,
                        # 'leave_applied':leave_applied,
                        # 'leave_pending':leave_pendings,
                        # 'leave_cancellation_applied':leave_cancellation_applied ,
                        # 'leave_cancellation_pending':leave_cancellation_pendings ,

                        'stationary_applied': stationary_applied,
                        'stationary_pending': stationary_pendings,
                        'opportunity_active_for_user': opportunity_active_for_user,
                        'opportunity_active_at_user': opportunity_active_at_user,
                        'workorder_active_for_user': workorder_active_for_user,
                        'workorder_active_at_user': workorder_active_at_user,
                        'lead_active_for_user':lead_active_for_user,
                        'lead_active_at_user':lead_active_at_user,
                        'salary_advance_applied': pending_advances_for_count,
                        'salary_advance_pending': pending_advances_at_count,
                        'ra_details_status': ra_details_status,
                        # 'other_action_status': other_action_status,
                        'project_task_reporting_status': project_task_reporting_status,
                        'task_review_pending_status': task_review_pending_status,
                        'active_project_team_member_status': active_project_member_status if active_project_member_status else "Completed",
                        'independent_task_pending_status': independent_task_pending_status,
                        'reg_process_status': reg_process_status,
                        'kt_process_status': kt_process_status,
                        'eos_process_status': eos_process_status,
                    })

    # @api.depends('applicant_id')
    # def _compute_advance_pendings(self):
    #     for eos in self:
    #         employee = eos.applicant_id
    #         if not employee:
    #             employee = self.env.user.employee_ids

    #         ''' Start Pending For '''
    #         pending_advances_for_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count([('employee_id','=',employee.id),('state','not in',['paid','cancel','reject'])])

    #         ''' End Pending For '''

    #         ''' Start Pending At '''
    #         pending_advances_at_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count([('action_to_be_taken_by','=',employee.id),('state','in',['applied','forward'])])

    #         eos.update({
    #             'advance_apply_pending_for_user':pending_advances_for_count,
    #             'advance_apply_pending_at_user':pending_advances_at_count
    #         })

    ''' Method for Check All EOS Checklist Completed OR Not '''

    @api.depends('applicant_id')
    def _compute_checklist_pendings(self):
        demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_eos.module_offboarding_mode_status')
        for eos in self:
            if demo_mode_enabled:
                eos.is_all_checklist_completed = True
                # if eos.kt_process_status in ["Completed",'Not Required'] and (eos.reg_process_status == "Termination Completed" or eos.reg_process_status == "Demise Completed" or eos.reg_process_status == "Contract Closure Completed" or eos.reg_process_status == "Retirement Completed" or eos.reg_process_status == "Resignation Completed") and  eos.tour_apply_pending_for_user == 0 and eos.tour_apply_pending_at_user==0 and eos.tour_cancellation_pending_for_user==0 and eos.tour_cancellation_pending_at_user==0:
                #     eos.is_all_checklist_completed = True
            else:
                if eos.kt_process_status in ["Completed", 'Not Required'] \
                        and eos.reg_process_status in ["Termination Completed", "Demise Completed",
                                                       "Contract Closure Completed", "Retirement Completed",
                                                       "Resignation Completed"] \
                        and eos.tour_apply_pending_for_user == 0 and eos.tour_apply_pending_at_user == 0 \
                        and eos.tour_cancellation_pending_for_user == 0 and eos.tour_cancellation_pending_at_user == 0 \
                        and eos.ra_details_status == "Completed" \
                        and eos.task_review_pending_status == "Completed" \
                        and eos.active_project_team_member_status == "Completed" \
                        and eos.assets_applied == 0 and eos.assets_pending == 0 \
                        and eos.leave_applied == 0 and eos.leave_pending == 0 \
                        and eos.leave_cancellation_applied == 0 and eos.leave_cancellation_pending == 0 \
                        and eos.salary_advance_applied == 0 and eos.salary_advance_pending == 0 \
                        and eos.card_applied == 0 and eos.card_pending == 0 \
                        and eos.opportunity_active_for_user == 0 and eos.opportunity_active_at_user == 0 \
                        and eos.lead_active_for_user == 0 and eos.lead_active_at_user == 0 \
                        and eos.workorder_active_for_user == 0 and eos.workorder_active_at_user == 0 :
                    eos.is_all_checklist_completed = True
            clearance_records = self.env['hr.employee.clearance'].sudo().search([('employee_id','=',eos.applicant_id.id)])
            # print("clearance_records===",clearance_records)
            if not clearance_records:
                # print("compute is true")
                eos.check_clearance_existance = True


    def update_clearance_record(self):
        """ insert new clearance record """
        offboard_rec = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', self.applicant_id.id), ('state', '=', 'grant')])
        clearance_obj = self.env['hr.employee.clearance']
        clearance_rec = clearance_obj.sudo().search([('employee_id','=',self.applicant_id.id)])
        if not clearance_rec:
            clearance_obj.sudo().create({'employee_id': self.applicant_id.id,
                                                                'resignation_id': offboard_rec.id,
                                                                'last_day_of_service': offboard_rec.last_working_date,
                                                                'hr_unit_date': offboard_rec.last_working_date,
                                                                'eos_id': self.id})
        else:
            raise ValidationError(f"""Clearance is already generated for {self.applicant_id.name}.""")
            
    # @api.depends('applicant_id')
    # def _compute_advance_pendings(self):
    #     for eos in self:
    #         employee = eos.applicant_id
    #         if not employee:
    #             employee = self.env.user.employee_ids

    #         ''' Start Pending For '''
    #         pending_advances_for_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count([('employee_id','=',employee.id),('state','not in',['paid','cancel','reject'])])

    #         ''' End Pending For '''

    #         ''' Start Pending At '''
    #         pending_advances_at_count = self.env['kw_advance_apply_salary_advance'].sudo().search_count([('action_to_be_taken_by','=',employee.id),('state','in',['applied','forward'])])

    #         eos.update({
    #             'advance_apply_pending_for_user':pending_advances_for_count,
    #             'advance_apply_pending_at_user':pending_advances_at_count
    #         })

    @api.depends('applicant_id')
    @api.multi
    def _compute_advance_claim(self):
        advance_checklist = self.env['ir.config_parameter'].sudo().get_param('kw_eos.advance_checklist')
        for eos in self:
            if not advance_checklist:
                eos.check_advance = True
            employee = eos.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos.petty_cash_applied = self.env['kw_advance_apply_petty_cash'].sudo().search_count(
                [('user_emp_id', '=', employee.id), ('state', '=', 'applied')])
            eos.petty_cash_pending = self.env['kw_advance_apply_petty_cash'].sudo().search_count(
                [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id),
                 ('state', 'in', ['applied', 'hold', 'forward'])])
            eos.claim_settlement_applied = self.env['kw_advance_claim_settlement'].sudo().search_count(
                [('empl_id', '=', employee.id), ('state', '=', 'applied')])
            eos.claim_settlement_pending = self.env['kw_advance_claim_settlement'].sudo().search_count(
                [('action_to_be_taken_by.user_id', '=', self.applicant_id.user_id.id),
                 ('state', 'in', ['applied', 'hold', 'forward'])])

    @api.depends('applicant_id')
    @api.multi
    def _compute_leave(self):
        for eos in self:
            employee = eos.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos.leave_applied = self.env['hr.leave'].sudo().search_count(
                [('employee_id', '=', employee.id), ('state', 'in', ['confirm', 'hold', 'forward'])])
            eos.leave_pending = self.env['hr.leave'].sudo().search_count(
                [('second_approver_id.user_id', '=', eos.applicant_id.user_id.id),
                 ('state', 'in', ['confirm', 'hold', 'forward'])])
            eos.leave_cancellation_applied = self.env['kw_cancel_leave'].sudo().search_count(
                [('approved_leave_emp_id', '=', employee.id), ('status', 'in', ['apply', 'forward'])])
            eos.leave_cancellation_pending = self.env['kw_cancel_leave'].sudo().search_count(
                [('approver_id.user_id', '=', eos.applicant_id.user_id.id),
                 ('status', 'not in', ['approve', 'reject'])])

    @api.depends('applicant_id')
    @api.multi
    def _compute_wfh_pendings(self):
        for eos in self:
            employee = eos.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos.wfh_request_pending_for_user = self.env['kw_wfh'].sudo().search_count(
                [('employee_id', '=', employee.id), ('state', '=', 'applied')])
            eos.wfh_request_pending_at_user = self.env['kw_wfh'].sudo().search_count(
                [('action_to_be_taken_by.user_id', '=', eos.applicant_id.user_id.id), ('state', '=', 'applied')])

    @api.depends('applicant_id')
    @api.multi
    def _compute_assesment_pendings(self):
        for eos in self:
            employee = eos.applicant_id
            if not employee:
                employee = self.env.user.employee_ids
            eos.assesment_pending_for_user = False
            eos.assesment_pending_at_user = False
            # eos.assesment_pending_for_user = self.env['kw_feedback_final_config'].sudo().search_count(
            #     [('assessee_id', '=', employee.id), ('feedback_status', '=', '1'),
            #      ('assessment_from_date', '>=', date.today()), ('assessment_to_date', '<=', date.today())])
            # eos.assesment_pending_at_user = self.env['kw_feedback_final_config'].sudo().search_count(
            #     [('assessor_id.user_id', '=', eos.applicant_id.user_id.id), ('feedback_status', '=', '1'),
            #      ('assessment_from_date', '>=', date.today()), ('assessment_to_date', '<=', date.today())])

    @api.depends('applicant_id')
    @api.multi
    def _compute_tour_pendings(self):
        user = self.env.user
        for eos in self:
            employee = eos.applicant_id
            tour_rec = self.env['kw_tour'].sudo().search([('employee_id', '=', employee.id), (
                'state', 'in', ['Applied', 'Approved', 'Forwarded', 'Traveldesk Approved', 'Finance Approved'])])
            un_settle_tours = tour_rec.filtered(lambda r: not set(r.settlement_ids.mapped('state')) & {'Payment Done'})
            if un_settle_tours:
                tour_settlement_details = "Not Clear"
            else:
                tour_settlement_details = 'Clear'
            pending_tours = self.env['kw_tour'].search_count([('employee_id', '=', employee.id), (
            'state', 'in', ['Applied', 'Approved', 'Forwarded', 'Traveldesk Approved'])])
            journey_incomplete_tours = self.env['kw_tour'].search_count(
                [('employee_id', '=', employee.id), ('state', '=', 'Finance Approved'),
                 ('date_return', '>=', date.today())])
            '''Start Pending At'''

            total_pending = 0
            pending_at_ra = self.env['kw_tour'].search_count(
                [('employee_id.parent_id', '=', employee.id), ('state', '=', 'Applied')])
            total_pending += pending_at_ra

            # if user.has_group('kw_tour.group_kw_tour_traveldesk'):
            #     pending_at_traveldesk = self.env['kw_tour'].search_count([('state','=','Approved')])
            #     total_pending += pending_at_traveldesk
            # if user.has_group('kw_tour.group_kw_tour_finance'):
            #     pending_at_finance = self.env['kw_tour'].search_count([('state','=','Approved')])
            #     total_pending += pending_at_finance

            pending_at_forwarded_user = self.env['kw_tour'].search_count(
                [('final_approver_id', '=', employee.id), ('state', '=', 'Forwarded')])
            total_pending += pending_at_forwarded_user
            ''' End Pending At'''

            """ Tour advance applied count """
            tour_advance_applied_count = self.env['kw_tour_advance_request'].search_count(
                [('employee_id', '=', employee.id), ('state', '=', 'Applied')])
            """ Tour advance pending count """
            tour_advance_pending_count = self.env['kw_tour_advance_request'].search_count(
                [('employee_id.parent_id', '=', employee.id), ('state', '=', 'Applied')])

            """ Tour settlement applied count """
            tour_settlement_applied_count = self.env['kw_tour_settlement'].search_count(
                [('employee_id', '=', employee.id), ('state', '=', 'Applied')])
            """ Tour settlement pending count """
            tour_settlement_pending_count = self.env['kw_tour_settlement'].search_count(
                [('employee_id.parent_id', '=', employee.id), ('state', '=', 'Applied')])

            cancellation_applied_count = self.env['kw_tour_cancellation'].search_count(
                [('tour_id.employee_id', '=', employee.id), ('state', '=', 'Applied')])

            cancellation_pending_count = self.env['kw_tour_cancellation'].search_count(
                [('tour_id.employee_id.parent_id', '=', employee.id), ('state', '=', 'Applied')])
            eos.update({
                'tour_apply_pending_for_user': pending_tours + journey_incomplete_tours,
                'tour_apply_pending_at_user': total_pending,
                'tour_cancellation_pending_for_user': cancellation_applied_count,
                'tour_cancellation_pending_at_user': cancellation_pending_count,
                'tour_settlement_details': tour_settlement_details,
                'tour_advance_pending_for_user': tour_advance_applied_count,
                'tour_advance_pending_at_user': tour_advance_pending_count,
                'toursettlement_pending_for_user': tour_settlement_applied_count,
                'tour_settlement_pending_at_user': tour_settlement_pending_count,
            })

    """EOS apply Reminder to User : Before 5 working days from Exit date"""

    def before_five_last_working_day(self):
        for rec in self:
            if datetime.now().date().day - rec.last_working_date.day == 5:
                one_day_before_last_day = rec.last_working_date - timedelta(days=1)
                template_obj = self.env.ref('kw_eos_integrations.reminder_mail_before_five_working_days')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    one_day_before_last_day=one_day_before_last_day).send_mail(
                    rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """EOS apply Reminder to User : Before 3 working days from Exit date"""

    def before_three_last_working_day(self):
        for rec in self:
            if datetime.now().date().day - rec.last_working_date.day == 3:
                one_day_before_last_day = rec.last_working_date - timedelta(days=1)
                template_obj = self.env.ref('kw_eos_integrations.reminder_mail_before_three_working_days')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    one_day_before_last_day=one_day_before_last_day).send_mail(
                    rec.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

    """EOS apply Reminder to User : Before 2 working days from Exit date"""

    def before_two_last_working_day(self):
        for rec in self:
            # if datetime.now().date().day - rec.last_working_date.day == 2:
            one_day_before_last_day = rec.last_working_date - timedelta(days=1)
            template_obj = self.env.ref('kw_eos_integrations.reminder_mail_before_two_working_days')
            mail = self.env['mail.template'].browse(template_obj.id).with_context(
                one_day_before_last_day=one_day_before_last_day).send_mail(rec.id,
                                                                           notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                           force_send=False)

    """EOS Remainder Cron"""

    @api.model
    def run_eos_remainder_mail(self):
        eos_rec = self.env['kw_eos_checklist'].search(
            [('last_working_date', '>=', datetime.now().date()), ('state', '=', 'Applied')])
        if eos_rec:
            for rec in eos_rec:
                rec.before_five_last_working_day()
                rec.before_three_last_working_day()
                rec.before_two_last_working_day()
