# *******************************************************************************************************************
#  File Name             :   bsscl_telephone_bill_expense.py
#  Description           :   This is a master model which is used to keep all records related to telephone expense
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from odoo.tools.mimetypes import guess_mimetype


class TelephoneExpense(models.Model):
    _name = 'bsscl.telephone.expense'
    _description = "BSSCL Telephone Expense"
    _rec_name='tel_exp_master_id'

    settlement_id = fields.Many2one(comodel_name="tour.settlement",string="Settlement")
    tel_exp_master_id = fields.Many2one(comodel_name="telephone.bill.expense.master",string="Telephone Bill Expense / टेलीफोन बिल खर्च")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency Type / मुद्रा प्रकार",
                                       required=True, domain=[('name', 'in', ['INR', 'USD'])])
    amount = fields.Float("Amount / मात्रा", required=True)
    # upload_document = fields.Binary(string="Upload Document / दस्तावेज़ अपलोड करें")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'tour_attachment_rel',
        'tour_id', 'attachment_id',
        string='Attachments / संलग्नक',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    tour_id = fields.Many2one(comodel_name="bsscl.tour", string="Tour Details / भ्रमण विवरण")
    attachment_checked = fields.Boolean(string="Attachment Checked", compute="_compute_attachment_checked")
    @api.depends('attachment_ids')
    def _compute_attachment_checked(self):
        for rec in self:
            if not rec.attachment_ids:
                rec.attachment_checked = False
            else:
                rec.attachment_checked = True  

    @api.constrains('attachment_ids')
    @api.onchange('attachment_ids')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for rec in self:
            for record in rec.attachment_ids:
                if record.datas:
                    # print('Record data==============',record.datas,len(record.datas),(len(record.datas) * 3 / 4))
                    print("length file record========================",((len(record.datas)*3/4)/1024)/1024)
                    # len(record.datas)
                    acp_size = ((len(record.datas) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.datas))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only .PDF/.jpg/.jpeg/.png format is allowed")
                    if acp_size > 2:
                        raise ValidationError("Document allowed size less than 2MB")

#************ Telephone expese Master Model ********************************
class TelephoneExpenseMaster(models.Model):
    _name = 'telephone.bill.expense.master'
    _description = "Telephone Bill Expense Master"
    _rec_name='name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have telephone bill with the same name / आपके पास एक ही नाम का टेलीफोन बिल नहीं हो सकता है!')
    ]
    name = fields.Char(string="Name / नाम")
    description = fields.Text(string="Description / विवरण")

   