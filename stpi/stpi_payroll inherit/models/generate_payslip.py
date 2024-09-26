# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def _employee_domain(self):
        domain = []
        branch_id = self._context.get('branch_id')
        branch_ids = self.env.user.branch_ids.ids
        if branch_id in branch_ids:
            domain += [['branch_id', '=', branch_id]]
        else:
            domain += [['branch_id', 'in', branch_ids]]
        return domain



    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    domain=_employee_domain)