from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_whatsapp = fields.Boolean(string='Enable WhatsApp notification to applicant', default=False)
    enable_sync_logging = fields.Boolean(string='Enable Sync Logging to applicant', default=False)
    enable_sms = fields.Boolean(string='Enable SMS notification to applicant', default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enable_whatsapp=self.env['ir.config_parameter'].sudo().get_param('kw_auth.enable_whatsapp'),
            enable_sms=self.env['ir.config_parameter'].sudo().get_param('kw_auth.enable_sms'),
            enable_sync_logging=self.env['ir.config_parameter'].sudo().get_param('kw_auth.enable_sync_logging'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.enable_whatsapp or False
        param.set_param('kw_auth.enable_whatsapp', field1)
        field2 = self.enable_sms or False
        param.set_param('kw_auth.enable_sms', field2)
        field3 = self.enable_sync_logging or False
        param.set_param('kw_auth.enable_sync_logging', field3)
