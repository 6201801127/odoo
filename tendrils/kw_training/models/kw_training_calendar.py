from odoo import models, fields, api, tools
from datetime import date, datetime, time
from odoo.exceptions import ValidationError, UserError


class TrainingCalendarReport(models.Model):
    _name = "kw_training_calendar_report"
    _rec_name = "name"
    _description = "Training Calendar"
    _auto = False
    
    name = fields.Char(string="Training Title", size=50)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    course_id = fields.Many2one('kw_skill_master', string="Course")
    instructor_type = fields.Selection(string='Instructor Type',
                                       selection=[('internal', 'Internal'), ('external', 'External')])
    empl_id = fields.Text(string="Instructor")
    nominate_btn_hide = fields.Boolean("hide bool",compute="_check_emp_in_nominate",default=False, store=False)
    training_approve_bool = fields.Boolean(compute="get_not_approved_plan",default=False, store=False)
    training_date_bool = fields.Boolean(compute="get_training_applied_date",store=False)
    training_calender_doc =  fields.Char(string="Training plan document",compute="get_training_doc")
    
    
    def get_training_doc(self):
        if not self.training_calender_doc:
            self.training_calender_doc = False
            
    @api.multi
    def action_download_training_document(self):
        training_plan_doc = self.env['kw_training_plan'].sudo().search([('training_id','=',self.id)])
        if not training_plan_doc.plan_doc:
                raise ValidationError("Documents not found.")
        else:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/download_training_plan_update_doc/{training_plan_doc.id}',
                'target': 'self',
            }
    
    
    def _check_emp_in_nominate(self):
        nominate_employee = self.env['kw_training_nominate_approve'].sudo().search([('empl_id','=',self.env.user.employee_ids.id),('name','=',self.name)])
        if  nominate_employee :
            self.nominate_btn_hide = True
        else:
            self.nominate_btn_hide = False
            # ,'&',('period_from','<=',date.today()),('period_to','>=',date.today())
    
    def get_training_applied_date(self):
        if self.start_date > date.today() :
            self.training_date_bool =True
        else:
            self.training_date_bool = False  
                 
    def get_not_approved_plan(self):
        approved_training_plans = approved_training_plans = self.env['kw_training_plan'].sudo().search([('training_id', '=', self.id), ('state', '=', 'approved'),])
        if approved_training_plans:
            self.training_approve_bool = True
        else:
            self.training_approve_bool = False
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          SELECT
            kwt.id AS id,
            kwt.name AS name,
            kwt.start_date AS start_date,
            kwt.end_date AS end_date,
            kwt.course_id AS course_id,
            kwt.instructor_type AS instructor_type,
            COALESCE((SELECT STRING_AGG(name, ', ') 
                FROM hr_employee 
                WHERE id IN (SELECT emp_id 
                FROM training_plan_hremp_rel 
                WHERE plan_id IN (SELECT id 
                FROM kw_training_plan 
                WHERE training_id = kwt.id))), 'NA') AS empl_id
            FROM kw_training kwt where kwt.training_type != 'PIP'
        )"""
        self.env.cr.execute(query)
        
        
    def get_training_nominate_form(self):
        form_view_id = self.env.ref('kw_training.kw_training_cal_wizard_form_view').id
        return {
            'name': 'Nominate Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'training_nominate_form_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'create': False},
        }
   
class TrainingnominateWizard(models.TransientModel):
    
    _name = "training_nominate_form_wizard"
    _description = "Training nominate wizard"

    remark = fields.Text() 
    empl_id = fields.Many2one('hr.employee',string="Employee",default=lambda self: self.env.user.employee_ids,)
    training_calendar_id = fields.Many2one('kw_training_calendar_report',string="Calendar id", default=lambda self: self.env.context.get('active_id'), readonly=1)
    training_approve_id = fields.Many2one('kw_training_nominate_approve',string="Approve id",default=lambda self: self.env.context.get('current_id'),readonly=1)
    
    
    def get_self_nominate_training(self):
        if self.empl_id:
            parent_id = self.empl_id.parent_id
            template_id = self.env.ref('kw_training.kw_training_nominate_approve_email_template')
            template_id.with_context(email_to=parent_id.work_email, email_from=self.env.user.employee_ids.work_email,user_name= self.empl_id.name,
                        name="Training | Nominate Approve Request").sudo().send_mail(self.training_calendar_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            nominate_data = {'name':self.training_calendar_id.name,
                             'start_date':self.training_calendar_id.start_date,
                             'end_date':self.training_calendar_id.end_date,
                             'course_id':self.training_calendar_id.course_id.id,
                             'instructor_type':self.training_calendar_id.instructor_type,
                             'empl_id':self.empl_id.id,
                             'training_cal_nominate_id':self.training_calendar_id.id,
                             'state':'Applied',
                             'nominate_user_remark':self.remark,
                            }
            self.env['kw_training_nominate_approve'].create(nominate_data)
            self.env.user.notify_success("Training nominate applied Successfully.")
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }
    def approved_training(self):
        context = dict(self._context)
        if context['button_name'] == 'Approve' and self.remark:
            self.training_approve_id.write({'state':'Approved','ra_approve_remark':self.remark,'hide_approve':True, 'approver_id': self.env.user.employee_ids.id})
            template = self.env.ref('kw_training.kw_training_nominate_ra_approved_email_template')
            cc_users = self.env.ref('kw_training.kw_training_cal_parameter').sudo().value
            email_cc = cc_users if cc_users else ''
            training_plan = self.env['kw_training_plan'].sudo().search([('training_id','=',self.training_approve_id.training_cal_nominate_id.id),('state','=','approved')]) 
            if training_plan and self.training_approve_id.empl_id.id not in training_plan.participant_ids.ids:
                training_plan.participant_ids = [(4, self.training_approve_id.empl_id.id, False)]
                template.with_context(email_to=self.training_approve_id.empl_id.work_email,ra_name=self.env.user.employee_ids.name, 
                        email_from=self.env.user.employee_ids.work_email,
                        email_cc = email_cc ,
                        remark = self.remark,
                        tra_name=self.training_approve_id.name,
                        start_date = self.training_approve_id.start_date.strftime("%d-%b-%Y"),
                        end_date = self.training_approve_id.end_date.strftime("%d-%b-%Y"),
                        user_name= self.training_approve_id.empl_id.name,
                        course_id = self.training_approve_id.course_id.name,
                        instructor = self.training_approve_id.instructor_type,
                        name="Training | Nominate Approved").sudo().send_mail(self.training_approve_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Training request approve Successfully.")
            else:
                raise ValidationError("Warning! Training is not approved OR Employee Already add in that training.")
        elif context['button_name'] == 'Reject' and self.remark:
            template = self.env.ref('kw_training.kw_training_nominate_ra_reject_email_template')
            cc_users = self.env.ref('kw_training.kw_training_cal_parameter').sudo().value
            email_cc = cc_users if cc_users else ''
            if template:
                template.with_context(email_to=self.training_approve_id.empl_id.work_email,ra_name=self.env.user.employee_ids.name, 
                        email_from=self.env.user.employee_ids.work_email,
                        email_cc = email_cc,
                        remark = self.remark,
                        tra_name=self.training_approve_id.name,
                        start_date = self.training_approve_id.start_date.strftime("%d-%b-%Y"),
                        end_date = self.training_approve_id.end_date.strftime("%d-%b-%Y"),
                        user_name= self.training_approve_id.empl_id.name,
                        course_id = self.training_approve_id.course_id.name,
                        instructor = self.training_approve_id.instructor_type,
                        name="Training | Nominate Rejected").sudo().send_mail(self.training_approve_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Training request rejected Successfully.")
            self.training_approve_id.write({'hide_approve': True,'state':'Reject','empl_id':False,'ra_reject_remark':self.remark,'approver_id': self.env.user.employee_ids.id})
        elif context['button_name'] == 'manager_cancel' and self.remark:
            self.training_approve_id.write({'hide_approve': True,'state':'Cancel','manager_remark':self.remark,'cancel_by_id':self.env.user.employee_ids.id})
            template = self.env.ref('kw_training.kw_training_nominate_manager_cancel_email_template')
            email_cc = self.training_approve_id.empl_id.parent_id.work_email if self.training_approve_id.empl_id.parent_id else ''
            if template:
                template.with_context(email_to=self.training_approve_id.empl_id.work_email, cancel_name=self.env.user.employee_ids.name,
                        email_from=self.env.user.employee_ids.work_email,
                        email_cc = email_cc,
                        remark = self.remark,
                        tra_name=self.training_approve_id.name,
                        start_date = self.training_approve_id.start_date.strftime("%d-%b-%Y"),
                        end_date = self.training_approve_id.end_date.strftime("%d-%b-%Y"),
                        user_name= self.training_approve_id.empl_id.name,
                        course_id = self.training_approve_id.course_id.name,
                        instructor = self.training_approve_id.instructor_type,
                        name="Training | Nominate Cancel").sudo().send_mail(self.training_approve_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            training_plan_del_emp=self.env['kw_training_plan'].sudo().search([('training_id','=',self.training_approve_id.training_cal_nominate_id.id)])
            training_plan_del_emp.participant_ids = [(3, self.training_approve_id.empl_id.id)]
            self.env.user.notify_success("Training  cancel Successfully.")
            
            
class TrainingnominateApprove(models.Model):
    _name = "kw_training_nominate_approve"
    _rec_name = "name"
    _description = "Training Nomination"
    
    
    training_cal_nominate_id = fields.Many2one('kw_training_calendar_report',string="Training Calendar")
    name = fields.Char(string="Training Title", size=50)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    course_id = fields.Many2one('kw_skill_master', string="Course")
    instructor_type = fields.Selection(string='Instructor',
                                       selection=[('internal', 'Internal'), ('external', 'External')])
    empl_id = fields.Many2one('hr.employee',string="Employee")
    hide_approve = fields.Boolean(string="Hide approve",default=False)
    state = fields.Selection(string='Status',
                        selection=[('Applied', 'Applied'), ('Approved', 'Approved'), ('Reject', 'Reject'),('Cancel','Cancel')])
    nominate_user_remark = fields.Text(string="Nominate User Remark")
    ra_approve_remark = fields.Text(string="Approved Remark")
    ra_reject_remark = fields.Text(string="Reject Remark")
    manager_remark = fields.Text(string="Cancel Remark")
    approver_id = fields.Many2one('hr.employee',string="Approved By")
    cancel_by_id = fields.Many2one('hr.employee',string="Cancel By")
        
        
    def get_training_approve_ra(self):
        form_view_id = self.env.ref('kw_training.kw_training_approved_ra_wizard_form_view').id
        return {
            'name': 'Approved Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'training_nominate_form_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'create': False},
        }
    
    def get_training_reject_ra(self):
        form_view_id = self.env.ref('kw_training.kw_training_approved_ra_wizard_form_view').id
        return {
            'name': 'Reject Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'training_nominate_form_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'create': False},
        }
    
    def get_cancel_nomination_manager(self):
        form_view_id = self.env.ref('kw_training.kw_training_cancel_manager_wizard_form_view').id
        return {
            'name': 'Cancel Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'training_nominate_form_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'create': False},
        }
        
    
    
    
                    
