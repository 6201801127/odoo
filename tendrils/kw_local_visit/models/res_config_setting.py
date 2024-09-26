# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class LocalVisitResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    lv_auto_approval_days = fields.Integer(string="Auto Approval(Days)")

    def set_values(self):
        res = super(LocalVisitResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_local_visit.lv_auto_approval_days', self.lv_auto_approval_days)
        return res

    @api.model
    def get_values(self):
        res = super(LocalVisitResConfigSettings, self).get_values()
        res.update(
            lv_auto_approval_days = int(self.env['ir.config_parameter'].sudo().get_param('kw_local_visit.lv_auto_approval_days')),
        )
        return res

