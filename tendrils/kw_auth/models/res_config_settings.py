from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_kw_auth_mode_status = fields.Boolean(string="Tendrils Sync Enable")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            module_kw_auth_mode_status=self.env['ir.config_parameter'].sudo().get_param(
                'kw_auth.module_kw_auth_mode_status'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.module_kw_auth_mode_status or False
        param.set_param('kw_auth.module_kw_auth_mode_status', field1)
