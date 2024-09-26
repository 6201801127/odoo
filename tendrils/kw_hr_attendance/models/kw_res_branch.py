# -*- coding: utf-8 -*-
# For Default shift of branch, Created By: T Ketaki Debadarshini, Created On : 27-April-2020

from odoo import api, fields, models


class ResBranch(models.Model):
    _inherit = 'kw_res_branch'

    shift_ids = fields.One2many('resource.calendar', 'branch_id', 'Shifts')
    default_shift_id = fields.Many2one('resource.calendar', 'Default Shift', ondelete='restrict')
