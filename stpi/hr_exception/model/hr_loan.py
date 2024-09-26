from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_loan', 'Hr Loan'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.loan', 'Hr Loan'),
            ('hr.loan.line', 'Hr Loan Line'),
        ])

class HrLoan(models.Model):
    _inherit = ['hr.loan', 'base.exception']
    _name = 'hr.loan'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_loan', 'Hr Loan')],
        default='hr_loan',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'waiting_approval_1')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception','loan_lines','state')
    def sale_check_exception(self):
        if self.state == 'approve':
            self._check_exception()

    @api.onchange('loan_lines')
    def onchange_ignore_exception(self):
        if self.state == 'approve':
            self.ignore_exception = False

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
    def action_refuse(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.loan' + ',' + str(self.id)),
                                                       ('state', '=', 'pending_approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(HrLoan, self).action_refuse()

    def _hr_loan_get_lines(self):
        self.ensure_one()
        return self.loan_lines

    @api.multi
    def action_approve(self):
        # print("------------approve_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            return self._popup_exceptions()
        else:
            return super(HrLoan, self).action_approve()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_loan_confirm')
        return action

class HrLoanLine(models.Model):
    _inherit = ['hr.loan.line', 'base.exception']
    _name = 'hr.loan.line'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('hr_loan_line', 'Hr Loan Line')],
        default='hr_loan_line',
    )

class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.loan':
                self.resource_ref.action_approve()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.loan':
                self.resource_ref.action_cancel()
        return res