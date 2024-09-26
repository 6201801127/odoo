# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cc_notify = fields.Many2many('hr.employee', 'res_config_rnr_employee_rel', 'employee_id', 'res_id',
                                 string='CC Notify')
    nomination_reminder = fields.Date(string='Nomination Reminder')
    review_reminder = fields.Date(string='Review Remainder')
    congratulation_reminder = fields.Date(string='Congratulation Reminder')
    congratulation_mail_from = fields.Char(string='Congratulation Mail From')
    congratulation_mail_to = fields.Char(string='Congratulation Mail To')

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.cc_notify', self.cc_notify.ids)
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.nomination_reminder',
                                                  self.nomination_reminder)
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.review_reminder', self.review_reminder)
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.congratulation_reminder',
                                                  self.congratulation_reminder)
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.congratulation_mail_from',
                                                  self.congratulation_mail_from)
        self.env['ir.config_parameter'].set_param('kw_reward_and_recognition.congratulation_mail_to',
                                                  self.congratulation_mail_to)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cc_notify = self.env['ir.config_parameter'].sudo().get_param('kw_reward_and_recognition.cc_notify')
        nomination_reminder = self.env['ir.config_parameter'].sudo().get_param(
            'kw_reward_and_recognition.nomination_reminder')
        review_reminder = self.env['ir.config_parameter'].sudo().get_param('kw_reward_and_recognition.review_reminder')
        congratulation_reminder = self.env['ir.config_parameter'].sudo().get_param(
            'kw_reward_and_recognition.congratulation_reminder')
        congratulation_mail_from = self.env['ir.config_parameter'].sudo().get_param(
            'kw_reward_and_recognition.congratulation_mail_from')
        congratulation_mail_to = self.env['ir.config_parameter'].sudo().get_param(
            'kw_reward_and_recognition.congratulation_mail_to')
        lines = False
        if cc_notify:
            lines = [(6, 0, literal_eval(cc_notify))]
        res.update(
            cc_notify=lines,
            nomination_reminder=nomination_reminder,
            review_reminder=review_reminder,
            congratulation_reminder=congratulation_reminder,
            congratulation_mail_from=congratulation_mail_from,
            congratulation_mail_to=congratulation_mail_to,
        )
        return res
