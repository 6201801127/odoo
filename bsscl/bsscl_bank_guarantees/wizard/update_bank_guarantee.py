from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class updatebankguarantee(models.TransientModel):
    _name = "update.bank.guarantee"
    _description = 'Update Bank Guarantee'

    name = fields.Char('Name')
    bank_name = fields.Char('Bank Name')
    recieved_date = fields.Date('Recieved Date')
    from_date = fields.Date('Valid From')
    to_date = fields.Date('Valid To')
    bsscl_contract_id = fields.Many2one('bsscl.contract.contract', 'Contract Name')
    upload = fields.Binary('Upload File')
    fname = fields.Char(string="File Name", copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)


    def update_bank_guarantee_details(self):
        if not (self.name or self.bank_name or self.bsscl_contract_id or self.from_date or self.to_date or self.recieved_date or self.upload):
            raise UserError(_("Please fill complete data."))
        bank_guarantee_obj = self.env['bank.guarantee']
        print(bank_guarantee_obj, 'bank_guarantee_obj')

        bank_guarantee_obj = self.env['bank.guarantee'].create({
                                'name': self.name,
                                'bank_name': self.bank_name,
                                'bsscl_contract_id': self.bsscl_contract_id.id,
                                'from_date': self.from_date,
                                'to_date': self.to_date,
                                'recieved_date': self.recieved_date,
                                'upload': self.upload,
                                'fname': self.fname,
                                'company_id': self.company_id.id,
                                'currency_id': self.currency_id.id,
                            })
        print(bank_guarantee_obj, 'bank_guarantee_obj')