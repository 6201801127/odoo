from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError,UserError
import mimetypes,openpyxl
from odoo.addons import decimal_precision as dp
from io import BytesIO
import ast
import base64
from datetime import datetime
from odoo.tools.mimetypes import guess_mimetype
from mimetypes import guess_extension

class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    loan_no = fields.Char(string="Loan No.")
    loan_name = fields.Char(string="Loan Name")
    date = fields.Date(string="Loan Month", default=fields.Date.today(), readonly=False)
    bank = fields.Char(string="Bank")
    installment = fields.Integer(string="Loan Tenor", default= 0)
    loan_account_id = fields.Many2one('account.account', string="Loan Account Code")
    ints_account_id = fields.Many2one('account.account', string="Interest Account Code")
    loan_amount = fields.Float(string="Loan Amount", digits=dp.get_precision('Loan'), track_visibility='onchange')
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    interest_log_lines = fields.One2many('loan_interest_log', 'loan_id', string="Loan Interest Log", index=True)
    file = fields.Binary(string='Upload File>>', attachment=True)
    interest_rate = fields.Float(string="Interest Rate")
    remarks = fields.Text(string="Remarks")
    loan_end_date = fields.Date(string="Loan End Date")
    principal_repayment = fields.Float(string="Principal Repayment", compute="_get_repayment_amount")
    interest_repayment = fields.Float(string="Interest Repayment", compute="_get_repayment_amount")
    loan_expenses = fields.Float(string="Loan Expenses")
    sanction_letter_file = fields.Binary(string="Sanction Letter",attachment=True)
    sanction_letter_file_name = fields.Char("Sanction Letter File Name", track_visibility='onchange')
    original_schedule_file = fields.Binary(string="Original Schedule",attachment=True)
    original_schedule_file_name = fields.Char(string="Original Schedule File Name",track_visibility='onchange')
    lock = fields.Boolean(string="Lock")
        
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.loan_name, record.loan_no)))
        return result

    @api.constrains('sanction_letter_file','original_schedule_file')
    def _check_uploaded_image(self):
        allowed_extension = {'.ods':'.ods','.xlsx':'.xlsx','.xlb':'.xls', '.pdf': '.pdf'}
        sanction_letter_file_size,original_schedule_file_size = 2048,512 # in kb
        for file in self:
            if file.sanction_letter_file:
                doc_extension = guess_extension(guess_mimetype(base64.b64decode(file.sanction_letter_file)))
                file_s = (len(file.sanction_letter_file)*3/4) / 1024
                if doc_extension not in allowed_extension:
                    raise ValidationError(f"Invalid file extension.\nAllowed extensions are {allowed_extension}.")
                if file_s > sanction_letter_file_size:
                    raise ValidationError(f"Maximum file size is {sanction_letter_file_size}kb.")

            if file.original_schedule_file:
                doc_extension = guess_extension(guess_mimetype(base64.b64decode(file.original_schedule_file)))
                file_s = (len(file.original_schedule_file)*3/4) / 1024
                if doc_extension not in allowed_extension:
                    raise ValidationError(f"Invalid file extension.\nAllowed extensions are {allowed_extension}.")
                if file_s > original_schedule_file_size:
                    raise ValidationError(f"Maximum file size is {original_schedule_file_size}kb.")

    def update_loan_line(self):
        self.loan_lines.update_loan_line(self.id)
    @api.multi
    def _get_repayment_amount(self):
        for rec in self:
            rec.principal_repayment = sum(rec.loan_lines.mapped('principle'))
            rec.interest_repayment = sum(rec.loan_lines.mapped('interest_amt'))

    @api.multi
    def generate_xls_format_loan(self):
        self.ensure_one()
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        result_url = f"{base_url}/download-xls-format-loan/"
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of XLS format",
            'url': result_url
        }

    def generate_loan_line(self):
        for rec in self:
            if not rec.file:
                raise ValidationError('Please Upload File')

            excel_data = BytesIO(base64.b64decode(rec.file))
            work_book = openpyxl.load_workbook(excel_data)
            worksheet = work_book.active

            loan_line = []
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                # total = sum(r if r else 0 for r in row[2:14])
                loan_line.append((0, 0, {
                    'sl_no': row[0],
                    'date': row[1].date() if row[1] else '',
                    'new_amount' : row[2] or 0,
                    'principle': row[3] or 0,
                    'interest_amt': row[4] or 0,
                    'amount': ((row[3] or 0) + (row[4] or 0)) or 0,                    
                }))
            rec.loan_lines = loan_line
            self.file = False

    file_name = fields.Char("File Name")

    @api.constrains('file')
    def _check_file_extension(self):
        for record in self:
            if record.file:
                file_name = record.file_name or ''
                file_extension = mimetypes.guess_extension(mimetypes.guess_type(file_name)[0])
                if file_extension != '.xlsx':
                    raise ValidationError("Please upload only XLSX files.")


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    @api.multi
    @api.onchange('opening_blance_principle','new_amount','interest_per','interest_amt','amount','principle','closing_blance_principle')
    def get_actual_amount(self):
        for rec in self:
            rec.amount = rec.principle + rec.interest_amt
            rec.closing_blance_principle = rec.opening_blance_principle + rec.new_amount - rec.principle
    

    date = fields.Date(string="Installment Date")
    sl_no = fields.Integer("SL No.")
    opening_blance_principle=fields.Float(string="Opening Principal", digits=dp.get_precision('Loan'))
    new_amount = fields.Float(string="Principal Recd.")
    interest_per= fields.Float(string="Interest Rate%",digits=dp.get_precision('Loan'),related="loan_id.interest_rate",store=True,group_operator="avg")
    interest_amt= fields.Float(string="Interest Amount",digits=dp.get_precision('Loan'))
    amount = fields.Float(string="EMI", digits=dp.get_precision('Loan'))
    principle= fields.Float(string="Principal Paid",digits=dp.get_precision('Loan'))
    closing_blance_principle=fields.Float(string="Closing Principal", digits=dp.get_precision('Loan'))
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    loan_bank = fields.Char(string="Bank",related="loan_id.bank",store=True)
    lock_date_check = fields.Boolean(string="Lock Date Check",compute="check_lock_date")

    @api.multi
    def check_lock_date(self):
        for rec in self:
            if rec.loan_id.lock and rec.date < date.today():
                rec.lock_date_check = True

    def update_loan_line(self,loan_id):
        installment_ids = self.search([('loan_id','=',loan_id)],order="date asc")
        previous_closing_balance = 0
        for rec in installment_ids:
            if previous_closing_balance is not None:
                x = previous_closing_balance
            
            # Calculate the closing balance for the current record
            actual_closing_balance = x + rec.new_amount - rec.principle
            # Update the record with the calculated closing balance
            y = actual_closing_balance
            
            # Update the previous closing balance for the next record in the loop
            previous_closing_balance = y
            rec.write({'opening_blance_principle':x,'closing_blance_principle':y})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.lock_date_check:
                raise UserError(_("It's locked. You can't delete a line."))
        return super(InstallmentLine, self).unlink()


class LoanInterestLog(models.Model):
    _name = 'loan_interest_log'
    _description = "Loan Interest Log"

    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    interest_per= fields.Float(string="Interest Rate%",digits=dp.get_precision('Loan'))



    