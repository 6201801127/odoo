from odoo import models,fields,api
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import ValidationError
from mimetypes import guess_extension
import base64
import datetime,calendar
from datetime import date, datetime, timedelta
from dateutil import relativedelta


class BGTracker(models.Model):
    _name = 'bg_tracker'
    _description = "BG Tracker"
    _rec_name = 'bg_number'

    sl_no = fields.Integer(string="Sl No")
    bank_id = fields.Many2one('res.bank',string="Bank Name")
    ifsc_code = fields.Char(related="bank_id.bic")
    bg_number = fields.Char(string="BG Number")
    bg_date_char = fields.Char("bg_date_char",compute="date_to_string")
    bg_date = fields.Date(string="BG Date")
    bg_amount = fields.Float(string="BG Amount")
    bg_expiry_date_char = fields.Char("bg_expiry_date_char",compute="date_to_string")
    bg_expiry_date = fields.Date(string="BG Expiry")
    claim_date_char = fields.Char("claim_date_char",compute="date_to_string")
    claim_date = fields.Date(string="Claim Date")
    bg_purpose = fields.Selection([('workorder','Workorder'),('others','Others'),('tender','Tender'),('empanelment','Empanelment')],string="BG Purpose")
    wo_id = fields.Many2one('crm.lead',string="Workorder")
    wo_number = fields.Char(string="WO/OPP Number",related="wo_id.code")
    wo_name = fields.Char(string="WO/Opportunity Name",related="wo_id.name")
    client_name = fields.Char(string="Client")
    project_amount = fields.Float(string="Project Amount")
    csg_head_id = fields.Many2one('hr.employee',string="CSG Head")
    account_holder_id = fields.Many2one('hr.employee',string="Account Holder")
    fd_amount = fields.Float(string="FD Amount")
    transaction_expiry_char = fields.Char("transaction_expiry_char",compute="date_to_string")
    transaction_expiry = fields.Date(string="Transaction Expiry")
    finance_remarks = fields.Text(string="Finance Remarks")
    bg_scan_file = fields.Binary(string="BG Scan Doc.",attachment=True)
    ref_doc = fields.Binary(string="Reference Doc.",attachment=True)
    fd_reference_ids = fields.One2many('fd_reference','parent_id',string="FD Reference")
    ckeck_thirty_days = fields.Date(string="Check 30 Days",compute="get_thirty_days")
    bg_closure_date_char = fields.Char("bg_closure_date_char",compute="date_to_string")
    bg_closure_date = fields.Date(string="BG Closure Date")
    bg_expenses = fields.Float(string="BG Expenses")

    def date_to_string(self):
        for rec in self:
            rec.bg_date_char = rec.bg_date.strftime("%d-%m-%y") if rec.bg_date else ''
            rec.bg_expiry_date_char = rec.bg_expiry_date.strftime("%d-%m-%y") if rec.bg_expiry_date else ''
            rec.claim_date_char = rec.claim_date.strftime("%d-%m-%y") if rec.claim_date else ''
            rec.transaction_expiry_char = rec.transaction_expiry.strftime("%d-%m-%y") if rec.transaction_expiry else ''
            rec.bg_closure_date_char = rec.bg_closure_date.strftime("%d-%m-%y") if rec.bg_closure_date else ''
    @api.constrains('bg_closure_date')
    def _check_(self):
        for record in self:
            if record.bg_closure_date and len(record.fd_reference_ids) > 0:
                raise ValidationError("Please release the FD.")
            
    
    def get_thirty_days(self):
        for rec in self:
            # print(datetime.today() + relativedelta.relativedelta(months=1))
            thirty_days = datetime.today() + relativedelta.relativedelta(months=1)
            rec.ckeck_thirty_days = thirty_days.date()

    # @api.model
    # def create(self,vals):
    #     record = super(BGTracker, self).create(vals)
    #     for rec in record.fd_reference_ids:
    #         rec.write({
    #             'bg_tagged_ids': [(4,[record.id])]
    #         })
    #     return record
    # # @api.multi
    # # def multi(self,vals):

    @api.constrains('bg_scan_file','ref_doc')
    def _check_uploaded_image(self):
        allowed_extension = '.pdf'
        bg_scan_file_size,ref_doc_file_size = 1536,1024 # in kb
        for file in self:
            if file.bg_scan_file:
                doc_extension = guess_extension(guess_mimetype(base64.b64decode(file.bg_scan_file)))
                file_s = (len(file.bg_scan_file)*3/4) / 1024
                if doc_extension != allowed_extension:
                    raise ValidationError(f"Invalid file extension.\nAllowed extensions are {allowed_extension}.")
                if file_s > bg_scan_file_size:
                    raise ValidationError(f"Maximum file size is {bg_scan_file_size}kb.")

            if file.ref_doc:
                doc_extension = guess_extension(guess_mimetype(base64.b64decode(file.ref_doc)))
                file_s = (len(file.ref_doc)*3/4) / 1024
                if doc_extension != allowed_extension:
                    raise ValidationError(f"Invalid file extension.\nAllowed extensions are {allowed_extension}.")
                if file_s > ref_doc_file_size:
                    raise ValidationError(f"Maximum file size is {ref_doc_file_size}kb.")

class FDReference(models.Model):
    _name = 'fd_reference'
    _description = 'FD Reference'
    _rec_name = 'fd_id'

    parent_id = fields.Many2one('bg_tracker',string="BG No")
    fd_id = fields.Many2one('fd_tracker',string="FD No.")
    fd_start_date = fields.Date('Start Dt.',related="fd_id.start_date")
    fd_maturity_date = fields.Date('Maturity Dt.',related="fd_id.maturity_date")
    fd_principal_amt = fields.Float('Principal',related="fd_id.principal_amt")
    bg_amount = fields.Float(string="BG Amount")

    @api.model
    def create(self,vals):
        record = super(FDReference, self).create(vals)
        for rec in record:
            print(rec.id,rec.fd_id,rec.parent_id.id,rec.bg_amount)
            self.env['bg_reference'].sudo().create({
                'fd_line_id': rec.id,
                'parent_id':rec.fd_id.id
            })
        return record



    
        