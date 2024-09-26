from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
        
    enable_work_from_home_survey = fields.Boolean(string="Enable Work From Home Survey")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enable_work_from_home_survey=self.env['ir.config_parameter'].sudo().get_param(
                'kw_surveys.enable_work_from_home_survey'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.enable_work_from_home_survey or False
        param.set_param('kw_surveys.enable_work_from_home_survey', field1)
