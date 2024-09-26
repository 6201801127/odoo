from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date


class ExceptionRule(models.Model):
	_inherit = 'exception.rule'

	rule_group = fields.Selection(
		selection_add=[('account_payment', 'Payment'),
		],
	)
	model = fields.Selection(
		selection_add=[
			('account.payment', 'Account Payment'),
		])


class AccountPayment(models.Model):
	_inherit = ['account.payment', 'base.exception']
	_name = 'account.payment'

	rule_group = fields.Selection(
		selection_add=[('account_payment', 'Account Payment')],
		default='account_payment',
	)

	@api.model
	def test_all_draft_orders (self):
		order_set=self.search([('state','=','verify')])
		order_set.test_exceptions()
		return True


	def action_post(self):
		if self.detect_exceptions():
			return self._popup_exceptions()
		else:
			return super(AccountPayment,self).action_post()

	@api.model
	def _get_popup_action (self):
		action=self.env.ref('hr_exception.action_payment_confirm')
		return action

class Approvalslist(models.Model):
	_inherit = "approvals.list"

	remarks = fields.Char("Remarks")

	def approve(self):
		res = super(Approvalslist, self).approve()
		if res:
			# print("----------------------self.model_id.model", self.model_id.model)
			if self.model_id.model == 'account.payment':
				self.resource_ref.action_post()
		return res

	def reject(self):
		res = super(Approvalslist, self).reject()
		if res:
			if self.model_id.model == 'account.payment':
				self.resource_ref.action_cancel()
		return res

