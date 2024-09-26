# -*- coding: utf-8 -*-

from odoo import models, fields, api


class kw_meeting_mode_master(models.Model):
    _name = 'kw_meeting_mode_master'
    _description = 'Meeting Modes'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Meeting Mode',required=True)
    mode_key = fields.Char(string='Meeting Mode Key',required=True)

    @api.onchange('name')
    def _compute_mode_key(self):
        for rec in self:
            if rec and rec.name:
                name = rec.name.lower().strip().replace(' ', '_')
                rec.mode_key = name
