# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PfTransfer(models.Model):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "employee.pf.transfer.wizard"
    _description = "PF Transfer"

    employee_pf = fields.Many2one('pf.employee')
    employee_pf_details = fields.One2many('employee.pf.transfer.details','wizard_emp_transfer', string='PF Transfer Details')




    @api.multi
    def confirm_button(self):
        pf_details_ids = []
        for line in self.employee_pf_details:
            pf_details_ids.append((0, 0, {
                'pf_details_id': self.employee_pf.id,
                'employee_id': self.employee_pf.employee_id.id,
                'type': line.type,
                'pf_code': line.pf_code,
                'description': line.description,
                'date': line.date,
                'amount': line.amount,
                'reference': line.reference,
            }))
        self.employee_pf.pf_details_ids = pf_details_ids




class PFTransferDetails(models.Model):
    _name = 'employee.pf.transfer.details'
    _description = 'Employee PF Transfer Details'

    wizard_emp_transfer = fields.Many2one('employee.pf.transfer.wizard')
    employee_id = fields.Many2one('hr.employee')
    date = fields.Date('Date')
    type = fields.Selection([
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
    ], string="Type")
    # pf_code = fields.Char(string='PF code')
    pf_code = fields.Selection([('CEPF', 'MPF'), ('VCPF', 'VPF'),
                                ('CPF', 'EPF'), ('CEPF + VCPF', 'MPF + VPF')], string='PF Code')
    description = fields.Char(string='Description')
    amount = fields.Float('Amount')
    reference = fields.Char('Reference')