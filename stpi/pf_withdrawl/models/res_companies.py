from odoo import models, fields, api,_

class ResCompanies(models.Model):
    _inherit = 'res.company'

    pf_table = fields.One2many('res.company.pf.interest','company_id')


class ResCompanyInterest(models.Model):
    _name = 'res.company.pf.interest'
    _description = 'PF'

    company_id = fields.Many2one('res.company')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    interest_rate = fields.Float('Interest Rate')
    attachment = fields.Binary('Attachment')
