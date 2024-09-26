# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class Employee(models.Model):
    _inherit = "hr.employee"

    sbu_type = fields.Selection(
        string='Resource Type',
        selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('none', 'None')])
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")

    @api.onchange('sbu_type')
    def _onchange_sbu_type(self):
        self.sbu_master_id = False
