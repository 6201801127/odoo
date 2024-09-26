from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_expense_sheet', 'Hr Expense'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.expense.sheet', 'Hr Expense'),
            ('hr.expense', 'Hr Expense Line')
        ])


class HrExpense(models.Model):
    _inherit = ['hr.expense.sheet', 'base.exception']
    _name = 'hr.expense.sheet'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_expense_sheet', 'Hr Expense')],
        default='hr_expense_sheet',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception','expense_line_ids','state')
    def sale_check_exception(self):
        if self.state == 'approve':
            self._check_exception()

    @api.onchange('expense_line_ids')
    def onchange_ignore_exception(self):
        if self.state == 'approve':
            self.ignore_exception = False

    @api.multi
    def reset_expense_sheets(self):
        # print("-----------------reset_expense_sheets-")
        res = super(HrExpense, self).reset_expense_sheets()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    def _hr_expense_sheet_get_lines(self):
        self.ensure_one()
        return self.expense_line_ids


    @api.multi
    def approve_expense_sheets(self):
        # print("------------approve_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            return self._popup_exceptions()
        else:
            return super(HrExpense, self).approve_expense_sheets()


    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_expense_confirm')
        return action

    @api.multi
    def reset_expense_sheets(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.expense.sheet' + ',' + str(self.id)),
                                                       ('state', '=', 'pending_approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Expense for reset.'))
        return super(HrExpense, self).reset_expense_sheets()


class HrExpenseLine(models.Model):
    _inherit = ['hr.expense', 'base.exception']
    _name = 'hr.expense'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('expense_line', 'Expense Line')],
        default='expense_line',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.expense.sheet':
                self.resource_ref.approve_expense_sheets()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.expense.sheet':
                self.resource_ref.reset_expense_sheets()
        return res
