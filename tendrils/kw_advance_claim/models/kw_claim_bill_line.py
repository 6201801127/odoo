from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError


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