from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError

class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('appraisal_main','Appraisal HoD'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('appraisal.main', 'Appraisal HoD')
        ])

class AppraisalHod(models.Model):
    _inherit = ['appraisal.main', 'base.exception']
    _name = 'appraisal.main'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('appraisal_main','Appraisal')],
        default='appraisal_main',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.test_exceptions()
        return True

    @api.multi
    def button_hod_reviewed(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        else:
            return super(AppraisalHod, self).button_hod_reviewed()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('hr_exception.action_appraisal_main_line_confirm')
        return action


    @api.multi
    def button_reject(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'appraisal.main' + ',' + str(self.id)),
                                                       ('state', '=', 'line_manager_review')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Transfer orders for Cancel.'))
        return super(AppraisalHod, self).button_reject()


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'appraisal.main':
                self.resource_ref.button_hod_reviewed()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'appraisal.main':
                self.resource_ref.button_reject()
        return res