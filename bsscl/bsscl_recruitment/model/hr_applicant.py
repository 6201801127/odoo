from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError,ValidationError
import re
import base64
from odoo.tools.mimetypes import guess_mimetype


def char_field_validation(string):
	if string:
		pattern = "^[a-zA-Z ]+"
		if re.fullmatch(pattern, string) == None:
			return False
	return True
class HRJob(models.Model):
	_inherit = 'hr.job'

	category_id = fields.Many2one('helpdesk.ticket.category',string='Category / वर्ग',required=False)
	sc = fields.Integer("SC")
	st = fields.Integer("ST")
	obc = fields.Integer("OBC")
	other = fields.Integer("Other")

class HRApplicant(models.Model):
	_inherit = 'hr.applicant'

	bool_stage=fields.Boolean("Boolean stage", compute="_compute_boolean_stage")

	def _compute_boolean_stage(self):
		model_id = self.env['hr.recruitment.stage'].sudo().search([('name','=','Initial Qualification')])
		for rec in self:
			if rec.stage_id == model_id:
				rec.bool_stage = True
			else:
				rec.bool_stage = False

	@api.constrains('name')
	@api.onchange('name')
	def validate_onchange_check (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Application Name!')

	@api.constrains('partner_name')
	@api.onchange('partner_name')
	def validate_name (self):
		if self.partner_name:
			result=char_field_validation(self.partner_name)
			if result==False:
				raise ValidationError('Only use characters in Applicant Name!')


	def check_mobile_number(self, phone):
		if phone:
			check_digit=phone.isdigit()
			if check_digit is False:
				raise UserError(_("Enter valid  number. Only Numeric Digits are allowed."))
			if len(phone)!=10:
				raise UserError(_("Mobile number should be only 10 digits only."))
			# if phone[0]=='0':
			# 	raise UserError(_("Mobile number should not started with Zero"))
			if phone[0] not in ['6','7','8','9']:
				raise UserError(_("Mobile number should started with 6,7,8 or 9"))
			for i in phone:
				my_count = phone.count(i)
				if my_count > 7:
					raise UserError(_("Number repetition should not be more than 7"))

	@api.constrains('partner_phone', 'partner_mobile')
	@api.onchange('partner_phone', 'partner_mobile')
	def check_mobile_number_no (self):
		if self.partner_phone:
			self.check_mobile_number(self.partner_phone)
		if self.partner_mobile:
			self.check_mobile_number(self.partner_mobile)

	@api.constrains('email_from','email_cc')
	@api.onchange('email_from', 'email_cc')
	def validate_mail (self):
		if self.email_cc:
			self.validate_mail_check(self.email_cc)
		if self.email_from:
			self.validate_mail_check(self.email_from)


	def validate_mail_check(self, email):
		if email:
			match=re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,7})$',email)
			if match==None:
				raise ValidationError('Please Enter valid E-mail !')


class RecruitmentStage(models.Model):
	_inherit = "hr.recruitment.stage"

	@api.onchange('name')
	def validate_name(self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')
		# else:
		# 	model_id = self.env['hr.recruitment.stage'].sudo().search([]).bool_stage
		# 	model_id.update = True
		# 	# return model_id = True
			
			

class MailComposeMessage(models.TransientModel):
	_inherit = 'mail.compose.message'

	@api.constrains('attachment_ids')
	# @api.onchange('attachment_ids')
	def _check_document_upload(self):
		for rec in self:
			allowed_file = ['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword']
			if rec.attachment_ids:
				for record in rec.attachment_ids:
					app_size = ((len(record.datas) * 3/4) / 1024) / 1024
					if app_size > 2:
						raise ValidationError("Document allowed size less than 2MB")
					mimetype = guess_mimetype(base64.b64decode(record.datas))
					if str(mimetype) not in allowed_file:
						raise ValidationError("Only PDF/docx format is allowed")


class HrApplicantCategory(models.Model):
	_inherit = "hr.applicant.category"

	@api.onchange('name')
	def validate_name (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')


class HrRecruitmentDegree(models.Model):
	_inherit = "hr.recruitment.degree"

	@api.onchange('name')
	def validate_name (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')


class HrJob(models.Model):
	_inherit = "hr.job"

	@api.onchange('name')
	def validate_name (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')

class HrRefuseReason(models.Model):
	_inherit = "hr.applicant.refuse.reason"

	@api.onchange('name')
	def validate_name (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')

class HrDepartment(models.Model):
	_inherit = "hr.department"

	@api.onchange('name')
	def validate_name (self):
		if self.name:
			result=char_field_validation(self.name)
			if result==False:
				raise ValidationError('Only use characters in Name!')



class SMSComposer(models.Model):
	_inherit = 'calendar.event'

	mobile = fields.Char("Mobile")


	@api.onchange('start','partner_ids')
	def _onchange_start(self):
		for rec in self:
			if self.start:
				# print("start---------------------",self.start)
				all_record = self.env['calendar.event'].sudo().search([('start','=',self.start)])
				print("all record--------------------",all_record)

				current_participant = rec.partner_ids.ids
				# print("participant--------------------",current_participant)
				# for rec in current_participant:
				for record in all_record:
					prev_part = record.mapped('partner_ids').ids
					print("current---------------",current_participant)
					print("previous-----------------",prev_part)
					for recco in current_participant:
						if recco in prev_part:
							raise ValidationError("Selected participant is already alloted for other meeting")





	@api.onchange('partner_ids')
	def _onchange_partner_ids(self):
		mobile=''
		if self.partner_ids:
			for par in self.partner_ids:
				if par.mobile:
					mobile += str(par.mobile)+','
		if mobile:
			self.mobile = mobile
		else:
			self.mobile = ''

	# @api.constrains('name')
	# @api.onchange('name')	
	# def _onchange_name(self):
	# 	for rec in self:
	# 		if rec.name and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.name)):
	# 			raise ValidationError("Your record is not created because Summary should be in alphabets only. please create again.")
	# 		if rec.name:
	# 			if len(rec.name) > 50:
	# 				raise ValidationError('Number of characters must not exceed 50. Please create again.')
				
				