from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_employee_transfer','HR Employee Transfer'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.employee.transfer', 'HR Employee Transfer')
        ])

class HREmployeeTransfer(models.Model):
    _inherit = ['hr.employee.transfer', 'base.exception']
    _name = 'hr.employee.transfer'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('hr_employee_transfer','HR Employee Transfer')],
        default='hr_employee_transfer',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.multi
    def button_approved(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(HREmployeeTransfer, self).button_approved()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_employee_transfer_confirm')
        return action


    @api.multi
    def button_rejected(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.employee.transfer' + ',' + str(self.id)),
                                                       ('state', '=', 'approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Transfer orders for Cancel.'))
        return super(HREmployeeTransfer, self).button_rejected()


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.employee.transfer':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.employee.transfer':
                self.resource_ref.button_rejected()
        return res