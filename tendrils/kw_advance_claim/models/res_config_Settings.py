# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    grant_ids = fields.Many2many('hr.job', 'kw_advance_hr_job_grant_rel', 'advance_id', 'job_id',
                                 string='Grant Notification')
    notification_cc_ids = fields.Many2many('hr.job', 'kw_advance_hr_job_notify_rel', 'advance_id', 'job_id',
                                           string='Mail CC Notification')
    individual_hr_email = fields.Char(string='HR Individual Email')
    advance_api = fields.Boolean(string="Enable API")
    advance_eligibility_criteria  = fields.Selection([('1', '1 Month'),('2', '2 Month'),('3', '3 Month'),('4', '4 Month'),('5', '5 Month'),('6', '6 Month'),('7', '7 Month'),('8', '8 Month'),('9', '9 Month'),('10', '10 Month'),('11', '11 Month'),('12', '12 Month')])

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_advance_claim.grant_ids', self.grant_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_advance_claim.notification_cc_ids', self.notification_cc_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_advance_claim.individual_hr_email', self.individual_hr_email)
        self.env['ir.config_parameter'].set_param('kw_advance_claim.advance_api', self.advance_api or False)
        self.env['ir.config_parameter'].set_param('kw_advance_claim.advance_eligibility_criteria', self.advance_eligibility_criteria or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config=self.env['ir.config_parameter']

        final_approver_ids = config.sudo().get_param('kw_advance_claim.grant_ids')
        flines = False
        if final_approver_ids:
            flines = [(6, 0, literal_eval(final_approver_ids))]

        notification_cc_ids = config.sudo().get_param('kw_advance_claim.notification_cc_ids')
        cclines = False
        if notification_cc_ids:
            cclines = [(6, 0, literal_eval(notification_cc_ids))]
        res.update(
            grant_ids=flines,
            notification_cc_ids=cclines,
            individual_hr_email=str(config.sudo().get_param('kw_advance_claim.individual_hr_email')),
            advance_api=config.sudo().get_param('kw_advance_claim.advance_api'),
            advance_eligibility_criteria=config.sudo().get_param('kw_advance_claim.advance_eligibility_criteria'),
        )
        return res
