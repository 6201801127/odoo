from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('reimbursement','Reimbursement'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('reimbursement', 'Reimbursement'),
        ])

class Reimbursement(models.Model):
    _inherit = ['reimbursement', 'base.exception']
    _name = 'reimbursement'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('reimbursement','Reimbursement')],
        default='reimbursement',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True
    #
    # @api.constrains('ignore_exception','relative_ids','state')
    # def sale_check_exception(self):
    #     if self.state == 'done':
    #         self._check_exception()
    #
    # @api.onchange('relative_ids')
    # def onchange_ignore_exception(self):
    #     if self.state == 'purchase':
    #         self.ignore_exception = False

    @api.multi
    def button_approved(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(Reimbursement, self).button_approved()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_reimbursement_confirm')
        return action

    # def _reimbursement_get_lines(self):
    #     self.ensure_one()
    #     return self.relative_ids


    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'reimbursement' + ',' + str(self.id)),
                                                       ('state', '=', 'waiting_for_approval')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Reimbursement for Cancel.'))
        return super(Reimbursement, self).button_reject()

#
# class ReimbursementLine(models.Model):
#     _inherit = ['reimbursement.relatives', 'base.exception']
#     _name = 'reimbursement.relatives'
#     _order = 'main_exception_id asc'
#
#     rule_group = fields.Selection(
#         selection_add=[('reimbursement_line','Reimbursement Line')],
#         default='reimbursement_line',
#     )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'reimbursement':
                self.resource_ref.button_approved()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'reimbursement':
                self.resource_ref.button_reject()
        return res
