# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    validation_check = fields.Boolean(string="Validation Check")
    one_day_validation_check = fields.Boolean(string="One Day Pop-up Check")
    one_day_restriction_check = fields.Boolean(string="One Day Restriction Check")
    ra_pm_reviewer_validation_check = fields.Boolean(string="One Day Validation for PM,Reviewer,RA")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_timesheets.validation_check', self.validation_check or False)
        self.env['ir.config_parameter'].set_param('kw_timesheets.one_day_validation_check', self.one_day_validation_check or False)
        self.env['ir.config_parameter'].set_param('kw_timesheets.ra_pm_reviewer_validation_check', self.ra_pm_reviewer_validation_check or False)
        self.env['ir.config_parameter'].set_param('kw_timesheets.one_day_restriction_check', self.one_day_restriction_check or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            validation_check=self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.validation_check'),
            one_day_validation_check=self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.one_day_validation_check'),
            ra_pm_reviewer_validation_check=self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.ra_pm_reviewer_validation_check'),
            one_day_restriction_check=self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.one_day_restriction_check'),
        )
        return res
