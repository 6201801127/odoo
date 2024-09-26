from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_loan_close', 'Hr Loan Close'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.loan.close', 'Hr Loan Close'),
            # ('hr.loan.line.unpaid', 'HR Loan Line Unpaid'),
        ])

class HrLoan(models.Model):
    _inherit = ['hr.loan.close', 'base.exception']
    _name = 'hr.loan.close'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('hr_loan_close', 'Hr Loan Close')],
        default='hr_loan_close',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'submitted')])
        order_set.test_exceptions()
        return True
    #
    # @api.constrains('ignore_exception','unpaid_loan_lines','state')
    # def sale_check_exception(self):
    #     if self.state == 'approved':
    #         self._check_exception()
    #
    # @api.onchange('unpaid_loan_lines')
    # def onchange_ignore_exception(self):
    #     if self.state == 'approved':
    #         self.ignore_exception = False

    @api.multi
    def action_cancel(self):
        # print("-----------------reset_expense_sheets-")
        res = super(HrLoan, self).action_cancel()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.loan.close' + ',' + str(self.id)),
                                                       ('state', '=', 'submitted')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(HrLoan, self).button_reject()
    #
    # def _hr_loan_get_lines(self):
    #     self.ensure_one()
    #     return self.unpaid_loan_lines

    @api.multi
    def button_approved(self):
        # print("------------approve_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            return self._popup_exceptions()
        else:
            return super(HrLoan, self).button_approved()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_loan_close_confirm')
        return action

# class HrLoanLine(models.Model):
#     _inherit = ['hr.loan.line.unpaid', 'base.exception']
#     _name = 'hr.loan.line.unpaid'
#     _order = 'main_exception_id asc'
#
#     rule_group = fields.Selection(
#         selection_add=[('hr_loan_line_unpaid', 'HR Loan Line Unpaid')],
#         default='hr_loan_line_unpaid',
#     )

class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.loan.close':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.loan.close':
                self.resource_ref.button_reject()
        return res