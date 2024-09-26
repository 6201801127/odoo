from odoo import api, fields, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    description = fields.Char('Description', )

    # name = fields.Char('Unit of Measure', required=True, translate=True)

    @api.onchange('name')
    def _onchange_name(self):
        self.name = self.name.upper() if self.name else ''

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = values['name'].upper()
        return super(UoM, self).create(vals_list)

    @api.multi
    def write(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        return super(UoM, self).write(values)
