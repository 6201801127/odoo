from odoo import fields,models,api
from odoo.exceptions import ValidationError


class AllowedLoanAmount(models.Model):
    _name='allowed.loan.amount'
    _description ='Allowed Loan Amount'

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    loan_type = fields.Many2one('loan.type' ,string='Loan Type')
    amount = fields.Float('Amount')


    @api.constrains('pay_level_id', 'loan_type')
    def _check_pay_level_id(self):
        for rec in self:
            if rec.pay_level_id and rec.loan_type:
                if rec.search([('pay_level_id', '=', rec.pay_level_id.id), ('loan_type', '=', rec.loan_type.id)]) - self:
                    raise ValidationError('This combination of pay level and loan type already exists')