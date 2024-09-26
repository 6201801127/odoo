from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
        
    enable_vocalize_from = fields.Boolean(string="Enable Vocalize")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enable_vocalize_from=self.env['ir.config_parameter'].sudo().get_param(
                'kw_vocalize.enable_vocalize_from'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.enable_vocalize_from or False
        param.set_param('kw_vocalize.enable_vocalize_from', field1)
