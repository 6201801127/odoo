from odoo import api, fields, models


class Respartner(models.Model):
    _inherit = "res.partner"

    vendor_code = fields.Char(string="Vendor Code", )

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.vendor_code:
                result.append((record.id, f'({record.vendor_code}) {record.name}'))
            else:
                result.append((record.id, f'{record.name}'))
        return result
