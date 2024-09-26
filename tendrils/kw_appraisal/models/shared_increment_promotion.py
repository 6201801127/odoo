import base64
from odoo import models, fields, api, tools,_
from odoo.exceptions import ValidationError , UserError
from dateutil.relativedelta import relativedelta
from datetime import date,datetime
import bs4 as bs

class SharedIncrementPromotion(models.Model):
    _name           = 'shared_increment_promotion'
    _description    = "Interim Promotion"


    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(related='employee_id.name')
    emp_code = fields.Char(related='employee_id.emp_code')
    grade_id = fields.Many2one('kwemp_grade_master')
    job_id = fields.Many2one('hr.job',string='Designation')
    department_id = fields.Many2one('hr.department',string='Department')
    date_of_joining = fields.Date(string='Date of Joining')
    state = fields.Many2one('hr.appraisal.stages')
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],string="Budget Type")
    division = fields.Many2one('hr.department', string="Division", domain="[('dept_type.code', '=', 'division')]")
    emp_band = fields.Many2one(string=u'Band', comodel_name='kwemp_band_master')
    level = fields.Many2one('kw_grade_level')
    grade_band = fields.Char(compute='_compute_grade_band')
    new_grade_band = fields.Char(compute='_compute_grade_band')
    
    experience = fields.Char(compute='_compute_total_exp', string='Total Experience')
    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    status = fields.Selection([('draft', 'Draft'), ('pending_at_hod', 'Pending at IAA'), ('pending_at_chro', 'Pending at CHRO'),('pending_at_ceo', 'Pending at CEO'),('hold', 'Hold'),('completed', 'Approved by CEO'),('mail_send','Mail Sent'),('resent_chro','Resent To CHRO'),('resentdata_submitted_chro','Resent Data Submitted By CHRO'),('settle','Settled')])
    total_final_score = fields.Float("Appraisal Score",related='appraisal_id.total_final_score')
    proposed_increment = fields.Float("Proposed Appraisal Inc (%)",related='appraisal_id.increment_percentage')
    actual_increment_percentage = fields.Float("Inc % (HR)")
    actual_increment_percentage_2  = fields.Float()
    actual_increment_amount = fields.Float("Inc Amt (HR)",digits=(16, 0))
    actual_ctc = fields.Float("New CTC (HR)",digits=(16, 0))
    current_ctc = fields.Float(string='Current CTC',digits=(16, 0))
    hod_id = fields.Many2one('hr.employee')
    hr_remark = fields.Text("HR Remark")
    updated_by_hr = fields.Boolean()
    
    send_to_hod = fields.Boolean()
    hod_inc_auto = fields.Float("IAA Inc (%)")
    hod_inc_auto_2 = fields.Float("")
    hod_amount_auto = fields.Float("IAA Amount",digits=(16, 0))
    hod_actual_ctc = fields.Float("IAA CTC",digits=(16, 0))
    hod_remark = fields.Text('IAA Remark')
    
    chro_inc_auto = fields.Float("CHRO Inc (%)")
    chro_inc_auto_2 = fields.Float("Inc")
    chro_amount_auto = fields.Float("CHRO Amount",digits=(16, 0))
    chro_actual_ctc = fields.Float("CHRO CTC",digits=(16, 0))
    chro_remark = fields.Text('CHRO Remark')
    send_to_chro = fields.Boolean()
    
    ceo_remark = fields.Text('CEO Remark')
    
    new_job_id =fields.Many2one('hr.job',string='New Designation')
    new_grade_id = fields.Many2one('kwemp_grade_master')
    new_band_id = fields.Many2one('kwemp_band_master')
    
    appraisal_id =  fields.Many2one('hr.appraisal')
    add_in_appraisal = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    appraisal_log_ids = fields.One2many('increment_promotion_log','appraisal_id')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('other', 'Other')])
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU", help="SBU")
    sbu_name = fields.Char(related='sbu_master_id.name',string='SBU Name')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill')
    increment_effective_date = fields.Date(string="Increment Effective Date")
    check_manager_bool = fields.Boolean(compute='_check_manager')
    check_hod_bool = fields.Boolean(compute='check_hod_login')
    appraisal_doc_attach = fields.Binary(string='Attachment')
    applied_eos = fields.Boolean()
    iaas_ids = fields.Many2many('res.users', 'inc_promotion_iaa_user_rel', 'increment_id', 'user_id', 'IAAs')
    previous_increment  = fields.Float("Previous Inc (%)")
    previous_increment_amt  = fields.Float("Previous Inc Amt",digits=(16, 0))
    
    amt_changed_by_hod = fields.Boolean(compute="compute_actual_increment_percentage")
    increment_month = fields.Integer()
    last_working_day = fields.Date()
    changed_by_iaa = fields.Boolean()
    jd = fields.Html(compute='compute_jd_html')
    jd_boolean = fields.Boolean()

    actual_revised_increment_percentage  = fields.Float()
    revised_increment = fields.Float("Revised Inc (%)")
    revised_amount = fields.Float("Revised Amount",digits=(16, 0))
    revised_job_id =fields.Many2one('hr.job',string='Revised Designation')
    revised_grade_id = fields.Many2one('kwemp_grade_master')
    revised_band_id = fields.Many2one('kwemp_band_master')
    revised_ctc = fields.Float("Revised CTC",digits=(16, 0))
    revised_jd = fields.Html(compute='compute_jd_html')
    revised_jd_boolean = fields.Boolean()
    revised_hr_remark = fields.Text("Revised HR Remark")
    revised_chro_remark = fields.Text("Revised CHRO Remark")


    
    def _check_manager(self):
        if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            for rec in self:
                rec.check_manager_bool = True
    
    @api.onchange('increment_effective_date')
    def change_inc_month(self):
        if self.increment_effective_date:
            self.increment_month = self.increment_effective_date.month

            
    
    @api.onchange('new_job_id','revised_job_id')
    def validate_new_job_id(self):
        if self.new_job_id:
            job_role_id = self.env['hr.job.role'].search([('designations', 'in', [self.new_job_id.id])], limit=1)
            if not job_role_id or not job_role_id.description:
                return {'warning': {
                            'title': _('Validation Error'),
                            'message': (
                                f"JD is missing for the designation - {self.new_job_id.name}")
                        }}
        if self.revised_job_id:
            rjob_role_id = self.env['hr.job.role'].search([('designations', 'in', [self.revised_job_id.id])], limit=1)
            if not rjob_role_id or not rjob_role_id.description:
                return {'warning': {
                            'title': _('Validation Error'),
                            'message': (
                                f"JD is missing for the designation - {self.revised_job_id.name}")
                        }}
 
    
    @api.depends('new_job_id','revised_job_id')
    def compute_jd_html(self):
        for rec in self:
            job_role_id = self.env['hr.job.role'].search([('designations', 'in', [rec.new_job_id.id])], limit=1)
            if job_role_id and isinstance(job_role_id.description, str):
                rec.jd = job_role_id.description
            new_job_role_id = self.env['hr.job.role'].search([('designations', 'in', [rec.revised_job_id.id])], limit=1)
            if new_job_role_id and isinstance(new_job_role_id.description, str):
                rec.revised_jd = new_job_role_id.description

    @api.constrains('actual_increment_percentage', 'hod_inc_auto', 'chro_inc_auto','revised_increment')
    def _check_percentage_range(self):
        for record in self:
            if (
                record.actual_increment_percentage < 0 or record.actual_increment_percentage > 100 or
                record.hod_inc_auto < 0 or record.hod_inc_auto > 100 or
                record.chro_inc_auto < 0 or record.chro_inc_auto > 100 or
                record.revised_increment <0 or record.revised_increment > 100
            ):
                raise ValidationError("Percentage values must be between 0 and 100, inclusive.")

    @api.depends('actual_increment_percentage','hod_inc_auto')
    def compute_actual_increment_percentage(self):
        for record in self:
            record.amt_changed_by_hod = True if record.hod_inc_auto and record.actual_increment_percentage != record.hod_inc_auto else False


    def action_btn_hold(self):
        self.status = 'hold'
    
    def action_btn_unhold(self):
        self.status = 'completed'

    # @api.depends('employee_id')
    # def _compute_eos(self):
    #     for rec in self:
    #         resignation = self.env['kw_resignation'].sudo().search(
    #             [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
    #         rec.applied_eos = True if resignation else False

    @api.depends('status','iaas_ids')
    def check_hod_login(self):
        for rec in self:
            if self.env.uid in rec.iaas_ids.ids and rec.status == 'pending_at_hod':
                rec.check_hod_bool = True

    @api.onchange('current_ctc','actual_increment_percentage','hod_inc_auto','chro_inc_auto','revised_increment','revised_amount')
    def calculate_new_ctc(self):
        self.actual_increment_amount = self.current_ctc * self.actual_increment_percentage/100
        self.actual_ctc = self.current_ctc + self.actual_increment_amount
        self.hod_amount_auto = self.current_ctc * self.hod_inc_auto/100
        self.hod_actual_ctc = self.current_ctc + self.hod_amount_auto
        self.chro_amount_auto = self.current_ctc * self.chro_inc_auto/100
        self.chro_actual_ctc = self.current_ctc + self.chro_amount_auto
        self.revised_amount = self.current_ctc * self.revised_increment/100
        self.revised_ctc = self.current_ctc + self.revised_amount if self.revised_amount > 0 else 0

    
        



    def action_btn_log(self):
        form_view_id = self.env.ref('kw_appraisal.increment_promotion_log_details_view_form').id
        action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                'flags': {'mode':'readonly'},
                'context': {'create': False,'edit': False,'delete': False}
            }
        return action

    def action_btn_edit_by_hr(self):
        form_view_id = self.env.ref('kw_appraisal.increment_promotion_hr_details_view_form').id
        action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
            }
        if self.env.user.has_group('kw_appraisal.group_appraisal_manager') and self.status == 'draft' and not self.env.context.get('view'):
            return action
        else:
            action['flags']={'mode': 'readonly'}
            action['context'] = {'create': False,'edit': False,'delete': False}
            return action


    def action_btn_submit_by_hr(self):
        if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
        # if self.actual_increment_percentage_2 != self.actual_increment_percentage:
            self.env['increment_promotion_log'].create({
                'appraisal_id': self.id,
                'employee_id':self.env.user.employee_ids.id,
                'old_inc_auto':self.actual_increment_percentage_2,
                'new_inc_ctc':self.actual_increment_percentage,
                'remark':self.hr_remark,
                'edit_by':'hr',
                'old_revised_inc_auto':self.actual_revised_increment_percentage,
                'revised_inc_ctc':self.revised_increment,
            })
            self.actual_increment_percentage_2 = self.actual_increment_percentage
            self.actual_revised_increment_percentage = self.revised_increment
       

    def action_btn_edit_by_hod(self):
        form_view_id = self.env.ref('kw_appraisal.increment_promotion_details_hod_view_form').id
        action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                }
        if self.env.uid in self.iaas_ids.ids and self.status == 'pending_at_hod':
            return action
        else:
            action['flags']={'mode': 'readonly'}
            action['context'] = {'create': False,'edit': False,'delete': False}
            return action

    def action_button_hod_submit(self):
        if self.env.uid in self.iaas_ids.ids:
            self.env['increment_promotion_log'].create({
                'appraisal_id': self.id,
                'employee_id':self.env.user.employee_ids.id,
                'old_inc_auto':self.hod_inc_auto_2,
                'new_inc_ctc':self.hod_inc_auto,
                'remark':self.hod_remark,
                'edit_by':'hod'
            })
            self.hod_inc_auto_2 = self.hod_inc_auto
            self.changed_by_iaa = True if self.hod_inc_auto and self.actual_increment_percentage != self.hod_inc_auto else False

    def action_btn_edit_by_chro(self):
        if self.status in ('pending_at_chro'):
            form_view_id = self.env.ref('kw_appraisal.increment_promotion_details_chro_view_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                
                }
            if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
                return action
            else:
                action['flags']={'mode': 'readonly'}
                action['context'] = {'create': False,'edit': False,'delete': False}
                return action
        elif self.status in ('mail_send','resentdata_submitted_chro','resent_chro'):
            form_view_id = self.env.ref('kw_appraisal.increment_promotion_resend_mail_view_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                
                }
            # if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            #     return action
            # else:
            #     action['flags']={'mode': 'readonly'}
            #     action['context'] = {'create': False,'edit': False,'delete': False}
            return action
        else:
            form_view_id = self.env.ref('kw_appraisal.increment_promotion_details_ceo_view_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                }
            if self.env.user.has_group('kw_appraisal.group_appraisal_ceo') and self.status == 'pending_at_ceo':
                return action
            else:
                action['flags']={'mode': 'readonly'}
                action['context'] = {'create': False,'edit': False,'delete': False}
                return action

    def action_button_chro_submit(self):
        # if self.chro_inc_auto != self.chro_inc_auto_2:
            self.env['increment_promotion_log'].create({
                'appraisal_id': self.id,
                'employee_id':self.env.user.employee_ids.id,
                'old_inc_auto':self.chro_inc_auto_2,
                'new_inc_ctc':self.chro_inc_auto,
                'old_revised_inc_auto':self.actual_revised_increment_percentage,
                'revised_inc_ctc':self.revised_increment,
                'remark':self.chro_remark,
                'edit_by':'chro'
            })
            self.chro_inc_auto_2 = self.chro_inc_auto
            self.actual_revised_increment_percentage = self.revised_increment
    def action_button_ceo_submit(self):
        # if self.chro_inc_auto != self.chro_inc_auto_2:
            self.env['increment_promotion_log'].create({
                'appraisal_id': self.id,
                'employee_id':self.env.user.employee_ids.id,
                'old_inc_auto':self.chro_inc_auto_2,
                'new_inc_ctc':self.chro_inc_auto,
                'remark':self.ceo_remark,
                'edit_by':'ceo'
            })
            self.chro_inc_auto_2 = self.chro_inc_auto

    # @api.model
    # def check_chro_group(self,args):
    #     u_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
    #     button_user = self.env['kw_appraisal_btn_config_master'].search([('user_ids', '=', self.env.uid),('active', '=', False),('type','=','chro')])
    #     action = args.get("action", False)
    #     action_id = self.env.ref('kw_appraisal.shared_increment_promotion_action')
    #     if button_user and action == action_id.id:
    #         return '1'

    # @api.model
    # def check_manager_group(self,args):
    #     u_id = self.env.user
    #     button_user = self.env['kw_appraisal_btn_config_master'].search([('user_ids', '=', u_id.id),('active', '=', False),('type','=','manager')])
    #     action = args.get("action", False)
    #     action_id = self.env.ref('kw_appraisal.shared_increment_promotion_action')
    #     if button_user and action == action_id.id and u_id.has_group('kw_appraisal.group_appraisal_manager'):
    #         return '1'

    @api.model
    def action_send_to_ceo(self):
        u_id = self.env.ref('kw_appraisal.group_appraisal_chro').users
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        if u_id:
            active_ids = self.env.context.get('active_ids', [])
            promotion = self.env['shared_increment_promotion'].search([('id', 'in', active_ids),('status','=','pending_at_chro')])
            if promotion:
                for rec in promotion:
                    rec.status='pending_at_ceo'
                ceo = self.env.ref('kw_appraisal.group_appraisal_ceo').users
                if ceo:
                    for users in ceo:
                        email_cc = ''
                        mail_group = self.env['mail_cc_config'].search([('period_id','=',rec.period_id.id)],limit=1).mail_to_appr_manager.ids
                        mail_to = []
                        if mail_group:
                            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                        email_cc = ",".join(mail_to) or ''
                        # appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                        # email_cc = ','.join(appraisal_manager.mapped("email")) if appraisal_manager else ''
                        to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                        user_name = users.employee_ids.name if users.employee_ids.name else ''
                        template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Review | CHRO to CEO',send_by = 'chro',email_cc = email_cc).sudo().send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                        self.env.user.notify_success(message='Record Send!.')
            else:
                raise ValidationError('As IAA, you can send data to CHRO only.')

    @api.model
    def action_send_to_hod(self):
        u_id = self.env.ref('kw_appraisal.group_appraisal_manager').users
        if u_id:
            config = self.env['kw_appraisal_btn_config_master'].search([])
            template = self.env.ref('kw_appraisal.appraisal_review_email_template')
            active_ids = self.env.context.get('active_ids', [])
            promotion = self.env['shared_increment_promotion'].search([('id', 'in', active_ids),('status','=','draft'),])
            
            hod_id_lst = []
            write_query = ''
            dept_lst = []
            if promotion:
                for rec in promotion:
                    write_query += f"update shared_increment_promotion set status='pending_at_hod',hod_inc_auto={rec.actual_increment_percentage},hod_inc_auto_2={rec.actual_increment_percentage},hod_amount_auto={rec.actual_increment_amount},hod_actual_ctc={rec.actual_ctc},send_to_hod=true where id = {rec.id};"
                    if rec.department_id.id not in dept_lst:
                        dept_lst.append(rec.department_id.id)
                for dept in dept_lst:
                    dept_config = config.filtered(lambda x:x.type == 'hod' and dept in x.department_ids.ids)
                    for depts in dept_config:
                        for user in depts.user_ids:
                            if user.employee_ids.id not in hod_id_lst:
                                hod_id_lst.append(user.employee_ids.id)

                if len(write_query) > 0:
                    self.env.cr.execute(write_query)
                employee = self.env['hr.employee'].search([('id','in',hod_id_lst)])
                for hod in employee:
                    email_cc = ''
                    mail_group = self.env['mail_cc_config'].search([('period_id','=',rec.period_id.id)],limit=1).mail_to_appr_manager.ids

                    mail_to = []
                    if mail_group:
                        emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                        mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    email_cc = ",".join(mail_to) or ''
                    template.with_context(mail_user=hod.name,mail_id=hod.work_email,subject='Increment Review | HR to IAA',send_by = 'hr',email_cc=email_cc).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success(message='Record Send!.')
            else:
                raise ValidationError ('Please select the validated records.')
  


    # @api.model
    # def check_ceo_group(self,args):
    #     button_user = self.env['kw_appraisal_btn_config_master'].search([('user_ids', 'in', self.env.uid),('active', '=', False),('type', '=', 'ceo')])
    #     action = args.get("action", False)
    #     action_id = self.env.ref('kw_appraisal.shared_increment_promotion_action')
    #     if button_user and action == action_id.id:
    #         return '1'

    @api.model
    def action_ceo_submit(self):
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
            active_ids = self.env.context.get('active_ids', [])
            promotion = self.env['shared_increment_promotion'].search([('id', 'in', active_ids),('status','=','pending_at_ceo')])
            if promotion:
                for rec in promotion:
                    rec.write({
                    'status':'completed',
                    'send_to_chro':False
                })
                manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                if manager:
                    for users in manager:
                        email_cc = ''
                        mail_group = self.env['mail_cc_config'].search([('period_id','=',rec.period_id.id)],limit=1).mail_to_appr_manager.ids

                        mail_to = []
                        if mail_group:
                            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                        email_cc = ",".join(mail_to) or ''
                        # appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                        # email_cc = ','.join(appraisal_manager.mapped("email")) if appraisal_manager else ''
                        to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                        user_name = users.employee_ids.name if users.employee_ids.name else ''
                        template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Review | CEO to HR',send_by = 'ceo',email_cc = email_cc).sudo().send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='Appraisal Completed!.')
            else:
                raise ValidationError('Please select the validated records.')
                

    # @api.model
    # def check_hod_group(self,args):
    #     button_user = self.env['kw_appraisal_btn_config_master'].search([('user_ids', 'in', self.env.uid),('active', '=', False),('type', '=', 'hod')])
    #     action = args.get("action", False)
    #     action_id = self.env.ref('kw_appraisal.shared_increment_promotion_action')
    #     if button_user and action == action_id.id:
    #         return '1'
    @api.model
    def action_send_to_chro_hr(self):
        active_ids = self.env.context.get('active_ids', [])
        promotion = self.env['shared_increment_promotion'].search([('id', 'in', active_ids),('status','=','draft')])
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        write_query = ''
        var = 0
        if promotion:
            for rec in promotion:
                var =  rec.id
                write_query += f"update shared_increment_promotion set status='pending_at_chro',chro_inc_auto={rec.actual_increment_percentage},chro_inc_auto_2={rec.actual_increment_percentage},chro_amount_auto={rec.actual_increment_amount},chro_actual_ctc={rec.actual_ctc},send_to_chro=true where id = {rec.id};"
            if len(write_query) > 0:
                self.env.cr.execute(write_query)
            chro = self.env.ref('kw_appraisal.group_appraisal_chro').users
            if chro:
                for users in chro:
                    email_cc = ''
                    mail_group = self.env['mail_cc_config'].search([('period_id','=',rec.period_id.id)],limit=1).mail_to_appr_manager.ids

                    mail_to = []
                    if mail_group:
                        emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                        mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    email_cc = ",".join(mail_to) or ''
                    # appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                    # email_cc = ','.join(appraisal_manager.mapped("email")) if appraisal_manager else ''
                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                    user_name = users.employee_ids.name if users.employee_ids.name else ''
                    template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Review | HR to CHRO',send_by = 'hr',email_cc=email_cc).sudo().send_mail(var, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='Record Send!.')
        else:
            raise ValidationError ('Please select the validated records for CHRO Approval.')
        

    @api.model
    def action_send_to_hr(self):
        active_ids = self.env.context.get('active_ids', [])
        if len(active_ids) == 1:
            self._cr.execute(f"select id from shared_increment_promotion where id = {active_ids[0]} and status = 'resent_chro'")
        else:
            active_tuple = tuple(active_ids)
            self._cr.execute(f"select id from shared_increment_promotion where id in {active_tuple} and status = 'resent_chro'")
        promotion_data = [row[0] for row in self._cr.fetchall()]
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        var = 0
        write_query = ''
        if promotion_data:
            for rec in promotion_data:
                var =  rec
                write_query += f"update shared_increment_promotion set status='resentdata_submitted_chro'  where id = {rec};"
            if len(write_query) > 0:
                self.env.cr.execute(write_query)        
            appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
            chro_user = self.env.ref('kw_appraisal.group_appraisal_chro').users
            
            if appraisal_manager:
                for users in appraisal_manager:
                    if users not in chro_user:
                        email_cc = ''
                        # mail_group = self.env['mail_cc_config'].search([],order="id desc",limit=1).mail_to_appr_manager.ids
                        mail_to = []
                        # if mail_group:
                        #     emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                        #     mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                        # email_cc = ",".join(mail_to) or ''
                        
                        to_mail = ','.join(users.mapped("email")) if appraisal_manager else ''
                        # to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                        user_name = users.employee_ids.name if users.employee_ids.name else ''
                        template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Resend | CHRO to HR',send_by = 'chro',email_cc=email_cc).sudo().send_mail(var, notif_layout="kwantify_theme.csm_mail_notification_light")
                        self.env.user.notify_success(message='Record Send!.')
        else:
            raise ValidationError ('Please select the validated records for CHRO Approval.')






        
    @api.model
    def action_send_publish_record_to_chro(self):
        active_ids = self.env.context.get('active_ids', [])
        if len(active_ids) == 1:
            self._cr.execute(f"select id from shared_increment_promotion where id = {active_ids[0]} and status = 'mail_send'")
        else:
            active_tuple = tuple(active_ids)
            self._cr.execute(f"select id from shared_increment_promotion where id in {active_tuple} and status = 'mail_send'")
        promotion_data = [row[0] for row in self._cr.fetchall()]
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        var = 0
        write_query = ''
        if promotion_data:
            for rec in promotion_data:
                var =  rec
                write_query += f"update shared_increment_promotion set status='resent_chro'  where id = {rec};"
            if len(write_query) > 0:
                self.env.cr.execute(write_query)        
            chro = self.env.ref('kw_appraisal.group_appraisal_chro').users
            if chro:
                for users in chro:
                    email_cc = ''
                    mail_group = self.env['mail_cc_config'].search([],order="id desc",limit=1).mail_to_appr_manager.ids
                    mail_to = []
                    if mail_group:
                        emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                        mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    email_cc = ",".join(mail_to) or ''
                    appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                    email_cc = ','.join(appraisal_manager.mapped("email")) if appraisal_manager else ''
                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                    user_name = users.employee_ids.name if users.employee_ids.name else ''
                    template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Resend | HR to CHRO',send_by = 'hr_chro',email_cc=email_cc).sudo().send_mail(var, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='Record Send!.')
        else:
            raise ValidationError ('Please select the validated records for CHRO Approval.')
    
        
    @api.model
    def action_send_to_chro(self):
        active_ids = self.env.context.get('active_ids', [])
        promotion = self.env['shared_increment_promotion'].search([('id', 'in', active_ids),('status','=','pending_at_hod'),('iaas_ids','in',self.env.uid)])
        template = self.env.ref('kw_appraisal.appraisal_review_email_template')
        write_query = ''
        var = 0
        if promotion:
            for rec in promotion:
                var =  rec.id
                write_query += f"update shared_increment_promotion set status='pending_at_chro',chro_inc_auto={rec.hod_inc_auto},chro_inc_auto_2={rec.hod_inc_auto},chro_amount_auto={rec.hod_amount_auto},chro_actual_ctc={rec.hod_actual_ctc},send_to_chro=true where id = {rec.id};"
            if len(write_query) > 0:
                self.env.cr.execute(write_query)
            chro = self.env.ref('kw_appraisal.group_appraisal_chro').users
            if chro:
                for users in chro:
                    email_cc = ''
                    mail_group = self.env['mail_cc_config'].search([('period_id','=',rec.period_id.id)],limit=1).mail_to_appr_manager.ids
                    mail_to = []
                    if mail_group:
                        emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                        mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    email_cc = ",".join(mail_to) or ''
                    # appraisal_manager = self.env.ref('kw_appraisal.group_appraisal_manager').users
                    # email_cc = ','.join(appraisal_manager.mapped("email")) if appraisal_manager else ''
                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                    user_name = users.employee_ids.name if users.employee_ids.name else ''
                    template.with_context(mail_user=user_name,mail_id=to_mail,subject='Increment Review | IAA to CHRO',send_by = 'hod',email_cc=email_cc).sudo().send_mail(var, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='Record Send!.')
        else:
            raise ValidationError('As CHRO, you can send data to CEO only.')
        

    @api.depends('employee_id','date_of_joining')
    def _compute_total_exp(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.date_of_joining:
                difference = relativedelta(datetime.now(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months

            if rec.employee_id.work_experience_ids:
                for exp_data in rec.employee_id.work_experience_ids:
                    exp_difference = relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:  
                rec.experience = " %s.%s " % (total_years, total_months)
            else:
                rec.experience = ''
    """Only manager can remove the data"""
    def unlink(self):
        if not self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            raise UserError('You can not delete any data.')
        return super(SharedIncrementPromotion, self).unlink()

    """Computing grade band"""
    def _compute_grade_band(self):
        for rec in self:
            if rec.grade_id:
                rec.grade_band = f"{rec.grade_id.name}{'-' if rec.emp_band else ''}{rec.emp_band.name[5:] if rec.emp_band and len(rec.emp_band.name) > 5 else ''}"
                rec.new_grade_band = f"{rec.new_grade_id.name if rec.new_band_id and rec.new_grade_id else rec.grade_id.name if rec.new_band_id else '--'}{'-' if rec.new_band_id else ''}{rec.new_band_id.name[5:] if rec.new_band_id and len(rec.new_band_id.name) > 5 else ''}"

    def action_btn_edit_by_hr_after_submit(self):
        if self.status  in('completed','mail_send','hold') and self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            form_view_id = self.env.ref('kw_appraisal.change_increment_promotion_form').id
            action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_promotion',
                'res_id':self.id,
                'target': 'new',
                }
            return action
    def action_btn_submit_by_hr_after_ceo_submit(self):
        if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            self.env['increment_promotion_log'].create({
                'appraisal_id': self.id,
                'employee_id':self.env.user.employee_ids.id,
                'old_inc_auto':self.chro_inc_auto_2,
                'new_inc_ctc':self.chro_inc_auto,
                'remark':self.hr_remark,
                'edit_by':'hr'
            })
            self.chro_inc_auto_2 = self.chro_inc_auto
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        query1 = query2 = query3 = query4 = ''
        inc1 = inc2 = inc3 = inc4 = []
        if not self.env.context.get('published'):
            if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
                query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
                self._cr.execute(query1)
                query_result1 = self._cr.fetchall()
                inc1 = [id_tuple[0] for id_tuple in query_result1]
            if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
                query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
                self._cr.execute(query2)
                query_result2 = self._cr.fetchall()
                inc2 = [id_tuple[0] for id_tuple in query_result2]
            if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
                query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
                self._cr.execute(query3)
                query_result3 = self._cr.fetchall()
                inc3 = [id_tuple[0] for id_tuple in query_result3]
            if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
                query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
                self._cr.execute(query4)
                query_result4 = self._cr.fetchall()
                inc4 = [id_tuple[0] for id_tuple in query_result4]
        else:
            query3 = f"SELECT id FROM shared_increment_promotion where status in ('mail_send','resentdata_submitted_chro','resent_chro')"
            self._cr.execute(query3)
            query_result3 = self._cr.fetchall()
            inc3 = [id_tuple[0] for id_tuple in query_result3]
            # if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            #     query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
            #     self._cr.execute(query4)
            #     query_result4 = self._cr.fetchall()
            #     inc4 = [id_tuple[0] for id_tuple in query_result4]
            # if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            #     query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'resent_chro'"
            #     self._cr.execute(query3)
            #     query_result3 = self._cr.fetchall()
            #     inc3 = [id_tuple[0] for id_tuple in query_result3]

            
        inc = inc4 + inc3 + inc2 + inc1
        args += [('id', 'in', inc)]

        return super()._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        query1 = query2 = query3 = query4 = ''
        inc1 = inc2 = inc3 = inc4 = []
        if not self.env.context.get('published'):
            if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
                query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
                self._cr.execute(query1)
                query_result1 = self._cr.fetchall()
                inc1 = [id_tuple[0] for id_tuple in query_result1]
            if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
                query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
                self._cr.execute(query2)
                query_result2 = self._cr.fetchall()
                inc2 = [id_tuple[0] for id_tuple in query_result2]
            if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
                query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
                self._cr.execute(query3)
                query_result3 = self._cr.fetchall()
                inc3 = [id_tuple[0] for id_tuple in query_result3]
            if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
                query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
                self._cr.execute(query4)
                query_result4 = self._cr.fetchall()
                inc4 = [id_tuple[0] for id_tuple in query_result4]
        else:
            # if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            #     query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
            #     self._cr.execute(query4)
            #     query_result4 = self._cr.fetchall()
            #     inc4 = [id_tuple[0] for id_tuple in query_result4]
            # if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
                query3 = f"SELECT id FROM shared_increment_promotion where status in ('mail_send','resentdata_submitted_chro','resent_chro')"
                self._cr.execute(query3)
                query_result3 = self._cr.fetchall()
                inc3 = [id_tuple[0] for id_tuple in query_result3]
                
        inc = inc4 + inc3 + inc2 + inc1
        domain += [('id', 'in', inc)]


        return super(SharedIncrementPromotion, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        query1 = query2 = query3 = query4 = ''
        inc1 = inc2 = inc3 = inc4 = []
        if not self.env.context.get('published'):

            if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
                query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
                self._cr.execute(query1)
                query_result1 = self._cr.fetchall()
                inc1 = [id_tuple[0] for id_tuple in query_result1]
            if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
                query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
                self._cr.execute(query2)
                query_result2 = self._cr.fetchall()
                inc2 = [id_tuple[0] for id_tuple in query_result2]
            if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
                query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
                self._cr.execute(query3)
                query_result3 = self._cr.fetchall()
                inc3 = [id_tuple[0] for id_tuple in query_result3]
            if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
                query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
                self._cr.execute(query4)
                query_result4 = self._cr.fetchall()
                inc4 = [id_tuple[0] for id_tuple in query_result4]
        else:
            # if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
            #     query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
            #     self._cr.execute(query4)
            #     query_result4 = self._cr.fetchall()
            #     inc4 = [id_tuple[0] for id_tuple in query_result4]
            query3 = f"SELECT id FROM shared_increment_promotion where status in ('mail_send','resentdata_submitted_chro','resent_chro')"
            self._cr.execute(query3)
            query_result3 = self._cr.fetchall()
            inc3 = [id_tuple[0] for id_tuple in query_result3]
                
        inc = inc4 + inc3 + inc2 + inc1
        domain += [('id', 'in', inc)]
        return super(SharedIncrementPromotion,self).search_read(domain, fields, offset, limit, order)
        
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     query1 = query2 = query3 = query4 = ''
    #     inc1 = inc2 = inc3 = inc4 = []
    #     if not self.env.context.get('published'):
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
    #             query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
    #             self._cr.execute(query1)
    #             query_result1 = self._cr.fetchall()
    #             inc1 = [id_tuple[0] for id_tuple in query_result1]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
    #             query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
    #             self._cr.execute(query2)
    #             query_result2 = self._cr.fetchall()
    #             inc2 = [id_tuple[0] for id_tuple in query_result2]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
    #     else:
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'resent_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
            
    #     inc = inc4 + inc3 + inc2 + inc1
    #     args += [('id', 'in', inc)]

    #     return super()._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     print('8888888888888888888888888888888888888888')
    #     query1 = query2 = query3 = query4 = ''
    #     inc1 = inc2 = inc3 = inc4 = []
    #     if not self.env.context.get('published'):
    #         print('cedhgcbsjdchsjdbcd')
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
    #             query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
    #             self._cr.execute(query1)
    #             query_result1 = self._cr.fetchall()
    #             inc1 = [id_tuple[0] for id_tuple in query_result1]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
    #             query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
    #             self._cr.execute(query2)
    #             query_result2 = self._cr.fetchall()
    #             inc2 = [id_tuple[0] for id_tuple in query_result2]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
    #     else:
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             print('33333333333333333333333333333333333')
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'resent_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
    #             print('inc3==888888888888888888888==================',inc3)
            
    #     inc = inc4 + inc3 + inc2 + inc1
    #     domain += [('id', 'in', inc)]


    #     return super(SharedIncrementPromotion, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)



    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print('=============8888888888888888999999999999999999')

    #     query1 = query2 = query3 = query4 = ''
    #     inc1 = inc2 = inc3 = inc4 = []
    #     if not self.env.context.get('published'):

    #         if self.env.user.has_group('kw_appraisal.group_appraisal_iaa'):
    #             query1 = f"SELECT a.id FROM shared_increment_promotion a JOIN inc_promotion_iaa_user_rel b ON a.id = b.increment_id WHERE status = 'pending_at_hod' AND user_id = {self.env.uid} "
    #             self._cr.execute(query1)
    #             query_result1 = self._cr.fetchall()
    #             inc1 = [id_tuple[0] for id_tuple in query_result1]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_ceo'):
    #             query2 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_ceo'"
    #             self._cr.execute(query2)
    #             query_result2 = self._cr.fetchall()
    #             inc2 = [id_tuple[0] for id_tuple in query_result2]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'pending_at_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('draft', 'hold', 'completed')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
            
    #     else:
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_manager'):
    #             query4 = f"SELECT id FROM shared_increment_promotion WHERE status IN ('mail_send','resentdata_submitted_chro')"
    #             self._cr.execute(query4)
    #             query_result4 = self._cr.fetchall()
    #             inc4 = [id_tuple[0] for id_tuple in query_result4]
    #         if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
    #             query3 = f"SELECT id FROM shared_increment_promotion WHERE status = 'resent_chro'"
    #             self._cr.execute(query3)
    #             query_result3 = self._cr.fetchall()
    #             inc3 = [id_tuple[0] for id_tuple in query_result3]
    #     inc = inc4 + inc3 + inc2 + inc1
    #     domain += [('id', 'in', inc)]
    #     return super(SharedIncrementPromotion,self).search_read(domain, fields, offset, limit, order)
class AppraisalLog(models.Model):
    _name           = 'increment_promotion_log'
    _description    = "Appraisal Log"
    _order = 'create_date desc'

    appraisal_id = fields.Many2one('shared_increment_promotion', ondelete="cascade")
    employee_id = fields.Many2one('hr.employee')
    old_inc_auto = fields.Float('Inc(%)')
    new_inc_ctc  = fields.Float('Revised Inc(%)')
    remark = fields.Text()
    edit_by = fields.Selection([('hr', 'HR'), ('hod', 'IAA'),('chro', 'CHRO'),('ceo', 'CEO')],string="Role")
    old_revised_inc_auto = fields.Float('Old Revised Inc(%)')
    revised_inc_ctc  = fields.Float('New Revised Inc(%)')



class ViewIncrementPromotion(models.Model):
    _name = 'shared_increment_view'
    _description = "view of increment promotion"
    _auto = False

    employee_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(related='employee_id.name')
    emp_code = fields.Char(related='employee_id.emp_code')
    grade_id = fields.Many2one('kwemp_grade_master', string='Grade')
    job_id = fields.Many2one('hr.job', string='Designation')
    department_id = fields.Many2one('hr.department', string='Department')
    date_of_joining = fields.Date(string='Date of Joining')
    state = fields.Many2one('hr.appraisal.stages', string='Appraisal State')
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')], string="Budget Type")
    division = fields.Many2one('hr.department', string="Division", domain="[('dept_type.code', '=', 'division')]")
    emp_band = fields.Many2one(string=u'Band', comodel_name='kwemp_band_master')
    level = fields.Many2one('kw_grade_level', string='Grade Level')
    grade_band = fields.Char(compute='_compute_grade_band')
    new_grade_band = fields.Char(compute='_compute_grade_band')
    experience = fields.Char(compute='_compute_total_exp', string='Total Experience')
    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    status = fields.Selection([('draft', 'Draft'), ('pending_at_hod', 'Pending at IAA'), ('pending_at_chro', 'Pending at CHRO'),
                               ('pending_at_ceo', 'Pending at CEO'), ('hold', 'Hold'), ('completed', 'Approved by CEO'),
                               ('mail_send', 'Mail Sent'),('resent_chro','Resent To CHRO'),('resentdata_submitted_chro','Resent Data Submitted By CHRO')], string='Status')
    total_final_score = fields.Float("Appraisal Score",related='appraisal_id.total_final_score' )
    proposed_increment = fields.Float("Proposed Appraisal Inc(%)",related='appraisal_id.increment_percentage')
    actual_increment_percentage = fields.Float("Inc % (HR)")
    actual_increment_percentage_2 = fields.Float()
    actual_increment_amount = fields.Float("Inc Amt (HR)",digits=(16, 0))
    actual_ctc = fields.Float("New CTC (HR)",digits=(16, 0))
    current_ctc = fields.Float(string='Current CTC',digits=(16, 0))
    hod_id = fields.Many2one('hr.employee')
    hr_remark = fields.Text("HR Remark")
    send_to_hod = fields.Boolean()
    hod_inc_auto = fields.Float("IAA Inc (%)")
    hod_inc_auto_2 = fields.Float("")
    hod_amount_auto = fields.Float("IAA Amount",digits=(16, 0))
    hod_actual_ctc = fields.Float("IAA CTC",digits=(16, 0))
    hod_remark = fields.Text(string='IAA Remark')
    chro_inc_auto = fields.Float("CHRO Inc (%)")
    chro_inc_auto_2 = fields.Float("Inc")
    chro_amount_auto = fields.Float("CHRO Amount",digits=(16, 0))
    chro_actual_ctc = fields.Float("CHRO CTC",digits=(16, 0))
    chro_remark = fields.Text('CHRO Remark')
    send_to_chro = fields.Boolean()
    ceo_remark = fields.Text(string='CEO Remark')
    new_job_id = fields.Many2one('hr.job', string='New Designation')
    new_grade_id = fields.Many2one('kwemp_grade_master')
    new_band_id = fields.Many2one('kwemp_band_master')
    
    appraisal_id = fields.Many2one('hr.appraisal')
    add_in_appraisal = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    sbu_master_id = fields.Many2one('kw_sbu_master', string='SBU', help="SBU")
    sbu_name = fields.Char(related='sbu_master_id.name', string='SBU Name')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill')
    increment_effective_date = fields.Date(string='Increment Effective Date')
    appraisal_doc_attach = fields.Binary(string='Appraisal Document Attachment')
    iaas_ids = fields.Many2many('res.users', 'inc_promotion_iaa_user_rel', 'increment_id', 'user_id', 'IAAs')
    previous_increment  = fields.Float("Previous Inc",digits=(16, 0))
    increment_month = fields.Integer()
    id = fields.Integer(string='ID', readonly=True) 
    appraisal_log_ids = fields.One2many('increment_promotion_log','appraisal_id')
    check_hod_bool = fields.Boolean(compute='check_hod_login')
    applied_eos = fields.Boolean()
    amt_changed_by_hod = fields.Boolean(compute="compute_actual_increment_percentage")
    previous_increment_amt  = fields.Float("Previous Inc Amt",digits=(16, 0))
    last_working_day = fields.Date()
    changed_by_iaa = fields.Boolean()
    jd = fields.Html(compute='compute_jd_html')

    actual_revised_increment_percentage  = fields.Float()
    revised_increment = fields.Float("Revised Inc (%)")
    revised_amount = fields.Float("Revised Amount",digits=(16, 0))
    revised_job_id =fields.Many2one('hr.job',string='Revised Designation')
    revised_grade_id = fields.Many2one('kwemp_grade_master')
    revised_band_id = fields.Many2one('kwemp_band_master')
    revised_ctc = fields.Float("Revised CTC",digits=(16, 0))
    revised_jd = fields.Html(compute='compute_jd_html')
    revised_jd_boolean = fields.Boolean()
    revised_hr_remark = fields.Text("Revised HR Remark")
    revised_chro_remark = fields.Text("Revised CHRO Remark")
    
    @api.depends('new_job_id','revised_job_id')
    def compute_jd_html(self):
        for rec in self:
            job_role_id = self.env['hr.job.role'].search([('designations', 'in', [rec.new_job_id.id])], limit=1)
            if job_role_id and isinstance(job_role_id.description, str):
                rec.jd = job_role_id.description
            new_job_role_id = self.env['hr.job.role'].search([('designations', 'in', [rec.revised_job_id.id])], limit=1)
            if new_job_role_id and isinstance(new_job_role_id.description, str):
                rec.revised_jd = new_job_role_id.description



    def action_btn_log(self):
        form_view_id = self.env.ref('kw_appraisal.increment_promotion_log_details_view_form').id
        action = {
                'type': 'ir.actions.act_window',
                'name': f'Change Details : {self.name}',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'shared_increment_view',
                'res_id':self.id,
                'target': 'new',
                'flags': {'mode':'readonly'},
                'context': {'create': False,'edit': False,'delete': False}
            }
        return action


    def _compute_grade_band(self):
        for rec in self:
            if rec.grade_id:
                rec.grade_band = f"{rec.grade_id.name}{'-' if rec.emp_band else ''}{rec.emp_band.name[5:] if rec.emp_band and len(rec.emp_band.name) > 5 else ''}"
                rec.new_grade_band = f"{rec.new_grade_id.name}{'-' if rec.new_band_id else ''}{rec.new_band_id.name[5:] if rec.new_band_id and len(rec.new_band_id.name) > 5 else ''}"
    @api.depends('employee_id','date_of_joining')
    def _compute_total_exp(self):
        for rec in self:
            total_years, total_months = 0, 0
            if rec.date_of_joining:
                difference = relativedelta(datetime.now(), rec.date_of_joining)
                total_years += difference.years
                total_months += difference.months

            if rec.employee_id.work_experience_ids:
                for exp_data in rec.employee_id.work_experience_ids:
                    exp_difference = relativedelta(exp_data.effective_to, exp_data.effective_from)
                    total_years += exp_difference.years
                    total_months += exp_difference.months

            if total_months >= 12:
                total_years += total_months // 12
                total_months = total_months % 12

            if total_years > 0 or total_months > 0:  
                rec.experience = " %s.%s " % (total_years, total_months)
            else:
                rec.experience = ''
    """Only manager can remove the data"""

    @api.depends('status','iaas_ids')
    def check_hod_login(self):
        for rec in self:
            if self.env.uid in rec.iaas_ids.ids and rec.status == 'pending_at_hod':
                rec.check_hod_bool = True

    # @api.depends('employee_id')
    # def _compute_eos(self):
    #     for rec in self:
    #         resignation = self.env['kw_resignation'].sudo().search(
    #             [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
    #         rec.applied_eos = True if resignation else False

    @api.depends('actual_increment_percentage','hod_inc_auto')
    def compute_actual_increment_percentage(self):
        for record in self:
            record.amt_changed_by_hod = True if record.hod_inc_auto and record.actual_increment_percentage != record.hod_inc_auto else False
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} as (
                           select * from shared_increment_promotion
        )"""
        self.env.cr.execute(query)