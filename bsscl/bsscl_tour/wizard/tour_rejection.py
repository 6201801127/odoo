from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError
import re


class Tour_Rejection_Remarks(models.TransientModel):
	_name = 'tour.reject.remarks.wiz'
	_description = "Tour Rejection Remarks"

	def default_get(self,vals):
		res = super(Tour_Rejection_Remarks, self).default_get(vals)
		active_id = self._context.get('active_id')
		act_id = self.env['bsscl.tour'].browse(int(active_id))
		if self.env.user.has_group('bsscl_tour.bsscl_tour_manager_group_id') and act_id.state == 'Applied':
			res.update({
				'boolean_checked_by_manager': True
			})
		else:
			res.update({
				'boolean_checked_by_manager': False
			})
		if self.env.user.has_group('bsscl_employee.deputy_com_id') and act_id.state == 'approved_by_manager':
				res.update({
				'boolean_checked_by_deputy_comm': True
			})
		else:
			res.update({
				'boolean_checked_by_deputy_comm': False
			})
		if self.env.user.has_group('bsscl_employee.commissioner_id') and act_id.state == 'approved_by_deputy':
				res.update({
				'boolean_checked_by_commissioner': True
			})
		else:
			res.update({
				'boolean_checked_by_commissioner': False
			})
		return res
	
	manager_rejection_reason = fields.Text("Manager Rejection Remarks")
	deputy_rejection_reason = fields.Text("Dpt-Commissioner Rejection Remarks")
	commissioner_rejection_reason = fields.Text("Commissioner Rejection Remarks")
	boolean_checked_by_manager = fields.Boolean('Checked By Manager')
	boolean_checked_by_deputy_comm = fields.Boolean('Checked By Deputy Commissioner')
	boolean_checked_by_commissioner = fields.Boolean('Checked By Commissioner')
	word_limit = fields.Integer(string="Limit", default=500)


	@api.constrains('manager_rejection_reason','deputy_rejection_reason','commissioner_rejection_reason')
	@api.onchange('manager_rejection_reason','deputy_rejection_reason','commissioner_rejection_reason')
	def _onchnage_description(self):
		if self.manager_rejection_reason:
			self.word_limit = 500 - len(self.manager_rejection_reason)
		if self.deputy_rejection_reason:
			self.word_limit = 500 - len(self.deputy_rejection_reason)
		if self.commissioner_rejection_reason:
			self.word_limit = 500 - len(self.commissioner_rejection_reason)
		if self.manager_rejection_reason and re.match(r'^[\s]*$', str(self.manager_rejection_reason)):
			raise ValidationError("Manager remarks allow  only alphabets / प्रबंधक की टिप्पणी केवल अक्षरों की अनुमति देती है")
		if self.deputy_rejection_reason and re.match(r'^[\s]*$', str(self.deputy_rejection_reason)):
			raise ValidationError("Deputy commissioner remarks allow  only alphabets / उपायुक्त की टिप्पणी केवल अक्षरों की अनुमति देती है")
		if self.commissioner_rejection_reason and re.match(r'^[\s]*$', str(self.commissioner_rejection_reason)):
			raise ValidationError("Commissioner remarks allow  only alphabets / कमिश्नर की टिप्पणी केवल अक्षरों की अनुमति देती है")
		if self.manager_rejection_reason and not re.match(r'^[A-Za-z ]*$',str(self.manager_rejection_reason)):
			raise ValidationError("Manager remarks allow only alphabets and space / प्रबंधक की टिप्पणी केवल अक्षर और स्थान की अनुमति देती है")
		if self.deputy_rejection_reason and not re.match(r'^[A-Za-z ]*$',str(self.deputy_rejection_reason)):
			raise ValidationError("Deputy commissioner remarks allow only alphabets and space / उपायुक्त की टिप्पणी केवल अक्षर और स्थान की अनुमति देती है")
		if self.commissioner_rejection_reason and not re.match(r'^[A-Za-z ]*$',str(self.commissioner_rejection_reason)):
			raise ValidationError("Commissioner remarks allow only alphabets and space / कमिश्नर की टिप्पणी केवल अक्षर और स्थान की अनुमति देती है")

	def action_reject_tour(self):
		active_id = self._context.get('active_id')
		act_id = self.env['bsscl.tour'].browse(int(active_id))
		act_id.state = 'cancelled'
		act_id.manager_rejection_reason = self.manager_rejection_reason
		act_id.deputy_rejection_reason = self.deputy_rejection_reason
		act_id.commissioner_rejection_reason = self.commissioner_rejection_reason
		
