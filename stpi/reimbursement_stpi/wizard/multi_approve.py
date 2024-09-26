# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class ReimburementApprove(models.TransientModel):
    _name = "reimbursement.approve"
    _description = "Multiple Approve for reimbursements"


    @api.multi
    def reimbursement_approve_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['reimbursement'] .browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_approved()


    @api.multi
    def reimbursement_reject_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['reimbursement'].browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_reject()