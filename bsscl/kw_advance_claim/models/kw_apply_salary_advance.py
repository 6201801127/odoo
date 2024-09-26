from email.policy import default
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import datetime
import re
import calendar
from datetime import datetime
from dateutil import relativedelta
from ast import literal_eval
import requests, json
import odoo.addons.decimal_precision as dp

state_selection = [('draft', 'Draft'), ('applied', 'Applied'),
                   ('approve', 'Approved'), ('hold', 'Hold'),
                   ('grant', 'Grant'), ('cancel', 'Cancelled'), ('release', 'Release'),('paid', 'Paid'),('reject', 'Rejected')]


class kw_apply_salary_advance(models.Model):
    _name = 'kw_advance_apply_salary_advance'
    _description = "Salary Advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.onchange('total_install')
    def _compute_install_amnt(self):
        try:
            for rec in self:
                rec.install_amnt = rec.adv_amnt / rec.total_install
        except ZeroDivisionError:
            pass

    @api.onchange('applicant')
    def _get_employee_id(self):
        if self.applicant == 'subordinate':
            self.employee_id = False
            return {'domain': {'employee_id': [('parent_id', '=', self.env.user.employee_ids.id)]}}
        else:
            self.employee_id = self.env.user.employee_ids.id

    @api.depends('current_user')
    def _check_ra(self):
        for rec in self:
            if rec.current_user.has_group('bsscl_employee.group_hr_ra'):
                rec.check_is_ra = True

    @api.depends('name')
    
    def _compute_btn_access(self):

        self.hide_btn_cancel = False
        self.show_ra_button = False
        self.show_accounts_button = False
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True

                if record.state == 'approve' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'grant' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True



    @api.onchange('emi_start_date')
    def _compute_emi_start_month(self):
        for rec in self:
            if self.emi_start_date:
                month = datetime.strptime(str(self.emi_start_date), "%Y-%m-%d").strftime('%B-%Y')
                self.emi_start_month = month
            else:
                month = datetime.strptime(str(date.today()), "%Y-%m-%d").strftime('%B-%Y')
                self.emi_start_month = month
                # print("emi_start_month---------------------------",self.emi_start_month)


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for res in self:
            if res.employee_id:
                empl_id = self.employee_id.id
                # empl_grade = res.employee_id.grade.id if res.employee_id.grade else False
                # empl_band = res.employee_id.emp_band.id if res.employee_id.emp_band else False
                # empl_location_id = res.employee_id.job_branch_id.id
                """fetch eligible amount for the employee"""
                # eligible_amount = self.env['kw_advance_amount_eligibility_conf'].sudo().search(
                #     [('location_ids', '=', empl_location_id), ('grade_ids', '=', empl_grade),
                #      ('band_ids', '=', empl_band)])
                eligible_amount = self.env['kw_advance_amount_eligibility_conf'].sudo().search([])
                if eligible_amount == 0:
                    """RET employee"""
                    advance_applicable = self.env['kw_advance_ret_config'].sudo().search([('employee_ids', '=', empl_id)])
                    if advance_applicable:
                        for rec in advance_applicable:
                            self.interest = rec.interest
                            self.eligibility_amt = rec.eligibility_amt
                    else:
                        """Other than RET"""
                        self.eligibility_amt = eligible_amount.max_elig_amount

                if res.eligibility_amt == 0 and eligible_amount:
                    self.eligibility_amt = eligible_amount.max_elig_amount

                if res.interest == 0 and eligible_amount:
                    self.interest = eligible_amount.interest

    @api.onchange('write_uid')
    def _compute_approved_by(self):
        for rec in self:
            if rec.write_uid:
                rec.approved_by = rec.write_uid.employee_ids.id

    @api.onchange('p_deduction_line_ids')
    def _compute_preclosure_applied(self):
        for rec in self:
            if len(rec.p_deduction_line_ids) >= 1:
                rec.pre_closure_applied = True
            else:
                rec.pre_closure_applied = False

    @api.onchange('relaxation_line_ids')
    def _compute_relaxation_line_ids(self):
        for rec in self:
            if len(rec.relaxation_line_ids) >= 1:
                rec.buffer_applied = True
            else:
                rec.buffer_applied = False

    # Form fields
    name = fields.Char(string="Ref No", required=True, default="New", readonly="1")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant = fields.Selection(string="Advance apply for", required=True,
                                 selection=[('self', 'Self'), ('subordinate', 'Subordinate')], default='self')
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    adv_amnt = fields.Float(string="Advance Amount", required=True, tracking=True,
                            digits=dp.get_precision('Advance'))
    adv_purpose = fields.Many2one('kw_advance_purpose', string="Advance Purpose", required=True)
    total_install = fields.Integer(string="No. of Installment", default=0, required=True)
    install_amnt = fields.Float(string="Installment Amount", compute='_compute_install_amnt')
    req_date = fields.Date(string="Required Date" ,default = date.today())
    description = fields.Text(string="Description", required=True)
    emi_start_date = fields.Date(string="Installment Start Date")
    payment_date = fields.Date(string="Disburse Date", tracking=True)
    eligibility_amt = fields.Integer(string="Eligible Amount", readonly=True)
    interest = fields.Integer(string='Interest(% pa)', readonly=True)
    state = fields.Selection(string='Status', selection=state_selection, default='draft', tracking=True)

    check_is_ra = fields.Boolean(string='Is RA', compute='_check_ra', default=False, store=True)
    current_user = fields.Many2one('res.users', default=lambda self: self.env.user)
    deduction_line_ids = fields.One2many('kw_advance_deduction_line', 'deduction_id', string='Deduction', ondelete='cascade')
    temp_deduction_line_ids = fields.One2many('kw_temp_advance_deduction_line', 'deduction_id', string='Temp Deduction', ondelete='cascade')
    p_deduction_line_ids = fields.One2many('kw_pre_closure_deduction_line', 'p_deduction_id',
                                           string='Pre closure Payment', ondelete='cascade')
    relaxation_line_ids = fields.One2many('kw_advance_log_relaxation_period', 'salary_adv_id',
                                          string='Relaxation Period', ondelete='cascade')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)

    # division = fields.Many2one('hr.department', string="Division", related='employee_id.division', store=True)
    # section = fields.Many2one('hr.department', string="Section", related='employee_id.section', store=True)
    # practise = fields.Many2one('hr.department', string="Practice", related='employee_id.practise', store=True)
    job_id = fields.Many2one('hr.job', string="Designation", related='employee_id.job_id', store=True)
    buffer_period = fields.Many2one('kw_advance_buffer_period_master', string='Relaxation Period')
    emi_start_month = fields.Char(string="Installment Start Month", compute=_compute_emi_start_month)
    # emp_grade = fields.Many2one('kwemp_grade_master',related="employee_id.grade")
    # emp_band = fields.Many2one('kwemp_band_master',related="employee_id.emp_band")
    # remark action on button
    remark = fields.Text(string="RA Remarks")
    accounts_remark = fields.Text(string="Finance Remarks")
    approved_on = fields.Date(string="Approved On",tracking=True)
    approved_by = fields.Many2one('hr.employee', string="Approved By", compute=_compute_approved_by,tracking=True)
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by",tracking=True)
    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By",tracking=True)
    forwarded_by = fields.Many2one('hr.employee', string="Forwarded By",tracking=True)
    # hide/show button
    hide_btn_cancel = fields.Boolean(compute='_compute_btn_access')
    show_apply_btn = fields.Boolean(string="Show Apply Button")
    show_ra_button = fields.Boolean(compute='_compute_btn_access')
    show_accounts_button = fields.Boolean(compute='_compute_btn_access')
    # finace_take_action = fields.Boolean(compute='_compute_btn_access')

    approval_id = fields.Many2one('hr.employee',tracking=True)
    approval_amount = fields.Float(string="Approval Amount")
    adv_amnt_required = fields.Float(string="Advance Required")
    installment_required = fields.Integer(string="Installment Required")
    pending_status = fields.Selection(string='Pending At',
                                      selection=[('ra', 'Pending at RA'), ('accounts', 'Pending at Accounts')],
                                      tracking=True)
    closer_type = fields.Selection(string='Closure Type', selection=[('partial', 'Partial'), ('full', 'Full')],
                                   tracking=True)
    total_month_count = fields.Integer(string='No. of Installment(s)', tracking=True)
    pre_closure_applied = fields.Boolean(compute=_compute_preclosure_applied)
    buffer_applied = fields.Boolean(compute=_compute_relaxation_line_ids)
    migrated_data = fields.Boolean(string='Migrated Data',default=False)
    check_user = fields.Boolean(compute="_check_user_loan")

    @api.depends('employee_id')
    def _check_user_loan(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
                # print("++++++++++++++++++++++")
            else:
                record.check_user = False
                # print("check user not=====================")



    @api.constrains('adv_amnt', 'eligibility_amt', 'total_install')
    def advance_amt_val(self):
        if self.total_install <= 0:
            raise ValidationError("No of installment cannot be 0 or less than 0.")
        
    @api.constrains('description')
    @api.onchange('description')	
    def _onchange_description(self):
        for rec in self:
            if rec.description and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.description)):
                raise ValidationError("Description should be an alphabet")
            if rec.description:
                if len(rec.description) > 500:
                    raise ValidationError('Number of characters must not exceed 500')
                
    @api.constrains('req_date')
    # @api.onchange('req_date')	
   
    def _check_req_date(self):
        for rec in self:
            today=datetime.now().date()
            print("today today", today, rec.req_date)
            if rec.req_date:
                if rec.req_date < today:
                    raise ValidationError(_('Your requested date can not be a past date.'))

    @api.model
    def default_get(self, fields):
        res = super(kw_apply_salary_advance, self).default_get(fields)
        # eos = self.env['kw_end_of_service'].search([('applicant_id', '=', self.env.user.employee_ids.id)])
        empl_grade = False
        empl_band = False
        eligible_amount = False
        # if eos:
        #     raise ValidationError("You cannot apply Salary Advance as you have applied for End of service.")

        # if not self.env.user.employee_ids:
        #     raise ValidationError("You are not allowed to apply for Salary Advance.")
        """ for Eligibility amount"""
        res['eligibility_amt'] = 0
        """ Interest Rate"""
        res['interest'] = 0
        restricted_users_val = self.env['kw_advance_allow_restricted_loan'].sudo().search(
            [('active', '=', True), ('advance_type', '=', 'salary_advance')])
        # print("restricted_users_val--------",restricted_users_val)
        users_list = restricted_users_val.mapped('employee_id').ids
        # print("users_list",users_list,self.env.user.employee_ids.id)
        if self.env.user.employee_ids.id not in users_list and self.env.user.employee_ids.transfer_date:
            eligibility_criteria = self.env['ir.config_parameter'].sudo().get_param('kw_advance_claim.advance_eligibility_criteria')
            dote_of_join = self.env.user.employee_ids.transfer_date + relativedelta.relativedelta(months=+int(eligibility_criteria))
            max_limit = dote_of_join - self.env.user.employee_ids.transfer_date
            days_total = date.today() - self.env.user.employee_ids.transfer_date
            if days_total.days < int(max_limit.days):
                raise ValidationError("You are not eligible to apply for salary advance.")
        granted_record = self.sudo().search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('state', 'not in', ['reject', 'cancel', 'paid'])])
        # record = self.sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('state', 'not in', ['reject', 'cancel', 'paid'])])
        record = granted_record
        if granted_record:
            if len(granted_record) > 1:
                raise ValidationError("You are not allowed to apply for more than 2 advance request.")
        if record:
            rec = self.env['kw_advance_allow_for_another_loan'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id)])
            if rec and rec.advance_type_id.alias == 'salary':
                res['eligibility_amt'] = rec.loan_elig_amnt
            else:
                raise ValidationError("You are not allowed to apply for another advance request.")

        if self.env.user:
            if self.env.user.employee_ids:
                empl_id = self.env.user.employee_ids.id
                # empl_grade = self.env.user.employee_ids.grade.id if self.env.user.employee_ids.grade else False
                # empl_band = self.env.user.employee_ids.emp_band.id if self.env.user.employee_ids.emp_band else False
                # empl_location_id = self.env.user.employee_ids.job_branch_id.id
                """fetch eligible amount for the employee"""
                domain = []
                # if self.env.user.employee_ids.grade.has_band:
                #     domain = [('location_ids', '=', empl_location_id), ('grade_ids', '=', empl_grade),
                #     ('band_ids', '=', empl_band)]
                # else:
                #     domain = [('location_ids', '=', empl_location_id), ('grade_ids', '=', empl_grade)]

                eligible_amount = self.env['kw_advance_amount_eligibility_conf'].sudo().search(domain)
                if res['eligibility_amt'] == 0:
                    """RET employee"""
                    advance_applicable = self.env['kw_advance_ret_config'].sudo().search(
                        [('employee_ids', '=', empl_id)])
                    if advance_applicable:
                        for rec in advance_applicable:
                            res['interest'] = rec.interest
                            res['eligibility_amt'] = rec.eligibility_amt
                    else:
                        """Other than RET"""
                        res['eligibility_amt'] = eligible_amount.max_elig_amount

                if res['eligibility_amt'] == 0 and eligible_amount:
                    res['eligibility_amt'] = eligible_amount.max_elig_amount

            # check_exec_interest = self.env['kw_advance_interest_exec'].sudo().search([('employee_id','=',empl_id)])
            # if check_exec_interest:
            # 	res['interest'] = check_exec_interest.interest
            # else:
            # 	res['interest'] = eligible_amount.interest
            if res['interest'] == 0 and eligible_amount:
                res['interest'] = eligible_amount.interest

        return res

    @api.model
    def create(self, vals):
        vals['show_apply_btn'] = True
        if vals.get('adv_amnt') <= 0.00:
            raise ValidationError("Please add advance amount.")
        vals['adv_amnt_required'] = vals.get('adv_amnt')
        vals['installment_required'] = vals.get('total_install')
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('kw_apply_salary_advance') or '/'
        res = super(kw_apply_salary_advance, self).create(vals)
        return res

    
    def write(self, vals):
        if vals.get('adv_amnt') and self.adv_amnt_required < vals.get('adv_amnt'):
            raise ValidationError("Advance amount can not be greater than applied amount.")

        # if vals.get('total_install') and self.installment_required < vals.get('total_install'):
        #     raise ValidationError("No. of installments can not be greater than requested installments.")

        res = super(kw_apply_salary_advance, self).write(vals)
        return res

    def apply_salary_advance(self):
        status = "Applied"
        if self.applicant == 'self':
            dept_head_mail = self.employee_id.department_id.manager_id.work_email
            self.write({'state': 'applied', 'action_to_be_taken_by': self.employee_id.parent_id.id, 'pending_status': 'ra'})
            template_id = self.env.ref('kw_advance_claim.kw_salary_advance_apply_mail_template')
            template_id.with_context(status=status, work_email=dept_head_mail).send_mail(self.id,
                                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")
            # self.env.user.notify_success("Salary Advance applied successfully.")
        else:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
            emp_name = current_employee and current_employee.name or self.env.user.name
            accounts_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_account')
            accounts_employees = accounts_group.users.mapped('employee_ids') or False
            email_ids = accounts_employees and ','.join(accounts_employees.mapped('work_email')) or ''
            mail_context = 'Approved'
            self.write({
                'state': 'approve',
                'approved_on': date.today(),
                'approved_by': self.env.user.employee_ids.id,
                'remark': self.remark,
                'action_to_be_taken_by': self.env.user.employee_ids.id,
                'action_taken_by': self.env.user.employee_ids.id,
                'approval_id': self.env.user.employee_ids.id,
                'approval_amount': self.adv_amnt,
                'pending_status': 'accounts',
            })
            # mail Ra to user
            template_id = self.env.ref('kw_advance_claim.kw_salary_advance_user_status_email_template')
            template_id.with_context(get_state=mail_context).send_mail(self.id,
                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")
            # mail RA to accounts
            template = self.env.ref('kw_advance_claim.kw_salary_advance_approve_mail_template')
            template.with_context(accounts_email=email_ids, user_name=emp_name, get_state=mail_context).send_mail(
                self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
          
    def advance_settelment_btn(self):
        for record in self.deduction_line_ids:
            if record and record.status == 'paid':
                self.state = 'paid' if self.state == 'release' else ''
            if record.status == 'paid':
                self.state = 'paid'
            if record.status == 'draft':
                self.state = 'release'
            if self.state == 'release':
                raise ValidationError("Some installments are still pending.")
                
    def update_advance_settlement_status(self):
        advance = self.env['kw_advance_apply_salary_advance'].sudo().search(['|', ('state', '=', 'release'), '|', ('state', '=', ''), ('state', '=', False)])
        for rec in advance:
            is_paid = True
            for record in rec.deduction_line_ids:
                if record.status != 'paid':
                    is_paid = False
            if is_paid is True:
                rec.state = 'paid'

    
    def sal_adv_take_action_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_takeaction_form').id
        action = self.env.ref('kw_advance_claim.kw_apply_salary_advance_takeaction_form_refresh').read()[0]

        target_id = self.id
        action['res_id'] = target_id
        return action
        # return {
        #     'name': 'Take Action',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_advance_apply_salary_advance',
        #     'res_id': target_id,
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'views': [(view_id, 'form')],
        #     'target': 'self',
        #     'view_id': view_id,
        # }

    
    def sal_adv_approve(self):
        if self.adv_amnt > self.eligibility_amt:
            view_id = self.env.ref('kw_advance_claim.kw_salary_advance_approve_remark_wizard_form_view2').id
        else:
            view_id = self.env.ref('kw_advance_claim.kw_salary_advance_approve_remark_wizard_form_view').id
        return {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_sal_approv_remark_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_sal_adv_id': self.id},
        }


    def sal_adv_grant_approve(self):
        if self.adv_amnt > self.eligibility_amt:
            view_id = self.env.ref('kw_advance_claim.kw_salary_advance_grant_remark_wizard_form_view2').id
        else:
            view_id = self.env.ref('kw_advance_claim.kw_salary_advance_grant_remark_wizard_form_view').id
        return {
            'name': 'Remarks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_sal_grant_remark_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_sal_adv_id': self.id},
        }


    def sal_adv_take_action_account_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_takeaction_account_form').id
        action = self.env.ref('kw_advance_claim.kw_apply_salary_advance_takeaction_account_action_form_refresh').read()[0]
        target_id = self.id
        action['res_id'] = target_id
        return action
        # return {
        #     'name': 'Take Action',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_advance_apply_salary_advance',
        #     'res_id': target_id,
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'views': [(view_id, 'form')],
        #     'target': 'self',
        #     'view_id': view_id,
        # }

    
    def get_emp_email(self):
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        if emp_name:
            return emp_name.work_email
        else:
            return ""

    def get_ra_email(self):
        emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        ra_email = ''
        if emp_id:
            ra_email = emp_id.parent_id.work_email if emp_id.parent_id else ""
        return ra_email

    def get_emp_name(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        username = employee and employee.name or self.create_uid.name
        return username

    
    def delete_deduction_lines(self):
        for rec in self:
            rec.deduction_line_ids = [(5, 0, 0)]

    # @api.constrains('payment_date')
    # def payment_date_check(self):
    #     if self.payment_date:
    #         if self.payment_date < self.create_date.date() or self.payment_date > datetime.today().date():
    #             raise ValidationError(_("Disburse date should be after Applied date: %s and before today date.") % (self.payment_date))

    """ EMI calculation """
    @api.onchange('adv_amnt', 'total_install', 'emi_start_date', 'req_date', 'payment_date', 'buffer_period',
                  'closer_type', 'total_month_count')
    def calculate_emi(self):
        buffer_value = False
        """ Assign buffer period variable as True when a buffer is added """
        if self.buffer_period:
            buffer_value = True
        """ 1) Update EMI start date 
            2) Raise Validation if emi start date less than today """
        if self.req_date and not self.buffer_period and not self.payment_date:
            # self.emi_start_date = self.req_date + relativedelta.relativedelta(months=1, day=1)
            self.emi_start_date = self.req_date
            if self.req_date < datetime.now().date() and not (self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group('bsscl_employee.group_hr_ra')) :
                self.req_date = False
                return {'warning': {
                    'title': _('Validation Error'),
                    'message': _('Required Date cannot be a past date.')
                }}
        """ Assign Employee id to variable """
        emp_id = self.employee_id
        """ Start EMI calculation """
        if self.total_install > 0 and self.adv_amnt > 0 and self.emi_start_date \
                and (self.req_date or self.payment_date) and not self.closer_type and not self.total_month_count:
            """ Clear one2many line ids when there is no buffer """
            if buffer_value == False and self.state != 'release':
                self.delete_deduction_lines()
            month_count = False
            next_month = False
            """ calculate principal,installment amount,paid amount,rate of interest """
            p = self.adv_amnt
            install_amnt = self.adv_amnt / self.total_install
            paid_amt = install_amnt
            new_dt = self.req_date  # fetch EMI start date from db
            dt = new_dt
            r = self.interest / 100
            required_date = self.req_date
            """ update required date variable when payment date is updated """
            if self.payment_date:
                required_date = self.payment_date
            current_req_Date = required_date
            """ Calculate interest of the left days of the current month """
            day_interst = ((p * r) / 12 / calendar.monthrange(current_req_Date.year, current_req_Date.month)[1]) * (
                    calendar.monthrange(current_req_Date.year, current_req_Date.month)[1] - current_req_Date.day + 1)
            remaining_day_interest = day_interst

            delete_list = []
            """ Generating EMI without buffer period """
            if buffer_value == False:
                total_instal = False
                """ Total_instal is used to iterate to calculate EMI on no of installment """
                if self.req_date.day == 1:
                    total_instal = self.total_install - 1
                elif self.total_install > 1:
                    total_instal = self.total_install - 1
                else:
                    total_instal = self.total_install
                remaining_count = False
                """ looping """
                for rec in range(total_instal):
                    no_months_days = calendar.monthrange(dt.year, dt.month)[1]  # no of days in the following month
                    if new_dt:
                        # if self.emi_start_date.day != 1:
                        #     return {'warning': {
                        #         'title': ('Validation Error'),
                        #         'message': (
                        #             'Please Ensure Installment Start Date should be the 1st day of the month.')
                        #     }}
                        # remaining_count = True
                        #     print("new_dt.day=",new_dt.day)
                        # else:
                        """ creating EMI line when next_month is false """
                        if next_month == False:
                            next_month = new_dt + relativedelta.relativedelta(months=1, day=1)
                            dt = next_month
                            dat =self.req_date
                            bal = abs(p - install_amnt)
                            employee = emp_id
                            mi = remaining_day_interest
                            total_amnt = install_amnt + remaining_day_interest
                            if self.temp_deduction_line_ids:
                                for rec1 in self:
                                    rec1.temp_deduction_line_ids = [(5, 0, 0)]
                            self.update_temp_deduction_lines(dat, mi, install_amnt, bal, total_amnt, employee)
                        else:
                            """ updating next month value """
                            next_month = next_month + relativedelta.relativedelta(months=1, day=1)
                            dt = next_month
                        """ creating EMI line when total_intall is greater than 1 """
                        if self.total_install > 1:
                            p = p - paid_amt
                            if remaining_day_interest and month_count == False:
                                emi = (((p * r) / 12 / no_months_days) * no_months_days)
                                month_count = True
                            else:
                                emi = (((p * r) / 12 / no_months_days) * no_months_days)
                            total_amnt = install_amnt + emi
                            balance = p
                            mi = emi
                            bal = abs(balance - install_amnt)
                            self.update_temp_deduction_lines(next_month, mi, install_amnt, bal, total_amnt, emp_id)
            """ Generating EMI with buffer period """
            if buffer_value == True:
                paid_installment = False
                paid_principal_amount = False
                left_month_list = []
                left_balance = []
                paid_status = False
                """ Calculating paid installment,current month date,left principal,left installment """
                if self.buffer_period:
                    left_month_list.clear()
                    for rec in self.deduction_line_ids:
                        if rec.status == 'paid':
                            paid_principal_amount = paid_principal_amount + rec.principal_amt
                            if rec.principal_amt != 0.00:
                                paid_installment = paid_installment + 1
                            left_month_list.append(rec.deduction_date)
                            left_balance.append(rec.balance)
                            paid_status = True
                        else:
                            delete_list.append(rec)
                left_principal = self.adv_amnt - paid_principal_amount
                left_installment = self.total_install - paid_installment
                current_month = False
                if left_month_list:
                    current_month = left_month_list[-1]
                dt = current_month
                month_count = False
                install_amnt = left_principal / left_installment
                skipped_month = False
                """ Beginning month is buffer """
                if self.buffer_period.buffer_period and not paid_installment and not paid_status:
                    """ Deleting one2many line ids """
                    if new_dt:
                        dt = new_dt
                        buffer_count = False
                        emi = False
                        """ creating buffered emi line depending upon total buffered month """
                        for buffer in delete_list[:self.buffer_period.buffer_period]:
                            if not buffer_count:
                                next_month = self.req_date
                                buffer_count = True
                                dt = next_month
                                emi = remaining_day_interest
                            else:
                                next_month = dt + relativedelta.relativedelta(months=1, day=1)
                                emi = (((p * r) / 12 / calendar.monthrange(next_month.year, next_month.month)[1]) *
                                       calendar.monthrange(next_month.year, next_month.month)[1])
                            self.update_buffered_record(buffer, next_month, 0, abs(emi), abs(emi), self.adv_amnt,  emp_id)
                           
                            """ Updating to Log """
                            self.update_advance_log(next_month, abs(emi), 0, self.adv_amnt, abs(emi), emp_id.id)
                            dt = next_month
                    
                    """ creating EMI line for the left principal,installment """
                    for rec in delete_list[self.buffer_period.buffer_period:]:
                        next_month = dt + relativedelta.relativedelta(months=1, day=1)
                        dt = next_month
                        no_months_days = calendar.monthrange(next_month.year, next_month.month)[1]
                        if month_count == False:
                            emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                            month_count = True
                        else:
                            emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                        total_amnt = install_amnt + emi
                        left_principal = left_principal - install_amnt
                        balance = left_principal
                        mi = emi
                        self.update_buffered_record(rec, next_month, install_amnt, mi, total_amnt, abs(balance),  emp_id)
                        
                        """ Updating to Log """
                        self.update_advance_log(next_month, mi, install_amnt , abs(balance), total_amnt, self.employee_id.id)
                    buff = len(self.deduction_line_ids.filtered(lambda rec : rec.principal_amt == 0.00)) + self.buffer_period.buffer_period
                    for rec in range(buff):
                        next_month = dt + relativedelta.relativedelta(months=1, day=1)
                        dt = next_month
                        no_months_days = calendar.monthrange(next_month.year, next_month.month)[1]
                        if month_count == False:
                            emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                            month_count = True
                        else:
                            emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                        total_amnt = install_amnt + emi
                        left_principal = left_principal - install_amnt
                        balance = left_principal
                        mi = emi
                        self.deduction_line_ids = [(0, 0, {
                            'deduction_date': next_month,
                            'principal_amt': install_amnt,
                            'monthly_interest': mi,
                            'amount': total_amnt,
                            'balance': abs(balance),
                            'tax_amount': 0.00,
                            'payment_by': '',
                            'status': 'draft',
                            'employee_id': emp_id.id,
                        })]
                        """ Updating to Log """
                        self.update_advance_log(next_month, mi, install_amnt, abs(balance), total_amnt, self.employee_id.id)
                    d_list = len(self.deduction_line_ids) - (self.total_install + self.buffer_period.buffer_period)
                    if d_list > 0:
                        self.deduction_line_ids = [(2, rec.id) for rec in self.deduction_line_ids[-d_list:]]

                """ Between month is buffer """
                if paid_installment or paid_status:
                    for rec in delete_list[self.buffer_period.buffer_period:]:
                        if dt:
                            """ creating buffered emi line depending upon total buffered month """
                            if self.buffer_period.buffer_period and skipped_month == False:
                                month_count = False
                                for buffer in delete_list[:self.buffer_period.buffer_period]:
                                    next_month = dt + relativedelta.relativedelta(months=1, day=1)
                                    emi = (((left_principal * r) / 12 /
                                            calendar.monthrange(next_month.year, next_month.month)[1]) *
                                           calendar.monthrange(next_month.year, next_month.month)[1])
                                    balance = left_balance[-1]
                                    self.update_buffered_record(buffer, next_month, 0, abs(emi), abs(emi), abs(balance),  emp_id)
                                    
                                    dt = next_month
                                    """ Updating to Log """
                                    self.update_advance_log(next_month,abs(emi), 0.00 , abs(balance), abs(emi),  emp_id.id)
                                skipped_month = True
                            else:
                                next_month = dt + relativedelta.relativedelta(months=1, day=1)
                                dt = next_month
                            """ creating EMI line for the left principal,installment """
                            no_months_days = calendar.monthrange(next_month.year, next_month.month)[1]
                            if month_count == False:
                                emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                                month_count = True
                            else:
                                emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                            total_amnt = install_amnt + emi
                            left_principal = left_principal - install_amnt
                            balance = left_principal
                            mi = emi
                            next_start_month = next_month + relativedelta.relativedelta(months=1, day=1)
                            self.update_buffered_record(rec, next_start_month, install_amnt, mi, total_amnt, abs(balance),  emp_id)
                            
                            """ Updating to Log """
                            self.update_advance_log(next_month, mi, install_amnt, abs(balance), total_amnt,  self.employee_id.id)
                    buff = self.total_install - len(self.deduction_line_ids.filtered(lambda rec : rec.principal_amt != 0.00))
                    dt = dt + relativedelta.relativedelta(months=1, day=1)
                    for rec in range(buff):
                        emi = (((left_principal * r) / 12 / no_months_days) * no_months_days)
                        total_amnt = install_amnt + emi
                        left_principal = left_principal - install_amnt
                        balance = left_principal
                        mi = emi
                        dt = dt + relativedelta.relativedelta(months=1, day=1)
                        self.update_advance_deduction_lines(dt, mi, install_amnt, abs(balance), total_amnt,  emp_id)
                        """ Updating to Log """
                        self.update_advance_log(dt, mi, install_amnt,  abs(balance) ,total_amnt, emp_id.id)
                        
        """ Full Closer"""
        if self.closer_type == 'full':
            paid_principal_amount = False
            paying_list = []
            left_month_list = []
            next_month = False
            new_dt = self.req_date
            for rec in self.deduction_line_ids:
                if rec.status == 'draft' and rec.amount != 0:
                    paid_principal_amount += rec.principal_amt
                    paying_list.append(rec)
                else:
                    left_month_list.append(rec.deduction_date)
            if left_month_list:
                next_month = left_month_list[-1] + relativedelta.relativedelta(months=1, day=1)
            """ Adding pre-closure payment line """
            if paid_principal_amount:
                self.p_deduction_line_ids = [(0, 0, {
                    'paid_date': date.today(),
                    'closer_type': self.closer_type,
                    'month_count': self.total_month_count,
                    'amount': paid_principal_amount,
                    'employee_id': emp_id.id,
                })]
            """ updating full closure month's payment """
            if paying_list:
                for individual in paying_list:
                    individual.sudo().write({
                        'amount': individual.amount - individual.monthly_interest,
                        'status': 'paid',
                        'monthly_interest': 0
                    })

        """ Partial Closure """
        if self.closer_type == 'partial' and self.total_month_count and self.env.context.get('pre_closure'):
            period = 0
            m_val = False
            left_month_list = []
            delete_list = []
            re_calc_record_list = []
            for rec in self.deduction_line_ids:
                if rec.status == 'draft' and rec.principal_amt != 0:
                    period += 1
                    delete_list.append(rec)
                else:
                    re_calc_record_list.append(rec)
                    left_month_list.append(rec.deduction_date)
            period_range = period - self.total_month_count
            reversed_list = delete_list[::-1]
            left_principal = self.install_amnt * period_range
            r = self.interest / 100
            balance = left_principal
            """ updating partial closure month's payment """
            for rec in reversed_list[slice(self.total_month_count)]:
                rec.sudo().write({
                    'amount': rec.amount - rec.monthly_interest,
                    'status': 'paid',
                    'monthly_interest': 0,
                    'balance': 0.0,
                })
            """ re calculating and updating the EMI with left over principal"""
            for rec in delete_list[:(period - self.total_month_count)]:
                emi = (((balance * r) / 12 / rec.deduction_date.day) * rec.deduction_date.day)
                balance = balance - abs(self.install_amnt)
                rec.sudo().write({
                    'monthly_interest': abs(emi),
                    'amount': self.install_amnt + abs(emi),
                    'balance': abs(balance),
                })
            """ Adding pre-closure payment line """
            self.p_deduction_line_ids = [(0, 0, {
                'paid_date': date.today(),
                'closer_type': self.closer_type,
                'month_count': self.total_month_count,
                'amount': self.total_month_count * (self.adv_amnt / self.total_install),
                'employee_id': emp_id.id,
            })]

    def update_advance_log(self, dat=False, mi=False, install_amnt=False, bal=False, total_amnt=False, employee=False):
        """ Updating to Log """
        self.env['kw_advance_emi_ledger_log'].sudo().create({
            'deduction_date': dat,
            'principal_amt': install_amnt if install_amnt else 0,
            'monthly_interest': mi,
            'amount': total_amnt,
            'balance': bal,
            'tax_amount': 0.00,
            'payment_by': '',
            'status': 'draft',
            'employee_id': employee,
        })
    
    def update_buffered_record(self, rec=False ,dat=False, install_amnt=False, mi=False, total_amnt=False, bal=False,  employee=False):
        """ Updating to deduction line """
        rec.write({
                'deduction_date': dat,
                'principal_amt': install_amnt,
                'monthly_interest': mi,
                'amount': total_amnt,
                'balance': bal,
                'tax_amount': 0.00,
                'payment_by': '',
                'status': 'draft',
                'employee_id': employee.id,
            })

    def update_advance_deduction_lines(self, dat=False, mi=False, install_amnt=False, bal=False, total_amnt=False, employee=False):
        """ Updating to deduction line """
        self.deduction_line_ids = [(0, 0,{
            'deduction_date': dat,
            'principal_amt': install_amnt,
            'monthly_interest': mi,
            'amount': total_amnt,
            'balance': bal,
            'tax_amount': 0.00,
            'payment_by': '',
            'status': 'draft',
            'employee_id': employee.id,
        })]

    def update_temp_deduction_lines(self, dat=False, mi=False, install_amnt=False, bal=False, total_amnt=False, employee=False):
        """ Updating to deduction line """
        self.temp_deduction_line_ids = [(0, 0,{
            'deduction_date': dat,
            'principal_amt': install_amnt,
            'monthly_interest': mi,
            'amount': total_amnt,
            'balance': bal,
            'tax_amount': 0.00,
            'payment_by': '',
            'status': 'draft',
            'employee_id': employee.id,
        })]

    def move_deduction_line_data(self):
        """ 1)EMI datas added to Main deduction line
            2)Data from Temp deduction line is flushed
            3)logs are updated
        """
        delete_list = []
        for emi_line in self.temp_deduction_line_ids:
            delete_list.append(emi_line)
            self.deduction_line_ids = [(0, 0,{
                'deduction_date': emi_line.deduction_date if emi_line.deduction_date else '',
                'principal_amt': emi_line.principal_amt  if emi_line.principal_amt else '',
                'monthly_interest': emi_line.monthly_interest if emi_line.monthly_interest else '',
                'amount': emi_line.amount if emi_line.amount else '',
                'balance': emi_line.balance if emi_line.balance else '',
                'tax_amount': emi_line.tax_amount if emi_line.tax_amount else '',
                'payment_by': emi_line.payment_by if emi_line.payment_by else '',
                'status': emi_line.status if emi_line.status else '',
                'employee_id': emi_line.employee_id.id if emi_line.employee_id else '',
            })]
            """ updating child log """
            self.update_advance_log(emi_line.deduction_date, emi_line.monthly_interest, emi_line.principal_amt,
                                    emi_line.balance, emi_line.amount, emi_line.employee_id.id)
        """ updating parent log """
        record = self
        self.update_sal_adv_log(record)
        if delete_list:
            self.temp_deduction_line_ids = [(2, rec.id) for rec in delete_list]

    def update_sal_adv_log(self, record=False):
        if record:
            self.env['kw_sal_adv_log'].sudo().create({
                'sal_adv_id': record.id,
                'employee_id': record.employee_id.id,
                'currency_id': record.currency_id.id,
                'adv_amnt': record.adv_amnt,
                'adv_purpose': record.adv_purpose.id,
                'total_install': record.total_install,
                'req_date': record.req_date,
                'applied_date': record.create_date,
                'description': record.description,
                'payment_date': record.payment_date,
                'eligibility_amt': record.eligibility_amt,
                'interest': record.interest,
                'state': record.state,
                'department_id': record.department_id.id,
                # 'division': record.division.id,
                # 'section': record.section.id,
                # 'practise': record.practise.id,
                # 'job_id': record.job_id.id,
                'buffer_period': record.buffer_period.id,
            })

    
    def get_cc_email(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        all_jobs = self.env['hr.job'].browse(cc_group)
        email_list = []
        if cc_group:
            empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
            if empls:
                email_list = [emp.work_email for emp in empls if emp.work_email]
        return ",".join(email_list)

    # @api.onchange('adv_amnt', 'eligibility_amt')
    # def validate_message(self):
    #     if self.adv_amnt > self.eligibility_amt:
    #         message = _('Advance Amount is greater than the Eligibility Amount.')
    #         mess = {
    #             'title': _('Warning!'),
    #             'message': message
    #         }
    #         return {'warning': mess}

    
    def users_status_cc(self):
        emp_cc_mail_list = []
        param = self.env['ir.config_parameter'].sudo()
        emp_cc_mail_list += self.employee_id.department_id.manager_id.mapped('work_email')
        cc_hr_mails = param.get_param('kw_advance_claim.individual_hr_email')
        if cc_hr_mails and cc_hr_mails != "False":
            emp_cc_mail_list += cc_hr_mails.split(',')
        return ','.join(set(emp_cc_mail_list))

    
    def users_grant_cc(self):
        unique_mail_list = []
        unique_mail_list += self.employee_id.department_id.manager_id.mapped('work_email')
        unique_mail_list += self.employee_id.parent_id.mapped('work_email')
        param = self.env['ir.config_parameter'].sudo()
        cc_notify = param.get_param('kw_advance_claim.individual_hr_email')
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        all_jobs = self.env['hr.job'].browse(cc_group)
        if cc_group:
            empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
            if empls:
                unique_mail_list += [emp.work_email for emp in empls if emp.work_email]
        if cc_notify and cc_notify != "False":
            unique_mail_list.append(cc_notify)
        return ','.join(set(unique_mail_list))
