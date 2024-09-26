from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError



class ContractManagement(models.Model):
    _name = "bsscl.contract.contract"
    _description = 'Contracts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Name' , track_visibility='onchange')
    start_date = fields.Date('Start Date', track_visibility='onchange')
    end_date = fields.Date('End Date', track_visibility='onchange')
    contract_to = fields.Char('Contract Assigned To', track_visibility='onchange')
    description = fields.Text('Description', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, track_visibility='onchange')
    bank_guarantee_line_ids = fields.One2many('bank.guarantee', 'bsscl_contract_id', string='Bank Guarantees',
                                              ondelete='cascade', track_visibility='onchange')


class BankGuarantees(models.Model):
    _name = "bank.guarantee"
    _description = 'Bank Guarantees'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


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

