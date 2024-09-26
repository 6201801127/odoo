from odoo import api, fields, models


class kw_inventory_transporter_master(models.Model):
    _name = "kw_inventory_transporter_master"
    _description = "A master model to create Transport Order"
    _rec_name = "transporter_name"

    transporter_code = fields.Char(string="Transporter Code")
    transporter_name = fields.Char(string="Transporter Name", required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.transporter_code:
                result.append((record.id, f'({record.transporter_code}) {record.transporter_name}'))
            else:
                result.append((record.id, f'{record.transporter_name}'))
        return result
