# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class loanmburementApprove(models.TransientModel):
    _name = "loan.approve"
    _description = "Multiple Approve for loans"


    @api.multi
    def loan_approve_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for loan in self.env['hr.loan'].browse(active_ids):
            if loan.state == 'waiting_approval_1' or loan.state == 'waiting_approval_2':
                loan.sudo().action_approve()
                loan.onchange_loan_state()


    @api.multi
    def loan_reject_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for loan in self.env['hr.loan'].browse(active_ids):
            if loan.state == 'waiting_approval_1' or loan.state == 'waiting_approval_2':
                loan.sudo().action_refuse()
                loan.onchange_loan_state()