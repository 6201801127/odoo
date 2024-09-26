# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    limit_value = fields.Integer(string="Set Update limit")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_emp_document_migration.limit_value', self.limit_value)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            limit_value = int(self.env['ir.config_parameter'].sudo().get_param('kw_emp_document_migration.limit_value')),
        )
        return res
