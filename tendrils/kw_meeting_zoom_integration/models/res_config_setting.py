from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char(string="Zoom API Key", help="Zoom API Key.", )
    api_secret = fields.Char(string="Zoom API Secret Key", help="Zoom API Key.", )
    webhook_token = fields.Char(string="Zoom Webhook Token", help="Zoom Webhook Token.",default="Z1sd0vIfTHib1PP4Q6WprA")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        res.update(
            api_key=str(param.get_param('kw_meeting_zoom_integration.api_key')),
            api_secret=str(param.get_param('kw_meeting_zoom_integration.api_secret')),
            webhook_token=str(param.get_param('kw_meeting_zoom_integration.webhook_token')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_meeting_zoom_integration.api_key', self.api_key)
        param.set_param('kw_meeting_zoom_integration.api_secret', self.api_secret)
        param.set_param('kw_meeting_zoom_integration.webhook_token', self.webhook_token)
