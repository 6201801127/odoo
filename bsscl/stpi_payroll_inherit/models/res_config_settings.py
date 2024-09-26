from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pmrf_deduct_days = fields.Char('No of days for PM relief fund')
    slip_visible_day = fields.Char('Slip Visible')


    
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.pmrf_deduct_days or False
        field2 = self.slip_visible_day or False
        param.set_param('hr_payslip.pmrf_deduct_days', field1)
        param.set_param('hr_payslip.slip_visible_day', field2)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            pmrf_deduct_days = self.env['ir.config_parameter'].sudo().get_param('hr_payslip.pmrf_deduct_days'),
            slip_visible_day = self.env['ir.config_parameter'].sudo().get_param('hr_payslip.slip_visible_day'),
        )
        return res