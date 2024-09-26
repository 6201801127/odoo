# -*- coding: utf-8 -*-
from odoo import fields, models, api
from ast import literal_eval


class kw_wfh_ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cc_notification_email = fields.Char(string='HRD Notification Email')
    hr_email = fields.Char(string='HR Individual Email')
    notification_cc_ids = fields.Many2many('hr.job', 'kw_wfh_hr_job_rel', 'wfh_id', 'job_id', string='Mail CC Notification')
    count_days = fields.Integer(string='No of days')

    def set_values(self):
        res = super(kw_wfh_ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_wfh.cc_notification_email', self.cc_notification_email)
        self.env['ir.config_parameter'].set_param('kw_wfh.hr_email', self.hr_email)
        self.env['ir.config_parameter'].set_param('kw_wfh.notification_cc_ids', self.notification_cc_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_wfh.count_days', self.count_days)
        return res

    @api.model
    def get_values(self):
        res = super(kw_wfh_ResConfigSettings, self).get_values()
        notification_cc_ids = self.env['ir.config_parameter'].sudo().get_param('kw_advance_claim.notification_cc_ids')
        cclines = False
        if notification_cc_ids:
            cclines = [(6, 0, literal_eval(notification_cc_ids))]
        res.update(
            hr_email=str(self.env['ir.config_parameter'].sudo().get_param('kw_wfh.hr_email')),
            cc_notification_email=str(self.env['ir.config_parameter'].sudo().get_param('kw_wfh.cc_notification_email')),
            count_days=int(self.env['ir.config_parameter'].sudo().get_param('kw_wfh.count_days')),
            notification_cc_ids = cclines
        )
        return res
