from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_csm_account_conf = fields.Boolean(string="Enable CSM Accounting Configuration")

    
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.enable_csm_account_conf or False
        param.set_param('kw_accounting.enable_csm_account_conf_status', field1)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            enable_csm_account_conf=self.env['ir.config_parameter'].sudo().get_param('kw_accounting.enable_csm_account_conf_status'),
        )
        return res