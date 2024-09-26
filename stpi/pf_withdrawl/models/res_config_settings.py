from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    pf_intres_calc_day = fields.Char("PF Interest Calculation Day")

    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        pf_intres_calc_day = self.pf_intres_calc_day or False
        param.set_param('pf_intres_calc_day', pf_intres_calc_day)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(pf_intres_calc_day = self.env['ir.config_parameter'].sudo().get_param('pf_intres_calc_day'))
        return res

    @api.constrains('pf_intres_calc_day')
    def check_constrains(self):
        if self.pf_intres_calc_day:
            try:
                calc_day = int(self.pf_intres_calc_day)
                if not (1 <= calc_day <= 31):
                   raise ValidationError('You need to enter numeric value between 1 to 31.') 
            except ValueError:
                raise ValidationError('You need to enter numeric value.')