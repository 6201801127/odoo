from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
        
    enable_medha_k_gpt = fields.Boolean(string="Enable Medha K ")

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_medha.enable_medha_k_gpt', self.enable_medha_k_gpt)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enable_medha_k_gpt=self.env['ir.config_parameter'].sudo().get_param(
                'kw_medha.enable_medha_k_gpt'),
        )
        return res



