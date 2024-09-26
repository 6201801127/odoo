"""
    This model is responsible for adding candidate to both Employee(hr.employee) & User(res.users) model
"""


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import hashlib, datetime
from kw_utility_tools import kw_validations


cur_dtime = datetime.datetime.now()
cur_dt = datetime.date(year=cur_dtime.year, month=cur_dtime.month, day=cur_dtime.day)


class kwonboard_new_joinee(models.Model):
    _name = 'kwonboard_new_joinee'
    _description = 'Onboarding New Joinee'
    _rec_name = 'enrollment_id'
    _order = "write_date desc"

    employee_code = fields.Char('Employee Code')
    enrollment_id = fields.Many2one('kwonboard_enrollment', string="New Joinee", domain=[('state', '=', '5')])
    fullname = fields.Char(string="Full Name")
    email_id = fields.Char(string="Email ID")
    username = fields.Char(string="User Name")
    dept_id = fields.Many2one('hr.department', string="Department", domain=[('dept_type.code', '=', 'department')])
    division_id = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
    section_id = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'section')])
    practise_id = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'practise')])
    designation = fields.Many2one('hr.job', string="Designation")
    tagged_to = fields.Many2one('kw_tag_master', string="Tagged To")
    proj_bill_amnt = fields.Integer(string="Project Billing Amount")
    func_area = fields.Many2one('kw_industry_type', string="Functional Area")
    job_loc_name = fields.Char(related='office_unit.location.name', string="Branch")
    office_unit = fields.Many2one('kw_res_branch', string="Base Location")
    grade = fields.Many2one('kwemp_grade_master', string="Grade")
    band = fields.Many2one('kwemp_band_master', string="Band")
    join_date = fields.Date(string="Joining Date", default=cur_dt)
    prob_compl_date = fields.Date(string="Probation Complete Date", default=cur_dt + relativedelta(months=6))
    confirm_status = fields.Selection(selection=[('on_probation', 'On Probation'),
                                                 ('confirmed', 'Confirmed')], string="Confirmation Status",
                                    default='on_probation')
    emp_role = fields.Many2one('kwmaster_role_name', ondelete='cascade', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', ondelete='cascade', string="Employee Category")
    employ_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")
    id_card = fields.Selection([('required', 'Required'), ('not required', 'Not Required')], string="ID Card")
    image = fields.Binary(string="Upload Photo", attachment=True,
                          help="Only .jpeg,.png,.jpg format are allowed. Maximum file size is 1 MB", store=True)
    image_id = fields.Char(compute='_compute_image_id')
    image_url = fields.Char(string="Image URL", compute="_get_image_url")
    """## Personal Information ##"""
    dob = fields.Date(string="Date of Birth")
    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], string="Gender")
    religion = fields.Many2one('kwemp_religion_master', string="Religion")
    source_id = fields.Many2one('utm.source', string="Reference Mode")
    employee_referred = fields.Many2one('hr.employee', string='Referred By')
    service_partner_id = fields.Many2one('res.partner', string='Partner')
    media_id = fields.Many2one('kw.social.media', string='Social Media')
    institute_id = fields.Many2one('res.partner', string='Institute')
    consultancy_id = fields.Many2one('res.partner', string='Consultancy')
    jportal_id = fields.Many2one('kw.job.portal', string='Job Portal')
    reference = fields.Char("Client Name")
    reference_walkindrive = fields.Char("Walk-in Drive")
    reference_print_media = fields.Char("Print Media")
    reference_job_fair = fields.Char("Job Fair")
    code_ref = fields.Char('Code')
    marital_ref = fields.Char('M Code')
    """## Reporting Authority ##"""
    admin_auth=fields.Many2one('hr.employee', string="Administrative Authority")
    func_auth=fields.Many2one('hr.employee', string="Functional Authority")
    """## Account Information ##"""
    domain_name = fields.Char(string="Domain Name")
    card_no = fields.Many2one('kw_card_master', string="Card No")
    project_id = fields.Many2one('crm.lead', string="Project")
    super_admin_access = fields.Boolean(string="Super Admin Previlege")
    job_position = fields.Many2one('hr.job', string="Job Position")
    shift = fields.Many2one('resource.calendar', string="Shift", domain=[('employee_id', '=', False)])
    """## Payroll Information ##"""
    enable_payroll = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Enable Payroll", default='no')
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")
    enable_gratuity = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Gratuity")
    """## Salary Information ##"""
    at_join_time = fields.Integer(string="At Joining Time", )
    current = fields.Integer(string="Current CTC")
    """## Basic Amount ##"""
    basic_at_join_time = fields.Integer(string="At Joining Time")
    account_no = fields.Many2one('res.partner.bank')
    bank = fields.Char(string="Bank Name")
    """## Allowances Information ##"""
    hra = fields.Integer(string="HRA(%)")
    conveyance = fields.Integer(string="Conveyance")
    medical_reimb = fields.Integer(string="Medical Reimbursement")
    transport = fields.Integer(string="Transport Allowance")
    productivity = fields.Integer(string="Productivity Allowance")
    commitment = fields.Integer(string="Commitment Allowance")
    """## Personnel Information ##"""
    marital_stat = fields.Many2one('kwemp_maritial_master', string="Marital Status")
    refered_by_emp = fields.Many2one('hr.employee', string="Referred By")
    """## Attendance Information ##"""
    enable_attendance=fields.Selection([('yes','Yes'),('no','No')], string="Enable Attendance", default='no')
    """## Personnel Information ##"""
    marriage_date=fields.Date(string="Marriage Date")
    """## Account Information ##"""
    state = fields.Selection([('draft', 'Draft'), ('authenticated', 'Authenticated'),
                              ('rejected', 'Rejected')], default='draft', track_visibility='onchange')
    emp_user_created = fields.Boolean('Emp/User Created', default=False)
    emp_user_synced = fields.Boolean('Emp/User Synced', default=False)
    user_count = fields.Integer('Users', compute='_compute_user_emp')
    cosolid_amnt = fields.Float(string="Consolidate Amount")
    work_location_id = fields.Many2one('res.partner')
    bank_account = fields.Char(string="Account No")
    bank_id = fields.Many2one('res.bank', string="Bank")
    worklocation_id = fields.Many2one('kw_res_branch', string='Work Location')
    location=fields.Selection(selection=[('onsite', 'Onsite'),('offsite', 'Offsite')], string="Onsite/Offsite", default="onsite")
    client_loc_id = fields.Many2one('res.partner')
    usersel = fields.Selection(selection=[('new', 'New'), ('existing', 'Existing')], string="User Tag", default='new')
    usersel_id = fields.Many2one('res.users', string="User")
    client_location = fields.Char(string='Client Location')
    start_dt = fields.Date(string="Contract Start Date")
    end_dt = fields.Date(string="Contract End Date")
    employement_type_code = fields.Char(related='employ_type.code')
    direct_indirect = fields.Selection(string="Direct/Indirect", selection=[('1', 'Direct'), ('2', 'Indirect')])
    current_basic = fields.Integer(string="Current Basic")
    need_sync = fields.Boolean(string="Create in Tendrils?")
    on_probation = fields.Boolean(string="On Probation", default=False)
    need_user = fields.Boolean(string="Create User?", default=True)
    
    @api.constrains('image')
    def _check_image_filename(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png']
        for rec in self:
            if rec.image:
                kw_validations.validate_file_mimetype(rec.image, allowed_file_list)
                kw_validations.validate_file_size(rec.image, 1)

    @api.onchange('hra')
    def onchange_hra(self):
        if self.hra!=0 and self.hra >= 100:
            raise ValidationError('HRA can not be more than or equal to 100')

    @api.onchange('dept_id')
    def onchange_department(self):
        self.division_id = False
        domain = {}
        for rec in self:
            domain['division_id'] = [('parent_id', '=', rec.dept_id.id),('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('division_id')
    def onchange_division(self):
        self.section_id = False
        domain = {}
        for rec in self:
            if rec.dept_id:
                domain['section_id'] = [('parent_id', '=', rec.division_id.id),('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section_id')
    def onchange_section(self):
        self.practise_id = False
        domain = {}
        for rec in self:
            if rec.section_id:
                domain['practise_id'] = [('parent_id', '=', rec.section_id.id),('dept_type.code', '=', 'practice')]
                return {'domain': domain}

    @api.onchange('enable_payroll')
    def onchange_payroll(self):
        self.basic_at_join_time = False
        self.bank_account = False
        self.bank_id = False
        self.hra = False
        self.conveyance = False
        self.medical_reimb = False
        self.transport = False
        self.productivity = False
        self.commitment = False
        self.cosolid_amnt = False

    @api.onchange('basic_at_join_time')
    def _onchange_basic_at_join(self):
        self.current_basic = self.basic_at_join_time

    @api.onchange('usersel')
    def onchange_usersel(self):
        domain = {}
        emp_rec_ids = self.env['hr.employee'].sudo().search([('user_id','!=',False)])
        user_rec_ids = emp_rec_ids.mapped('user_id.id')
        for rec in self:
            if rec.usersel == 'existing':
                domain['usersel_id'] = [('active', '=', True),('id', 'not in', user_rec_ids)]
                return {'domain': domain}

    @api.constrains('username')
    def check_username(self):
        for rec in self:
            if rec.username:
                new_joinee_rec = self.env['kwonboard_new_joinee'].sudo().search([('username', '=', rec.username)]) - self
                user_rec = self.env['res.users'].sudo().search([('login', '=', rec.username), '|', ('active', '=', True), ('active', '=', False)])
                if new_joinee_rec or user_rec:
                    raise ValidationError('Username already exists, Please choose a unique username.')

    @api.onchange('prob_compl_date')
    def set_conf_stat(self):
        if self.prob_compl_date != False:
            if self.prob_compl_date > cur_dt:
                self.confirm_status = 'on_probation'
            else:
                self.confirm_status = 'confirmed'

    @api.onchange('on_probation')
    def _onchange_on_probation(self):
        self.prob_compl_date = False

    @api.onchange('at_join_time')
    def onchange_at_join(self):
        self.current = self.at_join_time

    @api.onchange('confirm_status')
    def onchange_confirm_sts(self):
        self.prob_compl_date = False

    """ Profile image URL to be created which will be sent while syncing """
    @api.model
    def _compute_image_id(self):
        for record in self:
            attachment_data = self.env['ir.attachment'].search(
                [('res_id', '=', record.id), ('res_model', '=', 'kwonboard_new_joinee'), ('res_field', '=', 'image')])
            attachment_data.write({'public': True})
            record.image_id = attachment_data.id

    @api.model
    def _get_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.image_id:
                final_url = '%s/web/image/%s' % (base_url, record.image_id)
                record.image_url = final_url
            else:
                record.image_url = ''

    def _compute_user_emp(self):
        for record in self:
            user = self.env['res.users'].search_count([('email', '=', record.email_id)])
            empl = self.env['hr.employee'].search_count([('work_email', '=', record.email_id)])
            record.user_count = user

    @api.onchange('enrollment_id')
    def onchange_enrollment_id(self):
        enrollment = self.env['kwonboard_enrollment'].search([('name', '=', self.enrollment_id.name)])
        self.fullname = enrollment.name
        self.dept_id = enrollment.dept_name
        self.division_id = enrollment.division
        self.section_id = enrollment.section
        self.practise_id = enrollment.practise
        self.designation = enrollment.job_id
        self.emp_role = enrollment.emp_role
        self.emp_category = enrollment.emp_category
        self.employ_type = enrollment.employement_type
        self.office_unit = enrollment.location_id
        self.dob = enrollment.birthday
        self.gender = enrollment.gender
        self.religion = enrollment.emp_religion
        self.email_id = enrollment.csm_email_id
        self.card_no = enrollment.id_card_no.id
        self.marital_stat = enrollment.marital
        self.marriage_date = enrollment.wedding_anniversary
        self.image = enrollment.image
        self.job_position = enrollment.job_id
        if enrollment.applicant_id:
            self.source_id = self.enrollment_id.applicant_id.source_id.id

    @api.onchange('source_id')
    def onchange_source(self):
        self.code_ref = self.source_id.code

    @api.onchange('marital_stat')
    def onchange_marital_stat(self):
        self.marital_ref = self.marital_stat.code

    @api.model
    def create(self, values):
        record = super(kwonboard_new_joinee, self).create(values)
        if record:
            self.env.user.notify_success(message='New Joinee has been Created Successfully.')
        return record

    @api.multi
    def write(self, values):
        self.ensure_one()
        record = super(kwonboard_new_joinee, self).write(values)
        self.env.user.notify_info(message='New Joinee has been Updated Successfully.')
        return record

    @api.multi
    def new_joinee_cancel(self):
        for rec in self:
            rec.write({'state': 'rejected'})
        return True

    def choose_user_type(self):
        form_view_id = self.env.ref("kw_onboarding.kwonboard_usertypesel_form_view").id
        return {
            'name':' Select User Type',
            'type': 'ir.actions.act_window',
            'res_model': 'kwonboard_new_joinee',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'domain': [('id', '=', self.id)]
        }

    """ This method executes when Create Employee button is clicked, 
        depending on selection user may/may not be created.
    """
    @api.multi
    def create_employee_user(self):
        emp_vals = {}
        user_vals = {}
        for rec in self:
            aadhar_num, passport_num = False, False
            for r in rec.enrollment_id.identification_ids:
                if r.name == '5':
                    aadhar_num = r.doc_number
                elif r.name == '2':
                    passport_num = r.doc_number
                else:
                    pass
            if rec.username != False or rec.email_id != False:
                user = self.env['res.users'].search(['|',('login','=', rec.username),('email','=', rec.email_id)])
                if user:
                    raise ValidationError(f"User {user.name} already exists!")

            """ User to be created if Create User is checked """
            if rec.need_user:
                user_vals['image'] = rec.image
                user_vals['name'] = rec.fullname
                user_vals['email'] = rec.email_id
                user_vals['login'] = rec.username
                user_vals['branch_id'] = rec.office_unit.id
                user_vals['new_joinee_id'] = rec.id

                new_user_rec = self.env["res.users"].sudo().create(user_vals)
                self.env.user.notify_success(message='Congrats ! User Creation completed.')

            """ Employee record to be created with all given details """
            emp = self.env['hr.employee'].search([('work_email', '=', rec.email_id)])
            if emp and rec.email_id != False:
                raise ValidationError(f"Employee {emp.name} already exists!")
            else:
                new_emp_rec = self.env["hr.employee"].sudo().create({
                    'base_branch_id': rec.office_unit.id,
                    'job_branch_id': rec.worklocation_id.id,
                    'work_email': rec.email_id,
                    'user_id' : new_user_rec.id if rec.need_user else False,
                    'image': rec.image,
                    'name': rec.fullname,
                    'department_id': rec.dept_id.id,
                    'division': rec.division_id.id,
                    'section': rec.section_id.id,
                    'practise': rec.practise_id.id,
                    'job_id': rec.designation.id,
                    'resource_calendar_id': rec.shift.id if rec.shift else rec.worklocation_id.default_shift_id.id,
                    'birthday': rec.dob,
                    'gender': rec.gender,
                    'marital_sts' : rec.marital_stat.id,
                    'domain_login_id': rec.domain_name,
                    'job_title': rec.designation.name,
                    'grade': rec.grade.id,
                    'emp_band': rec.band.id,
                    'date_of_joining': rec.join_date,
                    'date_of_completed_probation': rec.prob_compl_date,
                    'on_probation': rec.on_probation,
                    'emp_category' : rec.enrollment_id.emp_category.id,
                    'id_card_no' : rec.card_no.id,
                    'employement_type' : rec.enrollment_id.employement_type.id,
                    'emp_religion' : rec.religion.id,
                    'mother_tongue_id' : rec.enrollment_id.mother_tounge_ids.id,
                    'permanent_addr_city' : rec.enrollment_id.permanent_addr_city,
                    'parent_id' : rec.admin_auth.id,
                    'coach_id' :  rec.func_auth.id,
                    'blood_group' : rec.enrollment_id.blood_group.id,
                    'country_id' : rec.enrollment_id.country_id.id,
                    'emp_refered' : rec.source_id.id,
                    'present_addr_street' : rec.enrollment_id.present_addr_street,
                    'present_addr_street2' : rec.enrollment_id.present_addr_street2,
                    'present_addr_country_id' : rec.enrollment_id.present_addr_country_id.id,
                    'present_addr_city' : rec.enrollment_id.present_addr_city,
                    'present_addr_state_id' : rec.enrollment_id.present_addr_state_id.id,
                    'present_addr_zip' : rec.enrollment_id.present_addr_zip,
                    'same_address' : rec.enrollment_id.same_address,
                    'permanent_addr_street' : rec.enrollment_id.permanent_addr_street,
                    'permanent_addr_street2' : rec.enrollment_id.permanent_addr_street2,
                    'permanent_addr_country_id' : rec.enrollment_id.permanent_addr_country_id.id,
                    'permanent_addr_state_id' : rec.enrollment_id.permanent_addr_state_id.id,
                    'permanent_addr_zip' : rec.enrollment_id.permanent_addr_zip,
                    'biometric_id' : rec.enrollment_id.biometric_id ,
                    'epbx_no': rec.enrollment_id.epbx_no,
                    'domain_login_pwd': rec.enrollment_id.domain_login_pwd,
                    'outlook_pwd': rec.enrollment_id.outlook_pwd,
                    'mobile_phone': rec.enrollment_id.mobile,
                    'emp_role' : rec.enrollment_id.emp_role.id,
                    'experience_sts': '2', # to be sent experience as default -- Abhijit 
                    'basic_at_join_time': rec.basic_at_join_time,
                    'medical_reimb': rec.medical_reimb,
                    'transport': rec.transport,
                    'productivity': rec.productivity,
                    'commitment': rec.commitment,
                    'enable_payroll': rec.enable_payroll,
                    'enable_epf': rec.enable_epf,
                    'enable_gratuity': rec.enable_gratuity,
                    'current_ctc': rec.current,
                    'at_join_time_ctc': rec.at_join_time,
                    'whatsapp_no': rec.enrollment_id.whatsapp_no,
                    'emergency_contact': rec.enrollment_id.emgr_contact,
                    'emergency_phone': rec.enrollment_id.emgr_phone,
                    'known_language_ids': [[0, 0, {
                            'language_id': r.language_id.id,
                            'reading_status': r.reading_status,
                            'writing_status': r.writing_status,
                            'speaking_status': r.speaking_status,
                            'understanding_status': r.understanding_status,
                        }] for r in rec.enrollment_id.known_language_ids],
                    'identification_ids': [[0,0,{
                        'name': r.name,
                        'doc_number': r.doc_number,
                        'date_of_issue': r.date_of_issue,
                        'date_of_expiry': r.date_of_expiry,
                        'renewal_sts': r.renewal_sts,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                            }]for r in rec.enrollment_id.identification_ids],
                    'educational_details_ids': [[0, 0, {
                        'course_type': r.course_type,
                        'course_id': r.course_id.id,
                        'stream_id': r.stream_id.id,
                        'university_name': r.university_name.id,
                        'passing_year': str(r.passing_year),
                        'division': r.division,
                        'marks_obtained': r.marks_obtained,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                        'passing_details': [(6, 0, r.passing_details.ids)],
                        }] for r in rec.enrollment_id.educational_ids],
                    'work_experience_ids': [[0, 0, {
                        'country_id': r.country_id.id,
                        'name': r.name,
                        'designation_name': r.designation_name,
                        'organization_type': r.organization_type.id,
                        'industry_type': r.industry_type.id,
                        'effective_from': r.effective_from,
                        'effective_to': r.effective_to,
                        'uploaded_doc': r.uploaded_doc,
                        'doc_file_name': r.filename,
                        }] for r in rec.enrollment_id.work_experience_ids],
                    'identification_id': aadhar_num,
                    'passport_id': passport_num,
                    'personal_email': rec.enrollment_id.email,
                    'no_attendance': True if rec.enable_attendance == 'no' else False,
                    'attendance_mode_ids': [(6,0,rec.atten_mode_ids.mapped('id'))] if rec.enable_attendance == 'yes' else False,
                    'wedding_anniversary': rec.marriage_date,
                    'bank_account': rec.bank_account,
                    'bankaccount_id': rec.bank_id.id,
                    'image_url': rec.image_url,
                    'location': rec.location,
                    'workstation_id': rec.work_station_id.id,
                    'emp_project_id': rec.project_id.id if rec.project_id else False,
                    'client_location': rec.client_location if rec.client_location else False,
                    'start_date': rec.start_dt if rec.start_dt else False,
                    'end_date': rec.end_dt if rec.end_dt else False,
                    'direct_indirect': rec.direct_indirect,
                    'hra': rec.hra,
                    'conveyance': rec.conveyance,
                    'current_basic': rec.current_basic,
                    'need_sync': False if rec.need_sync == False else True,
                    'infra_id': rec.infra_id.id if rec.infra_id else False,
                    'will_travel': rec.enrollment_id.will_travel,
                    'travel_abroad': rec.enrollment_id.travel_abroad,
                    'travel_domestic': rec.enrollment_id.travel_domestic,
                    })
                self.env.user.notify_success(message='Congrats ! Employee Creation completed.')
            """ Create bank account record in res.partner.bank """
            if rec.bank_account != False:
                bank_vals = {}
                bank = self.env['res.partner.bank'].sudo()
                bank_vals['acc_number'] = rec.bank_account
                bank_vals['bank_id'] = rec.bank_id.id
                bank_vals['partner_id'] = new_user_rec.partner_id.id

                bank.create(bank_vals)

            """ Create Post Onboarding Checklist """
            if rec.direct_indirect != '2':
                post_rec = self.env['kw_employee_onboarding_checklist'].sudo()
                post_rec_vals = {}

                post_rec_vals['employee_id'] = new_emp_rec.id
                post_rec_vals['image'] = rec.image
                post_rec_vals['designation_id'] = rec.designation.id
                post_rec_vals['pf'] = rec.enable_epf if rec.enable_payroll == 'yes' else 'no'
                post_rec_vals['gratuity'] = rec.enable_gratuity if rec.enable_payroll == 'yes' else 'no'
                post_rec_vals['email_id_creation'] = 'yes' if rec.enrollment_id.csm_email_id else 'no'
                post_rec_vals['telephone_extention'] = 'yes' if rec.enrollment_id.epbx_no else 'no'
                post_rec_vals['id_card'] = 'no'  # 'yes' if rec.card_no.id else 'no' '''to be sent always as no Pratima'''
                post_rec_vals['location'] = rec.location
                post_rec_vals['work_station'] = 'yes'
                post_rec_vals['client_loc_id'] = rec.client_loc_id.id if rec.location == 'onsite' else False
                post_rec_vals['workstation_id'] = rec.work_station_id.id if rec.location == 'offsite' else False
                post_rec_vals['infra_id'] = rec.infra_id.id if rec.location == 'offsite' else False
                post_rec_vals['client_location'] = rec.client_location
                post_rec_vals['kw_id_generation'] = 'yes' if rec.need_sync == True else 'no'
                post_rec_vals['kw_profile_update'] = 'yes'

                post_rec.create(post_rec_vals)

            rec.write({'state': 'authenticated'})
        return True