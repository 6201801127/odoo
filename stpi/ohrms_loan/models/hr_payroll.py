# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
from odoo.exceptions import ValidationError


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.one
    def compute_total_paid(self):
        """This compute the total paid amount of Loan.
            """
        total = 0.0
        for line in self.loan_ids:
            if line.paid:
                total += line.amount
        self.total_paid = total

    loan_ids = fields.One2many('hr.loan.line', 'payslip_id', string="Loans")
    total_paid = fields.Float(string="Total Loan Amount", compute='compute_total_paid')
    #added by sangita
    refund_id = fields.Many2one('hr.payslip')

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
        employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        if contracts:
            input_line_ids = self.get_inputs(contracts, date_from, date_to)
            input_lines = self.input_line_ids.browse([])
            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines
        return

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        for loan in lon_obj:
            for loan_line in loan.loan_lines:
                if date_from <= loan_line.date <= date_to and not loan_line.paid:
                    for result in res:
                        if result.get('code') == 'LO':
                            result['amount'] = loan_line.amount
                            result['loan_line_id'] = loan_line.id
        return res

    @api.multi
    def get_loan(self):
        """This gives the installment lines of an employee where the state is not in paid.
            """
        self.loan_ids.unlink()
        loan_list = []
        loan_id = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id),
                                                ('state', '=', 'grant')])
        loan_line_ids = self.env['hr.loan.line'].search([('loan_id', '=', loan_id.id), 
                                                            ('paid', '=', False)])
        for loan in loan_line_ids:
            print("--------------------------loan",loan.id)
            if loan.loan_id.state == 'grant':
                # loan_list.append(loan.id)
                loan_list.append((0, 0, {
                    "loan_payslip_id": loan.loan_id.id,
                    "date":loan.date,
                    "amount":loan.amount,
                    "paid":loan.paid
                }))
        self.loan_ids = loan_list
        for s in self:
            for loan in s.loan_ids:
                if loan.date <= s.date_to:
                    loan.paid = True
        return True

    #added by sangita
    @api.multi
    def compute_sheet(self):
        for s in self:
            s.get_loan()
        return super(HrPayslip, self).compute_sheet()
       
    @api.multi
    def refund_sheet(self):
        res =  super(HrPayslip,self).refund_sheet()
        self.state = 'cancel'
        for s in self:
            for loan in s.loan_ids:
                if loan.date <= s.date_to:
                    loan.paid = False
        self.refund_id = self.copy({'credit_note': True, 'name': _('Refund: ') + self.name})
        return True
         
#     @api.multi
#     def refund_sheet(self):
#         for payslip in self:
#             print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
#             copied_payslip = payslip.copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
#             print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;",copied_payslip)
#             copied_payslip.action_payslip_done()
#             print("=============================",copied_payslip.action_payslip_done())
#             payslip.state = 'cancel'
#             print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",payslip.state)
#             for loan in payslip.loan_ids:
#                 print(">>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<",loan)
#                 if loan.date <= payslip.date_to:
#                     print("'''''''''''''''''''''''''''''''''",loan.date)
#                     loan.paid = False
#                     print(";8888888888888888888888888",loan.paid)
# #         copied_payslip = self.copy({'credit_note': True, 'name': _('Refund: ') + s.name})
#             payslip.refund_id = copied_payslip
#             print("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[",payslip.refund_id)
#         formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
#         treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
# #         print"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,",copied_payslip.ids
#         return {
#             'name': ("Refund Payslip"),
#             'view_mode': 'tree, form',
#             'view_id': False,
#             'view_type': 'form',
#             'res_model': 'hr.payslip',
#             'type': 'ir.actions.do_nothing',
#             'target': 'current',
#             'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
#             'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
#             'context': {}
#         }


    @api.multi
    def action_payslip_done(self):
        for rec in self:
            loanObj = self.env['hr.loan'].sudo().search([('type_id.type_emp', '=', 'Short Term Loan'),
                                                        ('employee_id', '=', rec.employee_id.id),
                                                        ('state', '=', 'grant')])
            loan_line_id = self.env['hr.loan.line']\
                                .search([('loan_id','=',loanObj.id),('paid', '=', False), 
                                        ('date', '>=', rec.date_from),('date', '<=', rec.date_to)])
            loan_paid = sum(rec.line_ids.filtered(lambda x: x.code in ('LO','LOI')).mapped('total'))
            for loan in loan_line_id:
                loan.paid = True
                loan.loan_payslip_ref_id = rec.id
                if loan_paid != loan.amount:
                    self.env['hr.loan'].sudo().restructure_emi_ledger(rec, loanObj, loan_paid)
                    assignLoanObj = self.env['assign.loan.amount'].sudo()\
                                        .search([('employee_id', '=', rec.employee_id.id),
                                                ('installment_date', '>=', rec.date_from),
                                                ('installment_date', '<=', rec.date_to)], limit=1)
                    assignLoanObj.write({'is_paid': True})
                else:
                    loan.amount = loan_paid
                    loan.actual_paid = loan_paid
        res = super(HrPayslip, self).action_payslip_done()
        return res
    
    @api.multi
    def _get_loan_emi_amount(self, payslipObj):
        amountLis = []
        loanObjs = self.env['hr.loan'].sudo().search([('type_id.type_emp', '=', 'Short Term Loan'),
                                                    ('employee_id', '=', payslipObj.employee_id.id),
                                                    ('state', '=', 'grant')])
        loanObjs.sudo()._compute_paid_status()
        if loanObjs:
            amountLis = loanObjs.loan_lines.filtered(lambda x: x.date >= payslipObj.date_from and
                                            x.date <= payslipObj.date_to and 
                                            x.monthly_interest_amount != 0).mapped('amount')
        return amountLis[0] if len(amountLis) >= 1 else 0


    @api.multi
    def calculate_loan(self, payslip_id):
        payslipObj = self.env['hr.payslip'].sudo().browse(payslip_id)
        assignLoanObj = self.env['assign.loan.amount'].sudo()\
                            .search([('employee_id', '=', payslipObj.employee_id.id),
                                    ('installment_date', '>=', payslipObj.date_from),
                                    ('installment_date', '<=', payslipObj.date_to)], limit=1)
        if assignLoanObj:
            amount = assignLoanObj.amount
        else:
            amount = self._get_loan_emi_amount(payslipObj)
        return amount

    @api.multi
    def calculate_festival_loan(self, payslip):
        result_lis = []
        loanObjs = self.env['hr.loan'].sudo()\
                        .search([('type_id.type_emp', '=', 'Festival'),
                                ('employee_id', '=', payslip.employee_id),
                                ('state', '=', 'approve')], limit=1)
        loanObjs.sudo()._compute_paid_status()
        if loanObjs:
            result_lis = loanObjs.loan_lines.filtered(lambda x: x.date >= payslip.date_from and
                                             x.date <= payslip.date_to).mapped('amount')
        return result_lis[0] if len(result_lis) >=1 else 0

    def calculate_lo_interest(self, payslip):
        result = 0
        loan = self.env['hr.loan'].sudo().search([('type_id.type_emp', '=', 'Short Term Loan'),
                                                        ('employee_id', '=', payslip.employee_id),
                                                        ('state', '=', 'grant')])
        if loan:
            loan.sudo()._compute_paid_status()
            result = sum(loan.loan_lines.filtered(lambda x: x.date >= payslip.date_from and
                                                    x.date <= payslip.date_to and 
                                                    x.monthly_interest_amount == 0).mapped('amount'))
        return result

class AllocateLoanAmount(models.Model):
    _name = "assign.loan.amount"
    _description = "Assign Loan Amount"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    installment_date = fields.Date('Installment Date')
    amount = fields.Float('Amount')
    active = fields.Boolean('Active', default=True)
    loan_id = fields.Many2one('hr.loan', 'Loan', domain="[('state', '=', 'approve')]")
    is_paid = fields.Boolean('Is Paid')

    @api.constrains('amount', 'installment_date')
    def check_constrains(self):
        for rec in self:
            if rec.amount and rec.loan_id:
                if rec.loan_id.loan_amount < rec.amount:
                    raise ValidationError(f'Amount should be less than Loan Amount ({rec.loan_id.loan_amount})')
            if rec.installment_date and rec.loan_id:
                start_dt = rec.loan_id.dis_date
                end_dt = sorted(rec.loan_id.loan_lines.mapped('date'))[-1]
                if rec.installment_date < start_dt or rec.installment_date > end_dt:
                    raise ValidationError('Installment date should be between %s and %s' % (start_dt, end_dt))