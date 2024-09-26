from odoo import api,fields,models,_
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class Reason_wizard(models.TransientModel):
	_name='reason.wizard'
	_description="Reason Wizard"

	res_id=fields.Integer('ID')
	res_model=fields.Char('Model')
	reason_des=fields.Char('Reason')
	action_taken=fields.Selection([('approve','Approve'),('reject','Reject'),],string='Action Taken')

	def button_confirm (self):
		context=dict(self._context)
		intObj=self.env["approvals.list"]
		int_details=intObj.browse(context.get("active_id"))
		model_id=self.env[self.res_model].browse(self.res_id)
		# print('action taken===================', self.action_taken)
		if self.action_taken=='approve':
			_body=(_(("Reason for Approval: <ul><b style='color:green'>{0}</b></ul> ").format(self.reason_des)))
			# (wagisha) for working confirm and cancel button properly on wizard on approve button
			if int_details.env.user.id in int_details.group_id.users.ids:
				matrix_check=int_details.env['approval.user.matrix'].search(
					[('approval_id','=',int_details.id),('user','=',int_details.env.user.id)],limit=1)

				if matrix_check.user_response==False:
					int_details.approvals_done+=1

					matrix_check.accepted=True
					int_details.user_took_action_chatter('Approved')

					sumry="Approved " + str(datetime.now())
					int_details.activity_feedback(['base_exception_and_approval.mail_act_approval'],
						user_id=int_details.env.user.id,feedback=sumry)

					if int_details.approvals_done==int_details.approvals_required:
						int_details.all_activity_unlinks()
						int_details.state='approved'
						k=int_details.env['approvals.list'].search([(
						'resource_ref','=',int_details.resource_ref._name + ',' + str(int_details.resource_ref.id))])
						list_of_approvals=[approval.state=='approved' for approval in k]
						if all(list_of_approvals):
							int_details.resource_ref.ignore_exception=True
							if int_details.model_id.model=='hr.leave':
								int_details.resource_ref.action_approve()
							if int_details.model_id.model=='exit.transfer.management':
								int_details.resource_ref.commandant_remark=self.reason_des
								int_details.resource_ref.button_complete()
							if int_details.model_id.model=='account.move':
								int_details.resource_ref.action_post()
							if int_details.model_id.model=='account.payment':
								int_details.resource_ref.action_post()
				else:
					raise UserError('You already have a response on this record')

				if len(int_details.rule_id.group_approval_ids)>1:
					for exp_line in int_details.rule_id.group_approval_ids:
						print("-00000000000000",exp_line,exp_line.group)
						if exp_line.group==int_details.group_id:
							print("iuiuiuiiiiiiiiiiiiigroup",exp_line.sequence,(exp_line.sequence + 1))
							matrix_check=int_details.env['group.and.approval'].search(
								[('sequence','=',(exp_line.sequence + 1)),('rule_id','=',int_details.rule_id.id)])
							print('matrix_checkoooooooooooooooooooooo',matrix_check,matrix_check.group.name)
							exp1=int_details.env['approvals.list'].search([('group_id','=',matrix_check.group.id),(
							'resource_ref','=',
							int_details.resource_ref._name + ',' + str(int_details.resource_ref.id))])
							print('-==========',exp1)
							for rec in exp1:
								rec.condition_check=True
								print("oiiiiiiiiiiiiiiioioioioioi",rec,rec.condition_check)



			else:
				raise UserError('You are not authorized to take an action')

		elif self.action_taken=='reject':
			_body=(_(("Reason for Rejection: <ul><b style='color:red'>{0}</b></ul> ").format(self.reason_des)))
			# (wagisha) for working confirm and cancel button properly on wizard on reject button

			if int_details.env.user.id in int_details.group_id.users.ids:
				matrix_check=int_details.env['approval.user.matrix'].search(
					[('approval_id','=',int_details.id),('user','=',int_details.env.user.id)],limit=1)

				if matrix_check.user_response==False:
					int_details.rejections_done+=1

					matrix_check.rejected=True
					int_details.user_took_action_chatter('Rejected')

					sumry="Rejected " + str(datetime.now())
					int_details.activity_feedback(['base_exception_and_approval.mail_act_approval'],
						user_id=int_details.env.user.id,feedback=sumry)

					if int_details.rejections_done==int_details.rejections_required:
						int_details.state='rejected'
						int_details.all_activity_unlinks()
						# return True
						if int_details.model_id.model=='hr.leave':
							int_details.resource_ref.state='refuse'
							int_details.resource_ref.action_refuse()

				else:
					raise UserError('You already have a response on this record')
			else:
				raise UserError('You are not authorized to take an action')

		else:
			_body=(_(("<ul><b>{0}</b></ul> ").format(self.reason_des)))
		model_id.message_post(body=_body)
