from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re

class EmployeeProfile(models.Model):
    _name = "employee.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Profile"


    employee_id = fields.Many2one('hr.employee', string="Employee", store = True, track_visibility='onchange')
    requested_by = fields.Char(string='Requested By', invisible=1)
    date = fields.Date(string='Requested Date', default=fields.Date.today())
    designation = fields.Many2one('hr.job', string="Functional Designation")
    branch_id= fields.Many2one('res.branch', string="Center")
    department = fields.Many2one('hr.department', string="Department")

    prev_occu_ids = fields.One2many('employee.previous.occupation.update', 'employee_update_profile', 'Prev. Occupation Ref.')
    prev_occu_current_ids = fields.One2many('employee.previous.occupation.current', 'employee_current_profile', 'Prev. Occupation Current Ref.')

    address_ids = fields.One2many('employee.update.address', 'employee_update_profile', string='Address', track_visibility='always')
    address_current_ids = fields.One2many('employee.current.address', 'employee_current_profile', string='Current Address', track_visibility='always')

    relative_current_ids = fields.One2many('employee.relative.current', 'employee_current_profile', string='Current Relatives', track_visibility='always')
    relative_ids = fields.One2many('employee.relative.update', 'employee_update_profile', string='Relatives', track_visibility='always')

    resume_line_current_ids = fields.One2many('hr.resume.line.current', 'employee_current_profile', string="Resume lines")
    employee_skill_current_ids = fields.One2many('hr.employee.skill.current', 'employee_current_profile', string="Skills")

    resume_line_ids = fields.One2many('hr.resume.line.update', 'employee_update_profile', string="Resume lines")
    employee_skill_ids = fields.One2many('hr.employee.skill.update', 'employee_update_profile', string="Skills")

    category = fields.Many2one('employee.category', string='Category', track_visibility='always')
    religion = fields.Many2one('employee.religion', string='Religion', track_visibility='always')
    minority = fields.Boolean('Minority', default=False, track_visibility='always')

    emergency_contact = fields.Char("Emergency Contact")
    emergency_phone = fields.Char("Emergency Phone")
    phone = fields.Char('Phone (Home)', track_visibility='always')

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
    kind_of_disability = fields.Selection([('vh', 'Visually Handicappped'),
                                           ('hh', 'Hearing Handicapped'),
                                           ('ph', 'Physically Handicapped ')], string='Kind of Disability',
                                          track_visibility='always')
    perc_disability = fields.Char('% of Disability', track_visibility='always')
    certificate_upload = fields.Binary('Upload certificate', track_visibility='always')
    certificate_upload_filename = fields.Char("Upload certificate Filename")
    personal_remark = fields.Char('Personal mark of Identification', track_visibility='always')
    identify_id = fields.Char(string='Identification No.', copy=False, store=True, track_visibility='always')
    pan_no = fields.Char('PAN Card No.', track_visibility='always')
    pan_upload = fields.Binary('Upload(PAN)', track_visibility='always')
    pan_upload_filename = fields.Char("Upload(PAN) Filename")
    aadhar_no = fields.Char('Aadhar Card No.', track_visibility='always')
    aadhar_upload = fields.Binary('Upload(Aadhar)', track_visibility='always')
    aadhar_upload_filename = fields.Char("Upload(Aadhar) Filename")
    passport_upload = fields.Binary('Upload(Passport)', track_visibility='always')
    passport_upload_filename = fields.Char("Upload(Passport) Filename")
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account number')
    ifsc_code = fields.Char(string='IFSC Code')
    passport_id = fields.Char('Passport No')

    birthday = fields.Date('Date of Birth')
    place_of_birth = fields.Char('Place of Birth')
    country_of_birth = fields.Many2one('res.country', string="Country of Birth")

    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',
                                     track_visibility='always', store=True)

    recruitment_type = fields.Selection([
        ('d_recruitment', 'Direct Recruitment(DR)'),
        ('transfer', 'Transfer(Absorption)'),
        ('i_absorption', 'Immediate Absorption'),
        ('deputation', 'Deputation'),
        ('c_appointment', 'Compassionate Appointment'),
        ('promotion', 'Promotion'),
    ], 'Recruitment Type', track_visibility='always', store=True)

    salutation = fields.Many2one('res.partner.title', track_visibility='always')

    fax_number = fields.Char('FAX number', track_visibility='always')

    new_designation = fields.Many2one('hr.job', string="Functional Designation")
    new_branch_id = fields.Many2one('res.branch', string="Center")
    new_department = fields.Many2one('hr.department', string="Department")


    new_category = fields.Many2one('employee.category', string='Category', track_visibility='always')
    new_religion = fields.Many2one('employee.religion', string='Religion', track_visibility='always')
    new_minority = fields.Boolean('Minority', default=False, track_visibility='always')

    new_emergency_contact = fields.Char("Emergency Contact")
    new_emergency_phone = fields.Char("Emergency Phone")
    new_phone = fields.Char('Phone (Home)', track_visibility='always')

    new_height = fields.Float('Height (in CMs)', track_visibility='always')
    new_weight = fields.Float('Weight (in KGs)', track_visibility='always')
    new_blood_group = fields.Selection([('a+', 'A+'),
                                    ('a-', 'A-'),
                                    ('b+', 'B+'),
                                    ('b-', 'B-'),
                                    ('o+', 'O+'),
                                    ('o-', 'O-'),
                                    ('ab+', 'AB+'),
                                    ('ab-', 'AB-')], string='Blood Group', track_visibility='always')
    new_differently_abled = fields.Selection([('no', 'No'),
                                          ('yes', 'Yes')], string='Differently Abled?',
                                         track_visibility='always')
    new_kind_of_disability = fields.Selection([('vh', 'Visually Handicappped'),
                                           ('hh', 'Hearing Handicapped'),
                                           ('ph', 'Physically Handicapped ')], string='Kind of Disability',
                                          track_visibility='always')
    new_perc_disability = fields.Char('% of Disability', track_visibility='always')
    new_certificate_upload = fields.Binary('Upload certificate', track_visibility='always')
    new_certificate_upload_filename = fields.Char('Upload certificate Filename')
    new_personal_remark = fields.Char('Personal mark of Identification', track_visibility='always')
    new_pan_no = fields.Char('PAN Card No.', track_visibility='always')
    new_pan_upload = fields.Binary('Upload(PAN)', track_visibility='always')
    new_pan_upload_filename = fields.Char('Upload(PAN) Filename')
    new_aadhar_no = fields.Char('Aadhar Card No.', track_visibility='always')
    new_aadhar_upload = fields.Binary('Upload(Aadhar)', track_visibility='always')
    new_aadhar_upload_filename = fields.Char('Upload(Aadhar) Filename')
    new_passport_upload = fields.Binary('Upload(Passport)', track_visibility='always')
    new_passport_upload_filename = fields.Char('Upload(Passport) Filename')
    new_bank_name = fields.Char(string='Bank Name')
    new_bank_account_number = fields.Char(string='Bank Account number')
    new_ifsc_code = fields.Char(string='IFSC Code')
    new_passport_id = fields.Char(string='Passport No.')
    new_birthday = fields.Date('Date of Birth')
    new_place_of_birth = fields.Char('Place of Birth')
    new_country_of_birth = fields.Many2one('res.country', string="Country of Birth")
    new_salutation = fields.Many2one('res.partner.title', string='Salutation', track_visibility='always')
    new_fax_number = fields.Char('FAX number', track_visibility='always')
    new_employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_stpi', 'Contractual with STPI')], string='Employment Type',
                                     track_visibility='always', store=True)

    new_recruitment_type = fields.Selection([
        ('d_recruitment', 'Direct Recruitment(DR)'),
        ('transfer', 'Transfer(Absorption)'),
        ('i_absorption', 'Immediate Absorption'),
        ('deputation', 'Deputation'),
        ('c_appointment', 'Compassionate Appointment'),
        ('promotion', 'Promotion'),
    ], 'Recruitment Type', track_visibility='always', store=True)

    # Contract Page
    oc_struct_id = fields.Many2one('hr.payroll.structure', string='Salary Type')
    oc_pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    oc_pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell')
    oc_city_id = fields.Many2one('res.city', string='City', store=True)
    oc_employee_hra_cat = fields.Selection([('x', 'X'),
                                         ('y', 'Y'),
                                         ('z', 'Z'),
                                         ], string='HRA Category', store=True)
    oc_city_tier = fields.Selection([('a', 'A'),
                                  ('a1', 'A1'),
                                  ('other', 'Other'),
                                  ], string='City Tier')
    oc_date_start = fields.Date('Start Date', required=True, default=fields.Date.today,
                             help="Start date of the contract.")
    oc_date_end = fields.Date('End Date',
                           help="End date of the contract (if it's a fixed-term contract).")
    oc_trial_date_end = fields.Date('End of Probation Period',
                                 help="End date of the trial period (if there is one).")
    oc_wage = fields.Float('Wage', digits=(16, 2), track_visibility="onchange",
                           help="Employee's monthly gross wage.")



    nc_struct_id = fields.Many2one('hr.payroll.structure', string='Salary Type')
    nc_pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    nc_pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell')
    nc_city_id = fields.Many2one('res.city', string='City', store=True)
    nc_employee_hra_cat = fields.Selection([('x', 'X'),
                                         ('y', 'Y'),
                                         ('z', 'Z'),
                                         ], string='HRA Category',
                                        store=True)
    nc_city_tier = fields.Selection([('a', 'A'),
                                  ('a1', 'A1'),
                                  ('other', 'Other'),
                                  ], string='City Tier')
    nc_date_start = fields.Date('Start Date', required=True, default=fields.Date.today,
                             help="Start date of the contract.")
    nc_date_end = fields.Date('End Date',
                           help="End date of the contract (if it's a fixed-term contract).")
    nc_trial_date_end = fields.Date('End of Probation Period',
                                 help="End date of the trial period (if there is one).")
    nc_wage = fields.Float('Wage', digits=(16, 2), required=True, track_visibility="onchange",
                           help="Employee's monthly gross wage.")




    @api.constrains('new_bank_account_number')
    def _check_bank_acc_number(self):
        for rec in self:
            if rec.new_bank_account_number:
                for e in rec.new_bank_account_number:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter correct Account number, it must be numeric..."))


    @api.constrains('new_aadhar_no')
    def _check_aadhar_number(self):
        for rec in self:
            if rec.new_aadhar_no:
                for e in rec.new_aadhar_no:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter correct Aadhar number, it must be numeric..."))
                if len(rec.new_aadhar_no) != 12:
                    raise ValidationError(_("Please enter correct Aadhar number, it must be of 12 digits..."))


    @api.constrains('new_pan_no')
    def _check_pan_number(self):
        for rec in self:
            if rec.new_pan_no and not re.match(r'^[A-Za-z]{5}[0-9]{4}[A-Za-z]$', str(rec.new_pan_no)):
                raise ValidationError(_("Please enter correct PAN number..."))


    @api.constrains('new_emergency_contact','new_emergency_phone','new_phone')
    def _check_new_emergency_contact_num(self):
        for rec in self:
            if rec.new_emergency_phone and not rec.new_emergency_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number"))
            if rec.new_emergency_phone and len(rec.new_emergency_phone) != 10:
                raise ValidationError(_("Please enter correct Emergency Phone number."
                                        "It must be of 10 digits"))
            if rec.new_phone and not rec.new_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number"))
            if rec.new_phone and len(rec.new_phone) != 10:
                raise ValidationError(_("Please enter correct phone number."
                                                "It must be of 10 digits"))

    @api.multi
    @api.depends('employee_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.employee_id:
                name = 'Employee Profile - ' + str(record.employee_id.name) + ' - Update'
            else:
                name = 'Employee Profile'
            res.append((record.id, name))
        return res

    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')
                               ], required=True, string='Status', default='draft',track_visibility='always')


    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def onchange_emp_get_data(self,working_list=None):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id
            rec.category = rec.employee_id.category.id
            rec.religion = rec.employee_id.religion.id
            rec.minority = rec.employee_id.minority
            rec.height = rec.employee_id.height
            rec.weight = rec.employee_id.weight
            rec.blood_group = rec.employee_id.blood_group
            rec.differently_abled = rec.employee_id.differently_abled
            rec.kind_of_disability = rec.employee_id.kind_of_disability
            rec.perc_disability = rec.employee_id.perc_disability
            rec.certificate_upload = rec.employee_id.certificate_upload
            rec.personal_remark = rec.employee_id.personal_remark
            rec.identify_id = rec.employee_id.identify_id
            rec.emergency_contact = rec.employee_id.emergency_contact
            rec.emergency_phone = rec.employee_id.emergency_phone
            rec.phone = rec.employee_id.phone
            rec.birthday = rec.employee_id.birthday
            rec.place_of_birth = rec.employee_id.place_of_birth
            rec.country_of_birth = rec.employee_id.country_of_birth.id
            rec.pan_no = rec.employee_id.pan_no
            rec.pan_upload = rec.employee_id.pan_upload
            rec.aadhar_no = rec.employee_id.aadhar_no
            rec.aadhar_upload = rec.employee_id.aadhar_upload
            rec.passport_id = rec.employee_id.passport_id
            rec.passport_upload = rec.employee_id.passport_upload
            rec.bank_name = rec.employee_id.bank_name
            rec.bank_account_number = rec.employee_id.bank_account_number
            rec.ifsc_code = rec.employee_id.ifsc_code
            rec.salutation = rec.employee_id.salutation.id
            rec.employee_type = rec.employee_id.employee_type
            rec.recruitment_type = rec.employee_id.recruitment_type
            rec.fax_number = rec.employee_id.fax_number
            address_current_ids = []
            for address in rec.employee_id.address_ids:
                address_current_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'address_type': address.address_type,
                    'state_id': address.state_id.id,
                    'country_id': address.country_id.id,
                    'street': address.street,
                    'street2': address.street2,
                    'zip': address.zip,
                    'is_correspondence_address': address.is_correspondence_address,
                    'city': address.city,
                }))
            else:
                rec.address_current_ids = working_list
            rec.address_current_ids = address_current_ids
            resume_line_current_ids = []
            for address in rec.employee_id.resume_line_ids:
                resume_line_current_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'resume_employee_id': address.resume_employee_id.id,
                    'name': address.name,
                    'date_start': address.date_start,
                    'date_end': address.date_end,
                    'description': address.description,
                    'upload_qualification_proof': address.upload_qualification_proof,
                    'line_type_id': address.line_type_id.id,
                    'type_name': address.type_name,
                    'title': address.title.id,
                    'specialization': address.specialization,
                    'sequence': address.sequence,
                    'acquired': address.acquired,
                }))
            else:
                rec.resume_line_current_ids = working_list
            rec.resume_line_current_ids = resume_line_current_ids
            employee_skill_current_ids = []
            for address in rec.employee_id.employee_skill_ids:
                employee_skill_current_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'skill_id': address.skill_id.id,
                    'skill_level_id': address.skill_level_id.id,
                    'skill_type_id': address.skill_type_id.id,
                    'level_progress': address.level_progress,
                }))
            else:
                rec.employee_skill_current_ids = working_list
            rec.employee_skill_current_ids = employee_skill_current_ids
            relative_current_ids = []
            for address in rec.employee_id.relative_ids:
                relative_current_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'salutation': address.salutation.id,
                    'employee_id': address.employee_id.id,
                    'name': address.name,
                    'relate_type': address.relate_type.id,
                    'birthday': address.birthday,
                    'place_of_birth': address.place_of_birth,
                    'occupation': address.occupation,
                    'gender': address.gender,
                    'medical': address.medical,
                    'tuition': address.tuition,
                    'ltc': address.ltc,
                    'status': address.status,
                    'prec_pf': address.prec_pf,
                    'prec_gratuity': address.prec_gratuity,
                    'prec_pension': address.prec_pension,
                }))
            else:
                rec.relative_current_ids = working_list
            rec.relative_current_ids = relative_current_ids
            prev_occu_current_ids = []
            for address in rec.employee_id.prev_occu_ids:
                prev_occu_current_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'last_employer': address.last_employer,
                    'organization_type': address.organization_type.id,
                    'from_date': address.from_date,
                    'to_date': address.to_date,
                    'service_period': address.service_period,
                    'position': address.position,
                    'reason_for_leaving': address.reason_for_leaving,
                    'currency_id': address.currency_id.id,
                    'last_drawn_salary': address.last_drawn_salary,
                    'ref_name': address.ref_name,
                    'ref_position': address.ref_position,
                    'ref_phone': address.ref_phone,
                    'attachment': address.attachment,
                    'remarks': address.remarks,
                }))
            else:
                rec.prev_occu_current_ids = working_list
            rec.prev_occu_current_ids = prev_occu_current_ids
            emp_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            for em_c in emp_contract:
                rec.oc_struct_id = em_c.struct_id.id
                rec.oc_pay_level_id = em_c.pay_level_id.id
                rec.oc_pay_level = em_c.pay_level.id
                rec.oc_city_id = em_c.city_id.id
                rec.oc_employee_hra_cat = em_c.employee_hra_cat
                rec.oc_city_tier = em_c.city_tier
                rec.oc_date_start = em_c.date_start
                rec.oc_date_end = em_c.date_end
                rec.oc_trial_date_end = em_c.trial_date_end
                rec.oc_wage = em_c.wage




    @api.onchange('employee_id')
    def onchange_emp_temp_get_data(self,working_list=None):
        for rec in self:
            address_ids = []
            for address in rec.employee_id.address_ids:
                address_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'address_type': address.address_type,
                    'state_id': address.state_id.id,
                    'country_id': address.country_id.id,
                    'street': address.street,
                    'street2': address.street2,
                    'zip': address.zip,
                    'is_correspondence_address': address.is_correspondence_address,
                    'city': address.city,
                }))
            else:
                rec.address_ids = working_list
            rec.address_ids = address_ids
            resume_line_ids = []
            for address in rec.employee_id.resume_line_ids:
                resume_line_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'resume_employee_id': address.resume_employee_id.id,
                    'name': address.name,
                    'date_start': address.date_start,
                    'date_end': address.date_end,
                    'description': address.description,
                    'upload_qualification_proof': address.upload_qualification_proof,
                    'line_type_id': address.line_type_id.id,
                    'type_name': address.type_name,
                    'title': address.title.id,
                    'specialization': address.specialization,
                    'sequence': address.sequence,
                    'acquired': address.acquired,
                }))
            else:
                rec.resume_line_ids = working_list
            rec.resume_line_ids = resume_line_ids
            employee_skill_ids = []
            for address in rec.employee_id.employee_skill_ids:
                employee_skill_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'skill_id': address.skill_id.id,
                    'skill_level_id': address.skill_level_id.id,
                    'skill_type_id': address.skill_type_id.id,
                    'level_progress': address.level_progress,
                }))
            else:
                rec.employee_skill_ids = working_list
            rec.employee_skill_ids = employee_skill_ids
            relative_ids = []
            for address in rec.employee_id.relative_ids:
                relative_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': rec.employee_id.id,
                    'salutation': address.salutation.id,
                    'name': address.name,
                    'relate_type': address.relate_type.id,
                    'birthday': address.birthday,
                    'place_of_birth': address.place_of_birth,
                    'occupation': address.occupation,
                    'gender': address.gender,
                    'medical': address.medical,
                    'tuition': address.tuition,
                    'ltc': address.ltc,
                    'status': address.status,
                    'prec_pf': address.prec_pf,
                    'prec_gratuity': address.prec_gratuity,
                    'prec_pension': address.prec_pension,
                }))
            else:
                rec.relative_ids = working_list
            rec.relative_ids = relative_ids
            prev_occu_ids = []
            for address in rec.employee_id.prev_occu_ids:
                prev_occu_ids.append((0, 0, {
                    'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'last_employer': address.last_employer,
                    'organization_type': address.organization_type.id,
                    'from_date': address.from_date,
                    'to_date': address.to_date,
                    'service_period': address.service_period,
                    'position': address.position,
                    'reason_for_leaving': address.reason_for_leaving,
                    'currency_id': address.currency_id.id,
                    'last_drawn_salary': address.last_drawn_salary,
                    'ref_name': address.ref_name,
                    'ref_position': address.ref_position,
                    'ref_phone': address.ref_phone,
                    'attachment': address.attachment,
                    'remarks': address.remarks,
                }))
            else:
                rec.prev_occu_ids = working_list
            rec.prev_occu_ids = prev_occu_ids


    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.requested_by = rec.create_uid.name
            rec.write({'state': 'waiting_for_approval'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    @api.multi
    def unlink(self):
        for tour in self:
            if tour.state != 'draft':
                raise UserError(
                    'You cannot delete a Update Request which is not in draft state')
        return super(EmployeeProfile, self).unlink()

    @api.multi
    def button_revert(self):
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,

            default_model='employee.profile',
            default_is_log='True',
            custom_layout='mail.mail_notification_light'
        )
        mw = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        self.write({'state': 'draft'})
        return mw


    @api.multi
    def button_approved(self):
        for rec in self:
            if rec.new_employee_type:
                rec.employee_id.employee_type = rec.new_employee_type
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Employement Type',
                    'old_value': str(rec.employee_type),
                    'new_value': str(rec.new_employee_type),
                })
            if rec.new_recruitment_type:
                rec.employee_id.recruitment_type = rec.new_recruitment_type
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Recruitment Type',
                    'old_value': str(rec.recruitment_type),
                    'new_value': str(rec.new_recruitment_type),
                })
            if rec.new_designation:
                rec.employee_id.job_id = rec.new_designation.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Designation',
                    'old_value': str(rec.designation.name),
                    'new_value': str(rec.new_designation.name),
                })
            if rec.new_branch_id:
                rec.employee_id.branch_id = rec.new_branch_id.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Branch',
                    'old_value': str(rec.branch_id.name),
                    'new_value': str(rec.new_branch_id.name),
                })
            if rec.new_department:
                rec.employee_id.department_id = rec.new_department.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Department',
                    'old_value': str(rec.department.name),
                    'new_value': str(rec.new_department.name),
                })
            if rec.new_category:
                rec.employee_id.category = rec.new_category.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Category',
                    'old_value': str(rec.category.name),
                    'new_value': str(rec.new_category.name),
                })
            if rec.new_religion:
                rec.employee_id.religion = rec.new_religion.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Religion',
                    'old_value': str(rec.religion.name),
                    'new_value': str(rec.new_religion.name),
                })
            if rec.new_minority:
                rec.employee_id.minority = rec.new_minority
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Minority',
                    'old_value': str(rec.minority),
                    'new_value': str(rec.new_minority),
                })
            if rec.new_height:
                rec.employee_id.height = rec.new_height
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Height',
                    'old_value': str(rec.height),
                    'new_value': str(rec.new_height),
                })
            if rec.new_weight:
                rec.employee_id.weight = rec.new_weight
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Weight',
                    'old_value': str(rec.weight),
                    'new_value': str(rec.new_weight),
                })
            if rec.new_blood_group:
                rec.employee_id.blood_group = rec.new_blood_group
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Blood Group',
                    'old_value': str(rec.blood_group),
                    'new_value': str(rec.new_blood_group),
                })
            if rec.new_differently_abled:
                rec.employee_id.differently_abled = rec.new_differently_abled
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Differently Abled',
                    'old_value': str(rec.differently_abled),
                    'new_value': str(rec.new_differently_abled),
                })
            if rec.new_kind_of_disability:
                rec.employee_id.kind_of_disability = rec.new_kind_of_disability
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Kind of Disability',
                    'old_value': str(rec.kind_of_disability),
                    'new_value': str(rec.new_kind_of_disability),
                })
            if rec.new_perc_disability:
                rec.employee_id.perc_disability = rec.new_perc_disability
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': '% of disability',
                    'old_value': str(rec.perc_disability),
                    'new_value': str(rec.new_perc_disability),
                })
            if rec.new_certificate_upload:
                rec.employee_id.certificate_upload = rec.new_certificate_upload
            if rec.new_personal_remark:
                rec.employee_id.personal_remark = rec.new_personal_remark
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Personal Remark',
                    'old_value': str(rec.personal_remark),
                    'new_value': str(rec.new_personal_remark),
                })
            if rec.new_emergency_contact:
                rec.employee_id.emergency_contact = rec.new_emergency_contact
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Emergency Contact',
                    'old_value': str(rec.emergency_contact),
                    'new_value': str(rec.new_emergency_contact),
                })
            if rec.new_emergency_phone:
                rec.employee_id.emergency_phone = rec.new_emergency_phone
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Emergency Phone',
                    'old_value': str(rec.emergency_phone),
                    'new_value': str(rec.new_emergency_phone),
                })

            if rec.new_phone:
                rec.employee_id.phone = rec.new_phone
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Phone(Home)',
                    'old_value': str(rec.phone),
                    'new_value': str(rec.new_phone),
                })
            if rec.new_birthday:
                rec.employee_id.birthday = rec.new_birthday
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Birthday',
                    'old_value': str(rec.birthday),
                    'new_value': str(rec.new_birthday),
                })
            if rec.new_place_of_birth:
                rec.employee_id.place_of_birth = rec.new_place_of_birth
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Place of Birth',
                    'old_value': str(rec.place_of_birth),
                    'new_value': str(rec.new_place_of_birth),
                })
            if rec.new_country_of_birth:
                rec.employee_id.country_of_birth = rec.new_country_of_birth
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Country of Birth',
                    'old_value': str(rec.country_of_birth.name),
                    'new_value': str(rec.new_country_of_birth.name),
                })
            if rec.new_pan_no:
                rec.employee_id.pan_no = rec.new_pan_no
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'PAN No.',
                    'old_value': str(rec.pan_no),
                    'new_value': str(rec.new_pan_no),
                })
            if rec.new_pan_upload:
                rec.employee_id.pan_upload = rec.new_pan_upload
            if rec.new_aadhar_no:
                rec.employee_id.aadhar_no = rec.new_aadhar_no
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Aadhar No.',
                    'old_value': str(rec.aadhar_no),
                    'new_value': str(rec.new_aadhar_no),
                })
            if rec.new_aadhar_upload:
                rec.employee_id.aadhar_upload = rec.new_aadhar_upload
            if rec.new_passport_upload:
                rec.employee_id.passport_upload = rec.new_passport_upload
            if rec.new_passport_id:
                rec.employee_id.passport_id = rec.new_passport_id
                rec.employee_id.height = rec.new_height
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Passport No.',
                    'old_value': str(rec.passport_id),
                    'new_value': str(rec.new_passport_id),
                })
            if rec.new_bank_name:
                rec.employee_id.bank_name = rec.new_bank_name
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Bank Name',
                    'old_value': str(rec.bank_name),
                    'new_value': str(rec.new_bank_name),
                })
            if rec.new_bank_account_number:
                rec.employee_id.bank_account_number = rec.new_bank_account_number
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Bank Account Number',
                    'old_value': str(rec.bank_account_number),
                    'new_value': str(rec.new_bank_account_number),
                })
            if rec.new_ifsc_code:
                rec.employee_id.ifsc_code = rec.new_ifsc_code
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'IFSC Code',
                    'old_value': str(rec.ifsc_code),
                    'new_value': str(rec.new_ifsc_code),
                })
            if rec.new_salutation:
                rec.employee_id.salutation = rec.new_salutation.id
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'Salutation',
                    'old_value': str(rec.salutation.name),
                    'new_value': str(rec.new_salutation.name),
                })
            if rec.new_fax_number:
                rec.employee_id.fax_number = rec.new_fax_number
                self.env['employee.profile.report'].create({
                    'employee_id': str(rec.employee_id.name),
                    'requested_by': str(rec.requested_by),
                    'approved_by': str(rec.env.user.name),
                    'designation': str(rec.designation.name),
                    'department': str(rec.department.name),
                    'branch_id': str(rec.branch_id.name),
                    'date': rec.date,
                    'approved_date': datetime.now().date(),
                    'field_n': 'FAX No.',
                    'old_value': str(rec.fax_number),
                    'new_value': str(rec.new_fax_number),
                })
            if rec.address_ids:
                address_ids = []
                for address in rec.address_ids:
                    address_ids.append((0, 0, {
                        'employee_id': address.employee_id.id,
                        'address_type': address.address_type,
                        'state_id': address.state_id.id,
                        'country_id': address.country_id.id,
                        'street': address.street,
                        'street2': address.street2,
                        'zip': address.zip,
                        'is_correspondence_address': address.is_correspondence_address,
                        'city': address.city,
                    }))
                rec.employee_id.address_ids.unlink()
                rec.employee_id.address_ids = address_ids
            if rec.resume_line_ids:
                resume_line_ids = []
                for address in rec.resume_line_ids:
                    resume_line_ids.append((0, 0, {
                        'resume_employee_id': address.resume_employee_id.id,
                        'name': address.name,
                        'date_start': address.date_start,
                        'date_end': address.date_end,
                        'description': address.description,
                        'upload_qualification_proof': address.upload_qualification_proof,
                        'line_type_id': address.line_type_id.id,
                        'type_name': address.type_name,
                        'title': address.title.id,
                        'specialization': address.specialization,
                        'sequence': address.sequence,
                        'acquired': address.acquired,
                    }))
                rec.employee_id.resume_line_ids.unlink()
                rec.employee_id.resume_line_ids = resume_line_ids
            if rec.employee_skill_ids:
                employee_skill_ids = []
                for address in rec.employee_skill_ids:
                    employee_skill_ids.append((0, 0, {
                        'employee_id': address.employee_id.id,
                        'skill_id': address.skill_id.id,
                        'skill_level_id': address.skill_level_id.id,
                        'skill_type_id': address.skill_type_id.id,
                        'level_progress': address.level_progress,
                    }))
                rec.employee_id.employee_skill_ids.unlink()
                rec.employee_id.employee_skill_ids = employee_skill_ids
            if rec.relative_ids:
                relative_ids = []
                for address in rec.relative_ids:
                    relative_ids.append((0, 0, {
                        'employee_id': address.employee_id.id,
                        'salutation': address.salutation.id,
                        'name': address.name,
                        'relate_type': address.relate_type.id,
                        'birthday': address.birthday,
                        'place_of_birth': address.place_of_birth,
                        'occupation': address.occupation,
                        'gender': address.gender,
                        'medical': address.medical,
                        'tuition': address.tuition,
                        'ltc': address.ltc,
                        'status': address.status,
                        'prec_pf': address.prec_pf,
                        'prec_gratuity': address.prec_gratuity,
                        'prec_pension': address.prec_pension,
                    }))
                rec.employee_id.relative_ids.unlink()
                rec.employee_id.relative_ids = relative_ids

            if rec.relative_ids:
                prev_occu_ids = []
                for address in rec.prev_occu_ids:
                    prev_occu_ids.append((0, 0, {
                        'employee_current_profile': rec.id,
                    'employee_id': address.employee_id.id,
                    'last_employer': address.last_employer,
                    'organization_type': address.organization_type.id,
                    'from_date': address.from_date,
                    'to_date': address.to_date,
                    'service_period': address.service_period,
                    'position': address.position,
                    'reason_for_leaving': address.reason_for_leaving,
                    'currency_id': address.currency_id.id,
                    'last_drawn_salary': address.last_drawn_salary,
                    'ref_name': address.ref_name,
                    'ref_position': address.ref_position,
                    'ref_phone': address.ref_phone,
                    'attachment': address.attachment,
                    'remarks': address.remarks,
                    }))
                rec.employee_id.prev_occu_ids.unlink()
                rec.employee_id.prev_occu_ids = prev_occu_ids

            emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            for em_cnt in emp_contract:
                if rec.nc_struct_id:
                    emp_contract.write({
                        'struct_id': rec.nc_struct_id.id,
                    })
                if rec.nc_pay_level_id:
                    emp_contract.write({
                        'pay_level_id': rec.nc_pay_level_id.id,
                    })
                if rec.nc_pay_level:
                    emp_contract.write({
                        'pay_level': rec.nc_pay_level.id,
                    })
                if rec.nc_city_id:
                    emp_contract.write({
                        'city_id': rec.nc_city_id.id,
                    })
                if rec.nc_employee_hra_cat:
                    emp_contract.write({
                        'employee_hra_cat': rec.nc_employee_hra_cat,
                    })
                if rec.nc_city_tier:
                    emp_contract.write({
                        'city_tier': rec.nc_city_tier,
                    })
                if rec.nc_date_start:
                    emp_contract.write({
                        'date_start': rec.nc_date_start,
                    })
                if rec.nc_date_end:
                    emp_contract.write({
                        'date_end': rec.nc_date_end,
                    })
                if rec.nc_trial_date_end:
                    emp_contract.write({
                        'trial_date_end': rec.nc_trial_date_end,
                    })
                if rec.nc_wage:
                    emp_contract.write({
                        'wage': rec.nc_wage,
                    })
            rec.write({'state': 'approved'})



class CurrentAddress(models.Model):
    _name = "employee.current.address"
    _description = "Employee Current Address"


    address_type = fields.Selection([('permanent_add', 'Permanent Add'),
                                     ('present_add', 'Present Add'),
                                     ('office_add', 'Office Add'),
                                     ('hometown_add', 'HomeTown Add'),
                                    ],string='Address Type',required=True)
    employee_id = fields.Many2one('hr.employee','Employee Id')
    employee_current_profile = fields.Many2one('employee.profile','Employee Profile')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    is_correspondence_address = fields.Boolean('Is Correspondence Address')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')



class UpdateAddress(models.Model):
    _name = "employee.update.address"
    _description = "Employee Address"


    def default_country(self):
        return self.env['res.country'].search([('name', '=', 'India')], limit=1)


    address_type = fields.Selection([('permanent_add', 'Permanent Add'),
                                     ('present_add', 'Present Add'),
                                     ('office_add', 'Office Add'),
                                     ('hometown_add', 'HomeTown Add'),
                                    ],string='Address Type',required=True)
    employee_update_profile = fields.Many2one('employee.profile')
    employee_id = fields.Many2one('hr.employee', 'Employee Id')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    is_correspondence_address = fields.Boolean('Is Correspondence Address')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country', default = default_country)

    @api.constrains('employee_update_profile')
    def get_emp_id(self):
        for rec in self:
            rec.employee_id = rec.employee_update_profile.employee_id.id


class ResumeLineCurrent(models.Model):
    _name = 'hr.resume.line.current'
    _description = "Resume line of an employee"

    employee_current_profile = fields.Many2one('employee.profile', 'Employee Current Profile')
    resume_employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string='Title')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date()
    description = fields.Text(string="Description")
    upload_qualification_proof = fields.Binary(string="Upload")
    upload_qualification_proof_filename = fields.Char(string="Upload Filename")
    line_type_id = fields.Many2one('hr.resume.line.type', string="Type")
    type_name = fields.Char(related='line_type_id.name')
    title = fields.Many2one('hr.education', string='Qualification')
    specialization = fields.Char(string='Specialization')
    sequence = fields.Integer(default=100)
    acquired = fields.Selection([('at_appointment_time', 'At Appointment time'),
                                 ('subsequently_acquired', 'Subsequently Acquired'),
                                 ], default='at_appointment_time', string="Acquired")


class ResumeLineUpdate(models.Model):
    _name = 'hr.resume.line.update'
    _description = "Resume line of an employee - Update"

    employee_update_profile = fields.Many2one('employee.profile', 'Employee Updated Profile')
    resume_employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    name = fields.Char(string='Title')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date()
    description = fields.Text(string="Description")
    upload_qualification_proof = fields.Binary(string="Upload")
    upload_qualification_proof_filename = fields.Char(string="Upload Filename")
    line_type_id = fields.Many2one('hr.resume.line.type', string="Type")
    type_name = fields.Char(related='line_type_id.name')
    title = fields.Many2one('hr.education', string='Qualification')
    specialization = fields.Char(string='Specialization')
    sequence = fields.Integer(default=100)
    acquired = fields.Selection([('at_appointment_time', 'At Appointment time'),
                                 ('subsequently_acquired', 'Subsequently Acquired'),
                                 ], default='at_appointment_time', string="Acquired")


    @api.constrains('employee_update_profile')
    def get_emp_id(self):
        for rec in self:
            rec.resume_employee_id = rec.employee_update_profile.employee_id.id


class EmployeeSkillCurrent(models.Model):
    _name = 'hr.employee.skill.current'
    _description = "Skill level for an employee Current"

    employee_current_profile = fields.Many2one('employee.profile', 'Employee Current Profile')
    employee_id = fields.Many2one('hr.employee')
    skill_id = fields.Many2one('hr.skill')
    skill_level_id = fields.Many2one('hr.skill.level')
    skill_type_id = fields.Many2one('hr.skill.type')
    level_progress = fields.Integer(related='skill_level_id.level_progress')



class EmployeeSkillUpdtae(models.Model):
    _name = 'hr.employee.skill.update'
    _description = "Skill level for an employee update"

    employee_update_profile = fields.Many2one('employee.profile', 'Employee Update Profile')
    employee_id = fields.Many2one('hr.employee')
    skill_id = fields.Many2one('hr.skill')
    skill_level_id = fields.Many2one('hr.skill.level')
    skill_type_id = fields.Many2one('hr.skill.type')
    level_progress = fields.Integer(related='skill_level_id.level_progress')


    @api.constrains('employee_update_profile')
    def get_emp_id(self):
        for rec in self:
            rec.employee_id = rec.employee_update_profile.employee_id.id



class EmployeeRelativeCurrent(models.Model):
    _name = 'employee.relative.current'
    _description = "Employee Relative Current"

    employee_current_profile = fields.Many2one('employee.profile', 'Employee Current Profile')
    salutation = fields.Many2one('res.partner.title', string='Salutation')
    relate_type = fields.Many2one('relative.type', string="Relative Type")
    relate_type_name = fields.Char(related='relate_type.name')

    name = fields.Char(string='Name', )

    medical = fields.Boolean('Medical', default=False)
    tuition = fields.Boolean('Tuition', default=False)
    ltc = fields.Boolean('LTC', default=False)
    status = fields.Selection([('dependant', 'Dependant'),
                               ('non_dependant', 'Non-Dependant')
                               ], string='Status')
    prec_pf = fields.Float('PF%')
    prec_gratuity = fields.Float('Gratuity%')
    prec_pension = fields.Float('Pension%')

    age = fields.Float('Age')
    birthday = fields.Date(string='Date of Birth')
    place_of_birth = fields.Char(string='Place of Birth', size=128)
    occupation = fields.Char(string='Occupation', size=128)
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')], string='Gender',
        required=False)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref')


class EmployeeRelativeUpdtae(models.Model):
    _name = 'employee.relative.update'
    _description = "Employee Relative Update"

    employee_update_profile = fields.Many2one('employee.profile', 'Employee Update Profile')
    salutation = fields.Many2one('res.partner.title', string='Salutation')
    relate_type = fields.Many2one('relative.type', string="Relative Type")
    relate_type_name = fields.Char(related='relate_type.name')

    name = fields.Char(string='Name', )

    medical = fields.Boolean('Medical', default=False)
    tuition = fields.Boolean('Tuition', default=False)
    ltc = fields.Boolean('LTC', default=False)
    status = fields.Selection([('dependant', 'Dependant'),
                               ('non_dependant', 'Non-Dependant')
                               ], string='Status')
    prec_pf = fields.Float('PF%')
    prec_gratuity = fields.Float('Gratuity%')
    prec_pension = fields.Float('Pension%')

    age = fields.Float('Age')
    birthday = fields.Date(string='Date of Birth')
    place_of_birth = fields.Char(string='Place of Birth', size=128)
    occupation = fields.Char(string='Occupation', size=128)
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')], string='Gender',
        required=False)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref')


class EmployeePreviousOccupationCurrent(models.Model):

    _name = "employee.previous.occupation.current"
    _description = "Recruite Previous Occupation Current"
    _order = 'to_date desc'
    _rec_name = 'position'

    employee_current_profile = fields.Many2one('employee.profile', 'Employee Current Profile')
    employee_id = fields.Many2one('hr.employee', 'Employee Ref', ondelete='cascade')
    last_employer = fields.Char(string = 'Last Employer')
    organization_type = fields.Many2one('organization.type', string = "Organisation Type")
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    service_period = fields.Char(string='Service period', compute='service_period_count')
    position = fields.Char(string='Position')
    reason_for_leaving = fields.Char(string = 'Reason for Leaving')
    currency_id = fields.Many2one('res.currency')
    last_drawn_salary = fields.Monetary(string = 'Last Drawn Salary')
    ref_name = fields.Char(string='Reference Name')
    ref_position = fields.Char(string='Reference Position')
    ref_phone = fields.Char(string='Reference Phone')
    attachment = fields.Binary(string="Attachment")
    attachment_filename = fields.Char(string="Attachment Filename")
    remarks = fields.Text(string='Remarks')



    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def onchange_date(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))

    @api.depends('from_date', 'to_date')
    def service_period_count(self):
        if self.from_date and self.to_date:
            r = relativedelta(self.to_date, self.from_date)
            self.service_period = ("{0} years, {1} months, {2} days".format(r.years, r.months, r.days))


    @api.constrains('ref_phone')
    @api.onchange('ref_phone')
    def _check_ref_phone(self):
        for rec in self:
            if rec.ref_phone and not rec.ref_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number - Previous Occupation"))
            if rec.ref_phone and len(rec.ref_phone) != 10:
                raise ValidationError(_("Please enter correct phone number. - Previous Occupation"
                                        "It must be of 10 digits"))



class EmployeePreviousOccupation(models.Model):

    _name = "employee.previous.occupation.update"
    _description = "Recruite Previous Occupation Update"
    _order = 'to_date desc'
    _rec_name = 'position'


    employee_update_profile = fields.Many2one('employee.profile', 'Employee Update Profile')
    employee_id = fields.Many2one('hr.employee', 'Employee Ref', ondelete='cascade')
    last_employer = fields.Char(string = 'Last Employer')
    organization_type = fields.Many2one('organization.type', string = "Organisation Type")
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    service_period = fields.Char(string='Service period', compute='service_period_count')
    position = fields.Char(string='Position', required=True)
    reason_for_leaving = fields.Char(string = 'Reason for Leaving')
    currency_id = fields.Many2one('res.currency')
    last_drawn_salary = fields.Monetary(string = 'Last Drawn Salary')
    ref_name = fields.Char(string='Reference Name')
    ref_position = fields.Char(string='Reference Position')
    ref_phone = fields.Char(string='Reference Phone')
    attachment = fields.Binary(string="Attachment")
    attachment_filename = fields.Char(string="Attachment Filename")
    remarks = fields.Text(string='Remarks')



    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def onchange_date(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))

    @api.depends('from_date', 'to_date')
    def service_period_count(self):
        if self.from_date and self.to_date:
            r = relativedelta(self.to_date, self.from_date)
            self.service_period = ("{0} years, {1} months, {2} days".format(r.years, r.months, r.days))


    @api.constrains('ref_phone')
    @api.onchange('ref_phone')
    def _check_ref_phone(self):
        for rec in self:
            if rec.ref_phone and not rec.ref_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number"))
            if rec.ref_phone and len(rec.ref_phone) != 10:
                raise ValidationError(_("Please enter correct phone number."
                                        "It must be of 10 digits"))
