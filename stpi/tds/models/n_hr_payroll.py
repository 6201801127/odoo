# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    it_tax_payment_id = fields.Many2one('tax.payment', string="IT Installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.one
    def compute_total_paid_tax(self):
        """This compute the total paid amount of Loan.
            """
        total = 0.0
        for line in self.tax_payment_ids:
            if line.paid:
                total += line.amount
        self.total_paid_tax = total


    tax_payment_ids = fields.One2many('tax.payment', 'payslip_id', string="IT Declaration lines")
    total_paid_tax = fields.Float(string="Total Tax Amount", compute='compute_total_paid_tax')
    #added by sangita
    refund_id_tax = fields.Many2one('hr.payslip')

    # @api.onchange('employee_id', 'date_from', 'date_to')
    # def onchange_employee_get_it(self):
    #     if (not self.employee_id) or (not self.date_from) or (not self.date_to):
    #         return

    #     employee = self.employee_id
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     contract_ids = []

    #     ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
    #     locale = self.env.context.get('lang') or 'en_US'
    #     self.name = _('Salary Slip of %s for %s') % (
    #     employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
    #     self.company_id = employee.company_id

    #     if not self.env.context.get('contract') or not self.contract_id:
    #         contract_ids = self.get_contract(employee, date_from, date_to)
    #         if not contract_ids:
    #             return
    #         self.contract_id = self.env['hr.contract'].sudo().browse(contract_ids[0])

    #     if not self.contract_id.struct_id:
    #         return
    #     self.struct_id = self.contract_id.struct_id

    #     # computation of the salary input
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
    #     worked_days_lines = self.worked_days_line_ids.browse([])
    #     for r in worked_days_line_ids:
    #         worked_days_lines += worked_days_lines.new(r)
    #     self.worked_days_line_ids = worked_days_lines
    #     if contracts:
    #         input_line_ids = self.get_inputs(contracts, date_from, date_to)
    #         input_lines = self.input_line_ids.browse([])
    #         for r in input_line_ids:
    #             input_lines += input_lines.new(r)
    #         self.input_line_ids = input_lines
    #     return

    # def get_inputs(self, contract_ids, date_from, date_to):
    #     """This Compute the other inputs to employee payslip.
    #                        """
    #     res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
    #     contract_obj = self.env['hr.contract']
    #     emp_id = contract_obj.browse(contract_ids[0].id).employee_id
    #     lon_obj = self.env['hr.declaration'].search([('employee_id', '=', emp_id.id), ('state', '!=', 'rejected')])
    #     for tax in lon_obj:
    #         for tax_line in tax.tax_payment_ids:
    #             if date_from <= tax_line.date <= date_to and not tax_line.paid:
    #                 for result in res:
    #                     if result.get('code') == 'IT':
    #                         result['amount'] = tax_line.amount
    #                         # result['it_tax_payment_id'] = tax_line.id
    #     return res

    @api.multi
    def get_income_tax(self):
        """This gives the installment lines of an employee where the state is not in paid.
            """
        for rec in self:
            tax_payment_ids = self.env['tax.payment'].search([('tax_payment_id.employee_id', '=', rec.employee_id.id), 
                                                            ('paid', '=', False), ('tax_payment_id.state', '!=', 'rejected')])
            rec.tax_payment_ids = tax_payment_ids
        return True


    #added by sangita
    @api.multi
    def compute_sheet(self):
        for rec in self:
            daterange_obj = self.env['date.range'].sudo().search([('date_start', '<=', rec.date_from), 
                                                                    ('date_end', '>=', rec.date_to),
                                                                    ('tds', '=', True)])
            tds_obj = self.env['hr.declaration'].search([('employee_id', '=', rec.employee_id.id), 
                                                            ('state', '!=', 'rejected'),
                                                            ('date_range', '=', daterange_obj.id)])
            tds_obj.button_compute_tax(date_to=rec.date_to)
            rec.get_income_tax()
        res = super(HrPayslip, self).compute_sheet()
        return res
       
    @api.multi
    def refund_sheet(self):
        res =  super(HrPayslip,self).refund_sheet()
        self.state = 'cancel'
        for s in self:
            for loan in s.tax_payment_ids:
                if loan.date <= s.date_to:
                    loan.paid = False
        self.refund_id_tax = self.copy({'credit_note': True, 'name': _('Refund: ') + self.name})
        return True
         
#

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            rec.tax_payment_ids.filtered(lambda x: x.date <= rec.date_to and x.date >= rec.date_from).write({'paid': True, 'branch_id': rec.branch_id.id})
            for line in rec.tax_payment_ids:
                line.mona_payslip_id = rec.id if line.paid else False
            tds = self.env['misc.allowance.deduct'].search([('salary_rule_id.code', '=', 'TDS'),
                                                        ('employee_id', '=', rec.employee_id.id),
                                                        ('date', '>=', rec.date_from),
                                                        ('date', '<=', rec.date_to)])
            if tds:
                tds.active = False
        return res