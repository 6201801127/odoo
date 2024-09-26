# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class TourRequestApprove(models.TransientModel):
    _name = "employee.tour.claim.approve"
    _description = "Multiple Approve for hr declarations"


    @api.multi
    def action_approve_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['employee.tour.claim'].browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_approved()


    @api.multi
    def action_reject_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for rei in self.env['employee.tour.claim'].browse(active_ids):
            if rei.state == 'waiting_for_approval':
                rei.sudo().button_reject()