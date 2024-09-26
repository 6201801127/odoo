# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import tools, _
import pytz
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class Meetingevents(models.Model):
    _inherit = 'kw_meeting_events'
    # _description = "Meeting Information"

    enrollment_ids = fields.Many2many('kwonboard_enrollment', string="Applicant", )
    meetingtype_code = fields.Char('code')
    send_to_mail_applicant = fields.Boolean('Send to Applicant')
    app_mail_check = fields.Boolean('Applicant mail check', default=False)

    @api.onchange('meeting_type_id')
    def set_categ_ids(self):
        for record in self:
            record.categ_ids = record.meeting_type_id
            record.meetingtype_code = record.meeting_type_id.code

    @api.model
    def create(self, vals):
        record = super(Meetingevents, self).create(vals)

        if 'active_model' in self._context and 'active_id' in self._context:
            induction_rec = []
            if 'active_model' in self._context and self._context['active_model'] == 'kw_induction_plan_type_data':
                induction_rec = self.env['kw_induction_plan_type_data'].browse(self._context['active_id'])

                if induction_rec:
                    if vals.get('send_to_mail_applicant') == False:
                        # print("in if================================")
                        raise ValidationError('Please check the Send to applicant.')
                    data = {
                        'induction_meeting_id': record.id,
                    }
                induction_rec.write(data)
        # except Exception as e:
        #     pass

        if vals.get('send_to_mail_applicant'):
            vals['send_to_mail_applicant'] = vals.get('send_to_mail_applicant')

        email_user = self.env.user.email
        if email_user:
            template = self.env.ref('kw_onboarding_induction_feedback.kw_applicant_intimatation_counselling_schedule')
            mail_template = self.env['mail.template'].browse(template.id)
            calendar_view = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_calendar_event_calendar')
            action_id = self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id
            for meeting in record:
                if meeting.enrollment_ids:
                    for applicant in meeting.enrollment_ids:
                        if template and vals.get('send_to_mail_applicant') == True:
                            subject = 'Induction Schedule | CSM Technologies'
                            email_from_cc = meeting.enrollment_ids[0].email
                            applicant_mail = mail_template.with_context(
                                applicantname=applicant.name,
                                emailfrom=self.env.user.email,
                                emailcc=email_from_cc,
                                email_to=applicant.email,
                                subject=subject).send_mail(meeting.id, force_send=False)
                            vals = {}
                            vals['model'] = None  # We don't want to have the mail in the chatter while in queue!
                            vals['res_id'] = False
                            current_mail = self.env['mail.mail'].browse(applicant_mail)
                            current_mail.mail_message_id.write(vals)
        self.env.user.notify_success("Meeting created successfully.")
        return record

    @api.multi
    def write(self, values):
        result = super(Meetingevents, self).write(values)
        # timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        # start_time = meeting.start_datetime.astimezone(timezone)
        # combined_datetime_str = start_date + " " + str(start_time.time())
        # print(combined_datetime_str,"combined_datetime_str=============",start_date + " " + str(start_time.time()) )
        # combined_datetime = datetime.strptime(combined_datetime_str, "%d-%b-%Y %H:%M:%S")  # Adjust the format as needed
        for meeting in self:
            if not meeting.id and ('start' in values and 'stop' in values):
                details_induction = self.env['kw_induction_plan_type_data'].sudo().search(
                    [('induction_meeting_id', '=', meeting.id)])
                start_date = meeting.kw_start_meeting_date.strftime('%d-%b-%Y')
                if details_induction:
                    details_induction.write({'induction_date': start_date})
                email_user = self.env.user.email
                if email_user:
                    template = self.env.ref('kw_onboarding_induction_feedback.kw_applicant_intimatation_counselling_schedule')
                    mail_template = self.env['mail.template'].browse(template.id)
                    if meeting.enrollment_ids:
                        for applicant in meeting.enrollment_ids:
                            if (template and meeting.send_to_mail_applicant == True
                                    or values.get('send_to_mail_applicant') == True):
                                subject = 'Induction Schedule | CSM Technologies'
                                email_from_cc = meeting.enrollment_ids[0].email
                                applicant_mail = mail_template.with_context(
                                    applicantname=applicant.name,
                                    emailfrom=self.env.user.email,
                                    emailcc=email_from_cc,
                                    email_to=applicant.email,
                                    subject=subject).send_mail(meeting.id, force_send=False)
                                vals = {}
                                vals['model'] = None  # We don't want to have the mail in the chatter while in queue!
                                vals['res_id'] = False
                                current_mail = self.env['mail.mail'].browse(applicant_mail)
                                current_mail.mail_message_id.write(vals)
                self.env.user.notify_success("Meeting created successfully.")
        return result


class KwInductionPlan(models.Model):
    _name = 'kw_induction_plan_data'
    _description = "Induction Plan"
    _rec_name = 'applicant_induction_id'

    def get_applicant_join_rec(self):
        onboard_rec = self.env['kw_employee_induction_assessment'].sudo().search([])
        onboard_ids = onboard_rec.mapped('emp_id.onboarding_id.id')
        if onboard_ids:
            record_config = self.env['kwonboard_enrollment'].sudo().search([('id', 'not in', onboard_ids)]).mapped('id')
            return {'domain': {'applicant_induction_id': [('id', 'in', record_config)]}}
        else:
            return {'domain': {}}

    applicant_induction_id = fields.Many2one('kwonboard_enrollment', string="Applicant", default=get_applicant_join_rec)
    applicant_email = fields.Char(string="Email Id", related="applicant_induction_id.email", store=True)
    applicant_ph = fields.Char(string="Ph no", related="applicant_induction_id.mobile", store=True)
    applicant_dept_id = fields.Many2one('hr.department', string="Department",
                                        related="applicant_induction_id.dept_name", store=True)
    applicant_doj = fields.Date(string="Date of Joining", related="applicant_induction_id.tmp_join_date", store=True)
    applicant_data_ids = fields.One2many('kw_induction_plan_type_data', 'induction_plan_id',
                                         string="Induction plan details", required=True)
    status_of_induction = fields.Selection(string="Status",
                                           selection=[('Not complete', 'Not complete'),
                                                      ('In progress', 'In progress'),
                                                      ('Completed', 'Completed')], default="Not complete")
    status_update = fields.Boolean(string="Update", compute="_get_status_update_induction")

    @api.constrains('applicant_data_ids', 'applicant_induction_id')
    def get_validate_applicant_data(self):
        for rec in self:
            if not rec.applicant_data_ids:
                raise ValidationError("Warning! Enter at least One Induction.")

    def _get_status_update_induction(self):
        complete = []
        if self.applicant_data_ids:
            for rec in self.applicant_data_ids:
                if rec.meeting_status == 'Completed':
                    complete.append('complete')
            if len(self.applicant_data_ids) == len(complete):
                self.write({'status_of_induction': 'Completed', 'status_update': True})

    def get_adjusted_induction_time(self, induction_date):
        if induction_date:
            adjusted_time = induction_date + timedelta(hours=5, minutes=30)
            return adjusted_time.strftime("%H:%M:%S")
        return False


class InductionPlanWizard(models.TransientModel):
    _name = 'induction_plan_wizard'
    _description = 'induction_plan_wizard'

    @api.model
    def default_get(self, fields):
        res = super(InductionPlanWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'applicant_ids': active_ids,
        })
        return res

    applicant_ids = fields.Many2many(string='Applicants',
                                     comodel_name='kw_induction_plan_data',
                                     relation='induction_plan_relation',
                                     column1='induction_wizard_id',
                                     column2='plan_id', )

    note = fields.Text(string="Remarks", readonly=False)
    meeting_url = fields.Char(string="Meeting URL")
    meeting_room = fields.Many2one(string='Meeting Room',
                                   comodel_name='kw_meeting_room_master')
    induction_type_bool_check = fields.Boolean(string="Type check")
    
    
    # @api.depends('applicant_ids')
    # def get_induction_type_check(self):
    #     for rec in self.applicant_ids:
    #         if rec.applicant_data_ids:
    #             print(rec,"=====applicant_data_ids================")
    #             if any(record.induction_type == 'Virtual' for record in rec.applicant_data_ids):
    #                 self.induction_type_bool_check = True
    #             else:
    #                 self.induction_type_bool_check = False
                    
    
    

    @api.multi
    def send_mail_applicant(self):
        email_user = self.env.user.email
        if email_user:
            template = self.env.ref('kw_onboarding_induction_feedback.kw_induction_plan_email_template')
            if template:
                for rec in self.applicant_ids:
                    if any(record.induction_type in ['Offline','Virtual','Voice over'] and record.meeting_status == 'Not complete' for record in rec.applicant_data_ids):
                        record = self.env['kw_induction_plan_data'].search([('id', '=', rec.id)])
                        induction = ','.join(record.applicant_data_ids.mapped('type_induction_id.name'))
                        cc_email_list = record.applicant_data_ids.mapped('inductor_name_id.work_email')
                        cc_email_list.extend([self.env.user.employee_ids.work_email])
                        email_cc = ','.join(cc_email_list)
                        subject = 'Induction Schedule | CSM Technologies'
                        template.with_context(
                            mail_for = 'Offline',
                            applicantname=rec.applicant_induction_id.name,
                            email_from=self.env.user.email,
                            email_cc=email_cc,
                            description=self.note,
                            induction=induction,
                            record=record.applicant_data_ids,
                            meeting_link=self.meeting_url if self.meeting_url else '',
                            meeting_room=self.meeting_room.name,
                            floor_name=self.meeting_room.floor_name,
                            remarks=self.note,
                            email_to=rec.applicant_induction_id.email,
                            subject=subject).send_mail(rec.id, notif_layout='kwantify_theme.csm_mail_notification_light',
                                                    force_send=False)
                    # if any(record.induction_type == 'Virtual' and record.meeting_status == 'Not complete' for record in rec.applicant_data_ids):
                    #     record = self.env['kw_induction_plan_type_data'].search([('induction_plan_id', '=', rec.id),('induction_type','=','Virtual'),('meeting_status','=','Not complete')])
                    #     induction = ','.join(record.mapped('type_induction_id.name'))
                    #     emp_mail = self.env['hr.employee'].sudo().search([('onboarding_id','=',rec.applicant_induction_id.id)]) 
                    #     # cc_email_list = record.applicant_data_ids.mapped('inductor_name_id.work_email')
                    #     # cc_email_list = rec.applicant_induction_id.onboarding_id.work_email 
                    #     email_cc = self.env.user.employee_ids.work_email + ',' + emp_mail.work_email if emp_mail else self.env.user.employee_ids.work_email
                    #     subject = 'Induction Schedule | CSM Technologies'
                    #     template.with_context(
                    #         mail_for ='virtual',
                    #         applicantname=rec.applicant_induction_id.name,
                    #         email_from=self.env.user.email,
                    #         email_cc=email_cc,
                    #         description=self.note,
                    #         induction=induction,
                    #         record=record,
                    #         remarks=self.note,
                    #         email_to=rec.applicant_induction_id.email,
                    #         subject=subject).send_mail(rec.id, notif_layout='kwantify_theme.csm_mail_notification_light',
                    #                                 force_send=False)
            self.env.user.notify_success("Meeting send successfully.")

            # inductor_name = fields.Many2one('hr.employee',string="Inductor Name")
    # type_of_induction = fields.Many2many('kw_skill_master','induction_plan_skill_rel','ind_wizard_id','skill_wizard_id',string="Induction name",domain=_get_induction_data)   
    # induction_config = fields.Boolean()  

    # @api.depends('applicant_ids')
    # def _get_induction_data(self):
    #     for rec in self:
    #         record = self.env['kw_induction_plan_data'].search([('id','=',rec.applicant_ids.ids)])
    #         for rec in record:
    #             induction = []
    #             if rec.applicant_data_ids:
    #                 induction.extend(rec.applicant_data_ids.mapped('type_induction_id.id'))
    #     return [('id', 'in', induction.ids)]
    #     return{'domain':{'type_of_induction': [('id', 'in', induction)], }}


class KwInductionPlanType(models.Model):
    _name = 'kw_induction_plan_type_data'
    _description = "A model to type plan the induction"

    type_induction_id = fields.Many2one('kw_skill_master', string="Induction Type",
                                        domain="[('skill_type', '=', 'Induction')]")
    induction_date = fields.Datetime(string="Induction Datetime")
    inductor_name_id = fields.Many2one('hr.employee', string="Inductor Name")
    induction_plan_id = fields.Many2one('kw_induction_plan_data', string="induction plan")
    meeting_status = fields.Selection(string="Status",
                                      selection=[('Not complete', 'Not complete'), ('Completed', 'Completed')],
                                      default="Not complete")
    hide_meeting_btn = fields.Boolean(string="Hide")
    induction_meeting_id = fields.Many2one(comodel_name='kw_meeting_events', string='Meeting Name')
    induction_type = fields.Selection(string="Type",selection=[('Offline','Offline'),('Virtual','Virtual'),('Voice over','Voice over')])
    type_check_bool = fields.Boolean(string="check type", default=False)
    voice_type_bool = fields.Boolean(string="voice check type", default=False)
    handbook_category_id = fields.Many2one('kw_handbook_type',string="Handbook Category")
    
    @api.onchange('induction_type')
    def get_induction_type_data(self):
        inductor_data = self.env['kw_skill_master'].sudo().search([('id', '=', self.type_induction_id.id)])
        if self.induction_type and self.induction_type =='Virtual':
            self.type_check_bool = True
            self.inductor_name_id = False
        elif self.induction_type and self.induction_type =='Virtual' and self.type_induction_id:
            return {'domain': {'inductor_name_id': []}}
        else:
            if self.induction_type and self.induction_type =='Offline' and self.type_induction_id:
                self.type_check_bool = False
                self.handbook_category_id = False
                return {'domain': {'inductor_name_id': [('id', 'in', inductor_data.employee_id.ids)]}}
            if  self.induction_type and self.induction_type =='Voice over':
                self.inductor_name_id = False
                self.voice_type_bool = True
                self.handbook_category_id = False
            
        
    @api.onchange('type_induction_id')
    def get_inductor_data(self):
        self.inductor_name_id = False
        inductor_data = self.env['kw_skill_master'].sudo().search([('id', '=', self.type_induction_id.id)])
        if self.type_induction_id:
            return {'domain': {'inductor_name_id': [('id', 'in', inductor_data.employee_id.ids)]}}
        else:
            return {'domain': {'inductor_name_id': []}}
            
    @api.constrains('induction_date')
    def validation_of_datetime(self):
        for rec in self:
            if rec.induction_date and rec.induction_date < datetime.now():
                raise ValidationError("Warning! Date should not less than current date")

    def meeting_induction_applicant(self):
        self.ensure_one()
        if self.inductor_name_id:
            participants = self.inductor_name_id
            # participants += self.induction_plan_id.applicant_induction_id
            applicant = self.induction_plan_id.applicant_induction_id

        # res = self.env['ir.actions.act_window'].for_xml_id('kw_meeting_schedule', 'action_window_kw_meeting_schedule')
        meetingtype = self.env['calendar.event.type'].search([('code', '=', 'induction')], limit=1)
        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id

        context = {
            'visible': False,
            'default_user_id': self.env.uid,
            'default_name': f'{self.type_induction_id.name}',
            'default_email_subject_line': f'{self.type_induction_id.name}',
            'default_meeting_type_id': meetingtype.id,
            'default_kw_start_meeting_date': self.induction_date.strftime("%Y-%m-%d"),
            'default_employee_ids': [(6, 0, participants.ids)],
            'default_is_meeting_responsible': True,
            'default_enrollment_ids': [(6, 0, applicant.ids)],
        }
        _action = {
            'name': 'Induction Meeting Schedule',
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
        if (self.induction_meeting_id and self.induction_meeting_id.start_datetime
                and self.induction_meeting_id.start_datetime.astimezone(timezone) >= dt):
            _action['res_id'] = self.induction_meeting_id.id
        else:
            self.induction_meeting_id = False
            _action['res_id'] = False

        if not self.induction_meeting_id:
            _action['context'] = context
        else:
            _action['context'] = {'create': False}

        return _action

    @api.multi
    def meeting_complete_induction(self):
        self.write({'meeting_status': 'Completed',
                    'hide_meeting_btn': True, })
    #  'default_employee_ids': [(4, self.inductor_name_id.id, False)],
    
    
class KwUserInductionPlan(models.Model):
    _name = 'kw_induction_plan_user_data'
    _description = "User Induction"
    _auto = False
    
    empl_id = fields.Many2one('hr.employee',string="Name")
    applicant_induction_id = fields.Many2one('kwonboard_enrollment', string="Applicant")
    applicant_email = fields.Char(string="Email Id", related="applicant_induction_id.email",)
    applicant_ph = fields.Char(string="Ph no", related="applicant_induction_id.mobile",)
    applicant_dept_id = fields.Many2one('hr.department', string="Department",
                                        related="applicant_induction_id.dept_name" )
    applicant_doj = fields.Date(string="Date of Joining", related="applicant_induction_id.tmp_join_date")
    induction_type = fields.Selection(string="Type",selection=[('Offline','Offline'),('Virtual','Virtual')])
    induction_name = fields.Many2one('kw_skill_master', string="Induction name",
                                        domain="[('skill_type', '=', 'Induction')]")
    handbook_category_id = fields.Many2one('kw_handbook_type',string="Handbook Category")
    induction_date = fields.Datetime(string="Induction Datetime")
    # handbook_type_code_id = fields.Many2one('kw_handbook_type',related="handbook_category_id.handbook_type_id")
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           SELECT   
            ROW_NUMBER() OVER () as id,
            indp.applicant_induction_id as applicant_induction_id,
            td.induction_type as induction_type,
            td.type_induction_id as induction_name,
            td.handbook_category_id as handbook_category_id,
            td.induction_date as induction_date,
            (select id from hr_employee where onboarding_id = indp.applicant_induction_id) as empl_id

            FROM kw_induction_plan_data indp
            left join kw_induction_plan_type_data td on td.induction_plan_id = indp.id
            where td.induction_type in ('Virtual','Offline')
         )"""
        self.env.cr.execute(query)
    
    
    
    def handbook_view_policy(self):
        # tree_view_id = self.env.ref('kw_handbook.kw_handbook_tree_view').id
        kanban_view_id = self.env.ref('kw_handbook.kw_handbook_kanban_view').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Dep. Structure, CDP & JD',
            'view_mode': 'kanban',
            'res_model': 'kw_onboarding_handbook',
            'target': 'main',
            'views': [(kanban_view_id, 'kanban')],
            'context': {'search_default_handbook_type_id':self.handbook_category_id.id},
            'flags': {'create': False,'edit': False},
            
        }
        return action
    
    

    
    
    