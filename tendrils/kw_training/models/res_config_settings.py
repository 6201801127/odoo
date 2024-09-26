from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_kw_training_feedback_status = fields.Boolean(string="Training Feedback Check")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            module_kw_training_feedback_status=self.env['ir.config_parameter'].sudo().get_param(
                'kw_training.module_kw_training_feedback_status'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.module_kw_training_feedback_status or False
        param.set_param('kw_training.module_kw_training_feedback_status', field1)
