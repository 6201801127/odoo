from odoo import models, fields, api
import time


class PaymentAdvices(models.Model):
    _name = 'pf.payment.advice'
    _description = 'PF Payment Advices'

    name = fields.Char('Name')
    date = fields.Date('Date')
    bank_id = fields.Many2one('res.bank', 'STPI Salary Account')
    cheque_no = fields.Char('Cheque No.')
    cheque_date = fields.Date('Cheque Date')
    note = fields.Text('Note')
    line_ids = fields.One2many('pf.payment.advice.line', 'advice_id', 
                                    'Payment Advice Lines')
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'),
                                ('confirm', 'Confirm')], 'State', default='draft')
    company_id = fields.Many2one('res.company', 'Company', 
                                    default=lambda self: self.env.user.company_id)
    

    @api.multi
    def action_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})
        return True

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})
        return True

    def get_total_amount(self, code=None):
        if code == 'boi':
            line_ids = self.line_ids.filtered(lambda x: x.employee_id.bank_account_id.\
                                                bank_id.name.lower().strip() == 'bank of india')
        else:
            line_ids = self.line_ids.filtered(lambda x: x.employee_id.bank_account_id.\
                                                bank_id.name.lower().strip() != 'bank of india')
        return sum(line_ids.mapped('amount'))



class PaymentAdvicesLine(models.Model):
    _name = 'pf.payment.advice.line'
    _description = 'PF Payment Advice Lines'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    bank_name = fields.Char('Bank Name')
    account_no = fields.Char('Account No.')
    ifsc_code = fields.Char('IFSC Code')
    amount = fields.Float('Amount')
    advice_id = fields.Many2one('pf.payment.advice', 'Payment Advice')