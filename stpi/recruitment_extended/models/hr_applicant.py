from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ApplicantNationality(models.Model):
    _name = "applicant.nationality"
    _description = "Applicant Nationality"

    name = fields.Char("Nationality")
class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.model
    def get_default_nationality(self):
        return self.env['applicant.nationality'].search([('name','in',['Indian','indian'])],limit=1)

    date_of_birth = fields.Date('Date Of Birth')
    place_of_birth = fields.Char('Place Of Birth')

    achievements = fields.Text("Achievements")

    nationality = fields.Many2one('applicant.nationality',"Nationality",default=get_default_nationality)
    nationality_upload = fields.Binary('Upload(Nationality)', track_visibility='always')
    nationality_upload_filename = fields.Char('Upload(Nationality) Filename')
    nationality_upload_attachment_id = fields.Many2one('ir.attachment', compute='_compute_nationality_upload_attachment_id', string="Nationality Document Attachment")

    additional_information = fields.Text("Additional Information")
    penalty_last_10_year =  fields.Selection(selection=[("yes","Yes"),("no","No")],string="Any penalty awarded during the last 10 years")
    inquiry_going_on = fields.Selection(selection=[("yes","Yes"),("no","No")],string="Any action or inquiry is going on as far as candidate's knowledge")
    criminal_case_pending = fields.Selection(selection=[("yes","Yes"),("no","No")],string="Any criminal/ vigilance case is pending or contemplated")
    relative_ccs = fields.Selection(selection=[("yes","Yes"),("no","No")],string="Any relative defined in terms of CCS")
    relative_ccs_name = fields.Char(string="Relative Name")

    applicable_fee = fields.Selection(selection=[("Yes","Yes"),("No","No")],string="Fees Applicable ?")
    fees_amount = fields.Float("Fees Amount")

    payment_document = fields.Binary(string="Payment Document",attachment=True)
    payment_filename = fields.Char(string="Payment Filename")
    payment_document_attachment_id = fields.Many2one('ir.attachment',compute='_compute_payment_attachment_id', string="Payment Attachment")
    payment_details = fields.Text("Payment Details")

    signature = fields.Binary(string="Signature",attachment=True)
    signature_attachment_id = fields.Many2one('ir.attachment',compute='_compute_signature_attachment_id', string="Signature Attachment")
    signature_filename = fields.Char(string="Signature Filename")

    other_doc = fields.Binary("Other Document", attachment=True)
    other_doc_file_name = fields.Char("Other Document Filename") 
    other_doc_attachment_id = fields.Many2one('ir.attachment',compute='_compute_other_document_attachment_id', string="Other Document Attachment")

    dob_doc = fields.Binary("Date Of Birth Document", attachment=True)
    dob_doc_file_name = fields.Char("Date Of Birth Document Filename") 
    dob_doc_attachment_id = fields.Many2one('ir.attachment',compute='_compute_dob_document_attachment_id', string="Date Of Birth Document Attachment")

    def _compute_nationality_upload_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'nationality_upload')])
            applicant.nationality_upload_attachment_id = attachment_id
    
    def _compute_dob_document_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'dob_doc')])
            applicant.dob_doc_attachment_id = attachment_id

    def _compute_other_document_attachment_id(self):
        for applicant in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', applicant.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'other_doc')])
            applicant.other_doc_attachment_id = attachment_id

    def _compute_payment_attachment_id(self):
        for payment in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', payment.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'payment_document')])
            payment.payment_document_attachment_id = attachment_id

    def _compute_signature_attachment_id(self):
        for signature in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', signature.id), ('res_model', '=', 'hr.applicant'), ('res_field', '=', 'signature')])
            signature.signature_attachment_id = attachment_id

class ApplicantEducation(models.Model):
    _inherit = 'applicant.education'

    degree = fields.Char(string='Degree')
    is_high = fields.Boolean(string='Is Higher Education ?')
    certificate = fields.Binary(string="Document", attachment=True)
    attachment_id = fields.Many2one('ir.attachment',compute='_compute_attachment_id', string="Attachments")
    file_name = fields.Char('File Name')

    def _compute_attachment_id(self):
        for education in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', education.id), ('res_model', '=', 'applicant.education'), ('res_field', '=', 'certificate')])
            education.attachment_id = attachment_id

class ApplicantEducation(models.Model):
    _inherit = 'applicant.previous.occupation'

    document = fields.Binary(string="Document", attachment=True)
    attachment_id = fields.Many2one('ir.attachment',compute='_compute_attachment_id', string="Attachments")
    file_name = fields.Char('File Name')

    def _compute_attachment_id(self):
        for experience in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', experience.id), ('res_model', '=', 'applicant.previous.occupation'), ('res_field', '=', 'document')])
            experience.attachment_id = attachment_id