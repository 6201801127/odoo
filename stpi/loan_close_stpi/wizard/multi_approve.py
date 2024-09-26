# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class loanclosemburementApprove(models.TransientModel):
    _name = "loanclose.approve"
    _description = "Multiple Approve for loancloses"


    @api.multi
    def loanclose_approve_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for loanclose in self.env['hr.loan.close'].browse(active_ids):
            if loanclose.state == 'submitted':
                loanclose.sudo().button_approved()


    @api.multi
    def loanclose_reject_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for loanclose in self.env['hr.loan.close'].browse(active_ids):
            if loanclose.state == 'submitted':
                loanclose.sudo().button_reject()