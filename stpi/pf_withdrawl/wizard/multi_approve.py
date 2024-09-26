# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class pfmburementApprove(models.TransientModel):
    _name = "pf.approve"
    _description = "Multiple Approve for pfs"


    @api.multi
    def pf_approve_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for pf in self.env['pf.widthdrawl'].browse(active_ids):
            if pf.state == 'to_approve':
                pf.sudo().button_approved()


    @api.multi
    def pf_reject_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for pf in self.env['pf.widthdrawl'].browse(active_ids):
            if pf.state == 'to_approve':
                pf.sudo().button_reject()