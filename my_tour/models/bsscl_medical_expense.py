# *******************************************************************************************************************
#  File Name             :   bsscl_medical_expense.py
#  Description           :   This is a master model which is used to keep all records related to medical expense
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



class MedicalExpenseDetails(models.Model):
    _name = 'bsscl.medical.expense'
    _description = "BSSCL Medical Expense"
    _rec_name='mdl_exp_master_id'

    settlement_id = fields.Many2one(comodel_name="tour.settlement",string="Settlement")
    mdl_exp_master_id = fields.Many2one(comodel_name="medical.expense.master",string="Medical Expense / चिकित्सा खर्च")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency Type / मुद्रा प्रकार",
                                       required=True, domain=[('name', 'in', ['INR', 'USD'])])
    amount = fields.Float("Amount / मात्रा", required=True)
    # upload_document = fields.Binary(string="Upload Document / दस्तावेज़ अपलोड करें")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'medical_attachment_rel',
        'medical_id', 'attachment_id',
        string='Attachments / संलग्नक',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.(Document size should be less than 2MB(Any type of documents))')
    tour_id = fields.Many2one(comodel_name="bsscl.tour", string="Tour Details / भ्रमण विवरण")

    @api.constrains('attachment_ids')
    @api.onchange('attachment_ids')
    def _check_attachment_ids(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for rec in self:
            for record in rec.attachment_ids:
                if record.datas:
                    acp_size = ((len(record.datas) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.datas))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                    if acp_size > 2:
                        raise ValidationError("Document allowed size less than 2MB")

#************ Medical expese Master Model ********************************
class MedicalExpenseMaster(models.Model):
    _name = 'medical.expense.master'
    _description = "BSSCL Medical Expense Master"
    _rec_name='name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have medical expense with the same name ! / आप एक ही नाम से चिकित्सा व्यय नहीं कर सकते!')
    ]
    
    name = fields.Char(string="Name / नाम")
    description= fields.Text(string="Description / विवरण")
