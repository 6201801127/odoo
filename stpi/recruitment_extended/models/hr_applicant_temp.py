from datetime import datetime
from odoo import api, fields, models

class HrApplicantTemp(models.Model):
    _name = "hr_applicant_temp"
    _description = 'Hr Recruitment'

    # Personal Details Start
    image = fields.Binary(string="Applicant Image")
    salutation = fields.Many2one('res.partner.title', string="Salutaion")
    partner_first_name = fields.Char(string="First Name")
    partner_middle_name = fields.Char(string="Middle Name")
    partner_last_name = fields.Char(string="Last Name")
    father_name = fields.Char(string="Father Name")
    mother_name = fields.Char(string="Mother Name")
    email = fields.Char(string='Email')
    mobile = fields.Char(string='Mobile')
    phone_with_area_code = fields.Char(string='Phone with Area Code')

    aadhar = fields.Char(string='Aadhar Card No.')
    aadhar_upload = fields.Binary('Upload(Aadhar)', track_visibility='always')
    aadhar_upload_filename = fields.Char('Upload(Aadhar) Filename')
    aadhar_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_aadhar_upload_attachment_id', string="Aadhar Document Attachment")

    pan = fields.Char(string='PAN Card No.')
    pan_upload = fields.Binary('Upload(PAN)', track_visibility='always')
    pan_upload_filename = fields.Char('Upload(PAN) Filename')
    pan_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_pan_upload_attachment_id', string="PAN Document Attachment")

    dob = fields.Date(string='Date Of Birth')
    gender = fields.Selection(selection=[('male','Male'),('female','Female'),('transgender','Transgender')])

    nationality = fields.Many2one('applicant.nationality',string="Nationality")
    nationality_upload = fields.Binary('Upload(Nationality)', track_visibility='always')
    nationality_upload_filename = fields.Char('Upload(Nationality) Filename')
    nationality_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_nationality_upload_attachment_id', string="Nationality Document Attachment")

    category_id = fields.Many2one('employee.category',string="Category")
    # nationality = fields.Char(string="Nationality")
    religion = fields.Many2one('employee.religion',string="Religion")
    ex_serviceman = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Whether Ex-Serviceman")
    govt_employee = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Are you a Government Employee")
    physically_handicapped = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Differently Abled?")
    kind_of_disability = fields.Selection(
        [
            ('vh', 'Visually Handicapped'),
            ('hh', 'Hearing Handicapped'),
            ('ph', 'Physically Handicapped')
        ], string='Kind of Disability', track_visibility='always')
    perc_disability = fields.Char('% of Disability', track_visibility='always')
    certificate_upload = fields.Binary('Upload certificate', track_visibility='always')
    certificate_upload_filename = fields.Char('Upload certificate Filename')
    certificate_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_certificate_upload_attachment_id', string="Upload certificate Attachment")


    # Personal Details End

    #Communication Address Start
    address_ids = fields.One2many('communication_address_temp','hra_id',string='Communication Address')
    #Communication Address End

    #Educational Details Start
    education_ids = fields.One2many('educational_history_temp','hra_id',string='Educational Qualification')
    #Educational Details End

    #Employment Details Start
    experience_ids = fields.One2many('experience_temp','hra_id',string='Employment Details')
    #Employment Details End
 
    addition_information = fields.Text(string="Additional Information")
    achievements = fields.Text(string="Achievements")

    #Information on Vigilance and Discipline Start
    penalty = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Any penalty awarded during the last 10 years")
    action_inquiry = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Any action or inquiry is going on as far as candidate's knowledge")
    criminal = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Any criminal/ vigilance case is pending or contemplated")
    relative_ccs = fields.Selection(selection=[('yes','Yes'),('no','No')], string="Any relative defined in terms of CCS")
    relative_ccs_name = fields.Char(string="Relative Name")
    #Information on Vigilance and Discipline End

    payment_document = fields.Binary("Payment Document", attachment=True)
    payment_document_file_name = fields.Char("Payment Document Filename")
    payment_document_attachment_id = fields.Many2one('ir.attachment',compute='_compute_payment_document_attachment_id', string="Payment")

    signature_document = fields.Binary("Signature Document")
    signature_document_file_name = fields.Char("Signature Document Filename")
    signature_document_attachment_id = fields.Many2one('ir.attachment',compute='_compute_signature_document_attachment_id', string="Signature")

    other_doc = fields.Binary("Other Document", attachment=True)
    other_doc_file_name = fields.Char("Other Document Filename") 
    other_doc_attachment_id = fields.Many2one('ir.attachment',compute='_compute_other_document_attachment_id', string="Other Document Attachment")

    dob_doc = fields.Binary("Date Of Birth Document", attachment=True)
    dob_doc_file_name = fields.Char("Date Of Birth Document Filename") 
    dob_doc_attachment_id = fields.Many2one('ir.attachment',compute='_compute_dob_document_attachment_id', string="Date Of Birth Document Attachment")

    payment_details = fields.Text(string="Payment Details")

    state = fields.Selection(selection=[('draft','Draft'),('submit','Submitted')])
    otp = fields.Char("OTP")

    def _compute_certificate_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'certificate_upload')])
            applicant.certificate_upload_attachment_id = attachment_id

    def _compute_nationality_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'nationality_upload')])
            applicant.nationality_upload_attachment_id = attachment_id

    def _compute_pan_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'pan_upload')])
            applicant.pan_upload_attachment_id = attachment_id

    def _compute_aadhar_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'aadhar_upload')])
            applicant.aadhar_upload_attachment_id = attachment_id

    def _compute_payment_document_attachment_id(self):
        for payment in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', payment.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'payment_document')])
            payment.payment_document_attachment_id = attachment_id

    def _compute_signature_document_attachment_id(self):
        for signature in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', signature.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'signature_document')])
            signature.signature_document_attachment_id = attachment_id

    def _compute_other_document_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'other_doc')])
            applicant.other_doc_attachment_id = attachment_id

    def _compute_dob_document_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr_applicant_temp'), ('res_field', '=', 'dob_doc')])
            applicant.dob_doc_attachment_id = attachment_id

class CommunicationAddressTemp(models.Model):
    _name = "communication_address_temp"
    _description = "Communication Address"

    hra_id = fields.Many2one('hr_applicant_temp',string='Applicant Id',ondelete='cascade')
    address_type = fields.Selection(selection=[('present_add','Present'),('permanent_add','Permanent'),('communication_add','Communication')])
    street = fields.Char(string="Address 1")
    street2 = fields.Char(string="Address 2")
    city_id = fields.Many2one('res.city',string="City/District")
    state_id = fields.Many2one('res.country.state',string="State")
    country_id = fields.Many2one('res.country',string="State")
    zip = fields.Char('Pincode')

class EducationalHistoryTemp(models.Model):
    _name = "educational_history_temp"
    _description = 'Education History Temp'

    hra_id = fields.Many2one('hr_applicant_temp',string='Applicant Id',ondelete='cascade')
    grade = fields.Char('Education Field/Major')
    field = fields.Char(string='Major/Field of Education', size=128)
    stream = fields.Char("Stream")
    school_name = fields.Char(string='School Name', size=256)
    passing_year = fields.Integer("Passing Year")
    percentage = fields.Float("Percentage")
    certificate = fields.Binary("Certificate", attachment=True)
    file_name = fields.Char("File Name")
    attachment_id = fields.Many2one('ir.attachment',compute='_compute_attachment_id', string="Attachments")

    def _compute_attachment_id(self):
        for education in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', education.id), ('res_model', '=', 'educational_history_temp'), ('res_field', '=', 'certificate')])
            education.attachment_id = attachment_id

class ExperienceTemp(models.Model):
    _name = "experience_temp"
    _description = 'Experience Temp'

    hra_id = fields.Many2one('hr_applicant_temp',string='Applicant Id',ondelete='cascade')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    organization = fields.Char(string="Employer's Name and Address")
    position = fields.Char(string='Position Held')
    job_description = fields.Char(string='Job Description')
    pay_scale = fields.Char(string='Pay Scale')
    document = fields.Binary("Certificate", attachment=True)
    file_name = fields.Char("File Name")
    attachment_id = fields.Many2one('ir.attachment',compute='_compute_attachment_id', string="Attachments")

    def _compute_attachment_id(self):
        for experience in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', experience.id), ('res_model', '=', 'experience_temp'), ('res_field', '=', 'document')])
            experience.attachment_id = attachment_id
