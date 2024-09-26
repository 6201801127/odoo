from odoo import models, api, fields
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError






class kw_cpd_applications(models.Model):
    _name = 'kw_cpd_applications'
    _rec_name = 'employee_id'
    _description = 'Certified Professional Drive'


    employee_id = fields.Many2one('hr.employee', string="Employee Name",readonly=True,required=True,default=lambda self: self.env.user.employee_ids.id)
    institute_id = fields.Many2one('kw_institute_master', string="Institute Name",required=True)
    course_id = fields.Many2one('kw_course_master', string="Course Name",required=True,domain="[('institute_id', '=', institute_id)]")
    course_duration = fields.Integer(string='Course Duration (In Days)',required=True)
    course_fee = fields.Float(string='Course Fee (INR)',required=True)
    to_disburse_course_fee = fields.Float(string='Disbursement Amount (INR)')
    description = fields.Text(required=True)
    is_eligible = fields.Boolean(compute='_check_emp_eligibility')
    is_user_department_head = fields.Boolean(compute='_check_emp_department_head')
    is_user_l_and_k_mngr = fields.Boolean(compute='_check_emp_l_and_k_mngr')
    show_user_apply_cpd_btn = fields.Boolean(compute='_check_user_apply_cpd')
    show_ra_approve_cpd_btn = fields.Boolean(compute='_check_ra_approve_cpd')
    show_dh_approve_cpd_btn = fields.Boolean(compute='_check_dh_approve_cpd')
    show_lnk_approve_cpd_btn = fields.Boolean(compute='_check_lnk_approve_cpd')
    show_chro_approve_cpd_btn = fields.Boolean(compute='_check_chro_approve_cpd')
    show_reject_button = fields.Boolean(compute='_check_reject_button')
    state = fields.Selection(selection=[(0, 'Draft'), (1,'Pending at RA'), (2,'Pending at Dept Head'), (3,'Pending at L&K'),(4,'Pending at CHRO'),(5,'Approved'),(6,'Rejected'),(-1,'Hold')],default=0,string='Status')
    approval_log_ids = fields.One2many('kw_cpd_approval_log', 'cpd_id', string='Approval Logs')
    cpd_certification_id = fields.Many2one('kw_cpd_certification')
    certificate_file = fields.Binary(string='Upload Certificate',store=True)
    invoice_file = fields.Binary(string='Upload Invoice',store=True)
    is_payment_requested = fields.Boolean(default=False)
    is_disbursed = fields.Boolean(default=False)
    applied_date = fields.Date()






    @api.model
    def create(self, vals):
        record = super(kw_cpd_applications, self).create(vals)
        if record.is_eligible != True:
            raise ValidationError("Only Employees who have spent more than 3 years at CSM and have a grade of M5 or above can apply.")
        else:
            return record


    @api.onchange('course_fee')
    def calculate_to_disburse_course_fee(self):
        percentage = float(self.env['kw_cpd_percentage_config'].search([]).percentage)
        for rec in self:
            if rec.course_fee:
                rec.to_disburse_course_fee = rec.course_fee * percentage / 100.0


    @api.depends('employee_id')
    def _check_emp_eligibility(self):
        lead_managing_grade = ['M5','M6','M7','M8','M9','M10','E1','E2','E3','E4','E5']

        for record in self:
            if record.employee_id and record.employee_id.date_of_joining and record.employee_id.grade:
                three_years_ago = date.today() - relativedelta(years=3)
                if record.employee_id.date_of_joining <= three_years_ago and record.employee_id.grade.name in lead_managing_grade:
                    record.is_eligible = True
                else:
                    record.is_eligible = False
            else:
                record.is_eligible = False

    @api.depends('employee_id')
    def _check_emp_department_head(self):
        for record in self:
            if record.employee_id and record.employee_id.department_id.manager_id and record.employee_id.id == record.employee_id.department_id.manager_id.id:
                record.is_user_department_head = True
            else:
                record.is_user_department_head = False

    @api.depends()
    def _check_emp_l_and_k_mngr(self):
        for record in self:
            if self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager'):
                record.is_user_l_and_k_mngr = True
            else:
                record.is_user_l_and_k_mngr = False


    @api.depends()
    def _check_reject_button(self):
        for record in self:
            if (record.state == 1 and record.employee_id.parent_id.id == self.env.user.employee_ids.id) or (record.state == 2 and self.env.user.employee_ids.id == record.employee_id.department_id.manager_id.id) or (record.state == 3 and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')) or (record.state == 4 and self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                record.show_reject_button = True
            else:
                record.show_reject_button = False

    @api.depends()
    def _check_ra_approve_cpd(self):
        for record in self:
            if (record.state == 1 and record.employee_id.parent_id.id == self.env.user.employee_ids.id):
                record.show_ra_approve_cpd_btn = True
            else:
                record.show_ra_approve_cpd_btn = False

    @api.depends()
    def _check_dh_approve_cpd(self):
        for record in self:
            if (record.state == 2 and record.employee_id.department_id.manager_id.id == self.env.user.employee_ids.id):
                record.show_dh_approve_cpd_btn = True
            else:
                record.show_dh_approve_cpd_btn = False

    @api.depends()
    def _check_lnk_approve_cpd(self):
        for record in self:
            if (record.state == 3 and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')):
                record.show_lnk_approve_cpd_btn = True
            else:
                record.show_lnk_approve_cpd_btn = False

    @api.depends('employee_id')
    def _check_user_apply_cpd(self):
        for record in self:
            if (record.state in [-1,0] and self.env.user.employee_ids.id == record.employee_id.id):
                record.show_user_apply_cpd_btn = True
            else:
                record.show_user_apply_cpd_btn = False

    @api.depends()
    def _check_chro_approve_cpd(self):
        for record in self:
            if (record.state == 4 and self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                record.show_chro_approve_cpd_btn = True
            else:
                record.show_chro_approve_cpd_btn = False



    def kw_cpd_apply_btn(self):
        self.state = 1
        self.applied_date = date.today()

        self.env['kw_cpd_approval_log'].create({'cpd_id':self.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                               'status':'Applied','remark':'OK','pending_at':self.state})
        
        template = self.env.ref('kw_cpd.kw_cpd_applications_apply_mail_template')
        applied_user = self.employee_id.name if self.employee_id.name else ''
        template.with_context(applied_user=applied_user).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")


     

    def cpd_action_buttons(self):
        view_id = self.env.ref('kw_cpd.kw_cpd_approval_wizard_form').id
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_cpd_approval_wizard',
            'target': 'new',
        }



    def cpd_auto_reject_applications(self):
        all_cpd_applications = self.env['kw_cpd_applications'].sudo().search([('state','in',[1,2,3,4])])
        for ids in all_cpd_applications:
            all_dates = []
            all_actions = ids.approval_log_ids
            for rec in all_actions:
                all_dates.append(rec.action_taken_on)
            latest_date = max(all_dates)
            if latest_date + timedelta(days=30) < date.today():
                ids.state = 6
                self.env['kw_cpd_approval_log'].create({'cpd_id':ids.id,'action_taken_by':False,'action_taken_on':date.today(),
                                                'status':'Rejected','remark':'Auto Rejected','pending_at':ids.state})




    @api.multi
    def cpd_approval_server_action(self):
        department_heads_ids = self.env['hr.department'].sudo().search([]).mapped('manager_id').ids
        env_user_id = self.env.user.id

        tree_view_id = self.env.ref('kw_cpd.kw_cpd_application_apply_tree').id
        form_view_id = self.env.ref('kw_cpd.kw_cpd_application_apply_form').id
        action = {
                'type': 'ir.actions.act_window',
                'name': 'Cpd Approvals',
                'view_mode': 'form,tree',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'res_model': 'kw_cpd_applications',
                'context':{'create': False,'edit':False,'delete':False,'import':False}
                }
                

        # DO NOT CHANGE THE IF CONDITIONS STRUCTURE
        if self.env.user.has_group('kw_employee.group_hr_ra'):
            action['domain'] = ['&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id)]
        if self.env.user.employee_ids.id in department_heads_ids:
            action['domain'] = ['&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
        if self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager'):
            action['domain'] = [('state', '=', 3)]
        if self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            action['domain'] = [('state', '=', 4)]
        if self.env.user.has_group('kw_employee.group_hr_ra') and self.env.user.employee_ids.id in department_heads_ids:
            action['domain'] = ['|','&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id),'&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
        if self.env.user.has_group('kw_employee.group_hr_ra') and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager'):
            action['domain'] = ['|',('state','=',3),'&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id)]
        if self.env.user.has_group('kw_employee.group_hr_ra') and self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            action['domain'] = ['|',('state','=',4),'&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id)]
        if self.env.user.employee_ids.id in department_heads_ids and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager'):
            action['domain'] = ['|',('state','=',3),'&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
        if self.env.user.employee_ids.id in department_heads_ids and self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            action['domain'] = ['|',('state','=',4),'&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
        if self.env.user.has_group('kw_employee.group_hr_ra') and self.env.user.employee_ids.id in department_heads_ids and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager'):
            action['domain'] = ['|','|',('state','=',3),'&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id),'&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
        if self.env.user.has_group('kw_employee.group_hr_ra') and self.env.user.employee_ids.id in department_heads_ids and self.env.user.has_group('kw_appraisal.group_appraisal_chro'):
            action['domain'] = ['|','|',('state','=',4),'&',('state','=',1),('employee_id.parent_id.user_id','=',env_user_id),'&',('state','=',2),('employee_id.department_id.manager_id.user_id','=',env_user_id)]
            


        return action














class kw_cpd_approval_log(models.Model):
    _name = 'kw_cpd_approval_log'
    _description = 'Certified Professional Drive Approval Log'


    cpd_id = fields.Many2one('kw_cpd_applications')
    action_taken_by = fields.Many2one('hr.employee')
    action_taken_on = fields.Date()
    status = fields.Char()
    remark = fields.Char()
    pending_at = fields.Selection(selection=[(1,'RA'), (2,'Dept Head'), (3,'L&K'),(4,'CHRO'),(5,''),(6,'')])













class kw_cpd_approval_wizard(models.TransientModel):
    _name = "kw_cpd_approval_wizard"
    _description = "Certified Professional Drive Wizard"

    remark = fields.Text()



    def cpd_action_submit_btn(self):
        ctx_val = self.env.context.get('ctx_val')
        active_id = self.env.context.get('active_id')
        if ctx_val and active_id:
            cpd_record = self.env['kw_cpd_applications'].sudo().search([('id','=',active_id)])
            if cpd_record and ctx_val == 'RA_APPROVAL':
                for rec in cpd_record:
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.parent_id.id):
                        rec.state = 2
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.parent_id.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id):
                        rec.state = 3
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.parent_id.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')):
                        rec.state = 4
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.parent_id.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')) and (self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                        rec.state = 5

                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})
                    
                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    email_to = rec.employee_id.work_email if rec.employee_id.work_email else []
                    dear_user = rec.employee_id.name if rec.employee_id.name else 'User'
                    body = f"Your CPD application has been approved by {rec.employee_id.parent_id.name}."
                    state = 'Approved'
                    act_category = 'Reporting Authority'
                    template.with_context(email_to=email_to,dear_user=dear_user,act_category=act_category,state=state,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_to_next_authority')
                    email_to = rec.employee_id.department_id.manager_id.work_email if rec.employee_id.department_id.manager_id.work_email else []
                    emp_name = rec.employee_id.name
                    dear_user = rec.employee_id.department_id.manager_id.name if rec.employee_id.department_id.manager_id.name else 'User'
                    body = f"{rec.employee_id.parent_id.name} has approved the CPD application for {rec.employee_id.name}.Please review and provide your approval."
                    template.with_context(email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")




            elif ctx_val == 'DH_APPROVAL':
                for rec in cpd_record:
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id): 
                        rec.state = 3
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')):
                        rec.state = 4
                    if (self.env.user.employee_ids.id) and (self.env.user.employee_ids.id == rec.employee_id.department_id.manager_id.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')) and (self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                        rec.state = 5

                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})


                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email]))
                    dear_user = rec.employee_id.name + ' and ' + rec.employee_id.parent_id.name
                    body = f"The CPD application for {rec.employee_id.name} has been approved by {rec.employee_id.department_id.manager_id.name}."
                    state = 'Approved'
                    act_category = 'Department Head'
                    template.with_context(email_to=email_to,dear_user=dear_user,act_category=act_category,state=state,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_to_next_authority')
                    email_to= ','.join(self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email"))
                    emp_name = rec.employee_id.name
                    dear_user = 'Learning & Knowledge (L&K) Team'
                    body = f"The CPD application for {rec.employee_id.name} has been approved by {rec.employee_id.department_id.manager_id.name}.Please review and provide your input."
                    template.with_context(email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")




            elif ctx_val == 'LNK_APPROVAL':
                for rec in cpd_record:
                    if (self.env.user.employee_ids.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')):
                        rec.state = 4
                    if (self.env.user.employee_ids.id) and (self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')) and (self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                        rec.state = 5

                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})


                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email, rec.employee_id.department_id.manager_id.work_email]))
                    dear_user = rec.employee_id.name + ', ' + rec.employee_id.parent_id.name + ' and ' + rec.employee_id.department_id.manager_id.name
                    body = f"The CPD application for {rec.employee_id.name} has been approved by the Learning & Knowledge team."
                    state = 'Approved'
                    act_category = 'L&K'
                    template.with_context(email_to=email_to,dear_user=dear_user,act_category=act_category,state=state,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_to_next_authority')
                    email_to= ','.join(self.env.ref('kw_appraisal.group_appraisal_chro').users.mapped("email"))
                    emp_name = rec.employee_id.name
                    dear_user = 'CHRO'
                    body = f"The CPD application for {rec.employee_id.name} has been approved by the Learning & Knowledge team.Please review and provide your approval."
                    template.with_context(email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")


            if cpd_record and ctx_val == 'LNK_HOLD':
                for rec in cpd_record:
                    rec.state = -1
                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Hold','remark':self.remark,'pending_at':False})

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    email_to = rec.employee_id.work_email
                    email_cc = ','.join(filter(None, [rec.employee_id.parent_id.work_email,rec.employee_id.department_id.manager_id.work_email]))
                    dear_user = rec.employee_id.name
                    body = f"Your Certified Professional Drive (CPD) application has been placed on hold by the L&K department."
                    state = 'Placed on Hold'
                    act_category = 'L&K'
                    self.env.cr.execute("""SELECT remark FROM kw_cpd_approval_log WHERE cpd_id = %s AND status = %s ORDER BY ID DESC LIMIT 1""", (rec.id, 'Hold'))
                    reject_reason = 'Reason: ' + self.env.cr.fetchone()[0]
                    template.with_context(email_to=email_to,email_cc=email_cc,dear_user=dear_user,act_category=act_category,state=state,body=body,reject_reason=reject_reason).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")




            elif ctx_val == 'CHRO_APPROVAL':
                for rec in cpd_record:
                    if (self.env.user.employee_ids.id) and (self.env.user.has_group('kw_appraisal.group_appraisal_chro')):
                        rec.state = 5

                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    lnk_managers= ','.join(self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email"))
                    email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email, rec.employee_id.department_id.manager_id.work_email,lnk_managers]))
                    dear_user = rec.employee_id.name + ', ' + rec.employee_id.parent_id.name + ', ' + rec.employee_id.department_id.manager_id.name + ' and L&K Team'
                    body = f"The CPD application for {rec.employee_id.name} has been approved by the CHRO."
                    state = 'Approved'
                    act_category = 'CHRO'
                    template.with_context(email_to=email_to,dear_user=dear_user,act_category=act_category,state=state,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    
            elif ctx_val == 'REJECTED':
                for rec in cpd_record:
                    state_before_approval = rec.state
                    rec.state = 6
                    self.env['kw_cpd_approval_log'].create({'cpd_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                            'status':'Rejected','remark':self.remark,'pending_at':rec.state})
                    

                    template = self.env.ref('kw_cpd.kw_cpd_applications_take_action_mail_template_to_employee')
                    state = 'Rejected'
                    if state_before_approval == 1:
                        email_to = rec.employee_id.work_email if rec.employee_id.work_email else []
                        dear_user = rec.employee_id.name if rec.employee_id.name else 'User'
                        body = f"Your CPD application has been rejected by {self.env.user.employee_ids.name}."
                        act_category = 'Reporting Authority'
                        self.env.cr.execute("""SELECT remark FROM kw_cpd_approval_log WHERE cpd_id = %s AND action_taken_by = %s AND status = %s ORDER BY ID DESC LIMIT 1""", (rec.id, rec.employee_id.parent_id.id, 'Rejected'))
                    elif state_before_approval == 2:
                        email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email]))
                        dear_user = rec.employee_id.name + ' and ' + rec.employee_id.parent_id.name
                        body = f"The CPD application for {rec.employee_id.name} has been rejected by {rec.employee_id.department_id.manager_id.name}."
                        act_category = 'Department Head'
                        self.env.cr.execute("""SELECT remark FROM kw_cpd_approval_log WHERE cpd_id = %s AND action_taken_by = %s AND status = %s ORDER BY ID DESC LIMIT 1""", (rec.id, rec.employee_id.department_id.manager_id.id, 'Rejected'))
                    elif state_before_approval == 3:
                        email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email, rec.employee_id.department_id.manager_id.work_email]))
                        dear_user = rec.employee_id.name + ', ' + rec.employee_id.parent_id.name + ' and ' + rec.employee_id.department_id.manager_id.name
                        body = f"The CPD application for {rec.employee_id.name} has been approved by the Learning & Knowledge team."
                        act_category = 'L&K'
                        self.env.cr.execute("""SELECT remark FROM kw_cpd_approval_log WHERE cpd_id = %s AND status = %s ORDER BY ID DESC LIMIT 1""", (rec.id, 'Rejected'))
                    elif state_before_approval == 4:
                        lnk_managers= ','.join(self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email"))
                        email_to = ','.join(filter(None, [rec.employee_id.work_email, rec.employee_id.parent_id.work_email, rec.employee_id.department_id.manager_id.work_email,lnk_managers]))
                        dear_user = rec.employee_id.name + ', ' + rec.employee_id.parent_id.name + ', ' + rec.employee_id.department_id.manager_id.name + ' and L&K Team'
                        body = f"The CPD application for {rec.employee_id.name} has been rejected by the CHRO."
                        act_category = 'CHRO'
                        self.env.cr.execute("""SELECT remark FROM kw_cpd_approval_log WHERE cpd_id = %s AND status = %s ORDER BY ID DESC LIMIT 1""", (rec.id, 'Rejected'))


                    reject_reason = 'Reason: ' + self.env.cr.fetchone()[0]
                    template.with_context(email_to=email_to,dear_user=dear_user,body=body,act_category=act_category,state=state,reject_reason=reject_reason).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")






















