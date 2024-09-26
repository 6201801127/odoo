# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_to_rcm = fields.Many2many('hr.employee', 'emp_mail_rel', 'mail_id', 'emp_id', string='RCM Mail cc')
    skill_survey_enabled = fields.Boolean(string="Survey enabled")
    
    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_resource_management.mail_to_rcm', self.mail_to_rcm.ids)
        self.env['ir.config_parameter'].set_param('kw_resource_management.skill_survey_enabled', self.skill_survey_enabled or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        mail_to_rcm = self.env['ir.config_parameter'].sudo().get_param('kw_resource_management.mail_to_rcm')
        lines = False
        if mail_to_rcm:
            lines = [(6, 0, literal_eval(mail_to_rcm))]

        res.update(mail_to_rcm=lines,
                  skill_survey_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_resource_management.skill_survey_enabled'))
        return res
