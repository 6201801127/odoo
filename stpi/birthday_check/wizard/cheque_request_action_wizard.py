# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoiceConfirm(models.TransientModel):
    _name = "hr.employee.action.confirm"
    _description = "HR Employee Cheque Action"


    @api.multi
    def cheque_requests_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['cheque.requests'].browse(active_ids):
            if employee.state == 'to_approve':
                employee.sudo().button_approved()


    @api.multi
    def cheque_requests_action_reject_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['cheque.requests'].browse(active_ids):
            if employee.state == 'to_approve':
                employee.sudo().button_reject()