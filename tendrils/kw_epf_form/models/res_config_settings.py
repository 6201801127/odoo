from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    epf_status = fields.Boolean(string="EPF Status Check")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            epf_status=self.env['ir.config_parameter'].sudo().get_param(
                'kw_epf.epf_status'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.epf_status or False
        param.set_param('kw_epf.epf_status', field1)
