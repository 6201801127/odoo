from datetime import date
from kw_utility_tools import kw_validations
import datetime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KwCertification(models.Model):
    _name = 'kw_certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Certification"
    _rec_name = 'number'

    # def _default_employee(self):
    #     for rec in self.env['kw_certification'].sudo().search([]):
    #         if rec.suggested_by == 'Self':
    #             return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
    #         else:
    #             rec.suggested_by = False
    #             pass

    number = fields.Char(string='Certification Sequence No', default="New",
                         readonly=True, track_visibility='always')
    date_of_raised = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True,
                                     track_visibility='always')
    suggested_by = fields.Selection(string="Suggested By",
                             selection=[('Self', 'Self'),
                                        ('Others', 'Others')
                                        ], default="Self", track_visibility='always')
    raised_by_id = fields.Many2one('hr.employee', string="Suggested By",
                                   track_visibility='always', store=True)
    department_id = fields.Many2one('hr.department', readonly=1, track_visibility='always')
    require_department_id = fields.Many2one('hr.department', string='For Department', track_visibility='always', domain="[('dept_type','=',1)]")
    certification_type_id = fields.Many2one('kwmaster_stream_name', string='Certification Name',
                                            track_visibility='always',domain="[('course_id.code', '=', 'cert')]")
    technology_id = fields.Many2one('kw_skill_master', string='Technology',
                                    track_visibility='always')
    qualification_ids = fields.Many2many('kwmaster_stream_name', 'employee_qualification_rel', 'qualification_id', 'stream_id', string='Qualification', track_visibility='always',domain="[('course_id.course_type', '=', '1')]")
    year_of_experience = fields.Integer('Experience(Min)', track_visibility='always')
    year_of_experience_max = fields.Integer('Experience(Max)', track_visibility='always')
    no_of_candidate = fields.Integer('No of People', track_visibility='always')
    remarks = fields.Text('Remarks', track_visibility='always')
    assigned_user_ids = fields.Many2many('hr.employee', 'kw_employee_assigned_user_rel', 'employee_id', 'assigned_id',
                                       string='Assigned User')
    view_status_user_ids = fields.Many2many('hr.employee', 'kw_employee_view_status_rel', 'employee_id', 'view_status_id',)
    take_action_user_ids = fields.Many2many('hr.employee', 'kw_employee_take_action_rel', 'employee_id',
                                            'take_action_id', string="Pending At")
    
    assigned_emp_data = fields.One2many('assign_employee','certification_master_id')
    state = fields.Selection(string="Status",
                             selection=[('Draft', 'Draft'),
                                        ('Request Raised', 'Request Raised'),
                                        ('Assigned', 'Assigned'),
                                        ('Approved', 'Approved'),
                                        ('Closed', 'Closed')
                                        ], default="Draft", track_visibility='always')
    budget_for_certification = fields.Char('Budget For Certification',track_visibility='always')
    target_date = fields.Date('Target Date',track_visibility='always', required=True)
    enroll_policy = fields.Selection(string="Enroll policy", selection=[('Payment By Company','Payment By Company'),
                                                                        ('Payment By Employee','Payment By Employee'),
                                                                        ('Sharing','Sharing')],
                                     track_visibility='always')
    action_log_table_ids = fields.One2many('certification_log_table', 'certfication_con_id')
    cert_budget = fields.Char('Certification Budget')
    department_head_id = fields.Many2one('hr.employee')
    assign_button_hide_boolean = fields.Boolean(compute='assign_button_boolean_hide', store=False)
    accept_button_boolean = fields.Boolean(compute='accept_button_boolean_hide', store=False)
    approve_button_boolean = fields.Boolean(compute='approve_button_boolean_hide', store=False)
    pending_at = fields.Many2one('hr.employee')
    achieve_date = fields.Date('Achieve Date')
    upload_btn_hide_boolean = fields.Boolean(compute='upload_button_boolean_hide', store=False)
    self_boolean_readonly = fields.Boolean()
    rcm_head_manager_id = fields.Many2one('hr.employee')
    close_btn_hide_boolean = fields.Boolean(compute='upload_button_boolean_hide', store=False)
    target_date_boolean = fields.Boolean(compute='_target_date_boolean_hide', store=False)
    remainder_mail_boolean = fields.Boolean(compute='_target_date_boolean_hide', store=False)
    appreciation_mail_boolean = fields.Boolean(compute='_target_date_boolean_hide', store=False)

    # @api.depends('target_date')
    def _target_date_boolean_hide(self):
        for rec in self:
            status = []
            count = 0
            appre_status = []
            close_status = []
            for recc in rec.assigned_emp_data:
                count += 1
                if recc.status_certification == 'Accepted':
                    status.append(recc.status_certification)
                if recc.status_certification == 'Uploaded':
                    appre_status.append(recc.status_certification)
                if recc.status_certification == 'Mail Sent':
                    close_status.append(recc.status_certification)
            if rec.target_date:
                if len(status) > 0:
                    rec.target_date_boolean = True
                    # print('if target_date>>',rec.target_date_boolean)
                else:
                    rec.target_date_boolean = False
                    # print('else target_date>>',rec.target_date_boolean)
            if len(status) > 0:
                rec.remainder_mail_boolean = True
            else:
                rec.remainder_mail_boolean = False

            if len(appre_status) > 0:
                rec.appreciation_mail_boolean = True
            else:
                rec.appreciation_mail_boolean = False
            # print(len(close_status), count, '================>>')
            if len(close_status) == count:
                # print('111111111111111111111')
                rec.close_btn_hide_boolean = True
            else:
                # print('222222222222222')
                rec.close_btn_hide_boolean = False






    # def get_readonly_boolean(self):
    #     if self.suggested_by == 'Self':
    #         self.self_boolean_readonly = True
    #     else:
    #         self.self_boolean_readonly = False


    @api.onchange('suggested_by')
    def get_employee(self):
        if self.suggested_by == 'Self':
            # self.self_boolean_readonly = True
            self.raised_by_id = self.env.user.employee_ids.id
        else:
            self.raised_by_id = False
            # self.self_boolean_readonly = False
            pass

    @api.constrains('no_of_candidate')
    def get_onchange_value(self):
        if self.no_of_candidate <= 0:
            raise ValidationError('No of People should not be Zero.')

    @api.constrains('assigned_emp_data', 'no_of_candidate')
    def validation_defects(self):
        data = []
        if self.assigned_emp_data:
            for rec in self.assigned_emp_data:
                if rec.status_certification in ['Accepted', 'Pending']:
                    data.append(rec.id)
        if len(data) > self.no_of_candidate:
            raise ValidationError('Warning! You cannot add extra nominates.')



    def all_accepted_boolean_check(self):
        for rec in self:
            accept_length = []
            if rec.assigned_emp_data:
                for recc in rec.assigned_emp_data:
                    if recc.status_certification == 'Accepted':
                        accept_length.append(recc.status_certification)
            if rec.no_of_candidate == len(accept_length):
                rec.all_accepted_boolean = True
                rec.state = 'Accepted'
                rec.pending_at = rec.raised_by_id
            else:
                rec.all_accepted_boolean = False


    def assign_button_boolean_hide(self):
        for rec in self:
            dept_hod = self.env['hr.department'].sudo().search([('id', '=', rec.require_department_id.id)])
            rec.department_head_id = dept_hod.manager_id.user_id.employee_ids.id
            # print(rec.department_head_id, self.env.user.employee_ids.id)
            if self.env.user.employee_ids.id ==  rec.department_head_id.id:
                rec.assign_button_hide_boolean = True
            else:
                rec.assign_button_hide_boolean = False

    def accept_button_boolean_hide(self):
        for rec in self:
            emp_data = []
            if rec.assigned_emp_data:
                for recc in rec.assigned_emp_data:
                    if recc.status_certification == 'Pending':
                        emp_data.append(recc.employee_id.id)
            if self.env.user.employee_ids.id in emp_data:
                rec.accept_button_boolean = True
            else:
                rec.accept_button_boolean = False

    def approve_button_boolean_hide(self):
        for rec in self:
            if self.env.user.has_group('kw_resource_management.group_budget_manager'):
                rec.approve_button_boolean = True
            else:
                rec.approve_button_boolean = False
    def upload_button_boolean_hide(self):
        for rec in self:
            if self.env.user.has_group('kw_certification.group_landk_module_kw_certification'):
                rec.upload_btn_hide_boolean = True
            else:
                rec.upload_btn_hide_boolean = False
                
            # if self.env.user.has_group('kw_certification.group_manager_module_kw_certification') or self.env.user.has_group('kw_resource_management.group_budget_manager'):
            #     rec.close_btn_hide_boolean = True
            # else:
            #     rec.close_btn_hide_boolean = False


    @api.onchange('raised_by_id', 'certification_type_id')
    def _change_employee(self):
        self.department_id = self.raised_by_id.department_id.id if self.raised_by_id.department_id else False
        if self.certification_type_id:
            data = self.env['kw_certification_budget_master'].sudo().search([('certificate_id', '=',
                                                                self.certification_type_id.id)])
            if data:
                self.cert_budget = data.mapped('budget')[0]
            else:
                raise ValidationError(f'Certification {self.certification_type_id.name} budget is not set.')


    # def btn_submit(self):
    #     self.state = 'Request Raised'
    #     seq = self.env['ir.sequence'].next_by_code('self.kw_certification') or '/'
    #     seq_without_prefix = seq.split('-')[-1]
    #     self.number = f" CF/{self.certification_type_id.name}{seq_without_prefix}"
    #     dept_hod = self.env['hr.department'].sudo().search([('id', '=', self.require_department_id.id)])
    #     self.department_head_id = dept_hod.manager_id.user_id.employee_ids.id
    #     self.rcm_head_manager_id = self.env.user.employee_ids.id
    #     if self.department_head_id:
    #         self.assigned_user_ids = [(4, id, False) for id in [self.department_head_id.id,]]
    #         self.pending_at = self.department_head_id.id

    #         template_obj = self.env.ref('kw_certification.email_template_for_assign_emp')
    #         email_to = dept_hod.manager_id.user_id.employee_ids.work_email
    #         l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
    #         manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
    #         manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
    #         lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
    #         cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(manager_emp_l.mapped('work_email')) or ''
    #         if template_obj:
    #             template_obj.with_context(
    #                     subject="Please Assign Nominees for Certification",
    #                     mail_for='Submit',
    #                     email_to=email_to,
    #                     email_from=self.env.user.employee_ids.work_email,
    #                     mail_cc = cc_mail,
    #                     cert_number=self.number,
    #                     name=dept_hod.manager_id.user_id.employee_ids.name,
    #                 ).send_mail(
    #                 self.id,
    #                 notif_layout="kwantify_theme.csm_mail_notification_light",
    #             )
    #             self.env.user.notify_success("Mail Sent Successfully.")

    #         self.write({'action_log_table_ids': [[0, 0, {'state': 'Request Raised',
    #                                                     'designation': self.env.user.employee_ids.job_id.name,
    #                                                     'action_taken_by': self.env.user.employee_ids.name,
    #                                                     }]]})
    #     else:
    #         raise ValidationError('Department head is not set in given department.')


    def btn_assign(self):
        if not self.assigned_emp_data:
            raise ValidationError('Warning! Please add Nominees.')
        if not self.enroll_policy:
            raise ValidationError('Warning! Please add Enroll Policy.')
        else:
            for rec in self.assigned_emp_data:
                if rec.status_certification == 'Pending' and not rec.assigned_date:
                    rec.assigned_date = date.today()
            self.state = 'Assigned'
            emp_list = []
            template_obj = self.env.ref('kw_certification.email_template_for_assign_emp')
            l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
            lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
            manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
            manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
            cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(manager_emp_l.mapped('work_email')) or ''
            for rec in self.assigned_emp_data:
                emp_list.append(rec.employee_id.id)

                if template_obj and rec.status_certification == 'Pending' and not rec.mail_boolean:
                    email_to = rec.employee_id.work_email
                    template_obj.with_context(
                        mail_for='Assign',
                        subject="Nominated for " + self.certification_type_id.name +' certification !',
                        enroll_policy = self.enroll_policy,
                        cert_name = self.certification_type_id.name,
                        email_to=email_to,
                        mail_cc=cc_mail,
                        email_from=self.env.user.employee_ids.work_email,
                        name=rec.employee_id.name,
                        record_id=self.id,
                        employee_id=rec.employee_id.id,
                    ).send_mail(
                        self.id,
                        notif_layout="kwantify_theme.csm_mail_notification_light",
                    )
                    self.env.user.notify_success("Mail Sent Successfully.")
                    rec.mail_boolean = True
            self.write({'action_log_table_ids': [[0, 0, {'state': 'Assigned',
                                                        'designation': self.env.user.employee_ids.job_id.name,
                                                        'action_taken_by': self.env.user.employee_ids.name,
                                                        }]]})
        # self.assigned_user_ids = [(4, id, False) for id in emp_list]

    # def btn_reject(self):
    #     pass
    # def btn_accept(self):
    #     for rec in self:
    #         accept_length = []
    #         if rec.assigned_emp_data:
    #             for recc in rec.assigned_emp_data:
    #                 if recc.employee_id.id == self.env.user.employee_ids.id:
    #                     recc.status_certification = 'Accepted'
    #                 if recc.status_certification == 'Accepted':
    #                     accept_length.append(recc.status_certification)
    #         if rec.no_of_candidate == len(accept_length):
    #             rec.state = 'Accepted'
    #             rec.pending_at = rec.raised_by_id

    # def btn_approve(self):
        # self.state = 'Approved'
        # accepted_emp = []
        # for recc in self.assigned_emp_data:
        #     if recc.status_certification == 'Accepted':
        #         accepted_emp.append(recc.employee_id.work_email)
        # template_obj = self.env.ref('kw_certification.email_template_for_assign_emp')
        # manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
        # manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
        # l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
        # lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
        # cc_mail = ','.join(manager_emp_l.mapped('work_email'))+',' + ','.join(accepted_emp)  or ''
        # dept_hod = self.env['hr.department'].sudo().search([('id', '=', self.require_department_id.id)])
        # email_to = dept_hod.manager_id.user_id.employee_ids.work_email
        # if template_obj:
        #     template_obj.with_context(
        #             mail_for='Approve',
        #             subject= "Approved For Certification"+ '|'+ self.number,
        #             email_to=email_to,
        #             mail_cc=cc_mail,
        #             email_from=self.env.user.employee_ids.work_email,
        #             cert_number=self.number,
        #             name=dept_hod.manager_id.user_id.employee_ids.name,
        #             approver_name=self.env.user.employee_ids.name
        #         ).send_mail(
        #         self.id,
        #         notif_layout="kwantify_theme.csm_mail_notification_light",
        #     )
        #     self.env.user.notify_success("Mail Sent Successfully.")
        # if lk_employees:
        #     self.pending_at = lk_employees.ids[0]
        # else:
        #     raise ValidationError('Please Give  L&K Access Rights to At least One Person.')
        # self.assigned_user_ids = [(4, id, False) for id in lk_employees.ids]
        #
        # self.write({'action_log_table_ids': [[0, 0, {'state': 'Approved',
        #                                             'designation': self.env.user.employee_ids.job_id.name,
        #                                             'action_taken_by': self.env.user.employee_ids.name,
        #                                             }]]})
    # def btn_uploaded(self):
    #     for rec in self.assigned_emp_data:
    #         if rec.status_certification == 'Accepted' and rec.certificate_upload != None:
    #             rec.status_certification = 'Uploaded'
    #             template_obj = self.env.ref("kw_certification.email_template_for_assign_emp")
    #             manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
    #             manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
    #             rcm=self.env.ref('kw_resource_management.group_budget_manager')
    #             rcm_emp =  rcm.users.mapped('employee_ids') if manager_emp else ''
    #             cc_mail = ','.join(manager_emp_l.mapped('work_email')) + ',' + ','.join(rcm_emp.mapped('work_email')) + ',' + ','.join(self.require_department_id.manager_id.user_id.employee_ids.mapped('work_email'))
    #             emp_code_desg='('+rec.employee_id.emp_code +','+ rec.employee_id.job_id.name + ')'
    #             full_name = rec.employee_id.name
    #             first_name = full_name.split()[0]
    #             if template_obj:
    #                 template_obj.with_context(
    #                 mail_for='upload',
    #                 subject="Certification Appriciation Mail",
    #                 email_to='csmfamily@csm.tech',
    #                 certification_name = self.certification_type_id.name,
    #                 mail_cc=rec.employee_id.work_email,
    #                 emp_code_desg = emp_code_desg,
    #                 email_from=self.env.user.employee_ids.work_email,
    #                 name=rec.employee_id.name,
    #                 first_name=first_name
    #                 ).send_mail(
    #                 self.id,
    #                 notif_layout="kwantify_theme.csm_mail_notification_light",
    #             )
    #                 self.env.user.notify_success("Mail Sent Successfully.")

            # elif rec.status_certification == 'Rejected' and rec.certificate_upload == None:
            #     pass
            # elif rec.status_certification == 'Rejected' and rec.certificate_upload != None:
            #     raise ValidationError('Please Remove Rejected Nominates Certificate.')
            # else:
            #     raise ValidationError('Please Add all Nominates Certificate.')
            self.achieve_date = date.today()
            # self.state = 'Closed'

    def close_button(self):
        self.pending_at = False
        self.take_action_user_ids = False
        self.state = 'Closed'
        self.write({'action_log_table_ids': [[0, 0, {'state': 'Closed',
                                                    'designation': self.env.user.employee_ids.job_id.name,
                                                    'action_taken_by': self.env.user.employee_ids.name,
                                                    }]]})
         # self.write({'pending_at': False,
         #            'state':'Closed',
         #            'take_action_user_ids':False})

    def scheduler_for_late_mail_response(self):
        data = self.env['kw_certification'].sudo().search([])
        for rec in data:
            for recc in rec.assigned_emp_data:
                if recc.status_certification == 'Pending' and recc.assigned_date:
                    # two_days_after = recc.assigned_date + timedelta(days=2)
                    # date_string = two_days_after
                    # datee = datetime.strptime(date_string, "%Y-%m-%d")
                    # day_name = datee.strftime("%A")
                    # given_date = date(2023, 5, 19)
                    new_date = recc.assigned_date + timedelta(days=2)
                    while new_date.weekday() >= 5:
                        new_date += timedelta(days=2)
                    if date.today() == new_date:
                        template_obj = self.env.ref('kw_certification.email_template_for_assign_emp')
                        l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
                        lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                        manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
                        manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                        cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(
                            manager_emp_l.mapped('work_email')) or ''
                        if template_obj:
                            email_to = recc.employee_id.work_email
                            template_obj.with_context(
                                mail_for='Assign',
                                subject="Reminder | Nominated for"+'|'+ rec.certification_type_id.name +' certification !',
                                enroll_policy=rec.enroll_policy,
                                email_to=email_to,
                                mail_cc=cc_mail,
                                email_from='tendrils@csm.tech',
                                name=recc.employee_id.name,
                                record_id=rec.id,
                                employee_id=recc.employee_id.id,
                            ).send_mail(
                                rec.id,
                                notif_layout="kwantify_theme.csm_mail_notification_light",
                            )
    def get_all_status_details(self):
        action = self.env.ref('kw_certification.kw_certification_view_status_window').read()[0]
        # action.update({'domain': [('view_status_user_ids', 'in', self.env.user.employee_ids.id )]})
        return action

    def get_all_take_actions_user(self):
        action = self.env.ref('kw_certification.kw_certification_take_action_window').read()[0]
        action.update({'domain': [('take_action_user_ids', 'in', self.env.user.employee_ids.id)]})
        return action

    def send_mail_button_landk(self):
        for rec in self.assigned_emp_data:
                template_obj = self.env.ref("kw_certification.reminder_certification_upload_template")
                manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
                l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
                lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
                email_to = ','.join(lk_employees.mapped('work_email')) 
                manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                cc_mail = ','.join(manager_emp_l.mapped('work_email')) + ',' + ',' .join(self.require_department_id.manager_id.user_id.employee_ids.mapped('work_email'))
                # l_and_k_name = lk_employees.name
                if template_obj:
                    # print('template_obj called', template_obj)
                    template_obj.with_context(
                    email_to = email_to,
                    certification_name = self.certification_type_id.name,
                    email_from=self.env.user.employee_ids.work_email,
                    cc_mail = cc_mail,
                    # l_and_k_name = l_and_k_name,
                    name=rec.employee_id.name,
                    ).send_mail(
                    self.id,
                    notif_layout="kwantify_theme.csm_mail_notification_light",
                )
                self.env.user.notify_success("Mail Sent Successfully.")

    def send_mail_resource_button(self):
        for rec in self.assigned_emp_data:
            if rec.status_certification == 'Accepted':
                # accepted_emp.append(recc.employee_id.work_email)
                template_obj = self.env.ref("kw_certification.reminder_certification_complete_template")
                manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
                manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                cc_mail = ','.join(manager_emp_l.mapped('work_email')) + ',' + ',' .join(self.require_department_id.manager_id.user_id.employee_ids.mapped('work_email'))
                # emp_code_desg='('+rec.employee_id.emp_code +','+ rec.employee_id.job_id.name + ')'
                if template_obj:
                    email_to = rec.employee_id.work_email
                    template_obj.with_context(
                    email_to = email_to,
                    certification_name = self.certification_type_id.name,
                    mail_cc=rec.employee_id.work_email,
                    # emp_code_desg = emp_code_desg,
                    email_from=self.env.user.employee_ids.work_email,
                    cc_mail = cc_mail,
                    name=rec.employee_id.name,
                    ).send_mail(
                    self.id,
                    notif_layout="kwantify_theme.csm_mail_notification_light",
                )
                self.env.user.notify_success("Mail Sent Successfully.")

      
    

class CreateCertificationLogTable(models.Model):
    _name = 'certification_log_table'

    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    action_taken_by = fields.Char(string='Action Taken By')
    designation = fields.Char(string="Designation")
    state = fields.Char(string='State')
    certfication_con_id = fields.Many2one('kw_certification')
    
    
class HrEmployeeData(models.Model):
    _name = "assign_employee"


    employee_id = fields.Many2one('hr.employee', string="Employee")
    emp_qualification = fields.Char(string="Employee Qualification", compute='_compute_emp_qualification')
    deg_id = fields.Many2one('hr.job',string='Designation',related="employee_id.job_id")
    dept_id = fields.Many2one('hr.department',string='Department',related="employee_id.department_id")
    work_email= fields.Char(related="employee_id.work_email",string="Work Email")
    status_certification= fields.Char(string="Status", default="Pending")
    emp_year_of_exp= fields.Char(string="Year Of Experience",related="employee_id.total_experience_display")
    certification_master_id = fields.Many2one('kw_certification')
    certificate_upload = fields.Binary(string='Document')
    doc_file_name = fields.Char(string="Document Name")
    l_k_bool = fields.Boolean(string="L and K",compute="l_k_button_boolean_hide")
    assigned_date = fields.Date()
    mail_boolean = fields.Boolean()
    manual_certification_entry_id = fields.Many2one('kw_manual_certification')
    upload_bool = fields.Boolean(string="Upload SHow Hide",compute="upload_boolean_hide")
    show_upload_button = fields.Boolean(compute='_compute_show_upload_button', string='Show Upload Button')

    @api.depends('manual_certification_entry_id.state')
    def _compute_show_upload_button(self):
        for record in self:
            if record.manual_certification_entry_id.state == 'Submit':
                record.show_upload_button = True
            else:
                record.show_upload_button = False
    
    
    def l_k_button_boolean_hide(self):
        for rec in self:
            emp=self.env.ref("kw_certification.group_landk_module_kw_certification",False).mapped('users.employee_ids')
            if self.env.user.employee_ids.id in emp.mapped('id'):
                rec.l_k_bool = True
            else:
                rec.l_k_bool = False
    
    @api.constrains('uploaded_doc')
    def validate_educational_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.certificate_upload, allowed_file_list)
            kw_validations.validate_file_size(record.certificate_upload, 4)
    
    @api.depends('employee_id.educational_details_ids')
    def _compute_emp_qualification(self):
        for rec in self:
            highest_qualification = False
            for edu in rec.employee_id.educational_details_ids:
                if not highest_qualification or edu.passing_year > highest_qualification.passing_year:
                    highest_qualification = edu
            if highest_qualification:
                rec.emp_qualification = highest_qualification.stream_id.name
            else:
                rec.emp_qualification = False
    
class DoneRemarksWizard(models.TransientModel):
    _name = 'mail_notify_wizard'
    _description = 'Done  Wizard'
    
    def get_emp_id(self):
        emp_list = []
        current_record_id = self._context.get('current_record')
        data = self.env['kw_certification'].sudo().search([('id', '=', current_record_id), ('state', '=', 'Approved')])
        for rec in data:
            emp_id = []
            for recc in rec.assigned_emp_data:
                if recc.status_certification == 'Accepted' and recc.certificate_upload == None:
                    emp_id.append(recc.employee_id.id)
            emp_list = [('id','in',emp_id)]
        return emp_list

    def get_emp_ids(self):
        emp_domain = []
        current_record_id = self._context.get('current_record')
        if current_record_id:
            data = self.env['kw_certification'].sudo().search([('id', '=', current_record_id), ('state', '=', 'Approved')])
            for rec in data:
                emp_id = []
                for recc in rec.assigned_emp_data:
                    if recc.status_certification == 'Uploaded' and recc.certificate_upload is not None:
                        emp_id.append(recc.employee_id.id)
                emp_domain = [('id', 'in', emp_id)]
        return emp_domain


        
    
    email_cc = fields.Many2many('hr.employee',string="Email CC")
    certification_record_id = fields.Many2one('kw_certification',default=lambda self: self._context.get('current_record'))
    assign_emp_record_id = fields.Many2one('assign_employee')
    certificate_upload = fields.Binary(string='Document')
    employee_id = fields.Many2one('hr.employee',string="Employee Name", domain=get_emp_id)
    emp_id = fields.Many2many('hr.employee',string="Employee Name", domain=get_emp_ids)
    course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
                                                             ('3', 'Training And Certification')], default='3')
    course_id = fields.Many2one('kwmaster_course_name', string="Course Name", domain="[('code', '=', 'cert')]", default=lambda self: self._default_course_id(), readonly=True)
    university_name = fields.Many2one('kwmaster_institute_name', string="University/Institution")
    stream_id = fields.Many2one('kwmaster_stream_name', string="Certification", readonly=True, compute="get_stream", store=True)
    division = fields.Char(string="Division / Grade", size=6)
    marks_obtained = fields.Float(string="% of marks obtained")
    doc_file_name = fields.Char(string="Document Name")
    passing_year = fields.Selection(string="Passing Year", selection='_get_year_list')

    @api.depends('employee_id')
    def get_stream(self):
        for rec in self:
            rec.stream_id = rec.certification_record_id.certification_type_id.id

    def _default_course_id(self):
        cert_course = self.env['kwmaster_course_name'].search([('code', '=', 'cert')], limit=1)
        return cert_course.id if cert_course else False

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]

    def btn_submit(self):
        cc_mail= []
        self.certification_record_id.state = 'Request Raised'
        seq = self.env['ir.sequence'].next_by_code('self.kw_certification') or '/'
        seq_without_prefix = seq.split('-')[-1]
        self.certification_record_id.number = f" CF/{self.certification_record_id.certification_type_id.name}{seq_without_prefix}"
        cc_mail=self.email_cc.mapped('work_email') if self.email_cc else ''
        dept_hod = self.env['hr.department'].sudo().search([('id', '=', self.certification_record_id.require_department_id.id)])
        self.certification_record_id.department_head_id = dept_hod.manager_id.user_id.employee_ids.id
        self.certification_record_id.rcm_head_manager_id = self.env.user.employee_ids.id
        if self.certification_record_id.department_head_id:
            self.certification_record_id.assigned_user_ids = [(4, id, False) for id in [self.certification_record_id.department_head_id.id,]]
            self.certification_record_id.view_status_user_ids = [(4, id, False) for id in
                                                              [self.certification_record_id.department_head_id.id, self.env.user.employee_ids.id]]
            self.certification_record_id.take_action_user_ids = [(4, id, False) for id in
                                                                 [self.certification_record_id.department_head_id.id]]
            self.certification_record_id.pending_at = self.certification_record_id.department_head_id.id

            template_obj = self.env.ref('kw_certification.email_template_for_assign_emp')
            email_to = dept_hod.manager_id.user_id.employee_ids.work_email
            l_k_emp = self.env.ref("kw_certification.group_landk_module_kw_certification")
            manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
            manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
            lk_employees = l_k_emp.users.mapped('employee_ids') if l_k_emp else ''
            cc_mail = ','.join(lk_employees.mapped('work_email')) + ',' + ','.join(manager_emp_l.mapped('work_email')) +',' + ','.join(cc_mail) or ''
            if template_obj:
                template_obj.with_context(
                        # subject="Please Assign Nominees for Certification",
                        subject="Nomination for " + self.certification_record_id.certification_type_id.name + ' certification !',
                        mail_for='Submit',
                        email_to=email_to,
                        email_from=self.env.user.employee_ids.work_email,
                        mail_cc = cc_mail,
                        # cert_number=self.certification_record_id.number,
                        cert_name=self.certification_record_id.certification_type_id.name,
                        name=dept_hod.manager_id.user_id.employee_ids.name,
                    ).send_mail(
                    self.certification_record_id.id,
                    notif_layout="kwantify_theme.csm_mail_notification_light",
                )
                self.env.user.notify_success("Mail Sent Successfully.")

            self.certification_record_id.write({'action_log_table_ids': [[0, 0, {'state': 'Request Raised',
                                                        'designation': self.env.user.employee_ids.job_id.name,
                                                        'action_taken_by': self.env.user.employee_ids.name,
                                                        }]]})
        else:
            raise ValidationError('Department head is not set in given department.')
    
    def btn_cancel(self):
        pass
    
    def btn_submit_upload(self):
        if self.assign_emp_record_id.status_certification == 'Accepted':
            self.assign_emp_record_id.write({'status_certification' : 'Uploaded','certificate_upload':self.certificate_upload})
            employee_data = self.env['hr.employee'].search([('id', '=', self.assign_emp_record_id.employee_id.id)])
            skill_id = []
            for rec in employee_data.educational_details_ids:
                skill_id.append(rec.stream_id.id)
            if self.stream_id.id in skill_id:
                raise ValidationError(f'{self.stream_id.name} certification has already been updated against {self.employee_id.name}.')
            else:
                employee_data.write(
                            {'educational_details_ids':[[0,0,{  
                                'course_type':self.course_type,
                                'course_id':self.course_id.id,
                                'stream_id':self.stream_id.id,
                                'university_name':self.university_name.id,
                                'division':self.division,
                                'marks_obtained':self.marks_obtained,
                                'uploaded_doc':self.certificate_upload,
                                'passing_year':self.passing_year
                            }]]
                             })

    #         rec.write({'status_certification' : 'Uploaded','certificate_upload':self.certificate_upload})
        # print(self.certification_record_id, self.employee_id.name, self.stream_id.name
        # )
        # for rec in self.certification_record_id.assigned_emp_data:
        #     if rec.status_certification == 'Accepted' and self.employee_id.id == rec.employee_id.id:
        #         rec.write({'status_certification' : 'Uploaded','certificate_upload':self.certificate_upload})
        #         self.env['hr.employee'].search([('id', '=', self.employee_id.id)]).write(
        #             {'educational_details_ids':[[0,0,{
        #                 'course_type':self.course_type,
        #                 'course_id':self.course_id.id,
        #                 'stream_id':self.stream_id.id,
        #                 'university_name':self.university_name.id,
        #                 'division':self.division,
        #                 'marks_obtained':self.marks_obtained,
        #                 'uploaded_doc':self.certificate_upload,
        #                 'passing_year':self.passing_year
        #             }]]
        #              })
                # template_obj = self.env.ref("kw_certification.email_template_for_assign_emp")
                # manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
                # manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
                # # rcm=self.env.ref('kw_resource_management.group_budget_manager')
                # # rcm_emp =  rcm.users.mapped('employee_ids') if manager_emp else ''
                # cc_mail = ','.join(manager_emp_l.mapped('work_email')) + ',' + ','.join(self.certification_record_id.require_department_id.manager_id.user_id.employee_ids.mapped('work_email'))
                # emp_code_desg='('+rec.employee_id.emp_code +','+ rec.employee_id.job_id.name + ')'
                # full_name = rec.employee_id.name
                # first_name = full_name.split()[0]
                # if template_obj:
                #     template_obj.with_context(
                #     mail_for='upload',
                #     subject="Certification Appriciation Mail",
                #     email_to='csmfamily@csm.tech',
                #     certification_name = self.certification_record_id.certification_type_id.name,
                #     mail_cc=rec.employee_id.work_email,
                #     emp_code_desg = emp_code_desg,
                #     email_from=self.env.user.employee_ids.work_email,
                #     name=rec.employee_id.name,
                #     first_name=first_name
                #     ).send_mail(
                #     self.certification_record_id.id,
                #     notif_layout="kwantify_theme.csm_mail_notification_light",
                # )
                #     self.env.user.notify_success("Mail Sent Successfully.")
                    
    def btn_submit_close(self):
        # self.certification_record_id.write({'pending_at': False,
        #                                    'take_action_user_ids':False})
        for rec in self.emp_id:
            data = self.certification_record_id.assigned_emp_data
            for x in data:
                if x.employee_id.id == rec.id and x.status_certification == 'Uploaded':
                    x.status_certification = 'Mail Sent'
            #     print(x.status_certification, x.employee_id.id, rec.id)
            # print(data, '------------------->>')
            # print(n)
            template_obj = self.env.ref("kw_certification.email_template_for_assign_emp")
            manager_emp = self.env.ref("kw_certification.group_manager_module_kw_certification")
            manager_emp_l = manager_emp.users.mapped('employee_ids') if manager_emp else ''
            rcm=self.env.ref('kw_resource_management.group_budget_manager')
            rcm_emp =  rcm.users.mapped('employee_ids') if manager_emp else ''
            cc_mail = ','.join(manager_emp_l.mapped('work_email')) + ',' + ','.join(self.certification_record_id.require_department_id.manager_id.user_id.employee_ids.mapped('work_email'))
            emp_code_desg='('+rec.emp_code +','+ rec.job_id.name + ')'
            full_name = rec.name
            first_name = full_name.split()[0]
            if template_obj:
                template_obj.with_context(
                mail_for='upload',
                subject="Certification Appriciation Mail",
                email_to='csmfamily@csm.tech',
                certification_name = self.certification_record_id.certification_type_id.name,
                mail_cc=rec.work_email,
                emp_code_desg = emp_code_desg,
                email_from=self.env.user.employee_ids.work_email,
                name=rec.name,
                first_name=first_name
                ).send_mail(
                self.certification_record_id.id,
                notif_layout="kwantify_theme.csm_mail_notification_light",
            )
                self.env.user.notify_success("Mail Sent Successfully.")

        

    # @api.onchange('employee_id')
    # def change_employee_field(self):
    #     selected_employees_id = self.certification_master_id.assigned_emp_data.mapped('employee_id')
    #     return {
    #         'domain': {
    #             'employee_id': [('id', 'not in', selected_employees_id.ids)]
    #         }
    #     }
                