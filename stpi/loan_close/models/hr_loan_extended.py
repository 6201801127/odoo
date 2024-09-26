# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm


class HrLoan(models.Model):
    _inherit = 'hr.loan'
    _description = "Loan Request"

    # @api.depends('loan_move_ids')
    # def get_loan_moves_count(self):
    #     for record in self:
    #         if record.loan_move_ids:
    #             record.loan_moves_count = len(record.loan_move_ids)
    #
    # loan_move_ids = fields.Many2many("account.move", string='Moves', readonly=True,copy=False)
    # loan_moves_count = fields.Integer(string='Moves count', copy=False,compute="get_loan_moves_count")

    @api.multi
    def loan_close_approve(self):
        ctx = self._context.copy()
        view = self.env.ref('loan_close.form_view_loan_close_wizard')
        # print("self.loan_lines----------------",self.loan_lines,ctx)
        unpaid_lines = self.loan_lines.search([('paid','=',False),('loan_id','=',self.id)])
        # print("Unpaid Lines ============>>>>",unpaid_lines)
        wiz = self.env['hr.loan.close.wizard'].create({
            'employee_id':self.employee_id.id,
            # 'payment_account_id': self.emp_account_id.id,
            'loan_id':self.id,
        })
        for lines in unpaid_lines:
            # print("Got the lines============>>>",lines)
            self.env['hr.loan.line.unpaid'].create({
                'un_loan_id': wiz.id,
                'loan_line_id': lines.id,
                'amount': lines.amount,
                'paid': True    ,

                'date':lines.date,
            })
        return {
            'name': _('Close Loan'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.loan.close.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id':wiz.id,
            'target': 'new',
        }

    # @api.multi
    # def open_loan_moves(self):
    #     loan_moves = self.mapped('loan_move_ids')
    #     action = self.env.ref('account.action_move_journal_line').read()[0]
    #     if len(loan_moves) > 1:
    #         action['domain'] = [('id', 'in', loan_moves.ids)]
    #     elif len(loan_moves) == 1:
    #         action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
    #         action['res_id'] = loan_moves.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action
