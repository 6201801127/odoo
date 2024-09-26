from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('tour_request', 'Tour Request'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('tour.request', 'Tour Request'),
            ('tour.request.journey', 'Tour Request Line'),
        ])


class EmployeeTourRequest(models.Model):
    _inherit = ['tour.request', 'base.exception']
    _name = 'tour.request'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('tour_request', 'Tour Request')],
        default='tour_request',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'waiting_for_approval')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception', 'employee_journey', 'state')
    def sale_check_exception(self):
        if self.state == 'approved':
            self._check_exception()

    @api.onchange('employee_journey')
    def onchange_ignore_exception(self):
        if self.state == 'approved':
            self.ignore_exception = False


    @api.multi
    def action_cancel(self):
        # print("-----------------reset_expense_sheets-")
        res = super(EmployeeTourRequest, self).action_cancel()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search(
            [('resource_ref', '=', 'tour.request' + ',' + str(self.id)),
             ('state', '=', 'waiting_for_approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(EmployeeTourRequest, self).button_reject()

    def _employee_tour_request_get_lines(self):
        self.ensure_one()
        return self.employee_journey

    @api.multi
    def button_approved(self):
        # print("------------approved_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            self.action_app = True
            return self._popup_exceptions()

        else:
            return super(EmployeeTourRequest, self).button_approved()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_employee_tour_request_confirm')
        return action


class EmployeeTourRequestLine(models.Model):
    _inherit = ['tour.request.journey', 'base.exception']
    _name = 'tour.request.journey'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('tour_request_journey', 'Tour Request Line')],
        default='tour_request_journey',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'tour.request':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'tour.request':
                self.resource_ref.button_reject()
        return res
