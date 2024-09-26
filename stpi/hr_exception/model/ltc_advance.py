from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('employee_ltc_advance', 'Employee LTC Advance'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('employee.ltc.advance', 'Employee LTC Advance')
        ])


class EmployeeLtcAdvance(models.Model):
    _inherit = ['employee.ltc.advance', 'base.exception']
    _name = 'employee.ltc.advance'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('employee_ltc_advance', 'Employee LTC Advance')],
        default='employee_ltc_advance',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'to_approve')])
        order_set.test_exceptions()
        return True


    @api.multi
    def action_cancel(self):
        # print("-----------------reset_expense_sheets-")
        res = super(EmployeeLtcAdvance, self).action_cancel()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search(
            [('resource_ref', '=', 'employee.ltc.advance' + ',' + str(self.id)),
             ('state', '=', 'to_approve')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(EmployeeLtcAdvance, self).button_reject()


    @api.multi
    def button_approved(self):
        # print("------------approved_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            self.action_app = True
            return self._popup_exceptions()

        else:
            return super(EmployeeLtcAdvance, self).button_approved()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_employee_ltc_advance_confirm')
        return action


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'employee.ltc.advance':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'employee.ltc.advance':
                self.resource_ref.button_reject()
        return res
