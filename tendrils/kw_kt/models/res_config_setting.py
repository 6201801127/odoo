# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notify_kt_cc = fields.Many2many('hr.job', 'kt_notify_job_rel', 'job_id', 'cc_id', string='CC Notify')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_eos.notify_kt_cc', self.notify_kt_cc.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        notify_kt_cc = self.env['ir.config_parameter'].sudo().get_param('kw_eos.notify_kt_cc')
        lines = False
        if notify_kt_cc:
            lines = [(6, 0, literal_eval(notify_kt_cc))]

        res.update(
            notify_kt_cc=lines,
        )
        return res
