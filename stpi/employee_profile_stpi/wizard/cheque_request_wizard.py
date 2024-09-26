# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoiceConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "hr.employee.confirm"
    _description = "HR Employee"




    @api.multi
    def cheque_requests_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['hr.employee'].browse(active_ids):
            if employee.cheque_requested == 'no':
                cheque_request = self.env['cheque.requests'].create(
                    {
                        'employee_id': employee.id,
                        'identify_id': employee.identify_id,
                        'name': employee.name,
                        'job_id': employee.job_id.id,
                        'department_id': employee.department_id.id,
                        'gender': employee.gender,
                        'birthday': employee.birthday,
                        'state': 'draft',
                    }
                )
                employee.cheque_requested = 'yes'
