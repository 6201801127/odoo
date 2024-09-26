# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    notify_cc = fields.Many2many('hr.employee', 'res_config_employee_rel', 'employee_id', 'res_id', string='CC Notify')
    notice_period = fields.Char('Notice Period')    #to do
    hrd_ids = fields.Many2many('hr.employee', 'eos_hrd_config_rel', string="HRD")
    new_hrd_ids = fields.Many2many('hr.employee', 'eos_other_hrd_config_rel', string="Other HRD")
    module_offboarding_mode_status = fields.Boolean(string="Demo Mode")
    advance_checklist = fields.Boolean(string="Advance checklist")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_eos.notify_cc', self.notify_cc.ids)
        self.env['ir.config_parameter'].set_param('kw_eos.notice_period', self.notice_period)
        self.env['ir.config_parameter'].set_param('kw_eos.hrd_ids', self.hrd_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_eos.new_hrd_ids', self.new_hrd_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_eos.module_offboarding_mode_status',
                                                  self.module_offboarding_mode_status or False)
        self.env['ir.config_parameter'].set_param('kw_eos.advance_checklist',
                                                  self.advance_checklist or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        notify_cc = self.env['ir.config_parameter'].sudo().get_param('kw_eos.notify_cc')
        hrd_ids = self.env['ir.config_parameter'].sudo().get_param('kw_eos.hrd_ids')
        new_hrd_ids = self.env['ir.config_parameter'].sudo().get_param('kw_eos.new_hrd_ids')
        lines = False
        hrd_lines = False
        new_hrd_lines = False
        if notify_cc:
            lines = [(6, 0, literal_eval(notify_cc))]
        if hrd_ids:
            hrd_lines = [(6, 0, literal_eval(hrd_ids))]
        if new_hrd_ids:
            new_hrd_lines = [(6, 0, literal_eval(new_hrd_ids))]

        res.update(
            hrd_ids=hrd_lines,
            new_hrd_ids=new_hrd_lines,
            notify_cc=lines,
            notice_period=str(self.env['ir.config_parameter'].sudo().get_param('kw_eos.notice_period')),
            module_offboarding_mode_status=self.env['ir.config_parameter'].sudo().get_param(
                'kw_eos.module_offboarding_mode_status'),
            advance_checklist=self.env['ir.config_parameter'].sudo().get_param(
                'kw_eos.advance_checklist'),
        )
        return res
