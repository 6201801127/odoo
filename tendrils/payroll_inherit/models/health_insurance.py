from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class health_insurance_dependant(models.Model):
    _name = 'health_insurance_dependant'
    _description = "Health Insurance Details"
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        if current_fiscal:
            return current_fiscal

    def _default_employee(self):
        if self.env.context.get('apply_user'):
            return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
            else:
                record.check_user = False
            if record.employee_id.user_id.id == self.env.user.id and record.state == 'draft':
                record.edit_boolean = True
            if (self.env.user.has_group('kw_employee.group_payroll_manager') or 
                self.env.user.has_group('payroll_inherit.payroll_insurance_group') and 
                record.state in ['draft', 'applied']): 
                record.edit_boolean = True
            if self.env.context.get('apply_user'):
                record.check_user = True

    @api.multi
    @api.depends("no_of_installment", "family_details_ids", "family_details_ids.insurance_amount", "insurance_amount")
    def _compute_total(self):
        for rec in self:
            data_ = self.env['health_insurance_configuration'].sudo().search([('code', '=', 'IC')]).value
            totall = 0
            amountt = 0
            for data in rec.family_details_ids:
                totall += data.insurance_amount
            rec.total_insurance_amount = False
            amountt += rec.insurance_amount
            if data_ == 1:
                rec.total_insurance_amount = totall
            elif data_ == 2:
                rec.total_insurance_amount = amountt

    @api.multi
    @api.depends("no_of_installment", "family_details_ids", "total_insurance_amount", "insurance_amount")
    def _get_emi_details(self):
        for rec in self:
            rec.emi_details_ids = [(5,)]
            for rec1, index in enumerate(range(int(rec.no_of_installment))):
                if date.today().day <= 25:
                    nextmonth = date.today() + relativedelta.relativedelta(months=index)
                    datetime_object = datetime.strptime(str(nextmonth.month), "%m")
                    full_month_name = datetime_object.strftime("%B")
                    rec.emi_details_ids = [(0, 0, {
                        'year': nextmonth.year,
                        'month': full_month_name,
                        'installment': rec.total_insurance_amount / int(rec.no_of_installment),
                        'status': 'unpaid',
                        'emi_date': nextmonth,
                        'emi_details_id': rec.id
                    })]
                else:
                    nextmonth = date.today() + relativedelta.relativedelta(months=index+1)
                    datetime_object = datetime.strptime(str(nextmonth.month), "%m")
                    full_month_name = datetime_object.strftime("%B")
                    rec.emi_details_ids = [(0, 0, {
                                    'year': nextmonth.year,
                                    'month': full_month_name,
                                    'installment': rec.total_insurance_amount/int(rec.no_of_installment),
                                    'status': 'unpaid',
                                    'emi_date': nextmonth,
                                    'emi_details_id': rec.id
                                })]

    @api.multi
    @api.depends('amount_', 'insurance_amount', 'employeer_contribution', 'no_of_installment')
    def gst_calculated_(self):
        for rec in self:
            # if rec.amount_:
            emp_cont_data = self.env['health_insurance_configuration'].sudo().search([('code', '=', 'EC')])
            if emp_cont_data:
                rec.employeer_contribution = emp_cont_data.value
            rec.employee_contribution = False
            rec.employee_contribution = rec.amount_ - rec.employeer_contribution
            if rec.employee_contribution < 0:
                rec.insurance_amount = False
                rec.insurance_amount = 0
            else:
                rec.insurance_amount = False
                rec.insurance_amount = rec.employee_contribution
            data = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id)]).current_ctc
            below_60 = self.env['ir.config_parameter'].sudo().get_param('insurance_emi_below_60')
            above_60 = self.env['ir.config_parameter'].sudo().get_param('insurance_emi_above_60')
            if data > 60000:
                rec.no_of_installment = above_60
            else:
                rec.no_of_installment = below_60

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr, required=True)
    employee_id = fields.Many2one('hr.employee', string="Name", required=True, default=_default_employee)
    department = fields.Char(related='employee_id.department_id.name', string="Department", store=True, track_visibility='always')
    boolean_readonly = fields.Boolean(string='Printed In Payslip', default=False, track_visibility='always')
    sum_assured_select = fields.Selection([('3_lkh', '3 Lakh'), ('5_lkh', '5 Lakh'), ('7_lkh', '7 Lakh'), ('10_lkh', '10 Lakh')],
                                         string='Sum Assured Amount', required=True, track_visibility='onchange')
    sum_assured = fields.Integer(string="Sum Assured Amount", track_visibility='always')
    no_of_installment = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('6', '6')], string='No of Installment', required=True, store=True, track_visibility='onchange',compute="gst_calculated_")
    amount_ = fields.Float(string="Total Premium Including GST", track_visibility='onchange')
    employeer_contribution = fields.Integer(string="CSM Contribution including GST", readonly=True, compute="gst_calculated_", store=True, track_visibility='onchange')
    employee_contribution = fields.Integer(string="Employee Contribution", compute="gst_calculated_", store=True, readonly=1, track_visibility='onchange')
    insurance_amount = fields.Float(string="Employee Contribution including GST", readonly=True, compute="gst_calculated_", store=True, track_visibility='onchange')
    family_details_ids = fields.One2many('family_details', 'family_details_id', string='Family Details')
    times_of_ded = fields.Integer(string='No of Deduction', track_visibility='onchange')
    hide_edit_btn = fields.Char(compute='_get_approval_rec', track_visibility='onchange')
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'),
                                        ('closed', 'Closed'),('rejected', 'Rejected')], default='draft', track_visibility='onchange')
    num_dependant = fields.Integer(track_visibility='onchange',string='No. of Dependents')
    relationship_name = fields.Char(compute='compute_dependant', track_visibility='onchange',string='Relationship')
    emi_details_ids = fields.One2many('health_insurance_emi', 'emi_details_id', string='Installment Details', compute="_get_emi_details", store=True)
    amount = fields.Float(string="Amount", compute='compute_dependant', track_visibility='onchange')
    applied_by = fields.Many2one("hr.employee", string='Applied By', track_visibility='onchange')
    applied_on = fields.Date(string='Applied On',track_visibility='onchange')
    approved_by = fields.Many2one("hr.employee", string='Approved By', track_visibility='onchange')
    approved_on = fields.Date(string='Approved On', track_visibility='onchange')
    check_user = fields.Boolean(compute="_check_user")
    edit_boolean = fields.Boolean(compute="_check_user")
    total_insurance_amount = fields.Float(compute="_compute_total", store=True)
    enable_revert = fields.Boolean(compute='_enable_revert_btn')
    enable_insurance_calculation = fields.Boolean(compute='enable_insur_calcu')
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    birthday = fields.Date(string='Date of Birth',related='employee_id.birthday')
    level = fields.Char(string='Level',related='employee_id.level.name')
    grade = fields.Char(string='Grade',related='employee_id.grade.name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('other', 'Other')],related='employee_id.gender')
    job_branch_id = fields.Many2one('kw_res_branch',string='Work Location',related='employee_id.job_branch_id')
    on_job_sts = fields.Char(string='Status',compute='_compute_on_job_status')
    employee_name = fields.Char(related='employee_id.name')
    employee_code = fields.Char(related='employee_id.emp_code')
    generated_by = fields.Char()
    period_from = fields.Date()
    period_to = fields.Date()
    allow_insurance_edit_boolean = fields.Boolean(default = False)
    
    def btn_duplicate(self):
        form_view_id = self.env.ref('payroll_inherit.payroll_generate_insurance_individual_view_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'views': [ (form_view_id, 'form')],
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'payroll_generate_insurance',
            'target': 'new',
            'context': {'default_from_date_range': self.date_range.id,'create':False,'edit':False,'current_id':self.id}
        }
        return action
    
    @api.depends('employee_id')
    def _compute_on_job_status(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.on_job_sts = 'Inactive'  if rec.employee_id.active == False else  'on notice period' if resignation else 'Active'


    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'draft':
                super(health_insurance_dependant, record).unlink()
            else:
                raise ValidationError("You can only delete records in draft state.")
        return True

    @api.model
    def create(self, vals):
        value = self.env['ir.config_parameter'].sudo().get_param('enable_health_insurance')
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        if  (not self.env.user.has_group('hr_payroll.group_hr_payroll_manager') or not  self.env.user.has_group('payroll_inherit.payroll_insurance_group')):
            if value == '0' and self.env.user.employee_ids.date_of_joining < current_fiscal.date_start:
                raise ValidationError("You are not allowed to create Health Insurance.")
        return super(health_insurance_dependant, self).create(vals)

    @api.depends('state')
    def _compute_css(self):
        for rec in self:
            value = self.env['ir.config_parameter'].sudo().get_param('enable_health_insurance')
            if value == '0' and not self.env.user.has_group('hr_payroll.group_hr_payroll_manager') and not self.env.user.has_group('payroll_inherit.payroll_insurance_group'):
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
            else:
                rec.test_css = False



    @api.onchange('sum_assured_select')
    def get_sum_assured(self):
        if self.sum_assured_select:
            if self.sum_assured_select == '3_lkh':
                self.sum_assured = 300000
            if self.sum_assured_select == '5_lkh':
                self.sum_assured = 500000
            if self.sum_assured_select == '7_lkh':
                self.sum_assured = 700000
            if self.sum_assured_select == '10_lkh':
                self.sum_assured = 1000000


    @api.depends('employee_id')
    @api.multi
    def enable_insur_calcu(self):
        # print("method call")
        emp_insu_calc = self.env['health_insurance_configuration'].search([('code', '=', 'IC')])
        # print()
        if emp_insu_calc:
            if emp_insu_calc.value == 1:
                self.enable_insurance_calculation = True
            elif emp_insu_calc.value == 2:
                self.enable_insurance_calculation = False

    @api.onchange('amount_', 'employee_contribution', 'employeer_contribution','no_of_installment')
    def gst_calculated(self):
        for rec in self:
            data = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id)]).current_ctc
            if rec.amount_:
                emp_cont_data = self.env['health_insurance_configuration'].sudo().search([('code', '=', 'EC')])
                if emp_cont_data:
                    rec.employeer_contribution = emp_cont_data.value
                rec.employee_contribution = False
                rec.employee_contribution = rec.amount_ - rec.employeer_contribution
                rec.insurance_amount = False
                rec.insurance_amount = rec.employee_contribution
            below_60 = self.env['ir.config_parameter'].sudo().get_param('insurance_emi_below_60')
            above_60 = self.env['ir.config_parameter'].sudo().get_param('insurance_emi_above_60')
            if data > 60000:
                rec.no_of_installment = above_60
            else:
                rec.no_of_installment = below_60

    @api.depends('state')
    def _enable_revert_btn(self):
        for rec in self:
            if rec.state == 'applied' and not self.env.user.has_group('kw_employee.group_payroll_manager') or not self.env.user.has_group('payroll_inherit.payroll_insurance_group') and not rec.create_uid.has_group('kw_employee.group_payroll_manager') or not rec.create_uid.has_group('payroll_inherit.payroll_insurance_group'):
                rec.enable_revert = True

    def date_diff(self,start_date):
        date_value = self.env['ir.config_parameter'].sudo().get_param('insurance_fiscal_year_date_stop_value(DD-MM-YYYY)')
        parameter_end_date = datetime.strptime(date_value, '%d-%m-%Y').date() if date_value else self.date_range.date_stop
        # end_date = self.date_range.date_stop
        month_diff = (parameter_end_date.year - start_date.year) * 12 + parameter_end_date.month - start_date.month
        return month_diff

    @api.constrains('no_of_installment')
    def check_valid_no_of_installment(self):
        if datetime.now().day >= 26:
            if int(self.no_of_installment) > self.date_diff(date.today()):
                raise ValidationError(f'{self.no_of_installment} installments is not allowed')
            # elif self.applied_on:
            #     # if int(self.no_of_installment) >= self.date_diff(self.applied_on):
            #     raise ValidationError(f'{self.no_of_installment} installments is not allowed')

    @api.constrains('employee_id')
    def check_esi_validation(self):
        for record in self:
            if record.employee_id.esi_applicable == True:
                raise ValidationError("You are not applicable for applying.")
    # def _auto_init(self):
    #     super(health_insurance_dependant, self)._auto_init()
    #     self.env.cr.execute("UPDATE health_insurance_dependant p SET num_dependant = subquery.dependant_count FROM (     SELECT f.family_details_id, COUNT(f.id) AS dependant_count  FROM family_details f    GROUP BY f.family_details_id )subquery WHERE p.id = subquery.family_details_id")

    @api.depends('family_details_ids')
    def compute_dependant(self):
        for rec in self:
            if len(rec.family_details_ids) > 0:
                # rec.num_dependant = len(rec.family_details_ids)
                name_lst = []
                for record in rec.family_details_ids:
                    name_lst += [record.relationship_id.name if record.relationship_id.name != False else '']
                    rec.amount += record.insurance_amount 
                rec.relationship_name = ",".join(name_lst)

    def btn_revert_record(self):
        self.state = 'draft'

    @api.constrains('no_of_installment')
    def validate_no_of_installment(self):
        for rec in self:
            if int(rec.no_of_installment) <= 0:
                raise ValidationError('No. of installment should be greater than 0')

    def apply_record(self):
        for rec in self:
            # if rec.insurance_submitting_date:
            #     if rec.insurance_submitting_date < date.today():
            #         raise ValidationError("Insurance date has been expaired")
            if self.env.user.has_group('kw_employee.group_payroll_manager') or self.env.user.has_group('payroll_inherit.payroll_insurance_group'):
                rec.approve_record()
                rec.write({'applied_on': date.today(), 'applied_by': self.env.user.employee_ids.id})
                mail_template = self.env.ref('payroll_inherit.health_insurance_approved_mail_template')
                mail_template.send_mail(
                rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                rec.write({'state': 'applied', 'applied_on': date.today(), 'applied_by': self.env.user.employee_ids.id})
                payroll_manager = self.env.ref('kw_employee.group_payroll_manager').users
                mail_template = self.env.ref('payroll_inherit.health_insurance_dependant_mail_template')
                # email_to = ','.join(payroll_manager.mapped('employee_ids.work_email'))
                email_to = 'manasi.das@csm.tech,supriti.kar@csm.tech'
                mail_template.with_context(emails=email_to).send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            if self.applied_on:
                if int(self.no_of_installment) > self.date_diff(self.applied_on):
                    raise ValidationError(f'{self.no_of_installment} installments is not allowed')
            self._get_emi_details()

    def btn_reject_record(self):
        for rec in self:
            rec.write({'state': 'rejected'})
    
    def btn_reset_record(self):
        for rec in self:
            rec.write({'state': 'draft'})


    def add_new_members(self):
        view_id = self.env.ref("payroll_inherit.add_health_insurance_dependencies_tree").id
        for rec in self:
            action = {
                'name': 'Add New Dependant',
                'type': 'ir.actions.act_window',
                'res_model': 'add_health_insurance_dependencies',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'health_insurance_id': rec.id,'employee_id':rec.employee_id.id,'year_id':rec.date_range.id,'department':rec.department},
                'domain': [('employee_id.user_id', '=', self.env.user.id),('health_insurance_id', '=', rec.id),('year_id', '=', rec.date_range.id)]
            }
        return action
                
    def approve_record(self):
        for rec in self:
            rec.write({'state': 'approved', 'approved_on': date.today(), 'approved_by': self.env.user.employee_ids.id})
            mail_template = self.env.ref('payroll_inherit.health_insurance_approved_mail_template')
            mail_template.send_mail(
                rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        if self.approved_on:
            if int(self.no_of_installment) > self.date_diff(self.approved_on):
                raise ValidationError(f'{self.no_of_installment} installments is not allowed')
        self._get_emi_details()

    @api.depends('boolean_readonly')
    def _get_approval_rec(self):
        for rec in self:
            if rec.state == 'approved':
                rec.hide_edit_btn = 'Yes'
            else:
                rec.hide_edit_btn = 'No'

    @api.constrains('employee_id', 'date_range', 'family_details_ids')
    def validate_employee_id(self):
        for rec in self:
            record = self.env['health_insurance_dependant'].sudo().search(
                [('date_range', '=', rec.date_range.id), ('employee_id', '=', rec.employee_id.id)]) - self
            if record:
                raise ValidationError(
                    f"Duplicate entry found for {record.employee_id.emp_display_name} for year {record.date_range.name}.")
            if len(rec.family_details_ids) == 0:
                data = self.env['health_insurance_configuration'].sudo().search([('code', '=', 'IC')])
                if data.value == 1:
                    raise ValidationError("Please add at least one family member details")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            rec.family_details_ids = False
            family_rec = self.env['kwemp_family_info'].sudo().search(
                [('emp_id', '=', rec.employee_id.id), ('is_insured', '=', True)])  # , ('is_insured `', '=', True)])
            family_list = []
            if family_rec:
                for record in family_rec:
                    family_list.append((0, 0, {
                        'dependant_id': record.name,
                        'date_of_birth': record.date_of_birth,
                        'relationship_id': record.relationship_id.id,

                    }))
                rec.family_details_ids = family_list

    @api.onchange('no_of_installment', 'family_details_ids',"total_insurance_amount", "insurance_amount")
    def get_insurance_emi_details(self):
        self.num_dependant = len(self.family_details_ids)
        if int(self.no_of_installment) and self.family_details_ids or self.insurance_amount:
            # total=sum(self.family_details_ids.mapped('insurance_amount'))
            self.emi_details_ids = [(5,)]
            new_line = self.env['health_insurance_emi']
            for rec, index in enumerate(range(int(self.no_of_installment))):
                if date.today().day <= 25:
                    nextmonth = date.today() + relativedelta.relativedelta(months=index)
                    datetime_object = datetime.strptime(str(nextmonth.month), "%m")
                    full_month_name = datetime_object.strftime("%B")
                    self.emi_details_ids = [(0, 0, {
                                    'year': nextmonth.year,
                                    'month': full_month_name,
                                    'installment': self.total_insurance_amount/int(self.no_of_installment),
                                    'status': 'unpaid',
                                    'emi_date': nextmonth,
                                    'emi_details_id':self.id
                                })]


                else:
                    nextmonth = date.today() + relativedelta.relativedelta(months=index + 1)
                    datetime_object = datetime.strptime(str(nextmonth.month), "%m")
                    full_month_name = datetime_object.strftime("%B")
                    self.emi_details_ids = [(0, 0, {
                                    'year': nextmonth.year,
                                    'month': full_month_name,
                                    'installment': self.total_insurance_amount/int(self.no_of_installment),
                                    'status': 'unpaid',
                                    'emi_date': nextmonth,
                                    'emi_details_id': self.id
                                })]

        else:
            self.emi_details_ids = [(5,)]

    def check_employee_health_insurance(self, user):
        if user.employee_ids:
            if user.employee_ids[0].esi_applicable == True:
                return True
            curr_financial_yr = self._default_financial_yr()
            insurance_rec = self.sudo().search([('employee_id', '=', user.employee_ids[0].id),
                                                ('date_range', '=', curr_financial_yr.id)])
            if insurance_rec:
                return True
        return False


class family_details(models.Model):
    _name = 'family_details'
    _order = 'family_details_id asc,id asc,emp_name asc'
    _description = "Health Insurance Details of Family Members"
    _rec_name = "emp_name"
    # _order = "emp_name asc"

    def hide_fields(self):
        family_lst = []
        for record in self:
            if record.family_details_id.id not in family_lst:
                family_lst.append(record.family_details_id.id)
                record.invisible_boolean = True

    family_details_id = fields.Many2one('health_insurance_dependant', string='Family Details')
    relationship_id = fields.Many2one('kwmaster_relationship_name', string="Relation",
                                      domain="[('is_insure_covered','=',True)]", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')], required=True,
                              string="Gender")
    dependant_id = fields.Char(string='Name', required=True)
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    insurance_amount = fields.Integer(string="Premium", related='relationship_id.insurance_amount')
    emp_location = fields.Many2one('kw_res_branch', related="family_details_id.employee_id.job_branch_id",
                                   string="Location")
    emp_department = fields.Many2one('hr.department', related="family_details_id.employee_id.department_id")
    emp_code = fields.Char(related="family_details_id.employee_id.emp_code")
    emp_name = fields.Many2one('hr.employee', related="family_details_id.employee_id", string="Employee Name")
    year_id = fields.Many2one('account.fiscalyear', related="family_details_id.date_range")
    invisible_boolean = fields.Boolean(compute="hide_fields")

    @api.constrains('relationship_id')
    def validate_relationship_id(self):
        family_details_ids = self.env['family_details'].sudo().search([])
        for rec in self:
            record = family_details_ids.filtered(
                lambda x: x.relationship_id.name == 'Father' and x.family_details_id.id == rec.family_details_id.id)
            if len(record) > 1:
                raise ValidationError(f"Duplicate entry found for {rec.relationship_id.name}")

            mother_rec = family_details_ids.filtered(
                lambda x: x.relationship_id.name == 'Mother' and x.family_details_id.id == rec.family_details_id.id)
            if len(mother_rec) > 1:
                raise ValidationError(f"Duplicate entry found for {rec.relationship_id.name}")

            wife_rec = family_details_ids.filtered(
                lambda x: x.relationship_id.name == 'Wife' and x.family_details_id.id == rec.family_details_id.id)
            if len(wife_rec) > 1:
                raise ValidationError(f"Duplicate entry found for {rec.relationship_id.name}")

            hus_rec = family_details_ids.filtered(
                lambda x: x.relationship_id.name == 'Husband' and x.family_details_id.id == rec.family_details_id.id)
            if len(hus_rec) > 1:
                raise ValidationError(f"Duplicate entry found for {rec.relationship_id.name}")
            # inlaw_mother_rec = family_details_ids.filtered(
            #     lambda x: x.relationship_id.name == 'Mother-in-law' and x.family_details_id.id == rec.family_details_id.id)
            # if mother_rec and inlaw_mother_rec:
            #     raise ValidationError(f"You can't apply insurance for both your mother and your mother-in-law.")
            # inlaw_father_rec = family_details_ids.filtered(
            #     lambda x: x.relationship_id.name == 'Father-in-law' and x.family_details_id.id == rec.family_details_id.id)
            # if record and inlaw_father_rec:
            #     raise ValidationError(f"You can't apply insurance for both your father and your father-in-law.")

class health_insurance_self(models.Model):
    _name = 'health_insurance_self'
    _description = "Health Insurance Details"

    def _default_financial_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal

    year = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                           default=_default_financial_yr, required=True)
    employee_id = fields.Many2one('hr.employee', string="Name", required=True)
    department = fields.Char(related='employee_id.department_id.name', string="Department")
    division = fields.Char(related='employee_id.division.name', string="Division")
    section = fields.Char(related='employee_id.section.name', string="Section")
    practice = fields.Char(related='employee_id.practise.name', string="Practice")
    designation = fields.Char(related='employee_id.job_id.name', string="Designation")
    date_of_birth = fields.Date(string="Date of Birth")
    insurance_amount = fields.Integer(string="Insurance Amount", required=False)
    boolean_readonly = fields.Boolean(string='Printed In Payslip', default=False)
    insurance_amt = fields.Integer(string="Insurance Amount", required=False)

    @api.constrains('employee_id', 'year', 'insurance_amount')
    def validate_employee_id(self):
        for rec in self:
            record = self.env['health_insurance_self'].sudo().search(
                [('year', '=', rec.year.id), ('employee_id', '=', rec.employee_id.id)]) - self
            if record:
                raise ValidationError(
                    f"Duplicate entry found for {record.employee_id.emp_display_name} for {record.year.name}.")
            if rec.insurance_amount <= 0:
                raise ValidationError("Insurance Amount should be greater than 0.")

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 2, 2010, -1)]


class HealthInsuranceEmi(models.Model):
    _name = 'health_insurance_emi'
    _description = 'emi of heath insurance'

    year = fields.Integer(string="Year")
    month = fields.Char(string="Month")
    installment = fields.Float(string="Premium")
    status = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')], string="Status")
    emi_date = fields.Date(string="Emi Date")
    emi_details_id = fields.Many2one('health_insurance_dependant', string='EMI Details')


class GenerateHealthInsurance(models.TransientModel):
    _name = 'payroll_generate_insurance'
    _description = 'Gererate Insurance'

    from_date_range = fields.Many2one('account.fiscalyear', 'From Financial Year', track_visibility='always',required=True)
    to_date_range = fields.Many2one('account.fiscalyear', 'To Financial Year', track_visibility='always',required=True)

    def generate_individual_insurance(self):
        current_id = self.env.context.get('current_id')
        HealthInsuranceDependant = self.env['health_insurance_dependant'].sudo().search([('id', '=', current_id)])
        current_ctc = self.env['hr.employee'].sudo().browse(HealthInsuranceDependant.employee_id.id).current_ctc
        IrConfigParameter = self.env['ir.config_parameter']
        user_name = self.env.user.employee_ids.name
        # Fetching configurations
        below_60 = IrConfigParameter.sudo().get_param('insurance_emi_below_60')
        above_60 = IrConfigParameter.sudo().get_param('insurance_emi_above_60')

        # Fetching records
        check_ins = HealthInsuranceDependant.sudo().search([('employee_id', '=', HealthInsuranceDependant.employee_id.id),('date_range','=',self.to_date_range.id),('state', '!=', 'rejected')])
        if  check_ins:
            raise ValidationError('This Record is already present!')
        else:
        # Processing records
            if HealthInsuranceDependant.employee_id.active:
                no_of_installment = above_60 if current_ctc > 60000 else below_60

                # Create new insurance record
                insurance = self.env['health_insurance_dependant'].sudo().create({
                    'date_range': self.to_date_range.id,
                    'employee_id': HealthInsuranceDependant.employee_id.id,
                    'sum_assured_select': HealthInsuranceDependant.sum_assured_select,
                    'sum_assured': HealthInsuranceDependant.sum_assured,
                    'no_of_installment': no_of_installment,
                    'amount_': HealthInsuranceDependant.amount_,
                    'state': 'draft',
                    'generated_by': user_name,
                    'num_dependant' : len(HealthInsuranceDependant.family_details_ids)
                })

                # Write family details if they exist
                if HealthInsuranceDependant.family_details_ids:
                    family_details_data = [{
                        'family_details_id': insurance.id,
                        'gender': r.gender,
                        'dependant_id': r.dependant_id,
                        'date_of_birth': r.date_of_birth,
                        'relationship_id': r.relationship_id.id
                    } for r in HealthInsuranceDependant.family_details_ids]

                    insurance.write({'family_details_ids': [(0, 0, data) for data in family_details_data]})
    
    def generate_insurance(self):
        if not (self.from_date_range and self.to_date_range):
            return

        HealthInsuranceDependant = self.env['health_insurance_dependant']
        HrEmployee = self.env['hr.employee']
        IrConfigParameter = self.env['ir.config_parameter']
        user_name = self.env.user.employee_ids.name

        # Fetching configurations
        below_60 = IrConfigParameter.sudo().get_param('insurance_emi_below_60')
        above_60 = IrConfigParameter.sudo().get_param('insurance_emi_above_60')

        # Fetching records
        from_fy_records = HealthInsuranceDependant.sudo().search([('date_range', '=', self.from_date_range.id), ('state', '!=', 'rejected')])
        to_fy_employee_ids = HealthInsuranceDependant.sudo().search([('date_range', '=', self.to_date_range.id)]).mapped('employee_id').ids

        # Processing records
        for record in from_fy_records:
            if record.employee_id.id not in to_fy_employee_ids and record.employee_id.active:
                current_ctc = HrEmployee.sudo().browse(record.employee_id.id).current_ctc
                no_of_installment = above_60 if current_ctc > 60000 else below_60

                # Create new insurance record
                insurance = HealthInsuranceDependant.sudo().create({
                    'date_range': self.to_date_range.id,
                    'employee_id': record.employee_id.id,
                    'sum_assured_select': record.sum_assured_select,
                    'sum_assured': record.sum_assured,
                    'no_of_installment': no_of_installment,
                    'amount_': record.amount_,
                    # 'employeer_contribution': record.employeer_contribution,
                    # 'employee_contribution':record.employee_contribution,
                    'state': 'draft',
                    'generated_by': user_name,
                })

                # Write family details if they exist
                if record.family_details_ids:
                    family_details_data = [{
                        'family_details_id': insurance.id,
                        'gender': r.gender,
                        'dependant_id': r.dependant_id,
                        'date_of_birth': r.date_of_birth,
                        'relationship_id': r.relationship_id.id
                    } for r in record.family_details_ids]

                    insurance.write({'family_details_ids': [(0, 0, data) for data in family_details_data]})