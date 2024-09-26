from odoo import models, fields


class PurchaseAgreementMethod(models.Model):
    _name = 'purchase.agreement.method'
    _description = 'Tender Method'
    _rec_name = 'name'

    name = fields.Char("Name", required=True)
