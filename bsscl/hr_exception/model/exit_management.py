from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date


class ExceptionRule(models.Model):
	_inherit = 'exception.rule'

	rule_group = fields.Selection(
		selection_add=[('exit_transfer_management', 'Exit Management'),
		],
	)
	model = fields.Selection(
		selection_add=[
			('exit.transfer.management', 'Exit Management'),
		])


class ExitTransferManagement(models.Model):
	_inherit = ['exit.transfer.management', 'base.exception']
	_name = 'exit.transfer.management'

	rule_group = fields.Selection(
		selection_add=[('exit_transfer_management', 'Exit Management')],
		default='exit_transfer_management',
	)

	@api.model
	def test_all_draft_orders (self):
		order_set=self.search([('state','=','verify')])
		order_set.test_exceptions()
		return True


	def button_verify(self):
		if self.detect_exceptions():
			return self._popup_exceptions()
		else:
			return super(ExitTransferManagement,self).button_verify()

	@api.model
	def _get_popup_action (self):
		action=self.env.ref('hr_exception.action_exit_confirm')
		return action
class Approvalslist(models.Model):
	_inherit = "approvals.list"

	def approve(self):
		res = super(Approvalslist, self).approve()
		if res:
			# print("----------------------self.model_id.model", self.model_id.model)
			if self.model_id.model == 'exit.transfer.management':
				self.resource_ref.button_verify()
		return res

	def reject(self):
		res = super(Approvalslist, self).reject()
		if res:
			if self.model_id.model == 'exit.transfer.management':
				self.resource_ref.action_refuse()
		return res

