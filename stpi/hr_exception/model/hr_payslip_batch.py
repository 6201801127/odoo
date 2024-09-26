from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_payslip_run','Hr Payslip Batch'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.payslip.run', 'Hr Payslip Batch'),
        ])

class HrPayslip(models.Model):
    _inherit = ['hr.payslip.run', 'base.exception']
    _name = 'hr.payslip.run'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_payslip_run','Hr Payslip Batch')],
        default='hr_payslip_run',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True


    @api.multi
    def close_payslip_run(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(HrPayslip, self).close_payslip_run()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_payslip_run_confirm')
        return action


    @api.multi
    def draft_payslip_run(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.payslip.run' + ',' + str(self.id)),
                                                       ('state', '=', 'draft')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Payslip for Cancel.'))
        return super(HrPayslip, self).draft_payslip_run()



class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.payslip.run':
                self.resource_ref.forward_payslip_run()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.payslip.run':
                self.resource_ref.draft_payslip_run()
        return res
