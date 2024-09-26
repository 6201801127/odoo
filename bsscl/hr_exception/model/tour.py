from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date


class ExceptionRule(models.Model):
	_inherit = 'exception.rule'

	rule_group = fields.Selection(
		selection_add=[('bsscl_tour', 'Tour'),
		],
	)
	model = fields.Selection(
		selection_add=[
			('bsscl.tour', 'Tour'),
		])


class BssclTour(models.Model):
	_inherit = ['bsscl.tour', 'base.exception']
	_name = 'bsscl.tour'

	rule_group = fields.Selection(
		selection_add=[('bsscl_tour', 'Tour')],
		default='bsscl_tour',
	)

	@api.model
	def test_all_draft_orders (self):
		order_set=self.search([('state','=','verify')])
		order_set.test_exceptions()
		return True


	def apply_grievance(self):
		if self.detect_exceptions():
			return self._popup_exceptions()
		else:
			return super(BssclTour,self).apply_grievance()

	@api.model
	def _get_popup_action (self):
		action=self.env.ref('hr_exception.action_tour_confirm')
		return action

class Approvalslist(models.Model):
	_inherit = "approvals.list"

	remarks = fields.Char("Remarks")

	def approve(self):
		res = super(Approvalslist, self).approve()
		if res:
			# print("----------------------self.model_id.model", self.model_id.model)
			if self.model_id.model == 'bsscl.tour':
				self.resource_ref.cc_remark = self.remarks
				self.resource_ref.submit_grievance()
		return res

	def reject(self):
		res = super(Approvalslist, self).reject()
		if res:
			if self.model_id.model == 'bsscl.tour':
				self.resource_ref.action_refuse()
		return res

