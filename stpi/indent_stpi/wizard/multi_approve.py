# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class IssueRequestApprove(models.TransientModel):
    _name = "issuestock.approve"
    _description = "Multiple Approve for issuestocks"


    @api.multi
    def issuestock_approve_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['issue.request'].browse(active_ids):
            if rei.state == 'to_approve':
                rei.sudo().button_approved()


    @api.multi
    def issuestock_reject_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['issue.request'].browse(active_ids):
            if rei.state == 'to_approve':
                rei.sudo().button_reject()