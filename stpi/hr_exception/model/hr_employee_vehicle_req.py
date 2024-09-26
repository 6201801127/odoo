from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('employee_fleet','Employee Vehicle Request'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('employee.fleet', 'HR Employee Vehicle Request')
        ])

class HREmployeeVehicle(models.Model):
    _inherit = ['employee.fleet', 'base.exception']
    _name = 'employee.fleet'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('employee_fleet','HR Employee Vehicle Request')],
        default='employee_fleet',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.multi
    def approve(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(HREmployeeVehicle, self).approve()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_employee_vehicle_req_confirm')
        return action


    @api.multi
    def reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.employee.transfer' + ',' + str(self.id)),
                                                       ('state', '=', 'approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Transfer orders for Cancel.'))
        return super(HREmployeeVehicle, self).reject()


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'employee.fleet':
                self.resource_ref.approve()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'employee.fleet':
                self.resource_ref.reject()
        return res