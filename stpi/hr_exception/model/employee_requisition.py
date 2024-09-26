from odoo import api, models, fields


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_requisition', 'Hr Requisition')],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.requisition', 'Hr Requisition'),

        ])

class HrRequisitionException(models.Model):
    _inherit = ['hr.requisition', 'base.exception']
    _name = 'hr.requisition'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_requisition', 'Hr Requisition')],
        default='hr_requisition',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'approval')])
        order_set.test_exceptions()
        return True

    #
    # @api.constrains('ignore_exception', 'budget_line_ids', 'state')
    # def hr_requisition_check_exception(self):
    #     if self.state == 'approved':
    #         self._check_exception()
    #
    # @api.onchange('budget_line_ids')
    # def onchange_ignore_exception(self):
    #     if self.state == 'approved':
    #         self.ignore_exception = False

    @api.multi
    def button_approved(self):
        if self.detect_exceptions():

            return self._popup_exceptions()
        else:
            return super(HrRequisitionException, self).button_approved()
    #
    # def _hr_requisition_get_lines(self):
    #     self.ensure_one()
    #     return self.budget_line_ids

    @api.model
    def _get_popup_action(self):
        # print("----------------------------_get_popup_action")
        action = self.env.ref('hr_exception.action_hr_requisition_confirm')
        return action


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.requisition':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res=super(Approvalslist,self).reject()
        if res:
            if self.model_id.model == 'hr.requisition':
                self.resource_ref.cancel()
        return res
