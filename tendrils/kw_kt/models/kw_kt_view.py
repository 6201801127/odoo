# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date, time
from odoo.exceptions import ValidationError
import pytz
import json, ast
from ast import literal_eval


class kw_kt_view(models.Model):
    _name = "kw_kt_view"
    _description = "KT Plan"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'applicant_id'
    _order = 'id desc'

    manual = fields.Boolean(string="Manual KT", default=True)
    applied_for = fields.Selection(string="Applied For", selection=[('self', 'Self'), ('others', 'Subordinates')],
                                   required=True, default='self', track_visibility='onchange')
    applicant_id = fields.Many2one('hr.employee', "Applicant's Name", required=True, track_visibility='onchange')
    kt_type_id = fields.Many2one('kw_kt_type_master', "Reason of KT", required=True, domain=[('is_manual', '=', True)],
                                 track_visibility='onchange')
    apply_date = fields.Date(string="KT Apply Date", default=fields.date.today(), track_visibility='onchange')
    effective_form = fields.Date(string='Notice Start Date', track_visibility='onchange')
    last_working_date = fields.Date(string='Notice End Date', track_visibility='onchange')

    action_by = fields.Char(string="Action To Be Taken By", compute='_compute_action_taken_by',
                            track_visibility='onchange')
    action_taken_by = fields.Char(string="Action Taken By", compute='_compute_action_taken_by',
                                  track_visibility='onchange')
    ra_check = fields.Boolean(string="RA Check", compute='_compute_action_taken_by')
    dept_head_check = fields.Boolean(string="Dept Head Check", compute='_compute_action_taken_by')

    state = fields.Selection(string="Status",
                             selection=[('Draft', 'Draft'), ('Applied', 'Applied'), ('Approved', 'Approved'),
                                        ('Rejected', 'Rejected'), ('Scheduled', 'Final Approval'),
                                        ('Completed', 'Granted')], default="Draft", track_visibility='onchange')

    applicant_dept_id = fields.Many2one('hr.department', related="applicant_id.department_id", string="Department",
                                        track_visibility='onchange')
    applicant_division = fields.Many2one('hr.department', related="applicant_id.division", string="Division",
                                         track_visibility='onchange')
    applicant_section = fields.Many2one('hr.department', related="applicant_id.section", string="Practice",
                                        track_visibility='onchange')
    applicant_practise = fields.Many2one('hr.department', related="applicant_id.practise", string="Section",
                                         track_visibility='onchange')
    time_line_plan_ids = fields.One2many('kw_time_line_plan', 'kt_view_id', string="Time line plan ids",
                                         track_visibility='onchange')
    kt_project_doc_ids = fields.One2many('kw_kt_project_doc', 'kt_view_doc_id', string="Additional Documents",
                                         track_visibility='onchange')
    remark = fields.Text(string='Remarks', track_visibility='onchange')
    dept_head_remark = fields.Text(string='Remarks', track_visibility='onchange')
    forward_remark = fields.Text(string='Remarks', track_visibility='onchange')
    comp_remark = fields.Text(string='Remarks', track_visibility='onchange')
    reject_remark = fields.Text(string='Remarks', track_visibility='onchange')

    # kt_cnfig_rec_check = fields.Boolean(string="Config record Check",compute="_compute_check_kt_config")

    forward_employee = fields.Many2one('hr.employee', string="Forward Employee Id", track_visibility='onchange')
    stored_forward_emp_id = fields.Many2one('hr.employee', string="Stored Forward Employee Id",
                                            track_visibility='onchange')

    forward_check = fields.Boolean(string="Forward Check", compute='_compute_action_taken_by')
    # show_button = fields.Boolean(string="Show Button", compute='_compute_show_button')

    back_state = fields.Char(string='Back State')
    timeline_rec_check = fields.Boolean(string="Time line record", compute='_compute_action_taken_by')

    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id, track_visibility='onchange')
    kt_end = fields.Char(string="KT END", compute="_kt_end")
    is_completed = fields.Boolean(string="Is completed", compute="_compute_is_completed")
    is_RA = fields.Boolean(compute='_get_current_user')
    project_str_ids = fields.Char("projects", compute="_compute_projects", track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange',
                                    compute="_compute_details")
    job_id = fields.Many2one('hr.job', string="Job Position", track_visibility='onchange', compute="_compute_details")
    division = fields.Many2one('hr.department', string="Division", compute="_compute_details",
                               track_visibility='onchange')
    section = fields.Many2one('hr.department', string="Practice", compute="_compute_details",
                              track_visibility='onchange')
    practise = fields.Many2one('hr.department', string="Section", compute="_compute_details",
                               track_visibility='onchange')

    """ To sort according to variable state """
    sort = fields.Integer(compute='_compute_sort', store=True)
    active = fields.Boolean(default=True)

    @api.multi
    @api.depends('state')
    def _compute_sort(self):
        sort_order = {
            'Applied': 1,
            'Approved': 2,
            'Scheduled': 3,
            'Completed': 4,
            'Rejected': 5,
            'Draft': 6,
        }
        for record in self:
            record.sort = sort_order.get(record.state)

    @api.depends('applicant_id')
    def _compute_details(self):
        for rec in self:
            employee = rec.applicant_id
            rec.job_id = employee.job_id.id
            rec.division = employee.division.id
            rec.section = employee.section.id
            rec.practise = employee.practise.id
            rec.department_id = employee.department_id.id

    @api.depends('time_line_plan_ids', 'time_line_plan_ids.project_id')
    @api.multi
    def _compute_projects(self):
        for kt in self:
            kt.project_str_ids = str(kt.mapped("time_line_plan_ids.project_id").ids)

    @api.depends('kt_type_id')
    def _get_current_user(self):
        for res in self:
            if self.env.user.has_group('kw_employee.group_hr_ra'):
                res.is_RA = True

    @api.multi
    def _compute_is_completed(self):
        for kt in self:
            kt_status = kt.time_line_plan_ids.mapped('status')
            kt.is_completed = all(element == 'completed' for element in kt_status)
            # print(kt.is_completed)
            # completed_status= kt.time_line_plan_ids.filtered(lambda r:r.status == max_date)
            # kt.is_completed = bool(kt.time_line_plan_ids.filtered(lambda r: r.status == 'completed'))

    @api.multi
    def _kt_end(self):
        user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        curr_datetime = datetime.now(tz=user_tz).replace(tzinfo=None)
        for kt in self:
            for rec in kt.time_line_plan_ids:
                max_date = max(kt.time_line_plan_ids.mapped('kt_date'))
                max_date_records = kt.time_line_plan_ids.filtered(lambda r: r.kt_date == max_date)
                max_date_time = max(max_date_records.mapped(lambda r: datetime.strptime(r.kt_date.strftime("%Y-%m-%d") + ' ' + r.end_time, "%Y-%m-%d %H:%M:%S")))
                if kt.state == 'Approved' and curr_datetime > max_date_time:
                    kt.kt_end = 'upload'

    @api.constrains('last_working_date', 'time_line_plan_ids')
    def validate_last_working_date(self):
        # print('method called')
        for kt in self:
            for rec in kt.time_line_plan_ids:
                max_date = max(kt.time_line_plan_ids.mapped('kt_date'))
                # print('max_date', max_date)
                if kt.last_working_date and max_date > kt.last_working_date:
                    raise ValidationError("Please schedule KT within notice period")

    @api.onchange('applied_for')
    def _get_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # print(emp_ids)
        if self.applied_for == "others":
            self.applicant_id = False
            return {'domain': {'applicant_id': ([('parent_id', 'in', emp_ids.ids)])}}
        else:
            self.applicant_id = emp_ids.id
            return {'domain': {'applicant_id': ([('id', 'in', emp_ids.ids)])}}

    @api.model
    def create(self, vals):
        rec = super(kw_kt_view, self).create(vals)
        kt_view_record = self.env['kw_kt_view'].sudo().search(
            [('applicant_id', '=', rec.applicant_id.id), ('state', 'not in', ['Completed', 'Rejected'])]) - rec
        if kt_view_record:
            raise ValidationError("Already a KT is in progress")
        return rec

    @api.multi
    def btn_re_apply(self):
        self.state = "Draft"
        self.env.user.notify_success("KT moved to draft successfully.")

    @api.multi
    def btn_apply(self):
        self.state = "Applied"
        if not self.time_line_plan_ids:
            raise ValidationError("Please schedule KT plan")
        """ getting kt data """
        kt_data = self.get_kt_data()
        template_id = self.env.ref('kw_kt.kw_kt_apply_mail_ra_template')
        template_id.with_context(
            applicant_name=self.applicant_id.name,
            emp_code=self.applicant_id.emp_code,
            parent_id=self.applicant_id.parent_id.name,
            department_id=self.applicant_id.department_id.name,
            division=self.applicant_id.division.name,
            section=self.applicant_id.section.name,
            practise=self.applicant_id.practise.name,
            job_id=self.applicant_id.job_branch_id.name,
            parent_email=self.applicant_id.parent_id.work_email,
            applicant_email=self.applicant_id.work_email,
            kt_data=kt_data,
        ).send_mail(self.time_line_plan_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")
        action_id = self.env.ref('kw_kt.kt_view_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }
        # view_id = self.env.ref('kw_kt.kw_kt_view_tree').id
        # form_view_id = self.env.ref('kw_kt.kw_kt_view_form').id
        # return {
        #             'name'      : 'KT Application',
        #             'view_type' : 'form',
        #             'view_mode' : 'tree,form',
        #             'view_id'   : False,
        #             'res_model' : 'kw_kt_view',
        #             'type'      : 'ir.actions.act_window',
        #             'target'    : 'main',
        #             'views': [(view_id, 'tree'),(form_view_id,'form')],
        #         }

    @api.multi
    def _compute_action_taken_by(self):
        for record in self:
            timeline_record = self.env['kw_time_line_plan'].sudo().search([('kt_view_id', '=', record.id)])
            if timeline_record:
                record.timeline_rec_check = True
            if record.state == 'Applied':
                record.action_by = record.applicant_id.parent_id.name or False
                if self.env.user.employee_ids == record.applicant_id.parent_id:
                    record.ra_check = True
            elif record.state == 'Approved':
                record.action_taken_by = record.applicant_id.parent_id.name or False
                record.action_by = "--"
                if self.env.user.employee_ids == record.applicant_id.department_id.manager_id:
                    record.dept_head_check = True
            elif record.state == 'Completed':
                record.action_taken_by = record.applicant_id.parent_id.name or False
                record.action_by = "--"
            if record.state == 'Scheduled':
                record.action_by = record.applicant_id.parent_id.name or False
                if self.env.user.employee_ids == record.applicant_id.parent_id:
                    record.ra_check = True

    @api.multi
    def btn_comp(self):
        self.state = "Scheduled"
        """ getting kt data """
        kt_data = self.get_kt_data()
        """ Get notify cc from general settings """
        cc = self.get_kt_cc()
        template_id = self.env.ref('kw_kt.kw_kt_to_complete_mail_template')
        template_id.with_context(cc=cc,
                                 applicant_name=self.applicant_id.name,
                                 emp_code=self.applicant_id.emp_code,
                                 parent_id=self.applicant_id.parent_id.name,
                                 department_id=self.applicant_id.department_id.name,
                                 division=self.applicant_id.division.name,
                                 section=self.applicant_id.section.name,
                                 practise=self.applicant_id.practise.name,
                                 job_id=self.applicant_id.job_branch_id.name,
                                 parent_email=self.applicant_id.parent_id.work_email,
                                 applicant_email=self.applicant_id.work_email,
                                 kt_data=kt_data,
                                 ).send_mail(self.time_line_plan_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")
        action_id = self.env.ref('kw_kt.kt_view_action').id
        form_view_id = self.env.ref("kw_kt.kw_complete_kt_pop_up_form").id
        return {
            'name': 'Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'view_id': form_view_id,
            'res_id': self.id,
            'domain': [('id', '=', self.id)]
        }

    def get_kt_cc(self):
        email_list = []
        param = self.env['ir.config_parameter'].sudo()
        notify_group = param.get_param('kw_kt.notify_kt_cc')
        if notify_group:
            empls = self.env['hr.employee'].search([('job_id', 'in', notify_group)])
            email_list.append(empls.filtered(lambda r: r.work_email).mapped('work_email'))
        email_list.append(self.applicant_id.department_id.manager_id.work_email)
        email = set(email_list)
        cc = email and ",".join(email) or ''
        return cc

    def get_kt_data(self):
        kt_data = {}
        for rec in self.time_line_plan_ids:
            attendees = ''
            for employee in rec.employee_ids:
                attendees += str(employee.name) + ','
            data = {
                'kt_activies': rec.activities if rec.activities else '',
                'kt_project_id': rec.project_id.name if rec.project_id.name else '',
                'kt_description': rec.description,
                'kt_attendies': attendees,
                'kt_date': rec.kt_date.strftime("%d-%b-%Y"),
                'kt_start_time': rec.start_time if rec.start_time else '',
                'kt_end_time': rec.end_time if rec.end_time else '',
            }
            if rec.kt_type == 'project':
                data['kt_type'] = 'Current Project'
            elif rec.kt_type == 'other_project':
                data['kt_type'] = 'Other Project'
            else:
                data['kt_type'] = 'Administrative Activities'
            kt_data[rec.id] = data
        return kt_data

    def btn_complete_kt(self):
        action_id = self.env.ref('kw_kt.kt_view_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }

    @api.multi
    def btn_comp_conform(self):
        self.state = "Scheduled"
        template_id = self.env.ref('kw_kt.kw_kt_to_complete_mail_template')
        template_id.send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")
        action_id = self.env.ref('kw_kt.kt_view_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }

    @api.multi
    def btn_complete_take_action(self):
        view_id = self.env.ref('kw_kt.kw_new_plan_request_form').id
        target_id = self.id
        return {
            'name': 'View Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'self',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            # 'flags': {'action_buttons': True},
        }

    @api.multi
    def btn_take_action(self):
        view_id = self.env.ref('kw_kt.kw_new_plan_request_form').id
        target_id = self.id
        return {
            'name': 'View Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'self',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            # 'flags': {'action_buttons': True},
        }

    """ ======= Ra Approve Method ======== """

    @api.multi
    def action_remark_approve(self):
        self.state = "Approved"
        # self.time_line_plan_ids.kt_status = 'Approved'
        # if  self.time_line_plan_ids.kt_status == 'Approved':
        #     print('kt status')
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        # for rec in self.time_line_plan_ids:
        #     for kt_rec in rec.employee_ids:
        #         template_id = self.env.ref('kw_kt.kw_kt_ra_approved_mail_template')
        #         template_id.with_context(mailto=kt_rec.work_email,
        #         mailcc=kt_rec.parent_id.work_email,
        #         emp_name=kt_rec.name,
        #         project=rec.project_id.name,
        #         date=rec.kt_date,
        #         start=rec.start_time,
        #         end=rec.end_time).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')

        """ getting kt data """
        kt_data = self.get_kt_data()
        """ Get notify cc from general settings """
        cc = self.get_kt_cc()

        template_id = self.env.ref('kw_kt.kw_kt_ra_approve_mail_template')
        template_id.with_context(ra_email=self.applicant_id.parent_id.work_email,
                                 ra_name=self.applicant_id.parent_id.name,
                                 applicant_name=self.applicant_id.name,
                                 applicant_code=self.applicant_id.emp_code,
                                 applicant_email=self.applicant_id.work_email,
                                 remark=self.remark,
                                 cc=cc,
                                 kt_data=kt_data).send_mail(self.time_line_plan_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")

        action_id = self.env.ref('kw_kt.kt_new_plan_request_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }

    """ ===== Return Remark Form Clicking On Approve Button ======= """

    @api.multi
    def btn_approve(self):
        if self.time_line_plan_ids:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_kt_view',
                'name': "Remarks",
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'res_id': self.id,
                'view_id': self.env.ref('kw_kt.view_kw_ra_approve_remark_form').id
            }
            return action
        else:
            raise ValidationError("Please add KT details.")

    @api.multi
    def action_remark_reject(self):
        self.state = "Rejected"
        """ getting kt data """
        kt_data = self.get_kt_data()
        template_id = self.env.ref('kw_kt.kw_kt_reject_mail_template')
        template_id.with_context(ra_email=self.applicant_id.parent_id.work_email,
                                 emp_code=self.applicant_id.emp_code,
                                 ra_name=self.applicant_id.parent_id.name,
                                 applicant_name=self.applicant_id.name,
                                 applicant_email=self.applicant_id.work_email,
                                 kt_data=kt_data,
                                 remark=self.reject_remark, ).send_mail(self.time_line_plan_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")

        action_id = self.env.ref('kw_kt.kt_new_plan_request_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }

    @api.multi
    def btn_reject(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'name': "Reject Remarks",
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id': self.id,
            'view_id': self.env.ref('kw_kt.view_kw_reject_remark_form').id
        }
        return action

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('kt_report'):
            if self.env.user.has_group('kw_kt.group_kt_manager'):
                # print('manager found')
                args += [('state', '!=', 'Draft')]
            else:
                # print('else found')
                args += ['|', '|', ('applicant_id.user_id', '=', self.env.uid),
                         ('applicant_id.parent_id.user_id', '=', self.env.uid),
                         ('applicant_id.department_id.manager_id.user_id', '=', self.env.uid)]
        return super(kw_kt_view, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    @api.multi
    def btn_hold(self):
        self.state = "Hold"
        template_id = self.env.ref('kw_kt.kw_kt_hold_mail_template')
        template_id.send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")

    @api.multi
    def btn_unhold(self):
        self.state = "Unhold"

    @api.multi
    def btn_cancel(self):
        self.state = "Cancelled"

    @api.multi
    def btn_take_action(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'self',
            'res_id': self.id,
            # 'context': { 'default_applicant_id': self.applicant_id.id},
            'flags': {'mode': 'edit', "toolbar": False}
        }
        if self.state == 'Applied':
            if self.env.user.employee_ids == self.applicant_id.parent_id:
                action['view_id'] = self.env.ref('kw_kt.kw_new_plan_request_form').id
        if self.state == 'Approved':
            if self.env.user.employee_ids == self.applicant_id.department_id.manager_id:
                action['view_id'] = self.env.ref('kw_kt.kw_dept_head_new_plan_request_form').id
        return action

    @api.multi
    def btn_complete(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_kt_view',
            'name': "Remarks",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('kw_kt.view_kw_to_comp_remark_form').id,
            'target': 'new',
            'res_id': self.id,
        }
        return action

    @api.multi
    def btn_comp_remark_submit(self):
        self.state = "Completed"
        """ getting kt data """
        kt_data = self.get_kt_data()

        template_id = self.env.ref('kw_kt.kw_kt_complete_mail_template')
        """HRD users"""
        cc = self.get_kt_cc()

        template_id.with_context(cc=cc,
                                 applicant_name=self.applicant_id.name,
                                 applicant_code=self.applicant_id.emp_code,
                                 parent_id=self.applicant_id.parent_id.name,
                                 parent_email=self.applicant_id.parent_id.work_email,
                                 applicant_email=self.applicant_id.work_email,
                                 comp_remark=self.comp_remark,
                                 kt_data=kt_data,
                                 ).send_mail(self.time_line_plan_ids.ids[0], notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Mail sent successfully.")
        action_id = self.env.ref('kw_kt.kt_new_plan_request_action').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_kt_view&view_type=list',
            'target': 'self',
        }
