# -*- coding: utf-8 -*-
import base64
from datetime import date,datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.mimetypes import guess_mimetype
from mimetypes import guess_extension
from . import kw_training

start_date, end_date = kw_training.get_current_financial_dates()

class TrainingPlan(models.Model):
    _name = "kw_training_plan"
    _rec_name = "training_id"
    _description = "Training Plan"
    _order = "create_date desc"

    financial_year = fields.Many2one('account.fiscalyear',string="Financial Year",required=True,track_visibility='onchange')
    training_req_id = fields.Many2one('hr.employee',string="Training Requester")
    training_id = fields.Many2one("kw_training",string="Training Title",required=True,track_visibility='onchange',ondelete="cascade")
    period_from = fields.Date(related="training_id.start_date",string="From Date",track_visibility='onchange',store=True)
    period_to = fields.Date(related="training_id.end_date", string="To Date", required=True, track_visibility='onchange',store=True)
    details = fields.Text(string='Training Details',
                          track_visibility='onchange')
    instructor_type = fields.Selection(related="training_id.instructor_type", string='Instructor Type', selection=[('internal', 'Internal'), ('external', 'External')],
                                       default="internal", track_visibility='onchange',store=True)
    cost = fields.Integer(string="Trainer Remuneration", default=0,track_visibility='onchange')
    instructor_partner = fields.Many2one("res.partner", "Instructor",domain=[('partner_share','=',True)])
    internal_user_ids = fields.Many2many('hr.employee', 'training_plan_hremp_rel', 'plan_id',
                                         'emp_id', string="Instructors", domain=['|','&',('user_id','!=',False),('active','=',True),('active','=',False)], track_visibility='onchange')
    participant_ids = fields.Many2many(
        'hr.employee', string="Participants", domain=['|','&',('user_id','!=',False),('active','=',True),('active','=',False)], track_visibility='onchange')
    plan_doc = fields.Binary(string='Plan Document',
                             attachment=True, track_visibility='onchange')
    plan_doc_name = fields.Char("Document Name", track_visibility='onchange')
    ra_access = fields.Boolean(
        string='Access to RA', compute='_compute_ra_access', track_visibility='onchange')
    active = fields.Boolean(string="Active",default=True,track_visibility='onchange')
    state = fields.Selection(string="Status", selection=[('apply', 'Apply'), ('rejected', 'Rejected'), ('approved', 'Approved')], track_visibility='onchange')
    employee_id = fields.Many2one("hr.employee", string="Employee",domain=['|',('active','=',True),('active','=',False)])
    parent_id = fields.Many2one(
        related="employee_id.parent_id", string="Action Taken By/ To Be Taken By",)
    
    feedback_count = fields.Integer("Number Of Feedbacks", compute="_compute_feedback")
    session_count = fields.Integer("Number Of Sessions", compute="_compute_sessions")
    material_count = fields.Integer("Number Of Materials", compute="_compute_material")
    current_financial_year = fields.Boolean(
        "Search Current Financial Year", compute="_compute_financial_year",search="_search_current_financial_year")
    remark = fields.Text(string="Remarks", track_visibility='onchange')
    hide_training = fields.Boolean(string='hide_training',default=False)
    
    action_taken_on = fields.Datetime(string='action_taken_on')
    department_ids = fields.Many2many('hr.department', string='Departments',track_visibility='onchange')

    
    @api.multi
    def approve_remark(self):
        self.write({'state': 'approved', 'action_taken_on': datetime.now()})
        template = self.env.ref('kw_training.training_plan_action_mail')
        if template:
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        # now add trainers to trainer group in training mudule ,
        # so that they can create questions for assessment of participants
        survey_user_group = self.env.ref('survey.group_survey_user')
        dms_user_group = self.env.ref('kw_dms.group_dms_user')
        training_employee_group = self.env.ref('kw_training.group_kw_training_employee')
        trainer_group = self.env.ref('kw_training.group_kw_training_trainer')
        skill_assessment_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')
        trainer_users = self.internal_user_ids.mapped('user_id')
        for user in trainer_users:
            if not user.has_group('kw_training.group_kw_training_trainer'):
                trainer_group.sudo().write({'users': [(4, user.id)]})
            if not user.has_group('survey.group_survey_user'):
                survey_user_group.sudo().write({'users':[(4,user.id)]})
            if not user.has_group('kw_dms.group_dms_user'):
                dms_user_group.sudo().write({'users': [(4, user.id)]})
        participant_users = self.participant_ids.mapped('user_id')
        for p_user in participant_users:
            if not p_user.has_group('kw_training.group_kw_training_employee'):
                training_employee_group.sudo().write({'users': [(4, p_user.id)]})
            if not p_user.has_group('survey.group_survey_user'):
                survey_user_group.sudo().write({'users': [(4, p_user.id)]})
            if not p_user.has_group('kw_dms.group_dms_user'):
                dms_user_group.sudo().write({'users': [(4, p_user.id)]})
            if not p_user.has_group('kw_skill_assessment.group_kw_skill_assessment_user'):
                skill_assessment_user_group.sudo().write({'users': [(4, p_user.id)]})
                
        action_id = self.env.ref('kw_training.kw_training_plan_approve_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_training_plan&view_type=list',
            'target': 'self',
        }
    @api.multi

    def write(self,vals):
        email_list=[]
        # training = self.participant_ids.training_id
        # new_instructor_emp_rec = False
        new_instructors = list(set(vals.get('internal_user_ids')[0][2])-set(self.internal_user_ids.ids)) if vals.get('internal_user_ids') else False

        if self.state == 'approved':
            mail_cc = ''
            if new_instructors:
                email_list += self.env['hr.employee'].search([('id', 'in', new_instructors)]).mapped('work_email')
                mail_cc += ",".join(email_list)
                training=self.env['kw_training_assessment'].sudo().search([('training_id','=',self.training_id.id)])
                if training: 
                    template = self.env.ref('kw_training.training_assessment_notification_mail')
                    participant_emails = ','.join(self.participant_ids.mapped('work_email'))
                    if template:
                        template.with_context(participants=participant_emails, cc_emails=mail_cc).send_mail(training.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("Assessment mail sent successfully.")

        return super(TrainingPlan, self).write(vals)

    @api.multi
    def reject_remark(self):
        self.write({'state': 'rejected', 'active': False,'action_taken_on': datetime.now()})
        template = self.env.ref('kw_training.training_plan_action_mail')
        if template:
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        action_id = self.env.ref(
            'kw_training.kw_training_plan_approve_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_training_plan&view_type=list',
            'target': 'self',
        }

    @api.multi
    def take_action(self):
        form_view_id = self.env.ref("kw_training.view_kw_training_plan_approve_form").id
        return  {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_training_plan',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'self',
            'res_id':self.ids[0],
            'view_id':form_view_id,
        }

    @api.multi
    def _compute_feedback(self):
        for record in self:
            feedbacks = self.env['kw_training_feedback'].search([('training_id', '=', record.training_id.id)])
            record.feedback_count = len(feedbacks)
            
    @api.multi
    def _search_current_financial_year(self,operator,value):
        return ['&', ('period_from', '>=', start_date), ('period_to', '<=', end_date)]


    @api.multi
    def _compute_sessions(self):
        for record in self:
            sessions = self.env['kw_training_schedule'].search([('training_id', '=', record.training_id.id)])
            record.session_count = len(sessions)

    @api.multi
    def _compute_material(self):
        for record in self:
            materials = self.env['kw_training_material'].search([('training_id', '=', record.training_id.id)])
            record.material_count = len(materials)

    @api.multi
    def view_training_feedback(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_training', 'action_kw_training_feedback_act_window')
        res['domain'] = [('training_id', '=', self.training_id.id)]
        return res

    @api.multi
    def view_training_session(self):
        res = self.env['ir.actions.act_window'].for_xml_id(
            'kw_training', 'kw_training_session_act_window')
        res['domain'] = [('training_id', '=', self.training_id.id)]
        return res

    @api.multi
    def view_training_material(self):
        res = self.env['ir.actions.act_window'].for_xml_id(
            'kw_training', 'action_kw_training_material_act_window')
        res['domain'] = [('training_id', '=', self.training_id.id)]
        return res

    @api.constrains('training_id', 'participant_ids', 'internal_user_ids', 'instructor_partner')
    def _check_participant_or_training(self):
        # if self.training_id and not self.participant_ids:
        #     raise ValidationError(('Please add atleast one participant.'))   ## commented for training calendar use
        if self.instructor_type == 'internal' and not self.internal_user_ids:
            raise ValidationError(('Please add atleast one instructor.'))
        if self.instructor_type == 'external' and not self.instructor_partner:
            raise ValidationError(('Please add external instructor.'))
        if self.internal_user_ids and self.participant_ids:
            for instructor in self.internal_user_ids:
                for emp in self.participant_ids:
                    if instructor.id == emp.id:
                        raise ValidationError(f"Employee '{instructor.name}' cant' be instructor and participant.")

    @api.constrains('plan_doc')
    def validate_plan_doc(self):
        allowed_extension = {'.ods':'.ods','.xlsx':'.xlsx','.xlb':'.xls'}
        file_size = 100 # in kb
        for plan in self:
            if plan.plan_doc:
                doc_extension = guess_extension(guess_mimetype(base64.b64decode(plan.plan_doc)))
                img_size = (len(plan.plan_doc)*3/4) / 1024
                if doc_extension not in allowed_extension:
                    raise ValidationError(f"Invalid file extension.\nAllowed extensions are {', '.join(allowed_extension.values())}.")
                if img_size > file_size:
                    raise ValidationError(f"Maximum file size is {file_size}kb.")

    @api.multi
    def _compute_ra_access(self):
        employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        child_users = employee.child_ids
        for record in self:
            if record.employee_id and record.employee_id.id in child_users.ids:
                record.ra_access = True
            else:
                record.ra_access = False

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('ra_access_check'):
            employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
           
            child_users = employee.child_ids
            args += [('employee_id', 'in', child_users.ids),('state','=','apply')]
        return super(TrainingPlan, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        
    @api.constrains('training_id')
    def validate_duplicate(self):
        if self.training_id:
            rec = self.env['kw_training_plan'].search([('active','=',True)]) - self
            for r in rec:
                if r.training_id.id == self.training_id.id:
                    raise ValidationError(f"Training {self.training_id.name} is already planned.Try another.")

    @api.onchange('financial_year')
    def _set_training(self):
        if self.financial_year:
            if not (self.training_id and self.training_id.financial_year.id == self.financial_year.id):
                self.training_id = False
            return {'domain': {'training_id': [('financial_year.id', '=', self.financial_year.id)]}}

    def get_ra_email(self):
        emp = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)],limit=1)
        ra_email = emp and emp.parent_id and emp.parent_id.work_email or ""
        return ra_email
    
    @api.model
    def create(self, values):
        emp_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
        values['employee_id'] = emp_id.id if emp_id else False
        result = super(TrainingPlan, self).create(values)
        return result

    @api.multi
    def send_reject_mail(self):
        template = self.env.ref('kw_training.training_plan_action_mail')
        if template:
            template.send_mail(self.id, force_send=False, notif_layout="kwantify_theme.csm_mail_notification_light",
                               raise_exception=False)

    @api.multi
    def send_plan_approved_mail(self):
        template = self.env.ref('kw_training.training_plan_action_mail')
        if template:
            template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light", force_send=False, raise_exception=False)