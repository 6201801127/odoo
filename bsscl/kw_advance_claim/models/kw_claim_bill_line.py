from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError
import re
import base64
from odoo.tools.mimetypes import guess_mimetype


class kw_claim_bill_line(models.Model):
    _name = 'kw_advance_claim_bill_line'
    _description = 'Claim Bill Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    claim_line_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    description = fields.Text(string="Description", required=True)
    amount = fields.Float(string="Total Amount", required=True)
    claim_type_id = fields.Many2one('kw_advance_claim_type', string="Claim Type")
    category_id = fields.Many2one('kw_advance_claim_category', string="Category", required=True)
    upload_bill = fields.Binary(string='Upload Bill', attachment=True, required=True)
    file_name = fields.Char("File Name")
    sr_no = fields.Char(string="Sr No", required=True, default="New", readonly="1")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)


    @api.model
    def default_get(self, fields):
        res = super(kw_claim_bill_line, self).default_get(fields)
        if self.claim_line_id and self.claim_line_id.petty_cash_id:
            res['claim_type_id'] = self.claim_line_id.petty_cash_id.claim_type_id.id if self.claim_line_id.petty_cash_id.claim_type_id else False 
            res['category_id'] = self.claim_line_id.petty_cash_id.category_id.id if self.claim_line_id.petty_cash_id.category_id else False 
        return res

    @api.model
    def create(self, vals):
        if vals.get('sr_no', 'New') == 'New':
            vals['sr_no'] = self.env['ir.sequence'].next_by_code('kw_claim_bill_line') or '/'
        return super(kw_claim_bill_line, self).create(vals)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        lst = []
        self.claim_type_id = False
        for record in self:
            claim_type_record = self.env['kw_advance_claim_type'].sudo().search(
                [('claim_category_id', '=', record.category_id.id)])
            if claim_type_record:
                # for rec in claim_type_record:
                #     lst.append(rec.id)
                return {'domain': {'claim_type_id': [('id', 'in', claim_type_record.ids)]}}

    @api.constrains('date')
    def claim_date_validation(self):
        today_date = datetime.now().date()
        for record in self:
            if record.claim_line_id.petty_cash_id:
                if record.date > record.claim_line_id.applied_date.date():
                    raise ValidationError("You cannot apply for a Future date.")
            else:
                if record.date > today_date:
                    raise ValidationError("You cannot apply for a Future date.")
                
    @api.constrains('description')
    @api.onchange('description')
    def _onchange_name(self):
        for rec in self:
            if rec.description and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.description)):
                raise ValidationError("Description should be in alphabets only.")
            if rec.description:
                if len(rec.description) > 500:
                    raise ValidationError('Number of characters must not exceed 500.')
                
    @api.constrains('upload_bill')
    @api.onchange('upload_bill')
    def _check_document_upload(self):
        for rec in self:
            allowed_file = ['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword']
            if rec.upload_bill:
                app_size = ((len(rec.upload_bill) * 3/4) / 1024) / 1024
                if app_size > 2:
                    raise ValidationError("Document allowed size less than 2MB")
                mimetype = guess_mimetype(base64.b64decode(rec.upload_bill))
                if str(mimetype) not in allowed_file:
                    raise ValidationError("Only PDF/docx format is allowed")