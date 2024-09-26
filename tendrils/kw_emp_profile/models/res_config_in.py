# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employee_pan_check = fields.Boolean(string="Enable Employee PAN Update Screen after Login.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        
        res.update(employee_pan_check=self.env['ir.config_parameter'].sudo().get_param('kw_emp_profile.employee_pan_check'))
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('kw_emp_profile.employee_pan_check', self.employee_pan_check or False)
        