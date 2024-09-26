from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time




class nps_employee_data(models.Model):
    _name = 'nps_employee_data'
    _description = 'Corporate NPS'
    _rec_name = 'employee_id'
    _order = 'id asc'



    employee_id = fields.Many2one('hr.employee', string="Employee",required=True,default=lambda self: self.env.user.employee_ids.id)
    is_nps = fields.Selection([('Yes', 'Yes'),('No','No')],string="NPS")
    contribution = fields.Selection([(5, '5 % of Basic Salary'),(7, '7 % of Basic Salary'),(10, '10 % of Basic Salary'),(14, '14 % of Basic Salary')],string="NPS Contribution")
    existing_pran_no = fields.Selection([('Yes', 'Yes'),('No','No')],string="Existing PRAN")
    pran_no = fields.Char(string="PRAN")
    is_popup_submitted = fields.Boolean(default=False)
    emp_profile_id = fields.Many2one('kw_emp_profile')
    emp_contract_id = fields.Many2one('hr.contract')
    state = fields.Selection([('Running', 'Active'),('Requested','Under Process'),('Not_started', 'Not Started')],string="Status") 
    remark_of_action = fields.Text('Approver Remark')
    remark_of_apply = fields.Text('Remark')
    action_taken_date = fields.Date()



    @api.model
    def create(self, vals):
        existing_employee_ids = self.env['nps_employee_data'].search([]).mapped('employee_id.id')
        if self.env.user.employee_ids.id in existing_employee_ids:
            raise ValidationError('You already have an existing NPS..!')
        else:
            vals['state'] = 'Not_started' if vals.get('is_nps') == 'No' else 'Requested'
            record = super(nps_employee_data, self).create(vals)
            if (not 'is_popup_submitted' in vals or not vals['is_popup_submitted']) and vals.get('is_nps') == 'Yes':
                self.env['nps_update_data'].sudo().create({
                    'employee_id': vals['employee_id'],
                    'is_nps': vals['is_nps'],
                    'contribution': vals['contribution'],
                    'existing_pran_no': vals['existing_pran_no'],
                    'pran_no': vals['pran_no'],
                    'state': 'Requested' if vals['is_nps'] == 'Yes' else 'Approved',
                    'remark': vals.get('remark_of_apply'),
                    'applied_on': datetime.now(),
                    'nps_id': record.id if record else None,
                    'emp_contract_id': self.emp_contract_id,
                    'after_login': 'No'
                })
            if vals.get('is_nps') == 'No':
                emp_contract_id = self.env['hr.contract'].sudo().search([('employee_id', '=', vals.get('employee_id')), ('state', '=', 'open')], limit=1)
                emp_contract_id.sudo().write({'is_nps':vals.get('is_nps')})
            
            if vals.get('is_nps') == 'Yes':
                template = self.env.ref('payroll_inherit.nps_enrolment_mail_template')
                cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                res_id = record.id
                email_to = record.employee_id.work_email if record.employee_id.work_email else []
                applied_user = record.employee_id.name if record.employee_id.name else 'User'
                subject_emp = f"{applied_user} ({record.employee_id.emp_code})" if record.employee_id.emp_code else applied_user
                contribution = f"{record.contribution}% of Basic Salary" if record.contribution else None
                pran_no = record.pran_no if record.pran_no else 'To be generated'
                template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,contribution=contribution,pran_no = pran_no).send_mail(res_id,notif_layout="kwantify_theme.csm_mail_notification_light")


            return record




    @api.onchange('employee_id')
    def get_profile_and_contract_id(self):
        if self.employee_id:
            self.emp_profile_id =  self.env['kw_emp_profile'].sudo().search([('emp_id','=',self.employee_id.id)]).id
            self.emp_contract_id =  self.env['hr.contract'].sudo().search([('employee_id','=',self.employee_id.id),('state','=','open')]).id
        

    @api.onchange('existing_pran_no')
    def false_pran_no(self):
        if self.existing_pran_no == 'No':
            self.pran_no = False


    def employee_nps_create(self):
        self.env.cr.execute("""
                            SELECT e.id,ep.id AS profile_id ,ec.id AS contract_id FROM hr_employee e
                            LEFT JOIN kw_emp_profile ep ON e.id = ep.emp_id
                            LEFT JOIN hr_contract ec ON e.id = ec.employee_id
                            WHERE   e.active = True and 
                                    e.enable_payroll = 'yes' and e.company_id = 1
                                    AND ep.id IS NOT NULL 
                                    AND ec.id IS NOT NULL
                                    AND ec.state = 'open'
                            """)
        result = self.env.cr.fetchall()
        existing_nps_records = self.env['nps_employee_data'].sudo().search([]).mapped(lambda x: (x.employee_id.id, x.emp_profile_id.id, x.emp_contract_id.id))

        nps_create_query = "INSERT INTO nps_employee_data(employee_id, emp_profile_id, emp_contract_id, state) VALUES (%s, %s, %s, %s);"
        nps_create_params = []

        for emp_id, profile_id, contract_id in result:
            if (emp_id, profile_id, contract_id) not in existing_nps_records:
                nps_create_params.append((emp_id, profile_id, contract_id, 'Running'))

        if nps_create_params:
            self.env.cr.executemany(nps_create_query, nps_create_params)



    def request_update_nps_details(self):
        view_id = self.env.ref("payroll_inherit.nps_update_data_view_form").id
        action = {
            'name': 'Update NPS Details',
            'type': 'ir.actions.act_window',
            'res_model': 'nps_update_data',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'employee_id': self.employee_id.id,'nps_id':self.id,'is_nps':self.is_nps,'contribution':self.contribution,
                        'existing_pran_no':self.existing_pran_no,'pran_no':self.pran_no,'emp_contract_id':self.emp_contract_id.id}
        }
        return action













class nps_update_data(models.Model):
    _name = 'nps_update_data'
    _rec_name = 'employee_id'
    _description = 'NPS Update Model'
    _order = 'create_date DESC'


    employee_id = fields.Many2one('hr.employee', string="Employee",required=True)
    employee_name = fields.Char('Emp Name',related='employee_id.name')
    employee_code = fields.Char('Emp Code',related='employee_id.emp_code')
    work_email = fields.Char('E-Mail',related='employee_id.work_email')
    date_of_joining = fields.Date('Date of joining',related='employee_id.date_of_joining')
    job_id = fields.Many2one('hr.job',string='Designation',related='employee_id.job_id')
    date_of_birth = fields.Date('Date of Birth',related='employee_id.birthday')
    department_id = fields.Many2one('hr.department', string="Department",related='employee_id.department_id')
    job_branch_id = fields.Many2one('kw_res_branch', string="Location",related='employee_id.job_branch_id')
    is_nps = fields.Selection([('Yes', 'Yes'),('No','No')],string="NPS")
    contribution = fields.Selection([(5, '5 % of Basic Salary'),(7, '7 % of Basic Salary'),(10, '10 % of Basic Salary'),(14, '14 % of Basic Salary')],string="NPS Contribution")
    existing_pran_no = fields.Selection([('Yes', 'Yes'),('No','No')],string="Existing PRAN")
    pran_no = fields.Char(string="PRAN")
    state = fields.Selection([('Requested', 'Requested'),('Approved','Approved'),('Rejected','Rejected')],default='Requested')
    remark = fields.Text('Employee Remark')
    remark_of_action = fields.Text('Approver Remark')
    applied_on = fields.Datetime(default=datetime.now())
    action_taken_on = fields.Datetime()
    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By")
    nps_id = fields.Integer(string="NPS ID")
    emp_contract_id = fields.Many2one('hr.contract')
    after_login = fields.Selection([('Yes', 'Yes'),('No','No')])







    @api.onchange('is_nps')
    def get_context_values(self):
        if self.is_nps != 'No':
            self.nps_id = self.env.context.get('nps_id')
            self.contribution = self.env.context.get('contribution') if self.env.context.get('contribution') else None
            self.existing_pran_no = self.env.context.get('existing_pran_no') if self.env.context.get('contribution') else None
            self.pran_no = self.env.context.get('pran_no') if self.env.context.get('contribution') else None
            self.emp_contract_id = self.env.context.get('emp_contract_id') if self.env.context.get('contribution') else None

        if not self.employee_id :
            self.employee_id = self.env.context.get('employee_id')
            
        if self.is_nps == 'No':
            self.contribution = False


    @api.constrains('pran_no')
    def _check_pran_no(self):
        for record in self:
            if record.pran_no and (len(record.pran_no) != 12):
                raise ValidationError("Invalid PRAN: It must be a 12-digit number.")


    def submit_nps_details(self):
        employee_nps = self.env['nps_employee_data'].sudo().search([('id','=', self.nps_id)])
        employee_nps.sudo().write({'state':'Requested'})
        
        if (self.is_nps == 'Yes' and employee_nps.is_nps == 'No') or (self.is_nps == 'Yes' and not employee_nps.is_nps):  
            template = self.env.ref('payroll_inherit.nps_enrolment_mail_template')
            cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
            email_to = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else []
            applied_user = self.env.user.employee_ids.name if self.env.user.employee_ids.name else 'User'
            subject_emp = f"{applied_user} ({self.env.user.employee_ids.emp_code})" if self.env.user.employee_ids.emp_code else applied_user
            contribution = f"{self.contribution}% of Basic Salary" if self.contribution else None
            pran_no = self.pran_no if self.pran_no else 'To be generated'
            template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,contribution=contribution,pran_no = pran_no).send_mail(employee_nps.id,notif_layout="kwantify_theme.csm_mail_notification_light")


        elif self.is_nps == 'Yes' and employee_nps.is_nps == 'Yes':          #employee want to update contribution
            template = self.env.ref('payroll_inherit.nps_contribution_change_request_mail_template')
            email_to = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else []
            cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
            applied_user = self.env.user.employee_ids.name if self.env.user.employee_ids.name else 'User'
            subject_emp = f"{applied_user} ({self.env.user.employee_ids.emp_code})" if self.env.user.employee_ids.emp_code else applied_user
            old_contribution = f"{employee_nps.contribution}% of Basic Salary" if employee_nps.contribution else None
            new_contribution = f"{self.contribution}% of Basic Salary" if self.contribution else None
            template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,old_contribution=old_contribution,new_contribution = new_contribution).send_mail(employee_nps.id,notif_layout="kwantify_theme.csm_mail_notification_light")


        elif self.is_nps == 'No':  #employee want to stop NPS
            template = self.env.ref('payroll_inherit.nps_contribution_closure_request_mail_template')
            email_to = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else []
            cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
            applied_user = self.env.user.employee_ids.name if self.env.user.employee_ids.name else 'User'
            subject_emp = f"{applied_user} ({self.env.user.employee_ids.emp_code})" if self.env.user.employee_ids.emp_code else applied_user
            template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp).send_mail(employee_nps.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            




    

    def view_details_nps(self):
        view_id = self.env.ref("payroll_inherit.nps_update_data_view_form_manager").id
        action = {
            'name': 'NPS Details',
            'type': 'ir.actions.act_window',
            'res_model': 'nps_update_data',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.id,
            'context': {'create': False, 'delete': False}
        }
        return action
    

    def take_action_single_bulk_nps_data(self):
        view_id = self.env.ref("payroll_inherit.take_action_nps_action_wizard_form").id
        action = {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'nps_action_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'selected_active_ids': [self.id]}
        }
        return action


    def manual_rejection_nps_update_data(self):
        self.state = 'Rejected'
        self.action_taken_on = datetime.now()
        self.action_taken_by = self.env.user.employee_ids.id





class nps_action_wizard(models.TransientModel):
    _name = 'nps_action_wizard'


    remark = fields.Text('Remark')


    def action_approve_bulk_nps_data(self):
        active_ids = self.env.context.get('selected_active_ids')
        nps_data = self.env['nps_employee_data'].sudo().search([])
        contract_data =  self.env['hr.contract'].sudo().search([])
        update_records = self.env['nps_update_data'].search([('id','in',active_ids)])
        action_taken_rec = update_records.filtered(lambda x : x.state != 'Requested')
        if action_taken_rec:
            raise ValidationError('Approval cannot proceed as some requests have already been processed ..!')
        else:
            for ids in active_ids:
                active_rec = update_records.filtered(lambda x : x.id == ids)
                selected_emp_nps = nps_data.filtered(lambda x : x.id == active_rec.nps_id)
                selected_emp_contract = contract_data.filtered(lambda x : x.employee_id.id == active_rec.employee_id.id and x.state == 'open')
                update_records_len = len(self.env['nps_update_data'].search([('employee_id','=',selected_emp_nps.employee_id.id),('state','=','Approved')]))

                # IN OLD NPS CONTRIBUTION CHANGE CASE
                if active_rec.is_nps == 'Yes' and update_records_len > 0:
                    template = self.env.ref('payroll_inherit.nps_contribution_change_request_approval_mail_template')
                    email_to = active_rec.employee_id.work_email if active_rec.employee_id.work_email else []
                    cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                    applied_user = active_rec.employee_id.name if active_rec.employee_id.name else 'User'
                    subject_emp = f"{applied_user} ({active_rec.employee_id.emp_code})" if active_rec.employee_id.emp_code else applied_user
                    new_contribution = f"{active_rec.contribution}% of Basic Salary" if active_rec.contribution else None
                    template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,new_contribution = new_contribution).send_mail(active_rec.nps_id,notif_layout="kwantify_theme.csm_mail_notification_light")

                # IN NEW NPS CREATION CASE
                elif active_rec.is_nps == 'Yes' and update_records_len == 0 and active_rec.pran_no:
                    template = self.env.ref('payroll_inherit.nps_enrolment_approved_mail_template')
                    email_to = active_rec.employee_id.work_email if active_rec.employee_id.work_email else []
                    cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                    applied_user = active_rec.employee_id.name if active_rec.employee_id.name else 'User'
                    subject_emp = f"{applied_user} ({active_rec.employee_id.emp_code})" if active_rec.employee_id.emp_code else applied_user
                    contribution = f"{active_rec.contribution}% of Basic Salary" if active_rec.contribution else None
                    pran_no = active_rec.pran_no if active_rec.pran_no else 'To be generated'
                    template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,contribution=contribution,pran_no = pran_no).send_mail(active_rec.nps_id,notif_layout="kwantify_theme.csm_mail_notification_light")

                # IN NPS STOP CASE
                elif active_rec.is_nps == 'No':
                    template = self.env.ref('payroll_inherit.nps_contribution_closure_confirm_mail_template')
                    email_to = active_rec.employee_id.work_email if active_rec.employee_id.work_email else []
                    cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                    applied_user = active_rec.employee_id.name if active_rec.employee_id.name else 'User'
                    subject_emp = f"{applied_user} ({active_rec.employee_id.emp_code})" if active_rec.employee_id.emp_code else applied_user
                    pran_no = active_rec.pran_no if active_rec.pran_no else 'To be generated' 
                    closure_date = date.today().strftime('%d-%b-%Y')
                    template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,pran_no=pran_no,closure_date=closure_date).send_mail(active_rec.nps_id,notif_layout="kwantify_theme.csm_mail_notification_light")


                selected_emp_nps.sudo().write({'state': 'Not_started' if active_rec.is_nps == 'No' else 'Running' if active_rec.is_nps == 'Yes' and active_rec.pran_no else 'Requested',
                                               'is_nps':active_rec.is_nps,'contribution':active_rec.contribution,
                                                'existing_pran_no':active_rec.existing_pran_no if active_rec.is_nps == 'Yes' else False,
                                                'pran_no':active_rec.pran_no,'remark_of_action':self.remark,
                                                'action_taken_date':date.today()})
                
                selected_emp_contract.sudo().write({'is_nps': active_rec.is_nps if active_rec.is_nps else selected_emp_contract.is_nps,
                                            'contribution': active_rec.contribution if active_rec.contribution else False,
                                            'existing_pran_no': active_rec.existing_pran_no if active_rec.existing_pran_no else selected_emp_contract.existing_pran_no,
                                            'pran_no':active_rec.pran_no if active_rec.pran_no else selected_emp_contract.pran_no})

                active_rec.state = 'Approved'
                active_rec.remark_of_action = self.remark
                active_rec.action_taken_on = datetime.now()
                active_rec.action_taken_by = self.env.user.employee_ids.id




    def action_reject_bulk_nps_data(self):
        active_ids = self.env.context.get('selected_active_ids')
        nps_data = self.env['nps_employee_data'].sudo().search([])
        update_records = self.env['nps_update_data'].search([])
        update_selected_records = update_records.filtered(lambda x : x.id in active_ids)
        action_taken_rec = update_selected_records.filtered(lambda x : x.state != 'Requested')
        if action_taken_rec:
            raise ValidationError('Rejection cannot proceed as some requests have already been processed ..!')
        elif not self.remark:
            raise ValidationError('Provide remark before Rejecting ..!')
        else:
            for ids in active_ids:
                active_rec = update_records.filtered(lambda x : x.id == ids)
                selected_emp_nps = nps_data.filtered(lambda x : x.id == active_rec.nps_id)
                update_records_len = len(self.env['nps_update_data'].search([('employee_id','=',selected_emp_nps.employee_id.id),('state','=','Approved')]))

                # IN NEW NPS CREATION CASE
                # if selected_emp_nps.is_nps == 'No' or (selected_emp_nps.is_nps == 'No' and active_rec.is_nps == 'No'):
                if update_records_len == 0:
                    template = self.env.ref('payroll_inherit.nps_enrolment_rejected_mail_template')
                    email_to = active_rec.employee_id.work_email if active_rec.employee_id.work_email else []
                    cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                    applied_user = active_rec.employee_id.name if active_rec.employee_id.name else 'User'
                    subject_emp = f"{applied_user} ({active_rec.employee_id.emp_code})" if active_rec.employee_id.emp_code else applied_user
                    remark = self.remark if self.remark else ''
                    template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,remark=remark).send_mail(active_rec.nps_id,notif_layout="kwantify_theme.csm_mail_notification_light")


                # IN OLD NPS CONTRIBUTION CHANGE CASE
                # elif selected_emp_nps.is_nps == 'Yes' and active_rec.is_nps == 'Yes':
                elif update_records_len > 0:
                    template = self.env.ref('payroll_inherit.nps_contribution_change_request_rejected_mail_template')
                    email_to = active_rec.employee_id.work_email if active_rec.employee_id.work_email else []
                    cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                    applied_user = active_rec.employee_id.name if active_rec.employee_id.name else 'User'
                    subject_emp = f"{applied_user} ({active_rec.employee_id.emp_code})" if active_rec.employee_id.emp_code else applied_user
                    template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp).send_mail(active_rec.nps_id,notif_layout="kwantify_theme.csm_mail_notification_light")

                if active_rec.after_login == 'Yes':
                    selected_emp_nps.write({'state':'Not_started','remark_of_action':self.remark,'action_taken_date':date.today(),'contribution':None,'is_nps':False,'existing_pran_no':False,'pran_no':False})
                else:
                    emp_update_check = update_records.filtered(lambda x : x.employee_id.id == active_rec.employee_id.id and x.state == 'Approved')

                    if emp_update_check:
                        selected_emp_nps.write({'state':'Running','remark_of_action':self.remark,'action_taken_date':date.today()})
                    else:
                        selected_emp_nps.write({'state':'Not_started','remark_of_action':self.remark,'action_taken_date':date.today(),'contribution':None,'is_nps':False,'existing_pran_no':False,'pran_no':False})

                active_rec.state = 'Rejected'
                active_rec.action_taken_on = datetime.now()
                active_rec.action_taken_by = self.env.user.employee_ids.id
                active_rec.remark_of_action = self.remark