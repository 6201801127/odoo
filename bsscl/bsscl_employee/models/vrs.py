from odoo import models, fields,api,_
from datetime import date,datetime,timedelta
from odoo.exceptions import ValidationError
import re
from odoo.tools.mimetypes import guess_mimetype
import base64



class BssclVRS(models.Model):
    _name = 'bsscl.vrs'
    _description = 'Bsscl Vrs'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    def get_employee(self):
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            return employee

    employee_id = fields.Many2one('hr.employee', 'Employee / कर्मचारी', ondelete='cascade' ,default=get_employee,readonly=True)
   
    department_id = fields.Char(related="employee_id.department_id.name",string="Department (विभाग)", store=True)
    job_id  = fields.Char(related="employee_id.job_id.name",string="Designation (पद)", store=True)
    status  = fields.Selection([('draft', 'Draft'),('applied', 'Applied'),('approved', 'Validate'),('confirm', 'Confirm'),('reject', 'Reject')],string="Status / स्थति",default='draft',tracking=True)
    # joining_date  = fields.Date("Service Date / सेवा की तारीख")
    joining_date  = fields.Date(related="employee_id.transfer_date",string="Service Date / सेवा की तारीख")
    vrs_date  = fields.Date("Voluntary Retirement  Date / स्वैच्छिक सेवानिवृत्ति तिथि")
    description  = fields.Text("Description / विवरण")
    is_deputy_cc  = fields.Boolean()
    applied_on = fields.Date("Applied On / आवेदन तिथि",readonly=True ,tracking=True)
    dcc_comment = fields.Text('DC Remark (टिप्पणी)',tracking=True)
    cc_comment = fields.Text('Manager Remark (टिप्पणी)',tracking=True)
    cc_reject_remark = fields.Text('Manager Reject Remark (टिप्पणी)',tracking=True)
    check_user = fields.Boolean(compute="_check_user")
    # check_dc = fields.Boolean(compute="_check_user")
    # check_cc = fields.Boolean(compute="_check_user")

    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
            else:
                record.check_user = False
            # if self.env.user.has_group('bsscl_employee.deputy_com_id'):
            #         record.check_dc = True
            # else:
            #     record.check_dc = False
            # if self.env.user.has_group('bsscl_employee.commissioner_id'):
            #     record.check_cc = True
            # else:
            #     record.check_cc = False

    @api.constrains('joining_date')
    @api.onchange('joining_date')
    def _check_joining_date(self):
        for rec in self:
            today=datetime.now().date()
            print("today today", today, rec.joining_date)
            if rec.joining_date:
                if rec.joining_date > today:
                    raise ValidationError(_('Your Service date can not be a future date.'))
                
    @api.constrains('vrs_date')
    # @api.onchange('vrs_date')
    def _check_vrs_date(self):
        for rec in self:
            year_of_joining = rec.joining_date.strftime("%Y")
            mon_of_joining = rec.joining_date.strftime("%m")
            day_of_joining = rec.joining_date.strftime("%d")
            # print("date---- of joining------------------",day_of_joining,mon_of_joining,year_of_joining)

            year_of_vrs = rec.vrs_date.strftime("%Y")
            mon_of_vrs = rec.vrs_date.strftime("%m")
            day_of_vrs = rec.vrs_date.strftime("%d")
            # print("date---- of vrs------------------",day_of_vrs,mon_of_vrs,year_of_vrs)

            between_date = int(year_of_vrs) - int(year_of_joining)
            today=datetime.now().date()
            print("today today", today, rec.joining_date)
            if rec.vrs_date:
                if rec.vrs_date < today :
                    raise ValidationError(_('Your Voluntary Retirement date should not be less than  Current date.'))
            if between_date >= 0:
                # print("hhhhhhhhhhhheeeeeeeeeeelllllllooooooooooooooo")
                if between_date < 10:
                    raise ValidationError(_('Your Voluntary Retirement date should not be less than 10 years of Service date.')) 
                if between_date == 10:
                    if mon_of_vrs < mon_of_joining or day_of_vrs < day_of_joining:
                        raise ValidationError(_('Your Voluntary Retirement date should not be less than 10 years of Service date.')) 

    def apply_vrs(self):
        self.applied_on = datetime.today()

        self.status = 'applied'
       
                       
    # def approve_vrs(self):
    #     if not self.dcc_comment:
    #         raise ValidationError("Deputy Commisioner Remark is Required")
    #     else:
    #         self.status = 'approved'


    def reject_vrs(self):
        if not self.cc_reject_remark:
            raise ValidationError("Manager Reject Remarks is Required")
        self.status = 'reject'

    def confirm_vrs(self):
        if not self.cc_comment:
            raise ValidationError("Manager Remark is Required")
        else:
            self.status = 'confirm'

    @api.constrains('description')
    @api.onchange('description')	
    def _onchange_description(self):
        for rec in self:
            if rec.description and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.description)):
                raise ValidationError("Description should be an alphabet")
            if rec.description:
                if len(rec.description) > 500:
                    raise ValidationError('Number of characters must not exceed 500')






class ChangeRequest(models.Model):
    _name = 'change.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Change Request By Officers'
    _rec_name = 'employee_id'

    def get_employee(self):
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            return employee

    employee_id = fields.Many2one('hr.employee', 'Employee / कर्मचारी', ondelete='cascade' ,default=get_employee,readonly=True)
    department_id = fields.Many2one('hr.department',string="Department (विभाग)", track_visibility='onchange')
    job_id  = fields.Many2one('hr.job',string="Designation (पद)",track_visibility='onchange')
    status  = fields.Selection([('draft', 'Draft'),('applied', 'Applied'),('approved', 'Approved'),('confirm', 'Approved'),('reject', 'Reject')],string="Status / स्थति",default='draft',tracking=True)
   
    description  = fields.Text("Description / विवरण")
    applied_on = fields.Date("Applied On / आवेदन तिथि", default=date.today(),readonly=True)
   
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address', help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user")
   
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', 
        groups="hr.group_hr_user", track_visibility='onchange')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", default="male")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single')
    spouse_complete_name = fields.Char(string="Spouse Complete Name", groups="hr.group_hr_user")
    spouse_birthdate = fields.Date(string="Spouse Birthdate", groups="hr.group_hr_user")
    children = fields.Integer(string='Number of Children', groups="hr.group_hr_user")
    place_of_birth = fields.Char('Place of Birth', groups="hr.group_hr_user")
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user")
    ssnid = fields.Char('SSN No', help='Social Security Number', groups="hr.group_hr_user")
    sinid = fields.Char('SIN No', help='Social Insurance Number', groups="hr.group_hr_user")
    identification_id = fields.Char(string='Identification No', groups="hr.group_hr_user")
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user")
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]",
        groups="hr.group_hr_user",
        help='Employee bank salary account')
    permit_no = fields.Char('Work Permit No', groups="hr.group_hr_user")
    visa_no = fields.Char('Visa No', groups="hr.group_hr_user")
    visa_expire = fields.Date('Visa Expire Date', groups="hr.group_hr_user")
    additional_note = fields.Text(string='Additional Note', groups="hr.group_hr_user")
    certificate = fields.Selection([
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('other', 'Other'),
    ], 'Certificate Level', default='master', groups="hr.group_hr_user")
    study_field = fields.Char("Field of Study", placeholder='Computer Science', groups="hr.group_hr_user")
    study_school = fields.Char("School", groups="hr.group_hr_user")
    emergency_contact = fields.Char("Emergency Contact", groups="hr.group_hr_user")
    emergency_phone = fields.Char("Emergency Phone", groups="hr.group_hr_user")
    km_home_work = fields.Integer(string="Km home-work", groups="hr.group_hr_user")
    google_drive_link = fields.Char(string="Employee Documents", groups="hr.group_hr_user")
    job_title = fields.Char("Job Title")
    check_user = fields.Boolean(compute="_check_user")

   
    address_id = fields.Many2one(
        'res.partner', 'Work Address')
    work_phone = fields.Char('Work Phone',track_visibility='always')
    mobile_phone = fields.Char('Work Mobile', track_visibility='always')
    work_email = fields.Char('Work Email',track_visibility='always')
    work_location = fields.Char('Work Location',track_visibility='always')
    
    parent_id = fields.Many2one('hr.employee', 'Manager', track_visibility='always')
    child_ids = fields.One2many('hr.employee', 'parent_id', string='Subordinates')
    coach_id = fields.Many2one('hr.employee', 'Coach')
    
    identify_id = fields.Char(string='Identification No.',copy=False, store=True, track_visibility='always')
    pan_no = fields.Char('PAN Card No.',track_visibility='always')
    uan_no = fields.Char('UAN No.',track_visibility='always')
    pan_upload = fields.Binary('Upload(PAN)',track_visibility='always',attachment=True)
    pan_upload_filename = fields.Char('Upload(PAN) Filename / ')
    aadhar_no = fields.Char('Aadhaar Card No.',track_visibility='always')
    aadhar_upload = fields.Binary('Upload(Aadhaar)',track_visibility='always',attachment=True)
    aadhar_upload_filename = fields.Char('Upload(Aadhaar) Filename')
    passport_upload = fields.Binary('Upload(Passport)',track_visibility='always',attachment=True)
    passport_upload_filename = fields.Char('Upload(Passport) Filename')
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account number')
    ifsc_code = fields.Char(string='IFSC Code')
    image_name = fields.Char(string=u'Image Name', )

    height = fields.Float('Height (in CMs)',track_visibility='always')
    weight = fields.Float('Weight (in KGs)',track_visibility='always')
    blood_group = fields.Selection([('a+','A+'),
                                    ('a1+','A1+'),
                                     ('a-','A-'),
                                     ('b+','B+'),
                                     ('b-','B-'),
                                     ('o+', 'O+'),
                                     ('o-', 'O-'),
                                     ('ab+','AB+'),
                                     ('ab-','AB-')],string='Blood Group',track_visibility='always')
    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_bsscl', 'Contractual with BSSCL')], string='Employment Type',
                                      tracking=True, store=True)
    remarks = fields.Text('Remarks')
    reason = fields.Char('Reason for cancellation/Rejection')

    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
                print("++++++++++++++++++++++")
            else:
                record.check_user = False
                print("check user not=====================")

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            self.job_id =  self.employee_id.job_id.id
            self.country_id = self.employee_id.country_id.id
            self.aadhar_no = self.employee_id.aadhar_no

    @api.constrains('work_email')
    @api.onchange('work_email')
    def _check_work_email (self):
        for rec in self:
            if rec.work_email:
                match=re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,7})$',rec.work_email)
                if match==None:
                    raise ValidationError(_("Please enter correct Work Email.../ कृपया सही कार्य ईमेल दर्ज करें..."))
            
    @api.constrains('mobile_phone')
    @api.onchange('mobile_phone')
    def _check_mobile_phone (self):
        Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
        for rec in self:
            if rec.mobile_phone:
                if not Pattern.match(rec.mobile_phone):
                    raise ValidationError(_("Please enter correct Phone Number, it must be start from 6 to 9.../ ..."))
                for e in rec.mobile_phone:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter Phone Number, it must be numeric.../ ..."))
                if len(rec.mobile_phone)!=10:
                    raise ValidationError(_("Please enter Phone number, it must be of 10 digits.../..."))
                for k in rec.mobile_phone:
                    my_count = rec.mobile_phone.count(k)
                    if my_count > 7:
                        raise ValidationError(_("Number repetition should not be more than 7"))



    #********** (Aadhar Validation for change request form)************#
    @api.constrains('aadhar_no')
    @api.onchange('aadhar_no')
    def _onchange_aadhar_no(self):
        if self.aadhar_no:
            for e in self.aadhar_no:
                if not e.isdigit():
                    raise ValidationError(
                        _("Please enter correct Aadhar number, it must be numeric.../ कृपया सही आधार संख्या दर्ज करें, यह संख्यात्मक होना चाहिए..."))
            if len(self.aadhar_no)!=12:
                raise ValidationError(
                    _("Please enter correct Aadhar number, it must be of 12 digits.../ कृपया सही आधार संख्या दर्ज करें, यह संख्यात्मक होना चाहिए..."))
           
    @api.constrains('aadhar_upload')
    @api.onchange('aadhar_upload')
    def _onchange_aadhar_upload_aadhar(self):
            allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            for rec in self:
                if rec.aadhar_no:
                    if not rec.aadhar_upload:
                        raise ValidationError("Please upload your Aadhar / कृपया अपना आधार अपलोड करें")
                if rec.aadhar_upload:
                    acp_size = ((len(rec.aadhar_upload) *3/4) /1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(rec.aadhar_upload))        
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only .jpeg, .jpg, .png, .pdf, .doc, .docx format are allowed.")
                    if acp_size > 2:
                        raise ValidationError("Maximum file size is 2 MB / अधिकतम फ़ाइल आकार 2 एमबी है")
                

    

    def apply_change(self):
        self.applied_on = datetime.today()
        self.status = 'applied'
        return {
                'name': 'Change Request',
                'view_mode': 'tree',
                'res_model': 'change.request',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('bsscl_employee.view_change_request_tree').id,
                'domain': [('status','=','applied')],
                }
    

       
                       
    # def approve_change(self):
    #     self.status = 'approved'
    #     return {
    #             'name': 'Change Request',
    #             'view_mode': 'tree',
    #             'res_model': 'change.request',
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #             'view_id': self.env.ref('bsscl_employee.view_change_request_tree').id,
    #             'domain': [('status','=','applied')],
    #             }


    # def reject_change(self):
    #     if not self.reason:
    #         raise ValidationError(_("Please enter reason for rejection."))
    #     self.status = 'reject'
    #     return {
    #             'name': 'Change Request',
    #             'view_mode': 'tree',
    #             'res_model': 'change.request',
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #             'view_id': self.env.ref('bsscl_employee.view_change_request_tree').id,
    #             'domain': [('status','=','approved')],
    #             }

    def confirm_change(self):
        if not self.remarks:
            raise ValidationError("Please Fill Manager Remark")
        self.status = 'confirm'
        request_emp = self.env['hr.employee'].sudo().search([('id','=',self.employee_id.id)],limit=1)
        print("-----------------------------",request_emp,self.employee_id.id)
        for rec in request_emp:
            if self.department_id:
                rec.department_id = self.department_id.id
            if self.job_id:
                rec.job_id = self.job_id.id
            if self.work_email:
                rec.work_email = self.work_email
            if self.employee_type:
                rec.employee_type = self.employee_type
            if self.work_location:
                rec.work_location = self.work_location
            if self.mobile_phone:
                rec.mobile_phone = self.mobile_phone

            # if self.place_of_birth:
            #     rec.place_of_birth = self.place_of_birth
            # else:
            #     rec.place_of_birth
            if self.country_id.id:
                rec.country_id = self.country_id.id
            else:
                rec.country_id
            # if self.gender:
            #     rec.gende = self.gender
            # else:
            #     rec.gende
            # if self.bank_account_id.id:
            #     rec.bank_account_id = self.bank_account_id.id
            # else:
            #     rec.bank_account_id
            
            # if self.emergency_contact:
            #     rec.emergency_contact = self.emergency_contact
            # else:
            #     rec.emergency_contact
            # if self.emergency_phone:
            #     rec.emergency_phone = self.emergency_phone
            # else:
            #     rec.emergency_phone
            # if self.pan_no:
            #     rec.pan_no = self.pan_no
            # else:
            #     rec.pan_no

            # if self.uan_no:
            #     rec.uan_no = self.uan_no
            # else:
            #     rec.uan_no

            # if self.pan_upload:
            #     rec.pan_upload = self.pan_upload
            # else:
            #     rec.pan_upload
            # if self.pan_upload_filename:
            #     rec.pan_upload_filename = self.pan_upload_filename
            # else:
            #     rec.pan_upload_filename
            if self.aadhar_no:
                rec.aadhar_no = self.aadhar_no
            else:
                rec.aadhar_no
            if self.aadhar_upload:
                rec.aadhar_upload = self.aadhar_upload
            else:
                rec.aadhar_upload
            if self.aadhar_upload_filename:
                rec.aadhar_upload_filename = self.aadhar_upload_filename
            else:
                rec.aadhar_upload_filename

            # if self.passport_upload:
            #     rec.passport_upload = self.passport_upload
            # else:
            #     rec.passport_upload

            # if self.birthday:
            #     rec.birthday = self.birthday
            # else:
            #     rec.birthday
            # if self.passport_upload_filename:
            #     rec.passport_upload_filename = self.passport_upload_filename
            # else:
            #     rec.passport_upload_filename
            # if self.height:
            #     rec.height = self.height
            # else:
            #     rec.height
            # if self.weight:
            #     rec.weight = self.weight
            # else:
            #     rec.weight

            # if self.blood_group:
            #     rec.blood_group = self.blood_group
            # else:
            #     rec.blood_group
          
            # if self.certificate:
            #     rec.certificate = self.certificate
            # else:
            #     rec.certificate
            # if self.study_field:
            #     rec.study_field = self.study_field
            # else:
            #     rec.study_field
            # if self.blood_group:
            #     rec.study_school = self.study_school
            # else:
            #     rec.study_school
        return {
                'name': 'Change Request',
                'view_mode': 'tree',
                'res_model': 'change.request',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('bsscl_employee.view_change_request_tree').id,
                'domain': [('status','=','approved')],
                }

class LegalIssue(models.Model):
    _name='legal.issue'
    _inherit=['mail.thread','mail.activity.mixin']
    _description='Legal Issue'
    _rec_name='employee_id'

    def get_employee (self):
        employee=self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id)],limit=1)
        return employee

    employee_id=fields.Many2one('hr.employee','Employee / कर्मचारी',ondelete='cascade',default=get_employee,
        readonly=True)
    description = fields.Text("Description")
    
    #***Description validation(Only alphabets and space allowed also description start with alphabets not number, space and special char )****
    @api.constrains('description')
    @api.onchange('description')
    def _onchnage_description(self):
        if self.description and re.match(r'^[\s]*$', str(self.description)):
            raise ValidationError("Description only start with alphabets not space, number and special characters")
        if self.description and not re.match(r'^[A-Za-z ]*$',str(self.description)):
            raise ValidationError("Description only alphabets and space")