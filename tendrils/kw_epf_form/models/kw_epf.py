import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class kw_epf(models.Model):
    _name = 'kw_epf'
    _description = "Kwantify EPF"
    _rec_name = "employee_id"
    _order = 'id desc'

    @api.onchange('employee_id')
    def _compute_data(self):
        for rec in self:
            if rec.employee_id:
                if rec.employee_id.date_of_joining:
                    rec.date_of_joining = rec.employee_id.date_of_joining
                if rec.employee_id.bankaccount_id:
                    rec.bank = rec.employee_id.bankaccount_id.name
                if rec.employee_id.bank_account:
                    rec.bank_account = rec.employee_id.bank_account
                if rec.employee_id.grade:
                    rec.grade = rec.employee_id.grade
                if rec.employee_id.emp_band:
                    rec.band = rec.employee_id.emp_band
                if rec.employee_id.identification_ids:
                    for record in rec.employee_id.identification_ids:
                        if record.name == '5':
                            rec.aadhaar_no = record.doc_number
                            rec.upload_doc = record.uploaded_doc
                            rec.file_name = record.doc_file_name
                        if record.name == '1':
                            rec.pan_no = record.doc_number
                            rec.upload_pan_doc = record.uploaded_doc
                            rec.pan_file_name = record.doc_file_name
                    for record in rec.employee_id.educational_details_ids:
                        if record.course_id.name == 'Intermediate':
                            rec.upload_hsc_doc = record.uploaded_doc
                            rec.hsc_file_name = record.doc_file_name

    employee_id = fields.Many2one('hr.employee', string="Employee")
    member_name = fields.Char(string="Father/Husband Name")
    # service_period = fields.Char(string='Previous period of service', size=2)
    # service_period_year = fields.Char(string='Years', size=2, default='0')
    # service_period_month = fields.Char(string='Months', size=2, default='0')
    service_period_year = fields.Selection([(i, str(i)) for i in range(0, 16)], string='Year(s)', default=0)
    service_period_month = fields.Selection([(i, str(i)) for i in range(0, 13)], string='Month(s)', default=0)
    """Aadhaar"""
    aadhaar_no = fields.Char(string='Aadhaar No.', store=True, readonly=False, size=12)
    upload_doc = fields.Binary(string='Aadhaar document', attachment=True, store=True, readonly=False)
    file_name = fields.Char("Aadhaar File Name", store=True)

    """HSC"""
    upload_hsc_doc = fields.Binary(string='HSC Document', attachment=True, store=True, readonly=False)
    hsc_file_name = fields.Char("HSC File Name", store=True)
    """EPF"""
    epf_no = fields.Char(string="EPF No")
    """UAN"""
    uan_no = fields.Char(string='UAN No.')
    upload_epf_doc = fields.Binary(string='EPF Document', attachment=True, readonly=False)
    epf_file_name = fields.Char("UAN File")
    """PAN"""
    pan_no = fields.Char(string="PAN", store=True, readonly=False, size=12)
    upload_pan_doc = fields.Binary(string='PAN Document', attachment=True, store=True, readonly=False)
    pan_file_name = fields.Char("PAN File Name", store=True)

    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], string="State", default='pending')
    date_of_joining = fields.Date(string="Joining Date", store=True, readonly=False)
    bank = fields.Char(string="Bank Name", store=True, readonly=False)
    bank_account = fields.Char(string="Account No", store=True, readonly=False)

    grade = fields.Many2one('kwemp_grade_master', store=True, readonly=False, string='Grade')
    band = fields.Many2one('kwemp_band_master', string='Band', store=True, readonly=False, )

    remarks = fields.Char(string="Remarks")
    active = fields.Boolean(default=True)

    nominee_line_ids = fields.One2many('kw_epf_nominee_lines', 'kw_epf_id', string="Nominee's", ondelete='cascade')

    @api.model
    def check_pending_epf(self, user_id):
        feedback_url = False
        first_day_of_month = datetime.date.today().replace(day=1)
        # print(first_day_of_month)
        if user_id.employee_ids.enable_epf and user_id.employee_ids.date_of_joining > first_day_of_month:
            check_record = self.env['kw_epf'].sudo().search([('employee_id', '=', user_id.employee_ids.id)])
            if not check_record:
                feedback_url = f"/employee-epf-form/"
        return feedback_url

    @api.multi
    def approve_epf(self):
        if not self.nominee_line_ids:
            raise ValidationError('You need to add at least one nominee.')

        self.sudo().write({
            'state': 'approved',
        })

    @api.constrains('employee_id')
    def validate_unique_records(self):
        if self.employee_id:
            check_record = self.env['kw_epf'].sudo().search([('employee_id', '=', self.employee_id.id)]) - self
            if check_record:
                raise ValidationError("Multiple records cannot be created for same employee")

    # @api.constrains('epf_no', 'uan_no', 'aadhaar_no', 'service_period', 'pan_no')
    # def validate_fields(self):
    #     print(self.pan_no)
    #     if self.epf_no:
    #         if not re.match("[A-Za-z0-9]", str(self.epf_no)) != None:
    #             raise ValidationError("Your EPF No is invalid for: %s" % self.epf_no)
    #     if self.aadhaar_no:
    #         if not re.match("[0-9]", str(self.aadhaar_no)) != None:
    #             raise ValidationError("Your Aadhaar No is invalid for: %s" % self.aadhaar_no)
    #     if self.service_period:
    #         if not re.match("[0-9]", str(self.service_period)) != None:
    #             raise ValidationError("Your Previous period of service is invalid for: %s" % self.service_period)
    #     if self.uan_no:
    #         if not re.match("[0-9]", str(self.uan_no)) != None:
    #             raise ValidationError("Your UAN No is invalid for: %s" % self.uan_no)
        # if self.pan_no:
        #     if not re.match("[A-Za-z]{5}\d{4}[A-Za-z]{1}", str(self.pan_no)) != None:
        #         raise ValidationError("Your PAN No is invalid for: %s" % self.pan_no)


class kw_epf_nominee_lines(models.Model):
    _name = 'kw_epf_nominee_lines'
    _description = "EPF Nominees"

    kw_epf_id = fields.Many2one('kw_epf', string="EPF ID")
    nominee_name = fields.Char(string="Nominee Name")
    address = fields.Text(string="Address")
    relation_with_member = fields.Many2one('kwmaster_relationship_name', string="Nominee relationship with member")
    minor_nominee = fields.Text(string="Minor Nominee")
    dob = fields.Date(string="Date of Birth")
