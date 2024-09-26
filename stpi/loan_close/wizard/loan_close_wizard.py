from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LoanCloseWizard(models.TransientModel):
    _name = 'hr.loan.close.wizard'
    _description = "Installment Payment Close Wizard"

    @api.depends('unpaid_loan_lines','unpaid_loan_lines.paid')
    def get_loan_close_lines(self):
            temp = 0.0
            for line in self.unpaid_loan_lines:
                if line.paid:
                    temp += line.amount
                    # print("amount===============>>>>",temp,line.amount)
            self.loan_amount = temp

    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # credit_account_id = fields.Many2one('account.account', string="Credit Account")
    loan_amount = fields.Float(string="Loan Amount",compute='get_loan_close_lines')
    # payment_account_id = fields.Many2one('account.account', string="Payment Account")
    unpaid_loan_lines = fields.One2many('hr.loan.line.unpaid','un_loan_id', string="Loan Line", index=True)
    remarks = fields.Char(string='Remarks')


    @api.multi
    def confirm_loan_payment(self):
        # line = []
        # moves = self.env['account.move']
        # # if not self.loan_id.journal_id.id:
        # #     raise UserError("Please Select Journal on Loan Request")
        # # else:
        # #     Journal = self.loan_id.journal_id.id
        # # if not self.payment_account_id.id:
        # #     raise UserError("Please Select Payment Account on Loan Request")
        # if not self.loan_amount > 0.0:
        #     raise UserError("Please Select Loan Lines To Be Paid")
        # # print("journal_id==============>>",Journal)
        # values = {
        #     # 'journal_id': Journal,
        #     'journal_id': 1,
        #     'ref': self.loan_id.name ,
        #     'line_ids': [(6, 0, line)],
        # }
        # res = moves.create(values)
        # debit_line = self.env['account.move.line'].with_context(
        #     check_move_validity=False).create({
        #     'move_id': res.id,
        #     'account_id': 1,
        #     # 'account_id': self.payment_account_id.id,
        #     'name': self.loan_id.name,
        #     'debit': abs(self.loan_amount) if self.loan_amount else 0.0,
        # })
        # credit_line = self.env['account.move.line'].with_context(
        #     check_move_validity=False).create({
        #     'move_id': res.id,
        #     'account_id': 1,
        #     # 'account_id': self.credit_account_id.id,
        #     'name': self.loan_id.name,
        #     'credit': abs(self.loan_amount) if self.loan_amount else 0.0,
        # })
        # res.line_ids += debit_line
        # res.line_ids += credit_line
        # res.post()
        # self.loan_id.total_paid_amount += self.loan_amount
        # self.loan_id.loan_move_ids += res
        for lines in self.unpaid_loan_lines:
            if lines.paid:
                lines.loan_line_id.paid = True






class UnpaidInstallmentLine(models.TransientModel):
    _name = "hr.loan.line.unpaid"
    _description = "Installment Line"

    un_loan_id = fields.Many2one('hr.loan.close.wizard',string="Wizard ref")
    date = fields.Date(string="Payment Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount")
    paid = fields.Boolean(string="To be Paid", default=True)
    loan_line_id = fields.Many2one('hr.loan.line', string="Loan line Ref.")
    payslip_id = fields.Many2one('hr.payslip')
