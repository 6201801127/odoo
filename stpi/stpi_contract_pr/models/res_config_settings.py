from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    da_percent = fields.Char('DA')
    da_effective_date = fields.Date("DA Effective Date")

    basic_percent = fields.Char('Basic(%)')
    basic_effective_date = fields.Date("Basic Effective Date")

    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.da_percent or False
        field2 = self.basic_percent or False
        da_effective_date = self.da_effective_date
        basic_effective_date = self.basic_effective_date

        param.set_param('hr_contract.default_da_inc', field1)
        param.set_param('hr_contract.default_basic_inc', field2)

        param.set_param('hr_contract.da_effective_date', da_effective_date)
        param.set_param('hr_contract.basic_effective_date', basic_effective_date)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
        	da_percent = self.env['ir.config_parameter'].sudo().get_param('hr_contract.default_da_inc'),
            basic_percent = self.env['ir.config_parameter'].sudo().get_param('hr_contract.default_basic_inc'),
            da_effective_date = self.env['ir.config_parameter'].sudo().get_param('hr_contract.da_effective_date'),
            basic_effective_date= self.env['ir.config_parameter'].sudo().get_param('hr_contract.basic_effective_date')
        	)
        return res