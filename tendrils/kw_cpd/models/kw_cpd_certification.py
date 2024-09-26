from odoo import models, api, fields
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError






class kw_cpd_certification(models.Model):
    _name = 'kw_cpd_certification'
    _rec_name = 'employee_id'
    _description = 'CPD Certification'



    employee_id = fields.Many2one('hr.employee', string="Employee Name",readonly=True,required=True,default=lambda self: self.env.user.employee_ids.id)
    cpd_application_ids = fields.One2many('kw_cpd_applications', 'cpd_certification_id', string='CPD Applications')
    state = fields.Selection(selection=[(0, 'Draft'), (1,'Pending at L&K'),(2,'Pending at CORE HR'),(3,'Pending at FINANCE'),(4,'Disbursed'),(5,'Rejected')],default=0,string='Status')
    approval_log_ids = fields.One2many('kw_cpd_certification_log', 'cpd_cert_id', string='Post Approval Details')
    show_reject_button = fields.Boolean(compute='_check_reject_button')
    agreement_file = fields.Binary(string='Agreement')
    agreement_remark = fields.Text(string='Remark of Agreement')
    is_user_core_hr = fields.Boolean(compute='_check_emp_core_hr')





    @api.onchange('employee_id')
    def get_cpd_application_ids(self):
        self.cpd_application_ids = False
        application_ids = self.env['kw_cpd_applications'].sudo().search([('employee_id','=',self.employee_id.id),('state','=',5),('is_payment_requested','=',False)])
        self.cpd_application_ids = application_ids



    @api.depends()
    def _check_emp_core_hr(self):
        for record in self:
            if self.env.user.has_group('kw_cpd.group_kw_cpd_core_hr'):
                record.is_user_core_hr = True
            else:
                record.is_user_core_hr = False

    

    @api.model
    def create(self, vals):
        record = super(kw_cpd_certification, self).create(vals)
        cpd_application_ids = record.cpd_application_ids
        if not cpd_application_ids:
            raise ValidationError("Without any Approved CPD you cannot make a request ..!")
        
        for rec in cpd_application_ids:
            if rec.applied_date and rec.course_duration:
                if rec.applied_date + timedelta(days=rec.course_duration) > date.today():
                    raise ValidationError("You cannot apply for disbursement before the completion of the course ..!")
                
        for rec in cpd_application_ids:
            if not rec.certificate_file or not rec.invoice_file:
                raise ValidationError("Upload all the valid Documents ..!")
            
        for rec in cpd_application_ids:
                if rec.certificate_file and rec.invoice_file:
                    rec.is_payment_requested = True
        
        record.state = 1
        self.env['kw_cpd_certification_log'].create({'cpd_cert_id':record.id,'action_taken_by':record.env.user.employee_ids.id,'action_taken_on':date.today(),
                                               'status':'Applied','remark':'OK','pending_at':record.state})
        
        template = self.env.ref('kw_cpd.kw_cpd_certifications_take_action_mail_template')
        subject = f"Certificate Uploaded for CPD by {rec.employee_id.name}"
        email_to= ','.join(self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email"))
        emp_name = rec.employee_id.name
        dear_user = 'Learning & Knowledge (L&K) Team'
        body = f"{rec.employee_id.name} has uploaded their certificate for the approved CPD course. Please review the document and proceed with the next steps."
        template.with_context(subject=subject,email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        return record




    def cpd_certificate_verification(self):
        view_id = self.env.ref('kw_cpd.kw_cpd_cert_wizard_form').id
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_cpd_cert_approval_wizard',
            'target': 'new',
        }

    @api.depends()
    def _check_reject_button(self):
        for record in self:
            if (record.state == 1 and self.env.user.has_group('kw_cpd.group_kw_cpd_lnk_manager')) or (record.state == 2 and self.env.user.has_group('kw_cpd.group_kw_cpd_core_hr')) or (record.state == 3 and self.env.user.has_group('kw_cpd.group_kw_cpd_finance')):
                record.show_reject_button = True
            else:
                record.show_reject_button = False









class kw_cpd_certification_log(models.Model):
    _name = 'kw_cpd_certification_log'
    _description = 'CPD Certification Approval Log'


    cpd_cert_id = fields.Many2one('kw_cpd_certification')
    action_taken_by = fields.Many2one('hr.employee')
    action_taken_on = fields.Date()
    status = fields.Char()
    remark = fields.Char()
    pending_at = fields.Selection(selection=[(1,'L&K'), (2,'CORE HR'), (3,'FINANCE'),(4,''),(5,'')])














class kw_cpd_cert_approval_wizard(models.TransientModel):
    _name = "kw_cpd_cert_approval_wizard"
    _description = "CPD Certification Wizard"

    remark = fields.Text()



    def cpd_cert_action_submit_btn(self):
        ctx_val = self.env.context.get('ctx_val')
        active_id = self.env.context.get('active_id')
        if ctx_val and active_id:
            cpd_cert_record = self.env['kw_cpd_certification'].sudo().search([('id','=',active_id)])

            if cpd_cert_record and ctx_val == 'LNK_VERIFICATION':
                for rec in cpd_cert_record:
                    rec.state = 2
                    self.env['kw_cpd_certification_log'].create({'cpd_cert_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})
                    
                    template = self.env.ref('kw_cpd.kw_cpd_certifications_take_action_mail_template')
                    subject = f"CPD Certificate Review for {rec.employee_id.name}"
                    email_to= ','.join(self.env.ref('kw_cpd.group_kw_cpd_core_hr').users.mapped("email"))
                    emp_name = rec.employee_id.name
                    dear_user = 'CORE HR'
                    body = f"The Learning & Knowledge team has reviewed and redirected the CPD certificate uploaded by {rec.employee_id.name} for your further action."
                    template.with_context(subject=subject,email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    

            if cpd_cert_record and ctx_val == 'CORE_HR_VERIFICATION':
                for rec in cpd_cert_record:
                    rec.state = 3
                    self.env['kw_cpd_certification_log'].create({'cpd_cert_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})
                    
                    template = self.env.ref('kw_cpd.kw_cpd_certifications_take_action_mail_template')
                    subject = f"CPD Reimbursement Processing for {rec.employee_id.name}"
                    email_list = self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email") + self.env.ref('kw_cpd.group_kw_cpd_finance').users.mapped("email")
                    email_to = ','.join(filter(None, email_list))
                    emp_name = rec.employee_id.name
                    dear_user = 'Finance Team and L&K Team'
                    body = f"CORE HR has reviewed and redirected the CPD certificate for {rec.employee_id.name} for reimbursement processing. Please proceed with the disbursement."
                    template.with_context(subject=subject,email_to=email_to,emp_name=emp_name,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    
            if cpd_cert_record and ctx_val == 'FINANCE_DISBURSEMENT':
                for rec in cpd_cert_record:
                    cpd_applications = rec.cpd_application_ids
                    for cpd in cpd_applications:
                        cpd.is_disbursed = True

                    rec.state = 4
                    self.env['kw_cpd_certification_log'].create({'cpd_cert_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Approved','remark':self.remark,'pending_at':rec.state})
                    
                    template = self.env.ref('kw_cpd.kw_cpd_certifications_take_action_mail_template')
                    subject = f"CPD Reimbursement Disbursed for {rec.employee_id.name}"
                    email_list = [rec.employee_id.work_email] + self.env.ref('kw_cpd.group_kw_cpd_lnk_manager').users.mapped("email") + self.env.ref('kw_cpd.group_kw_cpd_core_hr').users.mapped("email")
                    email_to = ','.join(filter(None, email_list))
                    dear_user = f'{rec.employee_id.name}, CORE HR and L&K Team'
                    body = f"The reimbursement amount for the CPD course undertaken by {rec.employee_id.name } has been successfully disbursed by the Finance team."
                    template.with_context(subject=subject,email_to=email_to,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    
            if cpd_cert_record and ctx_val == 'REJECTED':
                for rec in cpd_cert_record:
                    rec.state = 5
                    self.env['kw_cpd_certification_log'].create({'cpd_cert_id':rec.id,'action_taken_by':self.env.user.employee_ids.id,'action_taken_on':date.today(),
                                                        'status':'Rejected','remark':self.remark,'pending_at':rec.state})
                    
                    template = self.env.ref('kw_cpd.kw_cpd_certification_rejection_mail')
                    email_list = [rec.employee_id.work_email] + self.env.user.employee_ids.mapped('work_email')
                    email_to = ','.join(filter(None, email_list))
                    dear_user = rec.employee_id.name
                    body = f"Your certification for CPD has been rejected by {self.env.user.employee_ids.name}."
                    template.with_context(email_to=email_to,dear_user=dear_user,body=body).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")
