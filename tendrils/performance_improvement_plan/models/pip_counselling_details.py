import pytz
import math
from datetime import datetime, date, timedelta
from werkzeug import urls
import base64
from odoo import models, fields, api,_, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.kw_utility_tools import kw_validations


class kw_feedback_details(models.Model):
    _name = 'kw_pip_counselling_details'
    _description = 'Performance Improvement Plan Process'
    _rec_name = 'assessee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def get_employee_data(self):
        domain = []
        data = self.env['pip_hr_employee_counselling'].sudo().search([('remark', '=', 'RP')])
        used_assessee_ids = self.env['kw_pip_counselling_details'].search([]).mapped('assessee_id.id')

        emp_ids = [rec.emp_id.id for rec in data]

        if used_assessee_ids:
            available_emp_ids = list(set(emp_ids) - set(used_assessee_ids))
            domain = [('id', 'in', available_emp_ids)]
        else:
            domain = [('id', 'in', emp_ids)]

        return domain

    reference = fields.Char(string="Reference No")
    pip_ref_id = fields.Many2one("performance_improvement_plan", string="PIP ref No")
    assessor_id = fields.Many2one('hr.employee', string='Assessor', domain="[('id','!=',assessee_id)]",
                                  track_visibility='always')
    assign_assessors_ids = fields.Many2many('hr.employee', 'pip_emp_rel', 'pip_con_id', 'emp_id',
                                            string="Assigned Assessors",
                                            domain="[('id','!=',assessee_id), ('employement_type.code', '!=', 'O')]",
                                            track_visibility='always')
    assessee_id = fields.Many2one('hr.employee', string='Assessee', domain=get_employee_data, required=True)
    raised_by = fields.Many2one('hr.employee', compute="_get_raised_by_employee", store=True)
    ra_id = fields.Many2one('hr.employee', string="Reporting Authority", related="assessee_id.parent_id",
                            track_visibility='always')
    assessee_job_id = fields.Many2one('hr.job', string="Designation", related="assessee_id.job_id",
                                      track_visibility='always')
    department = fields.Char(string="Department", compute="compute_department", track_visibility='always')
    image_small = fields.Binary(related='assessee_id.image', store=False)
    # counselling_id = fields.Many2one('counselling_configuration', ondelete='restrict')
    assessment_date = fields.Date(string='Counselling Date', autocomplete="off", track_visibility='always')

    feedback_status = fields.Selection(string='Status',
                                       selection=[('0', 'Not Schedule'), ('1', 'Counselling Scheduled'), ('2', 'Feedback received'),
                                                  ('3', 'Under Observation'), ('4', 'Second Counselling'),
                                                  ('5', 'Observation Complete'),('7','Training Feedback Received'),
                                                  ('6', 'PIP Closed')], default='0', track_visibility='onchange')

    meeting_id = fields.Many2one(comodel_name='kw_meeting_events', string='Meeting Name', track_visibility='always')
    meeting_date = fields.Date(related='meeting_id.kw_start_meeting_date', store=True)
    meeting_time = fields.Selection(related='meeting_id.kw_start_meeting_time')
    meeting_duration = fields.Selection(related='meeting_id.kw_duration')
    meeting_room = fields.Many2one(comodel_name='kw_meeting_room_master', related='meeting_id.meeting_room_id')

    keep_observation = fields.Selection(string="To Keep Under Observation", selection=[('Yes', 'Yes'), ('No', 'No')],
                                        track_visibility='onchange')
    observation_remarks = fields.Char(string="Remarks", track_visibility='always', size=1000)
    observation_duration = fields.Selection(string="Observation Duration",
                                            selection=[('7', '7 Days'), ('15', '15 Days'), ('30', '30 Days'),
                                                       ('45', '45 Days'), ('60', '60 Days')], track_visibility='onchange')
    release_duration = fields.Integer(string=" Notice period to release(days)")

    timeline_improvement = fields.Selection(string="Timeline for Performance Improvement Plan",
                                            selection=[('7', '7 Days'), ('15', '15 Days'), ('30', '30 Days'),
                                                       ('45', '45 Days'), ('60', '60 Days')], track_visibility='onchange')
    next_counselling = fields.Date(string="Next Counselling", compute="get_next_counselling", store=True,
                                   track_visibility='always')
    remarks_hr = fields.Text(string="Overall Comments", track_visibility='always')
    training_final_feedback = fields.Text(string="Training Final Feedback") 
    final_decision = fields.Selection(string="Final Closed Decision",
                                      selection=[('Meet Expectations', 'Meet Expectations'),
                                                 ('Doesn’t meet expectation', 'Doesn’t meet expectation')],
                                      track_visibility='onchange')
    hr_feedback_details_ids = fields.One2many('kw_feedback_config_details', 'pip_counselling_id', string="HR Feedback",
                                              track_visibility='always')
    hr_assessor_details_ids = fields.One2many('kw_feedback_config_details', 'pip_assessor_counselling_id',
                                              string="Assessors Feedback", track_visibility='always')
    hr_improvement_details_ids = fields.One2many('kw_feedback_config_details', 'pip_improve_counselling_id',
                                                 string="Improve Feedback", track_visibility='always')
    feedback_given_hide_btn = fields.Boolean(string="Given Button", compute="get_hide_feedback_btn")
    improve_btn_hide = fields.Boolean(string="improve hide")
    hide_hr_feedback = fields.Boolean(string="feedback hide", compute="get_hide_feedback_btn")
    reason_for_counselling = fields.Char(string="Reason", size=1000)
    meeting_log_id = fields.One2many('counselling_configuration_log', 'config_details_id', string="Meeting Details",
                                     track_visibility='always')
    in_observe = fields.Boolean(string="In observe")
    in_duration = fields.Boolean()
    user_agree_observation = fields.Selection(string="Agreed/Not Agreed",
                                              selection=[('Agree', 'Agreed'), ('Disagree', 'Not Agreed')])

    assessor_feedback_bool = fields.Boolean(string="Feedback", default=False, compute="_get_feedback_assessor")
    assessor_improvement_feedback_bool = fields.Boolean(string="Improvement Feedback", default=False,
                                                        compute="_get_improvement_feedback_assessor")
    pip_close_date = fields.Date(string="Closed Date")
    hr_final_decision = fields.Selection(string="Final Decision", selection=[('Employment_closed', 'Employment to be closed '), ('Continued', 'Continued')],
                                        track_visibility='onchange')
    closed_remarks_hr = fields.Text(string="Remark", track_visibility='always')
    documents = fields.Binary(string=u'Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    final_assessor_feedback = fields.One2many('kw_feedback_config_details', 'pip_final_assessor_feedback_id',
                                              string="Assessors Final Feedback", track_visibility='always')
    training_create_bool = fields.Boolean(string="Training Check")
    
    training_completion_expected_date = fields.Date(string="Training Completion Expected Date")

    training_completion_actual_date = fields.Date(string="Training Completion Actual Date")
    # accessor_feed_bool = fields.Boolean(string="feedback accessor",compute="get_hide_feedback_btn",default=False,store=False)

    @api.constrains('hr_feedback_details_ids')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf', 'application/zip',
                             'application/msword', 'application/vnd.ms-excel',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        max_file_size_mb = 2.0 
        if self.hr_feedback_details_ids:
            for docs in self.hr_feedback_details_ids:
                if docs.deliverables_uplod_doc: 
                    mimetype = guess_mimetype(base64.b64decode(docs.deliverables_uplod_doc))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError(_("Unsupported file format! Allowed file formats are .docs, .xls, .zip, .pptx and .pdf."))
                    elif ((len(docs.deliverables_uplod_doc) * 3 / 4) / 1024) / 1024 > max_file_size_mb:
                        raise ValidationError(_("Maximum file size should be less than {} MB.".format(max_file_size_mb)))
                    kw_validations.validate_file_mimetype(docs.deliverables_uplod_doc, allowed_file_list)
                    kw_validations.validate_file_size(docs.deliverables_uplod_doc, 2)
                else:
                    pass

    @api.multi
    @api.depends('assessor_id')
    def _get_feedback_assessor(self):
        for rec in self:
            feedback_rec = self.env['kw_pip_counselling_details'].sudo().search(
                [('hr_assessor_details_ids.assessor_id', '=', self.env.user.employee_ids.id), ('id', '=', rec.id)])
            if feedback_rec:
                rec.assessor_feedback_bool = True
            else:
                rec.assessor_feedback_bool = False

    def _get_improvement_feedback_assessor(self):
        for rec in self:
            pip_improve_rec = self.env['kw_pip_counselling_details'].sudo().search(
                [('hr_improvement_details_ids.assessor_id', '=', self.env.user.employee_ids.id), ('id', '=', rec.id)])
            if pip_improve_rec:
                rec.assessor_improvement_feedback_bool = True
            else:
                rec.assessor_improvement_feedback_bool = False
        # for rec in self:
        #     domain = [
        #         ('hr_improvement_details_ids.assessor_id', '=', self.env.user.employee_ids.id),
        #         ('id', '=', rec.id),
        #     ]
        #     pip_improve_rec = self.env['kw_pip_counselling_details'].sudo().search(domain)
        #     rec.assessor_improvement_feedback_bool = bool(pip_improve_rec)

    # @api.model
    # def create(self,vals):
    #     record = super(kw_feedback_details, self).create(vals)
    #     ref_id = self.env.ref('performance_improvement_plan.group_pip_assessor_user').id
    #     data = self.env['res.groups'].sudo().search([('id', '=', ref_id)])
    #     for rec in record.assessor_id:
    #         data.users = [(4, rec.user_id.id)]

    #     return record

    @api.onchange('assessee_id')
    def onchange_employee_id(self):
        data = self.env['pip_hr_employee_counselling'].sudo().search([('remark', '=', 'RP')])
        emp_ids = [rec.emp_id.id for rec in data]
        selected_employees = self.env['kw_pip_counselling_details'].search([]).mapped('assessee_id.id')
        if not self._context.get('current_emp'):
            return {
                'domain': {
                    'assessee_id': [('id', 'not in', selected_employees), ('id', 'in', emp_ids)]
                }
            }
        else:
            return {
                'domain': {
                    'assessee_id': [('id', '=', self._context.get('current_emp'))]
                }
            }

    def _get_raised_by_employee(self):
        if self.assessee_id:
            pip_data = self.env["pip_hr_employee_counselling"].search([('emp_id', '=', self.assessee_id.id)])
            self.raised_by = pip_data.raise_by_emp.id

    @api.multi
    def manage_meeting_counselling(self):
        self.ensure_one()
        participants = []
        if self.assign_assessors_ids:
            participants = self.assign_assessors_ids.ids

        participants += self.assessee_id.ids
        participants += self.env.user.employee_ids.ids

        ref_id = self.env.ref('performance_improvement_plan.group_pip_assessor_user')
        for rec in self.assign_assessors_ids:
            ref_id.sudo().write({'users': [(4, rec.user_id.id)]})

        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        counselling_tag = self.env.ref('kw_meeting_schedule.meeting_type_29')

        context = {
            'create': False,
            'default_kw_start_meeting_date': self.assessment_date,
            'default_name': "Counselling",
            'default_email_subject_line': "Counselling Schedule",
            'default_employee_ids': [(6, 0, participants)],
            'default_meeting_category': 'general',
            'default_agenda_ids': [[0, 0, {'name': self.reason_for_counselling}]],
            'default_meeting_type_id': counselling_tag.id,
            'default_categ_ids': [(6, 0, counselling_tag.ids)],
            'default_location_id': self.env.user.branch_id.id,
        }

        _action = {
            'name': 'Counselling Meeting Schedule',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'flags': {'action_buttons': True, 'mode': 'edit', 'toolbar': False, },
        }
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        dt = datetime.now(timezone)
        _action['context'] = context
        return _action

    @api.depends('assessee_id')
    @api.multi
    def get_hide_feedback_btn(self):
        for rec in self:
            record = self.env['kw_feedback_config_details'].sudo().search(
                [('pip_assessor_counselling_id', '=', rec.id)])
            if len(record) == 1 and rec.feedback_status == '1':
                rec.write({'feedback_status': '3',
                           'feedback_given_hide_btn': True})
            # for feedback in record:
            # if all('No' in rec.hr_assessor_details_ids.mapped('keep_observation')):
            # if rec.hr_assessor_details_ids:
            #     if all(['No' in obs for obs in rec.hr_assessor_details_ids.mapped('keep_observation')]):
            #          rec.write({'feedback_status': '2',
            #                'hide_hr_feedback': True})
            # if 'No' not in rec.hr_assessor_details_ids.mapped('keep_observation'):
            #         rec.accessor_feed_bool = True
            # record_improve = self.env['kw_feedback_config_details'].sudo().search(
            #     [('pip_improve_counselling_id', '=', rec.id)])
            # if len(record_improve) == len(rec.assign_assessors_ids) and rec.feedback_status == '4':
            #     rec.write({'feedback_status': '5'})

    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r: r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments

    @api.multi
    def compute_department(self):
        for rec in self:
            if rec.assessee_id.department_id:
                department = self.get_root_departments(rec.assessee_id.department_id)
                if department:
                    rec.department = department.name

    @api.model
    def get_cc_emails(self):
        values = ','.join(str(user_email.work_email) for user_email in self.assign_assessors_ids)
        values += ',' + self.counselling_id.create_uid.email
        return values

    @api.multi
    def btn_hr_confirm(self):
        for rec in self:
            # if not rec.timeline_improvement and not rec.next_counselling and not rec.remarks_hr and 'No' not in rec.hr_assessor_details_ids.mapped('keep_observation'):
            #     raise ValidationError("Warning! Please give the Timeline,Next counselling and Comments.")
            if not rec.hr_feedback_details_ids:
                if 'No' in rec.hr_assessor_details_ids.mapped('keep_observation') and rec.final_decision is False:
                    raise ValidationError("Warning! Please select final decision.")
                # for data in rec.hr_assessor_details_ids:
                #     if data.keep_observation == 'Yes':
                #         raise ValidationError("Warning! Enter at least One Deliverable and Achievement.")
                #     else:
                #         pass
            # else:
            #     if rec.hr_assessor_details_ids:
            #         if len(rec.hr_assessor_details_ids) == 0:
            #             raise ValidationError("Assessors not yet given feedback")
            #     else:
            #         raise ValidationError("Assessors not yet given feedback")
            # parent_feedback_status = '6'
            # feedb = rec.hr_assessor_details_ids.mapped('keep_observation')
            # if rec.feedback_status == '2' and any(['Yes' in obs for obs in feedb]) :
            #     parent_feedback_status = '3'
            # for feedback in rec.hr_assessor_details_ids:
            #     if feedback.keep_observation == 'Yes' and rec.feedback_status == '2':
            #         # print(feedback.keep_observation)
            #         parent_feedback_status = '3'
            rec.write({'feedback_status': '6'})
            rec.pip_ref_id.write({'status': 'Closed'})

            template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')
            # if rec.feedback_status == '3':
            #     rec.in_observe = True
            #     mail_cc = []
            #     mail_to = self.assessee_id.work_email
            #     if self.assessee_id.parent_id and self.assessee_id.parent_id.work_email:
            #         mail_cc.append(self.assessee_id.parent_id.work_email)
            #     if self.raised_by.work_email:
            #         mail_cc.append(self.raised_by.work_email)
            #     if self.assessee_id.department_id.manager_id.work_email:
            #         mail_cc.append(self.assessee_id.department_id.manager_id.work_email)
            #     hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
            #     pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
            #     hr_notify_emp = []
            #     hr_notify_emp.extend(pip_notify_emp.ids)
            #     hr_notify_emp.extend(hr_user.ids)
            #     manager_emp_hr = self.env['hr.employee'].sudo().search([('id','in', hr_notify_emp),('active','=',True)])
            #     cc_mail = ','.join(set(mail_cc)) + ',' + ','.join(manager_emp_hr.mapped('work_email'))
            #     if template_obj:
            #         template_obj.with_context(
            #             subject=f"PIP Process | {self.assessee_id.display_name} | Your Deliverables ",
            #             mail_for='Observation',
            #             email_to=mail_to,
            #             mail_cc=cc_mail,
            #             email_from=self.env.user.employee_ids.work_email,
            #             period_observ=self.timeline_improvement,
            #             name=self.assessee_id.name
            #         ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            # elif rec.feedback_status == '6':
            mail_cc = []
            mail_to = self.assessee_id.work_email
            if self.assessee_id.parent_id and self.assessee_id.parent_id.work_email:
                mail_cc.append(self.assessee_id.parent_id.work_email)
            if self.raised_by.work_email:
                mail_cc.append(self.raised_by.work_email)
            if self.assessee_id.department_id.manager_id.work_email:
                mail_cc.append(self.assessee_id.department_id.manager_id.work_email)
            mail_cc.extend(self.assign_assessors_ids.mapped('work_email'))
            hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
            pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
            hr_notify_emp = []
            hr_notify_emp.extend(pip_notify_emp.ids)
            hr_notify_emp.extend(hr_user.ids)
            manager_emp_hr = self.env['hr.employee'].sudo().search(
                [('id', 'in', hr_notify_emp), ('active', '=', True)])
            cc_mail = ','.join(set(mail_cc)) + ',' + ','.join(manager_emp_hr.mapped('work_email'))
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.assessee_id.display_name} | Outcome",
                    mail_for='Observation_no',
                    email_to=mail_to,
                    mail_cc=cc_mail,
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.assessee_id.name
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def closed_pip_hr_action(self):       
        view_id = self.env.ref("performance_improvement_plan.remarks_approver_final_close_view_pip_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Closed',
            'res_model': 'kw_pip_remark_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            }
    @api.multi
    def btn_hr_closed_stage(self):
        view_id = self.env.ref("performance_improvement_plan.pip_counselling_close_take_action").id
        action = {
            'name': 'Closed',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_pip_remark_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'pip_details_id':self.id}
        }
        return action

    def assessor_give_feedback(self):
        feedback_rec = self.env['kw_pip_counselling_details'].sudo().search(
            [('id', '=', self._context.get('default_active_rec')),
             ('hr_assessor_details_ids.assessor_id', '=', self.env.user.employee_ids.id)])
        if not feedback_rec:
            start_time_str = self.meeting_time
            start_time = datetime.strptime(start_time_str, '%H:%M:%S')
            meeting_duration = float(self.meeting_duration)
            hours = int(meeting_duration)
            minutes = int((meeting_duration - hours) * 60)
            duration = timedelta(hours=hours, minutes=minutes)
            end_time = start_time + duration
            current_datetime = datetime.now() + timedelta(hours=5, minutes=30)
            # if current_datetime.time() > end_time.time() and (
            #         self.assessment_date == date.today() or self.assessment_date < date.today()):
            demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mode_status')

            if (current_datetime.date() > self.assessment_date
                    or (current_datetime.date() == self.assessment_date and current_datetime.time() >= end_time.time())
                    or demo_mode_enabled):
                form_view_id = self.env.ref("performance_improvement_plan.assessor_counselling_feedback_view_pip_form").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Feedback',
                    'res_model': 'kw_pip_remark_wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': form_view_id,
                    'target': 'new',
                }

            else:
                raise ValidationError("Meeting is not yet concluded.")
        else:
            raise ValidationError("Already given Feedback")
        
    def assessor_add_extra_deliverables(self):
        form_view_id = self.env.ref("performance_improvement_plan.hr_add_deliverables_view_form").id
        return {
                'type': 'ir.actions.act_window',
                'name': 'Add Deliverables',
                'res_model': 'kw_pip_remark_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
                'context': {'type':'add_deliverables','default_feedback_ids': [(0, 0, {
                        'deliverable_rec': rec.deliverable_rec,
                        'excepted_achivement_rec': rec.excepted_achivement_rec,
                    }) for rec in self.hr_feedback_details_ids]
                }
            }

    def assessor_improvement_give_feedback(self):
        pip_improve_rec = self.env['kw_pip_counselling_details'].sudo().search(
            [('hr_improvement_details_ids.assessor_id', '=', self.env.user.employee_ids.id),
             ('id', "=", self._context.get('default_active_rec'))])
        start_time_str = self.meeting_time
        start_time = datetime.strptime(start_time_str, '%H:%M:%S')
        meeting_duration = float(self.meeting_duration)
        hours = int(meeting_duration)
        minutes = int((meeting_duration - hours) * 60)
        duration = timedelta(hours=hours, minutes=minutes)
        end_time = start_time + duration
        current_datetime = datetime.now() + timedelta(hours=5, minutes=30)
        form_view_id = self.env.ref("performance_improvement_plan.assessor_improvement_feedback_view_pip_form").id
        demo_mode_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.module_onboarding_mode_status')

        if not pip_improve_rec:
            if (current_datetime.date() > self.assessment_date
                    or (current_datetime.date() == self.assessment_date and current_datetime.time() >= end_time.time())
                    or demo_mode_enabled):
                if self.hr_feedback_details_ids.exists():
                    feedback_data = []
                    for rec in self.hr_feedback_details_ids:
                        feedback_data.append([0, 0, {
                            'pip_assessor_counselling_id': rec.id,
                            'deliverable_rec': rec.deliverable_rec,
                            'excepted_achivement_rec': rec.excepted_achivement_rec,
                        }])
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Final Feedback',
                        'res_model': 'kw_pip_remark_wizard',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'view_id': form_view_id,
                        'target': 'new',
                        'context': {'default_feedback_ids': feedback_data}
                    }
                else:
                    pass
                # 'context' : {'default_hr_delive_achi_feedbacks':feedback_data.hr_feedback_details_ids.ids,'create':False},
            else:
                raise ValidationError("Meeting is not yet concluded.")
        else:
            raise ValidationError("You have already given Feedback.")

    def hr_give_feedback(self):
        form_view_id = self.env.ref("performance_improvement_plan.view_hr_counselling_update_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Feedback',
            'res_model': 'kw_pip_remark_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    @api.onchange('timeline_improvement')
    def get_next_counselling(self):
        if self.timeline_improvement:
            duration_in_days = int(self.timeline_improvement)
            current_date = fields.Date.context_today(self)  # Use context_today to get today's date
            next_counselling_date = current_date + timedelta(days=duration_in_days)
            self.next_counselling = next_counselling_date
        else:
            self.next_counselling = False

    # def agree_observation(self):
    #     self.user_agree_observation = 'Agree'
    #     template = self.env.ref("performance_improvement_plan.email_template_confirm_pip")
    #     pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
    #     hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
    #     manager_emp_notify_user = self.env['hr.employee'].sudo().search(
    #         [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
    #     manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
    #     mail_cc = []
    #     if self.env.user.employee_ids.parent_id and self.env.user.employee_ids.parent_id.work_email:
    #         mail_cc.append(self.env.user.employee_ids.parent_id.work_email)

    #     if self.raised_by.work_email:
    #         mail_cc.append(self.raised_by.work_email)

    #     if self.env.user.employee_ids.department_id.manager_id.work_email:
    #         mail_cc.append(self.env.user.employee_ids.department_id.manager_id.work_email)
    #     mail_cc.extend(manager_emp_notify_user.mapped('work_email'))

    #     cc_mail = ','.join(set(mail_cc))
    #     if template:
    #         template.with_context(
    #             subject=f"PIP Process | {self.assessee_id.display_name} | Agreed Deliverables ",
    #             mail_for='Agree',
    #             email_to=','.join(manager_emp_hr.mapped('work_email')),
    #             mail_cc=cc_mail,
    #             email_from=self.env.user.employee_ids.work_email,
    #             name=self.assessee_id.display_name
    #         ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    # def disagree_observation(self):
    #     self.user_agree_observation = 'Disagree'
    #     template = self.env.ref("performance_improvement_plan.email_template_confirm_pip")
    #     pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
    #     hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
    #     manager_emp_notify_user = self.env['hr.employee'].sudo().search(
    #         [('id', 'in', pip_notify_emp.ids), ('active', '=', True)])
    #     manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
    #     mail_cc = []
    #     if self.env.user.employee_ids.parent_id and self.env.user.employee_ids.parent_id.work_email:
    #         mail_cc.append(self.env.user.employee_ids.parent_id.work_email)

    #     if self.raised_by.work_email:
    #         mail_cc.append(self.raised_by.work_email)

    #     if self.env.user.employee_ids.department_id.manager_id.work_email:
    #         mail_cc.append(self.env.user.employee_ids.department_id.manager_id.work_email)
    #     mail_cc.extend(manager_emp_notify_user.mapped('work_email'))

    #     cc_mail = ','.join(set(mail_cc))
    #     if template:
    #         template.with_context(
    #             subject=f"PIP Process | {self.assessee_id.display_name} | Deliverables Decline ",
    #             mail_for='Disagree',
    #             email_to=','.join(manager_emp_hr.mapped('work_email')),
    #             mail_cc=cc_mail,
    #             email_from=self.env.user.employee_ids.work_email,
    #             name=self.assessee_id.name
    #         ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    # def btn_user_not_agree(self):
    #     if self.user_agree_observation and self.user_agree_observation == 'Disagree':
    #         if not self.final_decision:
    #             raise ValidationError("Please give the Final Decision")
    #         else:
    #             self.feedback_status = '6'
    #             self.pip_ref_id.write({'status':'Closed'})
    #     elif self.user_agree_observation and self.user_agree_observation == 'Agree':
    #         self.feedback_status = '4'
    #         template_obj = self.env.ref('performance_improvement_plan.email_template_user_doc_pip')
    #         if template_obj:
    #             template_obj.with_context(
    #                 subject=f"PIP Process | {self.assessee_id.display_name} | Upload Documents ",
    #                 mail_for='User_doc',
    #                 email_to=self.assessee_id.work_email,
    #                 email_from=self.env.user.employee_ids.work_email,
    #                 name=self.assessee_id.name
    #             ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
    #     else:
    #         raise ValidationError("Employee is not given any feedback")

    def remainder_mail_cron(self):
        pip_emp_record = self.env['kw_pip_counselling_details'].search([('feedback_status', '=', '3')])
        template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')
        # PMS users
        hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
        manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
        today = date.today()

        if pip_emp_record:
            for rec in pip_emp_record:
                if rec.next_counselling:
                    reminder_date = rec.next_counselling - timedelta(days=1)
                    reminder_seven_date = rec.next_counselling - timedelta(days=7)
                    # print("reminder_date >>> >>>> >>>>>> ", reminder_date, reminder_seven_date, today)
                    if reminder_date == today or reminder_seven_date == today:
                        mail_cc = []
                        # if rec.assessee_id.parent_id and rec.assessee_id.parent_id.work_email:
                        #     mail_cc.append(rec.assessee_id.parent_id.work_email)
                        if rec.raised_by.work_email:
                            mail_cc.append(rec.raised_by.work_email)
                        # if rec.assessee_id.department_id.manager_id.work_email:
                        #     mail_cc.append(rec.assessee_id.department_id.manager_id.work_email)
                        # if rec.assessee_id.sbu_master_id.representative_id.work_email:
                        #     mail_cc.append(rec.assessee_id.sbu_master_id.representative_id.work_email)
                        mail_cc.extend(rec.assign_assessors_ids.mapped('work_email'))
                        mail_cc = ','.join(set(mail_cc)) + ',' + ','.join(manager_emp_hr.mapped('work_email'))
                        if template_obj:
                            template_obj.with_context(
                                subject=f"PIP Process | {rec.assessee_id.display_name} | Review of the Deliverables",
                                mail_for='mail_remainder',
                                email_to=rec.assessee_id.work_email,
                                mail_cc=mail_cc,
                                email_from="tendrils@csm.tech",
                                next_counselling=datetime.strptime(str(rec.next_counselling), "%Y-%m-%d").strftime("%d-%b-%Y") if rec.next_counselling else False,
                                name=pip_emp_record.assessee_id.name
                            ).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        pass
