from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_mail = fields.Boolean(string='Enable Appraisal Mail')

    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.enable_mail or False
        param.set_param('kw_appraisal.enable_mail', field1)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            enable_mail=self.env['ir.config_parameter'].sudo().get_param('kw_appraisal.enable_mail'),
        )
        return res
