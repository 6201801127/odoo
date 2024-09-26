from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('employee_tour_claim', 'Tour Claim'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('employee.tour.claim', 'Tour Claim'),
            ('tour.claim.journey', 'Tour Claim Line'),
        ])


class EmployeeTourClaim(models.Model):
    _inherit = ['employee.tour.claim', 'base.exception']
    _name = 'employee.tour.claim'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('employee_tour_claim', 'Tour Claim')],
        default='employee_tour_claim',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'submitted')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception', 'detail_of_journey', 'state')
    def sale_check_exception(self):
        if self.state == 'approved':
            self._check_exception()
        if self.state == 'paid':
            self._check_exception()

    @api.onchange('detail_of_journey')
    def onchange_ignore_exception(self):
        if self.state == 'approved':
            self.ignore_exception = False
        if self.state == 'paid':
            self.ignore_exception = False

    @api.multi
    def button_reject(self):
        # print("-----------------reset_expense_sheets-")
        res = super(EmployeeTourClaim, self).button_reject()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'employee.tour.claim' + ',' + str(self.id)),
                                                       ('state', '=', 'submitted')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(EmployeeTourClaim, self).button_reject()

    def _employee_tour_claim_get_lines(self):
        self.ensure_one()
        return self.detail_of_journey

    @api.multi
    def button_approved(self):
        # print("------------approved_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            self.action_app = True
            return self._popup_exceptions()

        else:
            return super(EmployeeTourClaim, self).button_approved()

    @api.multi
    def button_pay(self):
        # print("------------approved_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            self.action_clos = True
            return self._popup_exceptions()

        else:
            return super(EmployeeTourClaim, self).button_pay()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_employee_tour_claim_confirm')
        return action


class EmployeeTourClaimLine(models.Model):
    _inherit = ['tour.claim.journey', 'base.exception']
    _name = 'tour.claim.journey'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('tour_claim_journey', 'Tour Claim Line')],
        default='tour_claim_journey',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'employee.tour.claim':
                if self.resource_ref.action_app:
                    self.resource_ref.button_approved()
                    self.resource_ref.action_app = False
                if self.resource_ref.action_clos:
                    self.resource_ref.button_pay()
                    self.resource_ref.confirm_loan_payment()
                    self.resource_ref.action_clos = False

        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'employee.tour.claim':
                self.resource_ref.button_reject()
        return res
