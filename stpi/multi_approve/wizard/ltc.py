# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class ReimburementApprove(models.TransientModel):
    _name = "employee.ltc.advance.approve"
    _description = "Multiple Approve for employee.ltc.advances"


    @api.multi
    def action_approve_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['employee.ltc.advance'].browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_approved()


    @api.multi
    def action_reject_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['employee.ltc.advance'].browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_reject()