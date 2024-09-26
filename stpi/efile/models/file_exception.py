from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('folder_master', 'Files'),
                       ],
    )
    model = fields.Selection(
        selection_add=[
            ('folder.master', 'Files')
        ])

class FolderMaster(models.Model):
    _inherit = ['folder.master', 'base.exception']
    _name = 'folder.master'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('folder_master', 'Files')],
        default='folder_master',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'in_progress')])
        order_set.test_exceptions()
        return True


    @api.multi
    def action_cancel(self):
        # print("-----------------reset_expense_sheets-")
        res = super(FolderMaster, self).action_cancel()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    @api.multi
    def action_refuse(self):
        exception = self.env['approvals.list'].search([('resource_ref', '=', 'folder.master' + ',' + str(self.id)),
                                                       ('state', '=', 'in_progress')])
        # print("------------------exception",exception)
        if exception:
            raise UserError(_('Do not allow Pending Approval Files for Refuse.'))
        return super(FolderMaster, self).action_refuse()


    @api.multi
    def button_close(self):
        # print("------------approve_expense_sheets")
        if self.detect_exceptions():
            # print("--------------_popup_exceptions",self._popup_exceptions)
            return self._popup_exceptions()
        else:
            return super(FolderMaster, self).button_close()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('smart_office.action_folder_master_confirm')
        return action


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'folder.master':
                self.resource_ref.button_close()
        return res

    @api.multi
    def reject(self):
        res = super(Approvalslist, self).reject()
        if res:
            if self.model_id.model == 'folder.master':
                self.resource_ref.action_cancel()
        return res