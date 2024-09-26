from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_payslip','Hr Payslip'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.payslip', 'Hr Payslip'),
            ('hr.payslip.line','Hr Payslip Line'),
        ])

class HrPayslip(models.Model):
    _inherit = ['hr.payslip', 'base.exception']
    _name = 'hr.payslip'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_payslip','Hr Payslip')],
        default='hr_payslip',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.constrains('ignore_exception','line_ids','state')
    def sale_check_exception(self):
        for rec in self:
            if rec.state == 'done':
                rec._check_exception()

    @api.onchange('line_ids')
    def onchange_ignore_exception(self):
        if self.state == 'purchase':
            self.ignore_exception = False

    def action_payslip_done(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(HrPayslip, self).action_payslip_done()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_hr_payslip_confirm')
        return action

    def _hr_payslip_get_lines(self):
        self.ensure_one()
        return self.line_ids


    def action_payslip_cancel(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'hr.payslip' + ',' + str(self.id)),
                                                       ('state', '=', 'pending_approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Payslip for Cancel.'))
        return super(HrPayslip, self).action_payslip_cancel()


class PayslipLine(models.Model):
    _inherit = ['hr.payslip.line', 'base.exception']
    _name = 'hr.payslip.line'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('hr_payslip_line','Hr Payslip Line')],
        default='hr_payslip_line',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.payslip':
                self.resource_ref.action_payslip_done()
        return res

    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'hr.payslip':
                self.resource_ref.action_payslip_cancel()
        return res



class AddCHarterPayslip(models.Model):
    _inherit = ['hr.payslip','mail.thread', 'mail.activity.mixin']
    _name = 'hr.payslip'