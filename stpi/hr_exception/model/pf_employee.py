from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('pf_employee', 'PF Employee'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('pf.employee', 'PF Employee'),
            ('pf.employee.details', 'Pf Employee Details'),
        ])


class PFEmployee(models.Model):
    _inherit = ['pf.employee', 'base.exception']
    _name = 'pf.employee'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('pf_employee', 'PF Employee')],
        default='pf_employee',
    )

#     @api.model
#     def test_all_draft_orders(self):
#         order_set = self.search([('state', '=', 'to_approve')])
#         order_set.test_exceptions()
#         return True
# 
#     @api.constrains('ignore_exception', 'detail_of_journey', 'state')
#     def sale_check_exception(self):
#         if self.state == 'approved':
#             self._check_exception()
# 
# 
#     @api.onchange('detail_of_journey')
#     def onchange_ignore_exception(self):
#         if self.state == 'approved':
#             self.ignore_exception = False


    @api.multi
    def button_reject(self):
        # print("-----------------reset_expense_sheets-")
        res = super(PFEmployee, self).button_reject()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'pf.employee' + ',' + str(self.id)),
                                                       ])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Loan for Refuse.'))
        return super(PFEmployee, self).button_reject()

    def _employee_pf_get_lines(self):
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
            return super(PFEmployee, self).button_approved()



    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_pf_employee_confirm')
        return action


class EmployeeLtcClaimLine(models.Model):
    _inherit = ['pf.employee.details', 'base.exception']
    _name = 'pf.employee.details'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('pf_employee_details', 'PF Employee Details')],
        default='pf_employee_details',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'pf.employee':
                self.resource_ref.button_approved()

        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'pf.employee':
                self.resource_ref.button_reject()
        return res
