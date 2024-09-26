# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class ReimburementApprove(models.TransientModel):
    _name = "hr.declaration.approve"
    _description = "Multiple Approve for hr declarations"


    @api.multi
    def action_approve_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['hr.declaration'].browse(active_ids):
            if rei.state == 'to_approve':
                rei.sudo().button_approved()


    @api.multi
    def action_reject_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['hr.declaration'].browse(active_ids):
            if rei.state == 'to_approve':
                rei.sudo().button_reject()