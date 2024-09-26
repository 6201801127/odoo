import re
import os, base64
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID
from odoo import models, fields, api,_ , tools
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

class HRApplicant(models.Model):
    _inherit='hr.applicant'
    _description ='Applicant'

    def default_country(self):
        return self.env['res.country'].search([('name', '=', 'India')], limit=1)
    
    @api.model
    def get_resigned_employees(self):
        query = "select employee_id from exit_transfer_management where exit_type = 'technical resignation' and reg_type = 'internal' and state = 'complete'"
        self._cr.execute(query)
        emp_records = self._cr.dictfetchall()
        datas = [record['employee_id'] for record in emp_records]
        # resigned_ids = self.env['exit.transfer.management'].search([('exit_type','=','technical resignation'),('reg_type','=','internal'),('state','=','complete')])
        return [('id','in',datas),('roster_line_item','=',False)]

    image = fields.Binary("Photo")
    category_id = fields.Many2one('employee.category', string='Category')
    religion_id = fields.Many2one('employee.religion', string='Religion')
    ex_serviceman = fields.Selection([('no', 'No'),
                                      ('yes', 'Yes')], string='Whether Ex Service Man', track_visibility='always')

    minority = fields.Boolean(string="Minority",track_visibility='always')
    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',
                                     )
    branch_id = fields.Many2one('res.branch', string='Directorate', store=True, domain="['|',('parent_branch_id.code','=','HQ'),('code','=','HQ')]")
    center_id = fields.Many2one('res.branch',string="Center")
    recruitment_type = fields.Selection([
        ('d_recruitment', 'Direct Recruitment(DR)'),
        ('transfer', 'Transfer(Absorption)'),
        ('i_absorption', 'Immediate Absorption'),
        ('deputation', 'Deputation'),
        ('c_appointment', 'Compassionate Appointment'),
        ('promotion', 'Promotion'),
    ], 'Recruitment Type', track_visibility='always')

    dob = fields.Date(string='Date of Birth')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        )
    gende = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('transgender', 'Transgender')
    ], track_visibility='always')
    # nationality = fields.Many2one('res.country', string='Nationality')
    title = fields.Many2one('res.partner.title', string='Salutation')
    get_total_match_religion = fields.Integer(string="Get Total Match Religion",compute="get_total_match_religion_data")
    santioned_position = fields.Float(string="Sanctioned Position",compute="get_santioned_position_emp")
    cur_no_of_emp = fields.Float('current no of employee',compute="get_santioned_position_emp")
    get_total_match_category = fields.Integer('Get Total Match Category',compute="get_total_match_category_data")

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell')

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Type')

    country_id = fields.Many2one(
        'res.country', 'Country', default=default_country)
    citizen_number = fields.Char('Citizen Number',track_visibility='always')
    citizen_eligibility_date =fields.Date(string='Date of Eligibility',track_visibility='always')
    citizen_file_data = fields.Binary('Upload',track_visibility='always',attachment=True)
    date_of_eligibility = fields.Date(track_visibility='always')
    citizen_file_name = fields.Char('File Name',track_visibility='always')
    show_citizen_field = fields.Boolean('Show Field',default=False,copy=False,track_visibility='always')
    height = fields.Float('Height (in CMs)', track_visibility='always')
    weight = fields.Float('Weight (in KGs)', track_visibility='always')
    blood_group = fields.Selection([('a+', 'A+'),
                                    ('a-', 'A-'),
                                    ('b+', 'B+'),
                                    ('b-', 'B-'),
                                    ('o+', 'O+'),
                                    ('o-', 'O-'),
                                    ('ab+', 'AB+'),
                                    ('ab-', 'AB-')], string='Blood Group', track_visibility='always')
    differently_abled = fields.Selection([('no', 'No'),
                                          ('yes', 'Yes')], default='no', string='Differently Abled?',
                                         track_visibility='always')
    kind_of_disability = fields.Selection([('vh', 'Visually Handicapped'),
                                          ('hh', 'Hearing Handicapped'),
                                           ('ph', 'Physically Handicapped')],
                                          string='Kind of Disability',
                                         track_visibility='always')
    perc_disability = fields.Char('% of Disability', track_visibility='always')
    certificate_upload = fields.Binary('Upload certificate', track_visibility='always',attachment=True)
    certificate_upload_filename = fields.Char('Upload certificate Filename')
    certificate_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_certificate_upload_attachment_id', string="Upload certificate Attachment")

    personal_remark = fields.Char('Personal mark of Identification', track_visibility='always')

    pan_no = fields.Char('PAN Card No.', track_visibility='always')
    pan_upload = fields.Binary('Upload(PAN)', track_visibility='always',attachment=True)
    pan_upload_filename = fields.Char('Upload(PAN) Filename')
    pan_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_pan_upload_attachment_id', string="PAN Document Attachment")

    aadhar_no = fields.Char('Aadhar Card No.', track_visibility='always')
    aadhar_upload = fields.Binary('Upload(Aadhar)', track_visibility='always',attachment=True)
    aadhar_upload_filename = fields.Char('Upload(Aadhar) Filename')
    aadhar_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_aadhar_upload_attachment_id', string="Aadhar Document Attachment")

    passport_upload = fields.Binary('Upload(Passport)', track_visibility='always',attachment=True)
    passport_upload_filename = fields.Char('Upload(Passport) Filename')

    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account number')
    ifsc_code = fields.Char(string='IFSC Code')
    penalty_awarded = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Any Penalty awarded during the last 10 years')
    # penalty_awarded = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')],
    #     string='Any Penalty awarded during the last 10 years')
    action_can_know = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Any action or inquiry is going on as far as candidate knowledge')
    criminal_pending = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Any criminal/ vigilance case is pending or contemplated')
    relative_terms_css = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Any relative defined in terms of CCS')
    relative_terms_css_name = fields.Char(string='Relative Name')
    achievements_app = fields.Text('Achievements')
    # achievements_app = fields.Text('Additional Information')

    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        help='Employee bank salary account')

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single')
    spouse_complete_name = fields.Char(string="Spouse Complete Name", groups="hr.group_hr_user")
    spouse_birthdate = fields.Date(string="Spouse Birthdate", groups="hr.group_hr_user")
    children = fields.Integer(string='Number of Children', groups="hr.group_hr_user")

    address_home_id = fields.Many2one(
        'res.partner', 'Private Address',
        help='Enter here the private address of the employee, not the one linked to your company.',
        )
    is_address_home_a_company = fields.Boolean(
        'The employee adress has a company linked',
        compute='_compute_is_address_home_a_company',
    )
    emergency_contact = fields.Char("Emergency Contact", groups="hr.group_hr_user")
    emergency_phone = fields.Char("Emergency Phone", groups="hr.group_hr_user")
    km_home_work = fields.Integer(string="Km home-work", groups="hr.group_hr_user")
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user")
    place_of_birth = fields.Char('Place of Birth', groups="hr.group_hr_user")
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user")
    fax_number = fields.Char('FAX number', track_visibility='always')

    # work
    job_title = fields.Many2one('stpi.job.post','Functional Designation',old_name="Post")
    address_id = fields.Many2one(
        'res.partner', 'Work Address')
    work_phone = fields.Char('Work Phone')
    mobile_phone = fields.Char('Work Mobile')
    work_email = fields.Char('Work Email')
    work_location = fields.Char('Work Location')
    # office work
    recruitment_file_no = fields.Char('Recruitment File No.', track_visibility='always')
    office_file_no = fields.Char('Office Order No.', track_visibility='always')
    mode_of_recruitment = fields.Char('Mode Of Recruitment', track_visibility='always')
    post = fields.Char('Post', track_visibility='always')
    date_of_join = fields.Date('Date of Join', track_visibility='always')
    office_order_date = fields.Date('Office Order Date', track_visibility='always')

    # employee in company
    job_id = fields.Many2one('hr.job', 'Post',track_visibility='always')
    department_id = fields.Many2one('hr.department', 'Department')
    parent_id = fields.Many2one('hr.employee', 'Manager')
    child_ids = fields.One2many('hr.employee', 'parent_id', string='Subordinates')
    coach_id = fields.Many2one('hr.employee', 'Coach')
    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id',
        string='Tags')

    personal_email = fields.Char('Personal Email', track_visibility='always')
    phone = fields.Char('Phone (Home)', track_visibility='always')
    refuse_reason = fields.Text("Refuse Reason")

    address_ids = fields.One2many('applicant.address', 'applicant_id', string='Address', track_visibility='always')

    state = fields.Selection(selection=[('test_period', 'Probation'),('contract', 'Contract'),('deputation', 'Deputation'),('employment', 'Regular')], string='Stage', track_visibility='always', copy=False)
    is_final_statge = fields.Boolean("Final Stage ?",compute="_compute_final_stage")
    is_second_last_stage = fields.Boolean("Is Cecond Last Stage?",compute="_compute_final_stage")
    stage_change_reason = fields.Char(string='Stage Change Reason', track_visibility='onchange')
    technical_resignation = fields.Boolean(string="Technical Resignation")
    employee = fields.Many2one('hr.employee',string="Employee",domain=lambda self: self.get_resigned_employees())

    related_stage_id = fields.Char(related='stage_id.name')  
    

    @api.onchange('employee')
    def onchange_employee(self):
            self.job_title = self.employee.job_title
            self.parent_id = self.employee.parent_id
            self.center_id = self.employee.branch_id
            self.fax_number = self.employee.fax_number
            self.ex_serviceman = self.employee.ex_serviceman

            self.office_file_no = self.employee.office_file_no
            self.office_order_date = self.employee.office_order_date
            self.recruitment_file_no = self.employee.recruitment_file_no
            self.date_of_join = self.employee.date_of_join

            self.country_id = self.employee.country_id
            # self.bank_account_number = self.employee.bank_account_id
            self.gende = self.employee.gende

            self.emergency_contact = self.employee.emergency_contact
            self.emergency_phone = self.employee.emergency_phone
            self.personal_email = self.employee.personal_email
            self.phone = self.employee.phone

            self.pan_no = self.employee.pan_no
            self.pan_upload = self.employee.pan_upload
            self.aadhar_no = self.employee.aadhar_no
            self.aadhar_upload = self.employee.aadhar_upload
            self.passport_id = self.employee.passport_id
            self.passport_upload = self.employee.passport_upload

            self.dob = self.employee.birthday
            self.dob_doc = self.employee.place_of_birth
            self.country_of_birth = self.employee.country_of_birth

            self.religion_id = self.employee.religion
            self.category_id = self.employee.category
            self.minority = self.employee.minority

            self.height = self.employee.height
            self.weight = self.employee.weight
            self.blood_group = self.employee.blood_group
            self.differently_abled = self.employee.differently_abled
            self.personal_remark = self.employee.personal_remark

            self.resume_line_applicant_ids = False
            self.applicant_skill_ids = False
            self.address_ids = False
         
            self.resume_line_applicant_ids = [[0, 0, {'line_type_id':p.line_type_id.id, 
            'name' : p.name,
            'upload_qualification_proof' : p.upload_qualification_proof,
            'date_start' : p.date_start,
            'date_end' : p.date_end,
            'description':p.description}]for p in self.employee.resume_line_ids]

            self.applicant_skill_ids = [[0, 0, {'skill_type_id':q.skill_type_id.id,
            'skill_id' : q.skill_id.id,
            'skill_level_id' : q.skill_level_id.id,
            'level_progress' : q.level_progress}]for q in self.employee.employee_skill_ids]

            self.address_ids = [[0, 0, {'address_type':r.address_type, 
            'street':r.street, 
            'street2':r.street2, 
            'country_id':r.country_id.id, 
            'state_id':r.state_id.id, 
            'city_id':r.city_id.id, 
            'zip':r.zip}] for r in self.employee.address_ids]
           
    def _compute_pan_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'pan_upload')])
            applicant.pan_upload_attachment_id = attachment_id

    def _compute_aadhar_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'aadhar_upload')])
            applicant.aadhar_upload_attachment_id = attachment_id

    def _compute_certificate_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'certificate_upload')])
            applicant.certificate_upload_attachment_id = attachment_id
    
    @api.depends('stage_id')
    @api.multi
    def _compute_final_stage(self):
        hr_recruitment_stage = self.env['hr.recruitment.stage']
        last_stage = hr_recruitment_stage.search([], limit=1, order="sequence desc")
        second_last_stage = hr_recruitment_stage.search([], offset=1, limit=1, order="sequence desc")
        last_sequence = last_stage and last_stage.sequence or 0
        second_last_sequence = second_last_stage and second_last_stage.sequence or 0
        for applicant in self:
            if applicant.stage_id and applicant.stage_id.sequence == second_last_sequence:
                applicant.is_second_last_stage = True
            if applicant.stage_id and applicant.stage_id.sequence == last_sequence:
                applicant.is_final_statge = True

    @api.multi
    def write(self,vals):
        if vals.get('stage_id') and self.env.user.id != SUPERUSER_ID:
            stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            for applicant in self:
                if applicant.stage_id.sequence > stage.sequence:
                    raise ValidationError("Backward stage is not possible.")
        result = super(HRApplicant, self).write(vals)
        return result

    @api.multi
    def action_send_offer_letter(self):
        self.ensure_one()
        template_id = self.env.ref('hr_applicant.email_template_offer_letter').id
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.constrains('parent_id')
    def _check_parent_id(self):
        for employee in self:
            if not employee._check_recursion():
                raise ValidationError(_('You cannot create a recursive hierarchy.'))

    @api.constrains('personal_email')
    def _check_personal_mail_val(self):
        for employee in self:
            regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            if not (re.search(regex, employee.personal_email)):
                raise ValidationError(_('Please enter correct Personal Mail Address.'))

    @api.constrains('dob')
    def _check_dob_app(self):
        for employee in self:
            today = datetime.now().date()
            if employee.dob and employee.dob > today:
                raise ValidationError(_('Please enter correct date of birth'))

    @api.onchange('branch_id')
    @api.constrains('branch_id')
    def get_partner_from_branch(self):
        for rec in self:
            rec.partner_id = rec.branch_id.partner_id.id

    @api.constrains('office_order_date')
    def _check_office_order_date_app(self):
        for employee in self:
            today = datetime.now().date()
            if employee.office_order_date and employee.office_order_date > today:
                raise ValidationError(_('Please enter correct office order date'))

    @api.constrains('height')
    def _check_height(self):
        for rec in self:
            if rec.employee_type == 'regular' and rec.height <= 0.00:
                raise ValidationError(_("Height (in CMs) must be greater than 0."))
        return True

    @api.constrains('weight')
    def _check_weight(self):
        for rec in self:
            if rec.employee_type == 'regular' and rec.weight <= 0.00:
                raise ValidationError(_("Weight (in KGs) must be greater than 0."))
        return True

    @api.constrains('emergency_phone','phone')
    @api.onchange('emergency_phone','phone')
    def _check_mobile_phone(self):
        for rec in self:
            if rec.emergency_phone and not rec.emergency_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number"))
            if rec.emergency_phone and len(rec.emergency_phone) != 10:
                raise ValidationError(_("Please enter correct Mobile number."
                                        "It must be of 10 digits"))
            if rec.phone and not rec.phone.isnumeric():
                raise ValidationError(_("Phone number must be a number"))
            if rec.phone and len(rec.phone) != 10:
                raise ValidationError(_("Please enter correct phone number."
                                        "It must be of 10 digits"))

    @api.onchange('name')
    @api.constrains('name')
    def onchange_name_get_pname(self):
        for rec in self:
            if rec.name:
                rec.partner_name = rec.name

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            # self.job_title = self.job_id.name
            self.pay_level_id = self.job_id.pay_level_id.id
            # if self.job_id.employee_type:
            #     emp_type = self.job_id.employee_type[0]
            #     if emp_type.code =='regular':
            #         self.employee_type = 'regular'

            #     elif emp_type.code =='contract_agency':
            #         self.employee_type = 'contractual_with_agency'

            #     elif emp_type.code =='contract_stpi':
            #         self.employee_type = 'contractual_with_stpi'

    @api.onchange('pay_level')
    def _onchange_pay_level(self):
        if self.pay_level:
            self.salary_expected = self.pay_level.entry_pay
            self.salary_proposed = self.pay_level.entry_pay

    @api.onchange('address_id')
    def _onchange_address(self):
        self.work_phone = self.address_id.phone
        self.mobile_phone = self.address_id.mobile

    @api.onchange('company_id')
    def _onchange_company(self):
        address = self.company_id.partner_id.address_get(['default'])
        self.address_id = address['default'] if address else False

    @api.onchange('department_id')
    def _onchange_department(self):
        self.parent_id = self.department_id.manager_id

    @api.constrains('name')
    @api.onchange('name')
    def _check_name_validation(self):
        for rec in self:
            if rec.name:
                for e in rec.name:
                    if not(e.isalpha() or e == ' '):
                        raise ValidationError(_("Please enter correct Name."))

    @api.constrains('bank_account_number')
    def _check_bank_acc_number(self):
        for rec in self:
            if rec.bank_account_number:
                for e in rec.bank_account_number:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter correct Account number, it must be numeric..."))

    @api.constrains('aadhar_no')
    @api.onchange('aadhar_no')
    def _check_aadhar_number(self):
        for rec in self:
            if rec.aadhar_no:
                for e in rec.aadhar_no:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter correct Aadhar number, it must be numeric."))
                if len(rec.aadhar_no) != 12:
                    raise ValidationError(_("Please enter correct Aadhar number, it must be of 12 digits."))

    @api.constrains('date_of_join', 'office_order_date')
    @api.onchange('date_of_join','office_order_date')
    def _check_office_order_date(self):
        for record in self:
            if record.office_order_date and record.date_of_join and (record.office_order_date > record.date_of_join):
                raise ValidationError("Date of Joining should always be greater then equals to Office Order Date")

    # @api.constrains('pan_no')
    # @api.onchange('pan_no')
    # def _check_pan_number(self):
    #     for rec in self:
    #         if rec.pan_no and not re.match(r'^[A-Za-z]{5}[0-9]{4}[A-Za-z]$', str(rec.pan_no)):
    #             raise ValidationError(_("Please enter correct PAN number."))

    @api.constrains('image','pan_upload','aadhar_upload','passport_upload','dob_doc','nationality_upload','payment_document','signature','other_doc')
    def _check_size(self):
        for record in self:
            
            if record.image:
                img_size = (len(record.image)*3/4)
                if img_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Image is 1 MB."))

            elif record.pan_upload:
                pan_upload_size = (len(record.pan_upload)*3/4)
                if pan_upload_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of PAN is 1 MB."))
            elif record.aadhar_upload:
                aadhar_upload_size = (len(record.aadhar_upload)*3/4)
                if aadhar_upload_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Aadhar is 1 MB."))
            elif record.passport_upload:
                passport_upload_size = (len(record.passport_upload)*3/4)
                if passport_upload_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Passport is 1 MB."))
            elif record.dob_doc:
                dob_doc_size = (len(record.dob_doc)*3/4)
                if dob_doc_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Date Of Birth is 1 MB."))
            elif record.nationality_upload:
                nationality_upload_size = (len(record.nationality_upload)*3/4)
                if nationality_upload_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Nationality is 1 MB."))
            elif record.payment_document:
                payment_document_size = (len(record.payment_document)*3/4)
                if payment_document_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Payment Document is 1 MB."))
            elif record.signature:
                signature_size = (len(record.signature)*3/4)
                if signature_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Signature is 1 MB."))
            elif record.other_doc:
                other_doc_size = (len(record.other_doc)*3/4)
                if other_doc_size > 1 * 1024 * 1024:
                    raise ValidationError(_("The maximum upload size of Other Document is 1 MB."))

    @api.onchange('pan_no')
    def set_upper(self):
        if self.pan_no:
            self.pan_no = str(self.pan_no).upper()

    @api.depends('address_home_id.parent_id')
    def _compute_is_address_home_a_company(self):
        """Checks that choosen address (res.partner) is not linked to a company.
        """
        for employee in self:
            try:
                employee.is_address_home_a_company = employee.address_home_id.parent_id.id is not False
            except AccessError:
                employee.is_address_home_a_company = False

    @api.onchange('country_id')
    def ckech_nationality(self):
        if self.country_id:
            if self.country_id.name != 'India':
                self.show_citizen_field =True
            else:
                self.show_citizen_field =False

    @api.multi
    def create_employee_from_applicant(self):
        if not self.branch_id:
            raise UserError(_("Please define 'Branch' in Work Information tab."))
        res = super(HRApplicant, self).create_employee_from_applicant()
        if res.get('res_id', False):
            emp_id = self.env['hr.employee'].search([('id','=',res.get('res_id'))])
            resume_line_ids = []
            employee_skill_ids = []
            address_ids = []
            shift_id = False
            if emp_id:
                for emp in self.resume_line_applicant_ids:
                    resume_line_ids.append((0, 0, {
                    'resume_employee_id': emp_id.id,
                    'name': emp.name,
                    'date_start': emp.date_start,
                    'date_end': emp.date_end,
                    'description': emp.description,
                    'upload_qualification_proof': emp.upload_qualification_proof,
                    'line_type_id': emp.line_type_id.id,
                    'type_name': emp.type_name,
                    'title': emp.title.id,
                    'specialization': emp.specialization,
                    'sequence': emp.sequence,
                    'acquired': emp.acquired
                }))
                for emp in self.applicant_skill_ids:
                    employee_skill_ids.append((0, 0, {
                        'employee_id': emp_id.id,
                        'skill_id': emp.skill_id,
                        'skill_level_id': emp.skill_level_id.id,
                        'skill_type_id': emp.skill_type_id.id,
                        'level_progress': emp.level_progress
                    }))
                for emp in self.address_ids:
                    address_ids.append((0, 0, {
                        'employee_id': emp_id.id,
                        'address_type': emp.address_type,
                        'state_id': emp.state_id.id,
                        'country_id': emp.country_id.id,
                        'street': emp.street,
                        'street2': emp.street2,
                        'zip': emp.zip,
                        'is_correspondence_address': emp.is_correspondence_address,
                        'city': emp.city,
                        'count': emp.count,
                    }))

                stage_config = self.env['employee.stage.configuration'].sudo()
                stage_record = []
                stage_history_ids = []

                if self.employee_type:
                    if self.employee_type == 'regular' and self.recruitment_type and self.state:
                        stage_record = stage_config.search([('employee_type','=',self.employee_type),('recruitment_type','=',self.recruitment_type),('existing_state','=',self.state)])
                    elif self.employee_type == 'contractual_with_agency':
                        stage_record = stage_config.search([('employee_type','=','contractual_with_3rd_party'),('existing_state','=','contract')])
                    elif self.employee_type == 'contractual_with_stpi':
                        stage_record = stage_config.search([('employee_type','=','contractual'),('existing_state','=','contract')])
                    if stage_record:
                        for stages in stage_record:
                            add_stages = {}
                            add_stages.update({
                                'designation_id':emp_id.job_id.id if emp_id.job_id else False,
                                'file_no':self.recruitment_file_no if self.recruitment_file_no else False,
                                'order_no':self.office_file_no if self.office_file_no else False,
                                'state':stages.existing_state,
                                'order_date':self.date_of_join,
                                'start_date':self.date_of_join,
                                'end_date':self.date_of_join + relativedelta(months=stages.days) if stages.days > 0 else False,
                                }) 
                            stage_history_ids.append((0, 0, add_stages))

                file_name = ''
                image = False

                if self.image:
                    image = self.image
                    
                elif self.gende:
                    if self.gende == 'male':
                        file_name = 'male.jpeg'
                    else:
                        file_name = 'female.jpeg'

                    image_path = get_module_resource('groups_inherit', 'static/image', file_name)
                    image = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

                if self.employee_type == 'regular':
                    seq = self.env['ir.sequence'].next_by_code('hr.employee')
                    identify_id = '' + str(seq)
                else:
                    seq = self.env['ir.sequence'].next_by_code('identify.seqid')
                    identify_id = '' + str(seq)
                
                print("shift", self.center_id.id)
                if self.center_id:
                    shift_id = self.env['resource.calendar'].search([('branch_id','=',self.center_id.id),('is_default_shift','=',True)],limit=1)
                print(shift_id)
                emp_id.update({
                        'image':image if image else False,
                        'employee_type': self.employee_type,
                        'identify_id': identify_id,
                        'recruitment_type': self.recruitment_type,
                        'state':self.state if self.state else False,
                        'stages_history':stage_history_ids if stage_history_ids else False,
                        'salutation': self.title,
                        'country_id': self.country_id,
                        'gender': self.gender,
                        'gende': self.gende,
                        'birthday': self.dob,
                        'differently_abled': self.differently_abled,
                        'category': self.category_id,
                        'resume_line_ids': resume_line_ids,
                        'employee_skill_ids': employee_skill_ids,
                        'address_ids': address_ids,
                        'religion': self.religion_id,
                        'post': self.post,
                        'date_of_join': datetime.now().date(),
                        'office_order_date': self.office_order_date,
                        'job_id': self.job_id,
                        'branch_id': self.center_id,
                        'department_id': self.department_id,
                        'parent_id': self.parent_id,
                        'personal_email': self.personal_email,
                        'phone': self.phone,
                        'blood_group': self.blood_group,
                        'weight': self.weight,
                        'citizen_number': self.citizen_number,
                        'citizen_eligibility_date': self.citizen_eligibility_date,
                        'citizen_file_data': self.citizen_file_data,
                        'date_of_eligibility': self.date_of_eligibility,
                        'citizen_file_name': self.citizen_file_name,
                        'kind_of_disability': self.kind_of_disability,
                        'perc_disability': self.perc_disability,
                        'certificate_upload': self.certificate_upload,
                        'personal_remark': self.personal_remark,
                        'ex_serviceman': self.ex_serviceman,
                        'pan_no': self.pan_no,
                        'pan_upload': self.pan_upload,
                        'aadhar_no': self.aadhar_no,
                        'aadhar_upload': self.aadhar_upload,
                        'passport_upload': self.passport_upload,
                        'bank_account_id': self.bank_account_id,
                        'bank_account_number': self.bank_account_number,
                        'ifsc_code': self.ifsc_code,
                        'emergency_contact': self.emergency_contact,
                        'emergency_phone': self.emergency_phone,
                        'km_home_work': self.km_home_work,
                        'place_of_birth': self.place_of_birth,
                        'country_of_birth': self.country_of_birth,
                        'children': self.children,
                        'minority': self.minority,
                        'recruitment_file_no': self.recruitment_file_no,
                        'office_file_no': self.office_file_no,
                        'address_id': self.partner_id,
                        # 'work_email': self.email_from,
                        # 'work_phone': self.partner_phone,
                        # 'mobile_phone': self.partner_mobile,
                        'fax_number': self.fax_number,
                })
                if shift_id:
                    emp_id.update({
                        'resource_calendar_id': shift_id
                    })
                if self.employee_type == 'regular' and self.advertisement_line_id:
                    job_opening_line = self.advertisement_line_id.job_opening_line_id
                    roster = job_opening_line and job_opening_line.roster_line_id
                    if roster:
                        existing_employee_roster = self.env['hr.employee'].search([('roster_line_item','=',roster.id)])
                        if existing_employee_roster:
                            raise ValidationError(f"This roster is already linked with employee {existing_employee_roster[0].name}")
                        emp_id.update({
                            'roster_line_item':roster.id
                        })

                trial_date_end = False
                if self.state == 'test_period' and self.employee_type == 'regular':
                    stage_filtered = stage_config.search([('employee_type','=',self.employee_type),('recruitment_type','=',self.recruitment_type),('existing_state','=',self.state)],limit=1)

                    trial_date_end = self.date_of_join + relativedelta(months=stage_filtered.days) if stage_filtered.days > 0 else False

                if self.employee_type == 'regular' and self.recruitment_type == 'd_recruitment':
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )
                elif self.employee_type == 'regular' and self.recruitment_type == 'transfer':
                    
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )
                elif self.employee_type == 'regular' and self.recruitment_type == 'i_absorption':
                    
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )
                elif self.employee_type == 'regular' and self.recruitment_type == 'deputation':
                    emp_id.sudo().set_as_employee()
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )
                elif self.employee_type == 'regular' and self.recruitment_type == 'c_appointment':
                    
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )
                elif self.employee_type == 'regular' and self.recruitment_type == 'promotion':
                    
                    create_contract = self.env['hr.contract'].create(
                        {
                            'state': 'open',
                            'name': emp_id.name,
                            'employee_id': emp_id.id,
                            'department_id': emp_id.department_id.id,
                            'job_id': emp_id.job_id.id,
                            'pay_level_id': self.pay_level_id.id,
                            'pay_level': self.pay_level.id,
                            'struct_id': self.struct_id.id,
                            'date_start': datetime.now().date(),
                            'employee_type': self.employee_type,
                            'wage': self.salary_proposed,
                            
                        }
                    )

        return res

    def update_employee_from_applicant(self):
        print("update_employee_from_applicant123====")
        if not self.address_ids:
            raise ValidationError(_('Please check the address'))
        emp_id = self.env['hr.employee'].search([('id','=',self.employee.id)])
        print(emp_id)
        stage_config = self.env['employee.stage.configuration'].sudo()
        stage_record = []
        stage_history_ids = []
        contract_id = self.env['hr.contract'].search([('employee_id','=',self.employee.id),('state','=','open')],limit=1)
        if contract_id:
            contract_id.update({'state':'close','date_end': self.date_of_join - relativedelta(days=1)})
        if self.employee_type:
            if self.employee_type == 'regular' and self.recruitment_type == 'd_recruitment':
                stage_record = stage_config.search([('employee_type','=',self.employee_type),('recruitment_type','=',self.recruitment_type),('existing_state','=',self.state)])
                print(stage_record)
            if stage_record:
                for stages in stage_record:
                    add_stages = {}
                    add_stages.update({
                        'designation_id':emp_id.job_id.id if emp_id.job_id else False,
                        'file_no':self.recruitment_file_no if self.recruitment_file_no else False,
                        'order_no':self.office_file_no if self.office_file_no else False,
                        'state':self.state,
                        'order_date':self.office_order_date,
                        'start_date':self.date_of_join,
                        'end_date':self.date_of_join + relativedelta(months=stages.days) if stages.days > 0 else False,
                        }) 
                    stage_history_ids.append((0, 0, add_stages))
        print(stage_history_ids)
        emp_id.write({
            'job_id': self.job_id.id,
            'roster_line_item': self.advertisement_line_id.job_opening_line_id and self.advertisement_line_id.job_opening_line_id.roster_line_id.id,
            'recruitment_type': self.recruitment_type,
            'state': self.state,
            'branch_id': self.center_id.id,
            'department_id': self.department_id and self.department_id.id,
            'stages_history':stage_history_ids if stage_history_ids else False,
        })
        if self.employee_type == 'regular' and self.recruitment_type == 'd_recruitment' and self.technical_resignation == True:
            create_contract = self.env['hr.contract'].create(
                {
                    'state': 'open',
                    'name': emp_id.name,
                    'employee_id': emp_id.id,
                    'department_id': emp_id.department_id.id,
                    'job_id': emp_id.job_id.id,
                    'pay_level_id': self.pay_level_id.id,
                    'pay_level': self.pay_level.id,
                    'struct_id': self.struct_id.id,
                    'date_start': self.date_of_join,
                    'employee_type': self.employee_type,
                    'wage': self.salary_proposed,
                    'supplementary_allowance': contract_id.supplementary_allowance,
                    'voluntary_provident_fund': contract_id.voluntary_provident_fund,
                    'xnohra': contract_id.xnohra,
                    'misc_deduction': contract_id.misc_deduction,
                    'license_dee': contract_id.license_dee,
                    'arrear_amount': contract_id.arrear_amount
                }
            )
            print(create_contract)

    @api.multi
    def archive_applicant(self):
        print("method called")
        # form_view_id = self.env.ref('hr_applicant.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refuse Reason',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'applicant.refuse.reason',
            # 'views': [(form_view_id, 'form')],
            'target': 'new',
            'context':{'default_applicant_id':self.id}
        }

    def get_total_match_religion_data(self):
        pass
        #
        # if self.religion_id:
        #     emp_ids = self.env['hr.employee'].search([('religion','=',self.religion_id.id),('job_id','=',self.job_id.id)])
        #     employee_ids = self.env['hr.employee'].search([])
        #     for s in self:
        #         religion = len(emp_ids)
        #         emp = len(employee_ids)
        #         s.get_total_match_religion = round(religion/emp*100)

    def get_total_match_category_data(self):
        pass
        #
        # if self.category_id:
        #     emp_ids = self.env['hr.employee'].search([('category','=',self.category_id.id),('job_id','=',self.job_id.id)])
        #     employee_ids = self.env['hr.employee'].search([])
        #     for s in self:
        #         category = len(emp_ids)
        #         emp = len(employee_ids)
        #         s.get_total_match_category = round(category/emp*100)

    def get_santioned_position_emp(self):
        pass
#         emp_count_san = 0.0
#         for s in self:
#             for line in s.job_id.budget_id:
# #                 print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
#                 s.santioned_position = line.employee_count
# #                 print("???????????????????????????????",s.santioned_position)
#             s.cur_no_of_emp = s.job_id.no_of_employee
# #             print("==============================",s.cur_no_of_emp)

    @api.multi
    def get_religion_from_job_position(self):

        return{
            'name': _('Religion'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'src_model' : 'hr.applicant',
            'type': 'ir.actions.act_window',
            'context': {
                        'search_default_job_id': self.job_id.id,
                        'group_by':'religion'},
            'search_view_id' : self.env.ref('hr.view_employee_tree').id
            }

    @api.multi
    def get_category_from_job_position(self):

        return{
            'name': _('Category'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'src_model' : 'hr.applicant',
            'type': 'ir.actions.act_window',
            'context': {
                        'search_default_job_id': self.job_id.id,
                        'group_by':'category'},
            'search_view_id' : self.env.ref('hr.view_employee_tree').id
            }

class InheritRelative(models.Model):
    _inherit = 'applicant.relative'
    _description = "Applicant Relatives"

    relate_type = fields.Many2one('relative.type', string = "Relative Type")

class ApplicantTraining(models.Model):
    _name='applicant.training'
    _description ='Applicant Training'

    employee_id = fields.Many2one('hr.employee', string='employee')
    course = fields.Char('Course Title')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    location = fields.Text('Location')
    trainer_name = fields.Char('Trainer Name')
    training_type = fields.Selection([('internal','Internal'),
                                      ('external','External'),
                                      ('professional','Professional'),
                                      ('functional','Functional'),
                                      ('technical','Technical'),
                                      ('certification', 'Certification'),
                                      ],string='Training Type')
    organization_name = fields.Text('Organization Name')
    cert_file_data = fields.Binary('Certificate upload',attachment=True)
    cert_file_name = fields.Char('Certificate Name')
    skills = fields.Many2one('hr.skill', string = 'Skills')

class ApplicantAddress(models.Model):
    _name = 'applicant.address'
    _description = 'Applicant Address'

    def default_country(self):
        return self.env['res.country'].search([('name', '=', 'India')], limit=1)

    address_type = fields.Selection([('permanent_add', 'Permanent Add'),
                                     ('present_add', 'Present Add'),
                                     ('office_add', 'Office Add'),
                                     ('hometown_add', 'HomeTown Add'),
                                     ('communication_add','Communication Add')
                                     ], string='Address Type', required=True)
    applicant_id = fields.Many2one('hr.applicant', 'employee Id')
    street = fields.Char('Address Line 1')
    street2 = fields.Char('Address Line 2')
    zip = fields.Char('Pin', change_default=True)
    is_correspondence_address = fields.Boolean('Is Correspondence Address')
    city = fields.Char('City')
    city_id = fields.Many2one('res.city','City/District')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country', default=default_country)
    count = fields.Integer('Count')

    @api.onchange('street', 'street2', 'zip', 'country_id', 'is_correspondence_address', 'city', 'state_id')
    def _onchange_hometown_address(self):
        for rec in self:
            rec.count = 0
            if rec.address_type == 'hometown_add':
                rec.count += 1
            if rec.count > 2:
                raise ValidationError("You cannot change Homettown address more than 2 times")

    @api.constrains('address_type','employee_id')
    def check_unique_add(self):
        for rec in self:
            count = 0
            emp_id = self.env['applicant.address'].search([('address_type', '=', rec.address_type),('applicant_id', '=', rec.applicant_id.id)])
            for e in emp_id:
                count+=1
            if count >1:
                raise ValidationError("The Address Type must be unique")


class InheritMailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def action_send_mail(self):
        print(self._context)
        if self._context.get('active_model') == 'hr.applicant':
            contract_attachment_ids = []
            print(self.attachment_ids)
            for attachment in self.attachment_ids:
                    contract_attachment_ids.append((0, 0, {
                        'document': attachment.datas,
                        'document_filename': attachment.name,
                        'name': attachment.name
                    }))
            self.env['hr.applicant'].browse(self._context.get('active_id')).write({'contract_document_ids': contract_attachment_ids})
        self.send_mail()
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}