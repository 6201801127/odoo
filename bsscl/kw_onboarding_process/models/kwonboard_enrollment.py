# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.http import request
import re, random, string
import time
import datetime
from lxml import etree
import os, base64
from dateutil.relativedelta import relativedelta
from datetime import date
from ast import literal_eval

cur_dtime = datetime.datetime.now()
cur_dt = datetime.date(year=cur_dtime.year, month=cur_dtime.month, day=cur_dtime.day)

# Model Name    : kwonboard_enrollment
# Description   :  For the enrollment of the new employees , a reference number is created and Email will be sent to the employee
# Created By    :
# Created On    : 13-Jun-2019


class kwonboard_enrollment(models.Model):
	_name = 'kwonboard_enrollment'
	_description = "Candidate Enrollment"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = "write_date desc"

	@api.model
	def _get_no_month(self):
		return [(str(x), str(x)) for x in range(1, 13)]

	otp_number = fields.Char()
	generate_time = fields.Datetime(string="Expire Datetime")
	# dept_name = fields.Many2one('hr.department', string="Department", required=True,
	#                             domain=[('dept_type.code', '=', 'department')], help="")
	# division = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
	# section = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'section')])
	# practise = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'practise')])

	job_id = fields.Many2one('hr.job', string="Designation", help="")
	name = fields.Char(string="Candidate Name", required=True, size=100, help="",
		read=['base.group_user', 'kw_employee.group_hr_finance', 'kw_employee.group_hr_admin',
			'kw_employee.group_hr_nsa'])
	firstname = fields.Char(string="Candidate first name", help="")
	middlename = fields.Char(string="Candidate middle name", help="")
	lastname = fields.Char(string="Candidate last name", help="")
	email = fields.Char(string="Personal Email Id", size=50, required=True, help="")
	mobile = fields.Char(String="Mobile No", size=15, required=True, help="")
	whatsapp_no = fields.Char(String="Whatsapp No", size=15)
	reference_no = fields.Char('Reference No.')
	emp_id = fields.Many2one('hr.employee')
	emgr_contact=fields.Char(string="Emergency Contact Person")
	emgr_phone=fields.Char(string="Emergency Phone")
	company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
		default=lambda self: self.env.user.company_id)
	# location_id = fields.Many2one('kw_res_branch', string="Base Location")
	work_location_id = fields.Many2one('res.partner', string="Work Location", domain="[('parent_id', '=', company_id)]")
	work_location = fields.Char(string="Work Location", related='work_location_id.city', readonly=True)
	educational_ids=fields.One2many('kwonboard_edu_qualification','enrole_id',string="Educational Details")
	work_experience_ids=fields.One2many('kwonboard_work_experience','enrole_id',string='Work Experience Details')

	state = fields.Selection(
		[('1', 'Enrolled'), ('2', 'Profile Created'), ('3', 'Configuration Mapping'), ('4', 'Configuration Done'),
			('5', 'Approved'), ('6', 'Rejected')], required=True, default='1', track_visibility='onchange')

	birthday = fields.Date("Birthday")
	blood_group=fields.Selection([('a+','A+'),
                                    ('a1+','A1+'),
                                     ('a-','A-'),
                                     ('b+','B+'),
                                     ('b-','B-'),
                                     ('o+', 'O+'),
                                     ('o-', 'O-'),
                                     ('ab+','AB+'),
                                     ('ab-','AB-')],string="Blood Group")
	emp_religion = fields.Many2one('employee.religion',string='Religion',track_visibility='always')
	applicant_father_name=fields.Char(string="Father's Name",size=100)
	applicant_father_dob=fields.Date(string="Father's DOB")
	applicant_mother_name=fields.Char(string="Mother's Name",size=100)
	applicant_mother_dob=fields.Date(string="Mother's DOB")

	personal_bank_name=fields.Char(string="Bank Name",readonly=False)
	personal_bank_account=fields.Char(string="Account No",readonly=False)
	personal_bank_ifsc=fields.Char(string="IFSC Code")
	uan_id=fields.Char(string="UAN",help="UAN ")
	esi_id=fields.Char(string="ESI Number",help="ESI Number")

	present_addr_country_id=fields.Many2one('res.country',string="Present Address Country")
	present_addr_street=fields.Text(string="Present Address Line 1",size=500)
	present_addr_street2=fields.Text(string="Present Address Line 2",size=500)
	present_addr_city=fields.Char(string="Present Address City",size=100)
	present_addr_state_id=fields.Many2one('res.country.state',string="Present Address State")
	present_addr_zip=fields.Char(string="Present Address ZIP",size=10)
	# Present address : End
	same_address=fields.Boolean(string=u'Same as Present Address',default=False)
	# Permanent address : start
	permanent_addr_country_id=fields.Many2one('res.country',string="Permanent Address Country")
	permanent_addr_street=fields.Text(string="Permanent Address Line 1",size=500)
	permanent_addr_street2=fields.Text(string="Permanent Address Line 2",size=500)
	permanent_addr_city=fields.Char(string="Permanent Address City",size=100)
	permanent_addr_state_id=fields.Many2one('res.country.state',string="Permanent Address State")
	permanent_addr_zip=fields.Char(string="Permanent Address ZIP",size=10)
	experience_sts=fields.Selection(string="Work Experience ",selection=[('1','Fresher'),('2','Experience')],)
	identification_ids=fields.One2many('kwonboard_identity_docs','enrole_id',string='Identification Documents')
	create_full_profile=fields.Boolean("Create Full Profile",default=False)
	module_onboarding_mail_status=fields.Boolean(string="Send E-mail")
	module_onboarding_sms_status=fields.Boolean(string="Send SMS")
	tmp_join_date=fields.Date(string="Joining Date",default=cur_dt)


	@api.onchange('tmp_source_id')
	def onchange_tmp_source_id(self):
		for rec in self:
			rec.tmp_employee_referred = False
			rec.tmp_service_partner_id = False
			rec.tmp_media_id = False
			rec.tmp_consultancy_id = False
			rec.tmp_jportal_id = False
			rec.tmp_reference = False
			rec.tmp_reference_walkindrive = False
			rec.tmp_reference_print_media = False
			rec.tmp_reference_job_fair = False
			rec.tmp_institute_id = False

	@api.onchange('bond_required')
	def onchange_bond_required(self):
		for rec in self:
			if rec.bond_required == '0':
				rec.bond_years = False
				rec.bond_months = False

	@api.onchange('tmp_grade')
	def onchange_tmp_grade(self):
		for rec in self:
			rec.tmp_band = False
			if rec.tmp_grade.has_band:
				rec.tmp_has_band = True
			else:
				rec.tmp_has_band = False

	# === Enroll document smart button method ====

	def button_enroll_document(self):
		return {
			'type': 'ir.actions.act_url',
			'url': f'/download_enroll_doc/{self.id}',
			'target': 'new',
		}

	@api.onchange('mrf_id')
	def onchange_mrf_id(self):
		for rec in self:
			if rec.mrf_id:
				rec.finance_mrf_id = rec.mrf_id.id
			#     rec.budget_type = rec.mrf_id.requisition_type
			#     rec.tmp_emp_role = rec.mrf_id.role_id.id
			#     rec.tmp_emp_category = rec.mrf_id.categ_id.id
			#     rec.tmp_employement_type = rec.mrf_id.type_employment.id

			# elif rec.mrf_id.requisition_type == "project":
			#     self.type_of_project_id = rec.mrf_id.type_project
			#     self.project_name_id = rec.mrf_id.project
			#     self.engagement = rec.mrf_id.duration
			# else:
			#     rec.type_of_project_id = False
			#     rec.project_name_id = False
			#     rec.engagement = False

	@api.onchange('tmp_username')
	def check_username(self):
		for rec in self:
			if rec.tmp_username:
				enrollment_rec = self.env['kwonboard_enrollment'].sudo().search(
					[('tmp_username', '=', rec.tmp_username),
						'|', ('active', '=', True), ('active', '=', False)]) - self
				user_rec = self.env['res.users'].sudo().search(
					[('login', '=', rec.tmp_username), '|', ('active', '=', True), ('active', '=', False)])
				if enrollment_rec or user_rec:
					raise ValidationError('Username already exists, Please choose a unique username.')

	@api.onchange('tmp_contract_year_month', 'tmp_contract_period', 'tmp_start_dt')
	def _onchange_tmp_contract_year_month(self):
		if self.tmp_contract_period and self.tmp_start_dt:
			if self.tmp_contract_year_month == 'year':
				self.tmp_end_dt = self.tmp_start_dt + relativedelta(years=int(self.tmp_contract_period))
			else:
				self.tmp_end_dt = self.tmp_start_dt + relativedelta(months=int(self.tmp_contract_period))

	@api.onchange('start_dt', 'fin_engagement')
	def _onchange_contract_year_month(self):
		if self.start_dt:
			self.end_dt = self.start_dt + relativedelta(months=int(self.fin_engagement))
		# if self.contract_period and self.start_dt:
		#     if self.contract_year_month == 'year':
		#         self.end_dt = self.start_dt + relativedelta(years=int(self.contract_period))
		#     else:
		#         self.end_dt = self.start_dt + relativedelta(months=int(self.contract_period))

	@api.depends('tmp_worklocation_id')
	def _compute_work_location(self):
		for record in self:
			if record.tmp_worklocation_id:
				record.emp_worklocation = record.tmp_worklocation_id
	""" Profile image URL to be created which will be sent while syncing """
	def _compute_image_id(self):
		for record in self:
			attachment_data = self.env['ir.attachment'].search(
				[('res_id', '=', record.id), ('res_model', '=', 'kwonboard_enrollment'), ('res_field', '=', 'image')])
			attachment_data.write({'public': True})
			record.image_id = attachment_data.id

	def _get_image_url(self):
		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		for record in self:
			if record.image_id:
				final_url = '%s/web/image/%s' % (base_url, record.image_id)
				record.image_url = final_url
			else:
				record.image_url = ''

	@api.onchange('tmp_at_join_time')
	def onchange_at_join(self):
		self.current = self.tmp_at_join_time

	# @api.constrains('tmp_at_join_time')
	# def check_tmp_at_join_time(self):
	#     if self.tmp_at_join_time == 0.00:
	#         raise ValidationError("Salary at joining time should be greater than 0.00")

	@api.onchange('basic_at_join_time')
	def _onchange_basic_at_join(self):
		self.current_basic = self.basic_at_join_time
		# grade_id = self.env['kwemp_grade'].sudo().search([('grade_id','=',self.tmp_grade.id),('band_id','=',self.tmp_band.id)])
		# if grade_id:
		# record_id = self.env['kw_grade_pay'].sudo().search([('grade','=',grade_id.id),('country','=',self.tmp_worklocation_id.country.id)])
		record_id = self.env['kw_grade_pay'].sudo().search(
			[('grade', '=', self.tmp_grade.id), ('band', '=', self.tmp_band.id),
				('country', '=', self.tmp_worklocation_id.country.id)])
		if record_id:
			if self.basic_at_join_time > record_id.basic_max:
				return {'warning': {
					'title': _('Validation Error'),
					'message': (
						f'Basic amount at join time ({self.basic_at_join_time}) is greater than Grade pay Basic max amount ({record_id.basic_max}) for Grade {record_id.grade.name}.')
				}}
			if self.basic_at_join_time < record_id.basic_min:
				return {'warning': {
					'title': _('Validation Error'),
					'message': (
						f'Basic amount at join time ({self.basic_at_join_time}) is less than Grade pay Basic min amount ({record_id.basic_min} for Grade {record_id.grade.name}.')
				}}

	@api.onchange('enable_payroll')
	def onchange_payroll(self):
		if self.enable_payroll == 'no':
			self.basic_at_join_time = False
			self.bank_account = False
			self.bank_id = False
			self.hra = False
			self.conveyance = False
			self.medical_reimb = False
			self.transport = False
			self.productivity = False
			self.commitment = False
			self.cosolid_amnt = False
			self.enable_epf = False
			self.pf_deduction = False
			self.enable_gratuity = False
			self.current_basic = False

	@api.onchange('no_of_months')
	def _onchange_no_of_months(self):
		self.tmp_prob_compl_date = self.tmp_join_date+relativedelta(months=int(self.no_of_months))

	@api.onchange('tmp_worklocation_id')
	def _onchange_work_location(self):
		self.tmp_shift = False
		return {'domain': {'tmp_shift': [('branch_id', '=', self.tmp_worklocation_id.id)]}}

	@api.onchange('tmp_location')
	def _onchange_location(self):
		self.tmp_client_location = False
		self.infra_id = False
		self.work_station_id = False

	@api.onchange('tmp_on_probation')
	def _onchange_probation(self):
		self.tmp_prob_compl_date = False

	@api.onchange('card_type')
	def _onchange_card_type(self):
		self.id_card_no = False
		return {'domain': {'id_card_no': [('card_type', '=', self.card_type), ('state', '=', 'unassigned')]}}

	@api.onchange('tmp_employement_type')
	def _onchange_tmp_employement_type(self):
		if self.tmp_employement_type:
			self.tmp_direct_indirect = False
			self.tmp_project_id = False
			self.tmp_start_dt = False
			self.tmp_end_dt = False
			self.tmp_contract_period = False
			self.tmp_contract_year_month = False

	@api.onchange('tmp_emp_role')
	def _onchange_tmp_emp_role(self):
		if self.tmp_emp_role and self.tmp_emp_category:
			if self.tmp_emp_role not in self.tmp_emp_category.role_ids:
				self.tmp_emp_category = False
		else:
			self.tmp_emp_category = False

		return {'domain': {'tmp_emp_category': [('role_ids', '=', self.tmp_emp_role.id)], }}

	@api.constrains('confirm_outl_pwd', 'confirm_domain_pwd', 'biometric_id', 'epbx_no', 'start_dt', 'end_dt',
		'tmp_start_dt', 'tmp_end_dt')
	def check_constraints(self):
		enroll_rec = self.env['kwonboard_enrollment'].sudo()
		emp_rec = self.env['hr.employee'].sudo()
		for rec in self:
			if rec.outlook_pwd and rec.outlook_pwd != rec.confirm_outl_pwd:
				raise ValidationError("Outlook password and Confirm password must be same")
			if rec.domain_login_pwd and rec.domain_login_pwd != rec.confirm_domain_pwd:
				raise ValidationError("Domain password and Confirm password must be same")
			if rec.biometric_id:
				if enroll_rec.search([('biometric_id', '=', rec.biometric_id)]) - self\
					or emp_rec.search([('biometric_id', '=', rec.biometric_id)]):
					raise ValidationError("This Biometric ID is already assigned!")
			if rec.epbx_no:
				if enroll_rec.search([('epbx_no', '=', rec.epbx_no)]) - self\
					or emp_rec.search([('epbx_no', '=', rec.epbx_no)]):
					raise ValidationError("This EPBX is already assigned!")

	@api.onchange('end_dt')
	def _onchange_start_dt(self):
		if self.end_dt:
			if self.start_dt >= self.end_dt:
				raise ValidationError("Contract end date must not be before or equal to start date!")

	@api.onchange('tmp_end_dt')
	def _onchange_tmp_end_dt(self):
		if self.tmp_end_dt:
			if self.tmp_start_dt >= self.tmp_end_dt:
				raise ValidationError("Contract end date must not be before or equal to start date!")

	@api.constrains('tmp_start_dt')
	def _onchange_tmp_end_dt(self):
		print("======",self.tmp_start_dt)
		if self.tmp_join_date and self.tmp_start_dt:
			if self.tmp_join_date >= self.tmp_start_dt:
				raise ValidationError("Contract start date must not be before to join date!")

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		if self._context.get('group_check'):
			ids = []
			if self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_finance'):
				query = "select id from kwonboard_enrollment where finance_setting_status=False and state='3'"
				self._cr.execute(query)
				ids = self._cr.fetchall()
				args += [('id', 'in', ids)]

			elif self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_officer'):
				query = "select id from kwonboard_enrollment where state in ('1','2','3')"
				self._cr.execute(query)
				ids = self._cr.fetchall()
				args += [('id', 'in', ids)]

			elif self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_nsa'):
				query = "select id from kwonboard_enrollment where nsa_setting_status=False and state='3'"
				self._cr.execute(query)
				ids = self._cr.fetchall()
				args += [('id', 'in', ids)]

			elif self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_admin'):
				query = "select id from kwonboard_enrollment where admin_setting_status=False and state='3'"
				self._cr.execute(query)
				ids = self._cr.fetchall()
				args += [('id', 'in', ids)]

			else:
				query = "select id from kwonboard_enrollment"
				self._cr.execute(query)
				ids = self._cr.fetchall()
				args += [('id', 'in', ids)]

		return super(kwonboard_enrollment, self)._search(args, offset=offset, limit=limit, order=order, count=count,
			access_rights_uid=access_rights_uid)

	def check_access_finance(self):
		cur_user = self.env.user
		if cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_manager')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_finance')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_officer'):
			for rec in self:
				rec.check_finance = True

	def check_access_it(self):
		cur_user = self.env.user
		if cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_manager')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_nsa')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_officer'):
			for rec in self:
				rec.check_it = True

	def check_access_admin(self):
		cur_user = self.env.user
		if cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_manager')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_admin')\
			or cur_user.has_group('kw_onboarding_process.group_kw_onboarding_process_officer'):
			for rec in self:
				rec.check_admin = True

	def check_access_manager(self):
		self.check_manager = False
		if self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_manager'):
			self.check_manager = True

	def check_access_officer(self):
		self.check_officer = False
		if self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_officer'):
			self.check_officer = True

	@api.constrains('whatsapp_no')
	def check_whatsapp_no(self):
		for record in self:
			if record.whatsapp_no:
				if not len(record.whatsapp_no) == 10:
					raise ValidationError("Your whatsapp number is invalid for: %s" % record.whatsapp_no)
				if not re.match("^[0-9]*$", str(record.whatsapp_no)) != None:
					raise ValidationError("Your WhatsApp number is invalid for: %s" % record.whatsapp_no)

	@api.constrains('emgr_phone')
	def check_emgr_phone(self):
		for record in self:
			if record.emgr_phone:
				if not len(record.emgr_phone) == 10:
					raise ValidationError("Your emergency number is invalid for: %s" % record.emgr_phone)
				if not re.match("^[0-9]*$", str(record.emgr_phone)) != None:
					raise ValidationError("Your emergency number is invalid for: %s" % record.emgr_phone)
				if record.emgr_phone == record.whatsapp_no or record.emgr_phone == record.mobile:
					raise ValidationError("Your Emergency number can not same as WhatsApp or Primary no")



	@api.onchange('applicant_id')
	def onchange_applicant_id(self):
		self.name = self.applicant_id.partner_name
		self.dept_name = self.applicant_id.department_id
		self.job_id = self.applicant_id.job_id
		self.email = self.applicant_id.email_from
		self.mobile = self.applicant_id.partner_mobile
		self.division = self.applicant_id.division
		self.section = self.applicant_id.section
		self.practise = self.applicant_id.practise
		self.gender = self.applicant_id.gender
		if self.applicant_id.job_position.mrf_id:
			self.tmp_emp_role = self.applicant_id.job_position.mrf_id.role_id.id
			self.tmp_emp_category = self.applicant_id.job_position.mrf_id.categ_id.id
			self.tmp_employement_type = self.applicant_id.job_position.mrf_id.type_employment.id
			self.tmp_project_id = self.applicant_id.job_position.mrf_id.project.id
			# print("22222222222222222")
		elif self.applicant_id.mrf_id:
			self.tmp_emp_role = self.applicant_id.mrf_id.role_id.id
			self.tmp_emp_category = self.applicant_id.mrf_id.categ_id.id
			self.tmp_employement_type = self.applicant_id.mrf_id.type_employment.id
			self.tmp_project_id = self.applicant_id.mrf_id.project.id
			# print("33333333333333333333")

	@api.onchange('dept_name')
	def onchange_department(self):
		self.division = False
		domain = {}
		for rec in self:
			domain['division'] = [('parent_id', '=', rec.dept_name.id), ('dept_type.code', '=', 'division')]
			return {'domain': domain}

	@api.onchange('division')
	def onchange_division(self):
		self.section = False
		domain = {}
		for rec in self:
			if rec.dept_name:
				domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
				return {'domain': domain}

	@api.onchange('section')
	def onchange_section(self):
		self.practise = False
		domain = {}
		for rec in self:
			if rec.section:
				domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
				return {'domain': domain}

	@api.onchange('company_id')
	def _onchange_company_id(self):
		self.work_location_id = False
		return {'domain': {'work_location_id': [('parent_id', '=', self.company_id.partner_id.id)], }}

	@api.model
	def _inverse_field(self):
		if self.image:
			bin_value = base64.b64decode(self.image)
			if not os.path.exists('onboarding_docs/' + str(self.id)):
				os.makedirs('onboarding_docs/' + str(self.id))
			full_path = os.path.join(os.getcwd() + '/onboarding_docs/' + str(self.id), self.image_name)
			# if os.path.exists(full_path):
			#     raise ValidationError("The file name "+self.filename+" exists.Please change your file name.")
			try:
				with open(os.path.expanduser(full_path), 'wb') as fp:
					fp.write(bin_value)
					fp.close()
			except Exception as e:
				print(e)

	@api.onchange('same_address')
	def _change_permanent_address(self):
		if self.same_address:
			self.permanent_addr_country_id = self.present_addr_country_id
			self.permanent_addr_street = self.present_addr_street
			self.permanent_addr_street2 = self.present_addr_street2
			self.permanent_addr_city = self.present_addr_city
			self.permanent_addr_state_id = self.present_addr_state_id
			self.permanent_addr_zip = self.present_addr_zip

	@api.depends('system_configuration')
	def _compute_config_setting(self):
		for config_rec in self.system_configuration:
			for sel_group in config_rec.authorized_group:
				# #if the group is selected grouyp or HR manage group
				if sel_group in self.env.user.groups_id:
					self.other_user_status = True

			if self.env.user.has_group('kw_onboarding_process.group_kw_onboarding_process_manager'):
				self.other_user_status = False

			if config_rec.configuration_type_id.code == 'idcard':
				self.user_grp_id_card = True
			elif config_rec.configuration_type_id.code == 'budget':
				self.user_grp_budget = True
			elif config_rec.configuration_type_id.code == 'outlookid':
				self.user_grp_outlook = True
			elif config_rec.configuration_type_id.code == 'biometric':
				self.user_grp_biometric = True
			elif config_rec.configuration_type_id.code == 'system':
				self.user_grp_domain_pwd = True
			elif config_rec.configuration_type_id.code == 'epbx':
				self.user_grp_epbx = True

		if (self.user_grp_outlook or self.user_grp_biometric or self.user_grp_domain_pwd or self.user_grp_epbx) and (
			not self.nsa_setting_status and self.state == '3'):
			self.display_nsa_btn = True

	"""# onchange of present address country change the state"""
	@api.onchange('present_addr_country_id')
	def _change_present_address_state(self):
		country_id = self.present_addr_country_id.id
		self.present_addr_state_id = False
		return {'domain': {'present_addr_state_id': [('country_id', '=', country_id)], }}

	"""# onchange of employee category change the role"""

	@api.onchange('emp_role', 'fin_budget_type', 'emp_category', 'employement_type', 'fin_type_of_project_id',
		'fin_engagement', 'fin_project_name_id', 'start_dt', 'end_dt')
	def _get_categories(self):
		role_id = self.emp_role.id
		# self.emp_category = False
		for rec in self:
			rec.budget_type = rec.fin_budget_type
			rec.tmp_emp_role = rec.emp_role
			rec.tmp_emp_category = rec.emp_category
			rec.tmp_employement_type = rec.employement_type.id,
			rec.type_of_project_id = rec.fin_type_of_project_id
			rec.engagement = rec.fin_engagement
			rec.project_name_id = rec.fin_project_name_id
			rec.tmp_start_dt = rec.start_dt
			rec.tmp_end_dt = rec.end_dt
		return {'domain': {'emp_category': [('role_ids', '=', role_id)], }}

	"""# onchange of permanent address country change the state"""
	@api.onchange('permanent_addr_country_id')
	def _change_permanent_address_state(self):
		country_id = self.permanent_addr_country_id.id
		self.permanent_addr_state_id = False
		if self.same_address and self.present_addr_state_id and (self.permanent_addr_country_id == self.present_addr_country_id):
			self.permanent_addr_state_id = self.present_addr_state_id
		return {'domain': {'permanent_addr_state_id': [('country_id', '=', country_id)], }}

	""" This method is used to get email of responsible person for onboarding if create_uid is odoobot 
		then use responsible person email from general settings else use email of enrollment creator 
		while communicating 
	"""
	def get_email_from(self):
		email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.responsible_person')
		emp_id = int(email_fr) if email_fr != 'False' else False
		for rec in self:
			if rec.create_uid.id == 1 and emp_id:
				emp = self.env['hr.employee'].sudo().browse(emp_id)
				email_to, email_name = emp.work_email, emp.name
			else:
				emp = self.env['res.users'].sudo().browse(rec.create_uid.id)
				email_to, email_name = emp.email, emp.name
		return {'email_to': email_to, 'email_name': email_name}

	""" This method executes when Submit for configuration is clicked, it then sends mail notification to  
		Admin/IT/Finance group depending on the environment mapping selection.
	"""

	def complete_env_mapping(self):
		template = self.env.ref('kw_onboarding_process.config_mail_template')
		template_id = self.env['mail.template'].browse(template.id)
		email_to = self.get_email_from()
		for rec in self:
			if rec.system_configuration:
				admin_setting_status = True
				finance_setting_status = True
				nsa_setting_status = True
				temp_user = []
				view_id = self.env.ref('kw_onboarding_process.kwonboard_enrollment_action_window').id
				for config_rec in rec.system_configuration:
					if config_rec.configuration_type_id.code == 'idcard':
						admin_setting_status = False
					elif config_rec.configuration_type_id.code == 'budget':
						finance_setting_status = False
					else:
						nsa_setting_status = False

					for group in config_rec.authorized_group:
						for user in group.users:
							# if user.id not in config_user_id_list:
							if config_rec.configuration_type_id.code == 'idcard':
								mail_status = template_id.with_context(dept_name='Admin', user_name=user.name,
									user_mail=user.email, view_id=view_id,
									rec_id=rec.id, email_to=email_to.get('email_to'))\
									.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
								# rec.activity_schedule('kw_onboarding_process.mail_act_env_config_admin', fields.Date.today(), user_id=user.id)
							elif config_rec.configuration_type_id.code == 'budget':
								mail_status = template_id.with_context(dept_name='Finance', user_name=user.name,
									user_mail=user.email, view_id=view_id,
									rec_id=rec.id, email_to=email_to.get('email_to'))\
									.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
								# rec.activity_schedule('kw_onboarding_process.mail_act_env_config_finance', fields.Date.today(), user_id=user.id)
							else:
								if user.id not in temp_user:
									temp_user.append(user.id)
									mail_status = template_id.with_context(dept_name='IT', user_name=user.name,
										user_mail=user.email, view_id=view_id,
										rec_id=rec.id,
										email_to=email_to.get('email_to'))\
										.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
								# rec.activity_schedule('kw_onboarding_process.mail_act_env_config_nsa', fields.Date.today(), user_id=user.id)
								# config_user_id_list.append(user.id)
							# ,author_id=self.env.user.partner_id.id
				# change the status into mapped
				rec.write({'state': '3',
					'admin_setting_status': admin_setting_status,
					'finance_setting_status': finance_setting_status,
					'nsa_setting_status': nsa_setting_status,
					'emp_role': rec.tmp_emp_role.id,
					'emp_category': rec.tmp_emp_category.id,
					'employement_type': rec.tmp_employement_type.id,
					'project_id': rec.tmp_project_id.id,
					'start_dt': rec.tmp_start_dt,
					'end_dt': rec.tmp_end_dt,
					'direct_indirect': rec.tmp_direct_indirect,
					'contract_period': rec.tmp_contract_period,
					'contract_year_month': rec.tmp_contract_year_month,
					'fin_engagement': rec.engagement,
					'fin_type_of_project_id': rec.type_of_project_id,
					'fin_budget_type': rec.budget_type})
			else:
				raise ValidationError(_('Please choose the required configurations'))
		return True


	def button_take_action(self):
		view_id = self.env.ref('kw_onboarding_process.kwonboard_enrollment_view_form').id
		target_id = self.id
		return {
			'name': 'Configure Environment',
			'type': 'ir.actions.act_window',
			'res_model': 'kwonboard_enrollment',
			'res_id': target_id,
			'view_type': 'form',
			'view_mode': 'tree,form',
			'target': 'self',
			'views': [(view_id, 'form')],
			'view_id': view_id,
			'flags': {'action_buttons': True},
		}

	""" This method is used to get all designation specific employees' (which is set in general settings) email 
		which will be in cc while Admin/IT/Finance group submits configuration.
	"""
	def get_designation_cc(self, rec_set=None):
		get_desig_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.employee_creation_inform_ids')
		get_emp_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.onboarding_cc_ids')
		email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding_process.responsible_person')
		emp_id = int(email_fr) if email_fr != 'False' else False
		emails = ''
		email_cc = ''
		get_desig_list = literal_eval(get_desig_ids) if get_desig_ids else []
		get_emp_list = literal_eval(get_emp_ids) if get_emp_ids else []
		if rec_set == None:
			for rec in self:
				if len(get_desig_list) > 0:
					employee = self.env['hr.employee']
					emps = employee.sudo().search([('job_id', 'in', [int(x) for x in get_desig_list]), ('work_email', '!=', False)])
					additional_emp = employee.sudo().search([('id', 'in', [int(x) for x in get_emp_list]), ('work_email', '!=', False)])
					emails += ','.join(emps.mapped('work_email')) or ''
					if additional_emp:
						email_cc += ','.join(additional_emp.mapped('work_email')) or ''
					if rec.create_uid.id != 1 and rec.create_uid.id != self.env['hr.employee'].sudo().browse(emp_id).user_id.id:
						emails += ','+self.env['hr.employee'].sudo().browse(emp_id).work_email
		else:
			for rec in rec_set:
				if len(get_desig_list) > 0:
					employee = self.env['hr.employee']
					emps = employee.sudo().search([('job_id', 'in', [int(x) for x in get_desig_list]), ('work_email', '!=', False)])
					additional_emp = employee.sudo().search([('id', 'in', [int(x) for x in get_emp_list]), ('work_email', '!=', False)])
					emails += ','.join(emps.mapped('work_email')) or ''
					if additional_emp:
						email_cc += ','.join(additional_emp.mapped('work_email')) or ''
					if rec.create_uid.id != 1 and rec.create_uid.id != self.env['hr.employee'].sudo().browse(emp_id).user_id.id:
						emails += ','+self.env['hr.employee'].sudo().browse(emp_id).work_email
		return emails + ',' + email_cc

	""" This method executes when Submit IT settings is clicked and 
	checks for necessary IT settings assigned by Officer/Manager """


	def complete_nsa_setting(self):
		template = self.env.ref('kw_onboarding_process.config_completion_mail_template')
		template_id = self.env['mail.template'].browse(template.id)
		email_to = self.get_email_from()
		for rec in self:
			for config_rec in rec.system_configuration:
				if config_rec.configuration_type_id.code == 'outlookid' and not (rec.csm_email_id and rec.outlook_pwd):
					raise ValidationError(_(' IT settings can not be completed without outlook configuration details'))

				elif config_rec.configuration_type_id.code == 'biometric' and not rec.biometric_id:
					raise ValidationError(_(' IT settings can not be completed without biometric configuration details'))

				elif config_rec.configuration_type_id.code == 'system' and not (rec.domain_login_id and rec.domain_login_pwd):
					raise ValidationError(_('IT settings can not be completed without system domain configuration details'))

				elif config_rec.configuration_type_id.code == 'epbx' and not rec.epbx_no:
					raise ValidationError(_('IT settings can not be completed without EPBX configuration details'))
			new_state = '3'

			if rec.admin_setting_status and rec.finance_setting_status:
				new_state = '4'

			self.write({'state': new_state, 'nsa_setting_status': True})
			if rec.nsa_setting_status == True:
				self.env.user.notify_info(message='IT settings Completed')
				# code to complete the activity
				mail_status = template_id.with_context(dept_name='IT', user_mail=self.env.user.email,
					emails_cc=self.get_designation_cc(),
					email_to=email_to.get('email_to'),
					user_name=email_to.get('email_name'))\
					.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
				# rec.activity_feedback(['kw_onboarding_process.mail_act_env_config_nsa'])
		return True

	""" This method executes when Submit Finance settings is clicked and 
	checks for necessary Finance settings assigned by Officer/Manager """


	def complete_finance_setting(self):
		template = self.env.ref('kw_onboarding_process.config_completion_mail_template')
		template_id = self.env['mail.template'].browse(template.id)
		email_to = self.get_email_from()
		for rec in self:
			if rec.direct_indirect != '2':
				if rec.emp_role and rec.emp_category and rec.employement_type:
					new_state = '3'
					if rec.nsa_setting_status and rec.admin_setting_status:
						new_state = '4'
					rec.write({'state': new_state, 'finance_setting_status': True})

					# code to complete the activity
					# rec.activity_feedback(['kw_onboarding_process.mail_act_env_config_finance'])
					mail_status = template_id.with_context(dept_name='Finance', user_mail=self.env.user.email,
						emails_cc=self.get_designation_cc(),
						email_to=email_to.get('email_to'),
						user_name=email_to.get('email_name'))\
						.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
					self.env.user.notify_info(message='Finance settings Completed')
				else:
					raise ValidationError(_('Please enter all the setting details'))
			else:
				if rec.nsa_setting_status and rec.admin_setting_status:
					new_state = '4'
				else:
					new_state = '3'
				rec.write({'state': new_state, 'finance_setting_status': True})
				mail_status = template_id.with_context(dept_name='Finance', user_mail=self.env.user.email,
					emails_cc=self.get_designation_cc(),
					email_to=email_to.get('email_to'),
					user_name=email_to.get('email_name'))\
					.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
		return True

	""" This method executes when Submit Admin settings is clicked and 
	checks for necessary Admin settings assigned by Officer/Manager """


	def complete_admin_setting(self):
		template = self.env.ref('kw_onboarding_process.config_completion_mail_template')
		template_id = self.env['mail.template'].browse(template.id)
		email_to = self.get_email_from()
		for rec in self:
			if rec.id_card_no:
				new_state = '3'
				if rec.nsa_setting_status and rec.finance_setting_status:
					new_state = '4'
				rec.write({'state': new_state, 'admin_setting_status': True})
				# code to complete the activity
				# rec.activity_feedback(['kw_onboarding_process.mail_act_env_config_admin'])
				mail_status = template_id.with_context(dept_name='Admin', user_mail=self.env.user.email,
					emails_cc=self.get_designation_cc(),
					email_to=email_to.get('email_to'),
					user_name=email_to.get('email_name'))\
					.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
				self.env.user.notify_info(message='Admin settings Completed')
			else:
				raise ValidationError(_('Please enter ID Card No'))
		return True

	""" This method is executed when Officer/Manager validates a candidature, 
	this will also create a record in Onboarding for further process."""


	def make_enrole_to_employee(self):
		emp_vals = {}
		user_vals = {}
		# user_action = self.env.ref('kw_hr_attendance.action_my_office_time')
		user_action = self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action')
		# print("user_action==",user_action)
		for rec in self:
			# check for validations for selected services
			for config_rec in rec.system_configuration:
				if config_rec.configuration_type_id.code == 'idcard' and not rec.id_card_no:
					raise ValidationError(_('Please provide all admin setting details before proceeding for approval'))
				elif config_rec.configuration_type_id.code == 'budget' and not (rec.emp_role or rec.emp_category or rec.employement_type):
					raise ValidationError(_('Please provide all finance setting details before proceeding for approval'))
				elif config_rec.configuration_type_id.code == 'outlookid' and not (rec.csm_email_id or rec.outlook_pwd):
					raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
				elif config_rec.configuration_type_id.code == 'biometric' and not rec.biometric_id:
					raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
				elif config_rec.configuration_type_id.code == 'system' and not (rec.domain_login_id or rec.domain_login_pwd):
					raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
				elif config_rec.configuration_type_id.code == 'epbx' and not rec.epbx_no:
					raise ValidationError(_('Please provide all IT setting details before proceeding for approval'))
			# End : validation check
			if rec.enable_payroll == 'yes':
				pass
				# if rec.basic_at_join_time <= 0 or rec.current_basic <= 0:
				#     raise ValidationError("Enter valid Basic amount")
				# if rec.hra <= 0:
				#     raise ValidationError("Enter valid HRA percentage")
				# if rec.conveyance <= 0:
				#     raise ValidationError("Enter valid Conveyance percentage")
				# if rec.productivity <= 0:
				#     raise ValidationError("Enter valid Productive bonus")
				# if rec.commitment <= 0:
				#     raise ValidationError("Enter valid Commitment bonus")
			else:
				# if rec.cosolid_amnt <= 0:
				#     raise ValidationError("Enter valid Consolidate amount")
				pass
			aadhar_num, passport_num = False, False
			for r in rec.identification_ids:
				if r.name == '5':
					aadhar_num = r.doc_number
				elif r.name == '2':
					passport_num = r.doc_number
				else:
					pass
			if rec.tmp_username and rec.csm_email_id:
				user = self.env['res.users'].search(
					['&',
						'|', ('login', '=', rec.tmp_username), ('email', '=', rec.csm_email_id),
						'|', ('active', '=', True), ('active', '=', False)])
				if user:
					if user.login == rec.tmp_username:
						raise ValidationError(f"User {user.name} with same username already exists!")
					elif user.email == rec.csm_email_id:
						raise ValidationError(f"User {user.name} with same email already exists!")

			""" User to be created if Create User is checked """
			if rec.need_user and rec.tmp_username and rec.csm_email_id:
				user_vals['image'] = rec.image
				user_vals['name'] = rec.name
				user_vals['email'] = rec.csm_email_id
				user_vals['login'] = rec.tmp_username
				user_vals['branch_id'] = rec.location_id.id
				user_vals['action_id'] = int(user_action) if user_action else False
				# user_vals['new_joinee_id'] = rec.id

				''' Passing branch_ids in res.users - Modified by Soumyajit Pan '''
				user_vals['branch_ids'] = [(6, 0, [rec.location_id.id])]
				user_vals['home_action_id'] = int(self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action'))

				new_user_rec = self.env['res.users'].sudo().create(user_vals)

			""" Employee record to be created with all given details """
			emp = self.env['hr.employee'].search([('work_email','=', rec.csm_email_id)])
			if emp and rec.csm_email_id != False:
				continue
				# raise ValidationError(f"Employee {emp.name} already exists!")
			else:
				new_emp_rec = self.env["hr.employee"].sudo().create({
					'base_branch_id': rec.location_id.id,
					'job_branch_id': rec.tmp_worklocation_id.id,
					'work_email': rec.csm_email_id,
					'user_id': new_user_rec.id if rec.need_user and rec.tmp_username and rec.csm_email_id else False,
					'image': rec.image,
					'name': rec.name,
					'department_id': rec.dept_name.id,
					'division': rec.division.id,
					'section': rec.section.id,
					'practise': rec.practise.id,
					'job_id': rec.job_id.id,
					'resource_calendar_id': rec.tmp_shift.id if rec.tmp_shift else rec.tmp_worklocation_id.default_shift_id.id,
					'birthday': rec.birthday,
					'gender': rec.gender,
					'marital_sts' : rec.marital.id,
					'domain_login_id': rec.domain_login_id,
					'job_title': rec.job_id.name,
					'grade': rec.tmp_grade.id,
					'emp_band': rec.tmp_band.id,
					'date_of_joining': rec.tmp_join_date,
					'date_of_completed_probation': rec.tmp_prob_compl_date,
					'on_probation': rec.tmp_on_probation,
					'emp_category': rec.emp_category.id,
					'id_card_no': rec.id_card_no.id,
					'employement_type': rec.employement_type.id,
					'emp_religion': rec.emp_religion.id,
					'mother_tongue_id': rec.mother_tounge_ids.id,
					'permanent_addr_city': rec.permanent_addr_city,
					'parent_id': rec.tmp_admin_auth.id,
					'coach_id': rec.tmp_func_auth.id,
					'blood_group': rec.blood_group,
					'country_id': rec.country_id.id,
					'emp_refered': rec.tmp_source_id.id,
					'emp_reference_walkindrive': rec.tmp_reference_walkindrive,
					'emp_reference_print_media': rec.tmp_reference_print_media,
					'emp_reference_job_fair': rec.tmp_reference_job_fair,
					'emp_employee_referred': rec.tmp_employee_referred.id,
					'emp_media_id': rec.tmp_media_id.id,
					'emp_institute_id': rec.tmp_institute_id.id,
					'emp_consultancy_id': rec.tmp_consultancy_id.id,
					'emp_jportal_id': rec.tmp_jportal_id.id,
					'emp_service_partner_id': rec.tmp_service_partner_id.id,
					'emp_reference': rec.tmp_reference,
					'emp_code_ref': rec.tmp_code_ref,
					'present_addr_street': rec.present_addr_street,
					'present_addr_street2': rec.present_addr_street2,
					'present_addr_country_id': rec.present_addr_country_id.id,
					'present_addr_city': rec.present_addr_city,
					'present_addr_state_id': rec.present_addr_state_id.id,
					'present_addr_zip': rec.present_addr_zip,
					'same_address': rec.same_address,
					'permanent_addr_street': rec.permanent_addr_street,
					'permanent_addr_street2': rec.permanent_addr_street2,
					'permanent_addr_country_id': rec.permanent_addr_country_id.id,
					'permanent_addr_state_id': rec.permanent_addr_state_id.id,
					'permanent_addr_zip': rec.permanent_addr_zip,
					'biometric_id': rec.biometric_id,
					'epbx_no': rec.epbx_no if rec.epbx_no and rec.epbx_no != False else '',
					'domain_login_pwd': rec.domain_login_pwd,
					'outlook_pwd': rec.outlook_pwd,
					'mobile_phone': rec.mobile,
					'emp_role': rec.emp_role.id,
					'experience_sts': '2',  # to be sent experience as default -- Abhijit
					'basic_at_join_time': rec.basic_at_join_time,
					'medical_reimb': rec.medical_reimb,
					'transport': rec.transport,
					'productivity': rec.productivity,
					'commitment': rec.commitment,
					'enable_payroll': rec.enable_payroll,
					'enable_epf': rec.enable_epf,
					'enable_gratuity': rec.enable_gratuity,
					'is_consolidated':rec.is_consolidated,
					'current_ctc': rec.current,
					'at_join_time_ctc': rec.tmp_at_join_time,
					'whatsapp_no': rec.whatsapp_no,
					'emergency_contact': rec.emgr_contact,
					'emergency_phone': rec.emgr_phone,
					'known_language_ids': [[0, 0, {
						'language_id': r.language_id.id,
						'reading_status': r.reading_status,
						'writing_status': r.writing_status,
						'speaking_status': r.speaking_status,
						'understanding_status': r.understanding_status,
					}] for r in rec.known_language_ids],
					'identification_ids': [[0, 0, {
						'name': r.name,
						'doc_number': r.doc_number,
						'date_of_issue': r.date_of_issue,
						'date_of_expiry': r.date_of_expiry,
						'renewal_sts': r.renewal_sts,
						'uploaded_doc': r.uploaded_doc,
						'doc_file_name': r.filename,
					}] for r in rec.identification_ids],
					'educational_details_ids': [[0, 0, {
						'course_type': r.course_type,
						'course_id': r.course_id.id,
						'stream_id': r.stream_id.id,
						'university_name': r.university_name.id,
						'passing_year': str(r.passing_year),
						'division': r.division,
						'marks_obtained': r.marks_obtained,
						'uploaded_doc': r.uploaded_doc,
						'doc_file_name': r.filename,
						'passing_details': [(6, 0, r.passing_details.ids)],
					}] for r in rec.educational_ids],
					'work_experience_ids': [[0, 0, {
						'country_id': r.country_id.id,
						'name': r.name,
						'designation_name': r.designation_name,
						'organization_type': r.organization_type.id,
						'industry_type': r.industry_type.id,
						'effective_from': r.effective_from,
						'effective_to': r.effective_to,
						'uploaded_doc': r.uploaded_doc,
						'doc_file_name': r.filename,
					}] for r in rec.work_experience_ids],
					'identification_id': aadhar_num,
					'passport_id': passport_num,
					'personal_email': rec.email,
					'no_attendance': True if rec.tmp_enable_attendance == 'no' else False,
					'attendance_mode_ids': [(6,0,rec.atten_mode_ids.mapped('id'))] if rec.tmp_enable_attendance == 'yes' else False,
					'wedding_anniversary': rec.wedding_anniversary,
					'bank_account': rec.bank_account,
					'bankaccount_id': rec.bank_id.id,
					'image_url': rec.image_url,
					'location': rec.tmp_location,
					'wfa_city': rec.wfa_city.id,
					'workstation_id': rec.work_station_id.id if rec.work_station_id else False,
					# 'emp_project_id': rec.project_id.id if rec.project_id else False,
					'client_location': rec.tmp_client_location if rec.tmp_client_location else False,
					'start_date': rec.start_dt if rec.start_dt else False,
					'end_date': rec.end_dt if rec.end_dt else False,
					'direct_indirect': rec.direct_indirect,
					'hra': rec.hra,
					'conveyance': rec.conveyance,
					'current_basic': rec.current_basic,
					'need_sync': False if rec.need_sync == False else True,
					'infra_id': rec.infra_id.id if rec.infra_id else False,
					'will_travel': rec.will_travel,
					'travel_abroad': rec.travel_abroad,
					'travel_domestic': rec.travel_domestic,
					'linkedin_url': rec.linkedin_url,
					'cosolid_amnt': rec.cosolid_amnt,
					'acc_branch_unit_id': rec.branch_unit_id.id if rec.branch_unit_id else False,
					'struct_id': rec.struct_id.id if rec.struct_id else False,
					'bond_required': rec.bond_required if rec.bond_required else False,
					'bond_years': rec.bond_years if rec.bond_years else False,
					'bond_months': rec.bond_months if rec.bond_months else False,
					'medical_certificate': rec.medical_certificate if rec.medical_certificate else False,
					'certificate_name': rec.certificate_name if rec.certificate_name else False,
					'onboarding_id': rec.id,
					'infra_unit_loc_id': rec.infra_unit_loc_id.id if rec.infra_unit_loc_id else False,
					'sbu_master_id': rec.sbu_master_id.id if rec.sbu_master_id else False,
					'sbu_type': rec.sbu_type,
					'uan_id': rec.uan_id,
					'esi_id': rec.esi_id,
					'personal_bank_name': rec.personal_bank_name,
					'personal_bank_account': rec.personal_bank_account,
					'personal_bank_ifsc': rec.personal_bank_ifsc,
					'pf_deduction': rec.pf_deduction,
					'mrf_id': rec.mrf_id.id if rec.mrf_id else False,
					'budget_type': rec.budget_type,
					'emp_project_id': rec.project_name_id.id if rec.project_name_id else False,

					'family_details_ids': [[0, 0,
						{'relationship_id': self.env['kwmaster_relationship_name'].sudo().search([('kw_id', '=', 3)], limit=1).id,
							'name': rec.applicant_father_name if rec.applicant_father_name else 'NA',
							'date_of_birth': rec.applicant_father_dob,
							'gender': 'M',
							'dependent': '2'}],
						[0, 0,
							{'relationship_id': self.env['kwmaster_relationship_name'].sudo().search([('kw_id', '=', 4)], limit=1).id,
								'name': rec.applicant_mother_name if rec.applicant_mother_name else 'NA',
								'date_of_birth': rec.applicant_mother_dob,
								'gender': 'F',
								'dependent': '2'}]]
				})
				# 'budget_type': rec.mrf_id.requisition_type if rec.mrf_id and rec.mrf_id.requisition_type else False,
				# 'type_of_project': rec.mrf_id.type_project if rec.mrf_id.type_project else False,
				# 'engagement': rec.mrf_id.duration,
				# 'emp_project_id': rec.mrf_id.project.id if rec.mrf_id.project else False,
				# 'emp_project_id': rec.applicant_id.mrf_project.id if rec.applicant_id.mrf_project else rec.mrf_id.project.id if rec.mrf_id.project else False,


			""" Create bank account record in res.partner.bank """
			if rec.bank_account != False:
				bank_vals = {}
				bank = self.env['res.partner.bank'].sudo()
				bank_vals['acc_number'] = rec.bank_account
				bank_vals['bank_id'] = rec.bank_id.id
				bank_vals['partner_id'] = new_user_rec.partner_id.id

				bank.create(bank_vals)

			""" Create Post Onboarding Checklist """
			if rec.direct_indirect != '2':
				post_rec = self.env['kw_employee_onboarding_checklist'].sudo()
				post_rec_vals = {}

				post_rec_vals['employee_id'] = new_emp_rec.id
				post_rec_vals['image'] = rec.image
				post_rec_vals['designation_id'] = rec.job_id.id
				post_rec_vals['pf'] = rec.enable_epf if rec.enable_payroll == 'yes' else 'no'
				post_rec_vals['gratuity'] = rec.enable_gratuity if rec.enable_payroll == 'yes' else 'no'
				post_rec_vals['email_id_creation'] = 'yes' if rec.csm_email_id else 'no'
				post_rec_vals['telephone_extention'] = 'yes' if rec.epbx_no else 'no'
				post_rec_vals['id_card'] = 'no' # 'yes' if rec.card_no.id else 'no' '''to be sent always as no Pratima'''
				post_rec_vals['location'] = rec.tmp_location
				post_rec_vals['work_station'] = 'yes'
				post_rec_vals['workstation_id'] = rec.work_station_id.id if rec.tmp_location == 'offsite' else False
				post_rec_vals['infra_id'] = rec.infra_id.id if rec.tmp_location == 'offsite' else False
				post_rec_vals['wfa_city'] = rec.wfa_city.id if rec.tmp_location == 'wfa' else False
				post_rec_vals['client_location'] = rec.tmp_client_location
				post_rec_vals['kw_id_generation'] = 'yes' if rec.need_sync == True else 'no'
				post_rec_vals['kw_profile_update'] = 'yes'

				post_rec.create(post_rec_vals)

			rec.write({'state': '5'})
		return True


	def reject_enroll(self):
		for rec in self:
			rec.write({'state': '6'})
		return True
	#
	# @api.constrains('work_experience_ids', 'birthday')
	# def validate_experience(self):
	# 	if self.work_experience_ids:
	# 		if not self.birthday:
	# 			raise ValidationError("Please enter your date of birthday.")
	# 		for experience in self.work_experience_ids:
	# 			if str(experience.effective_from) < str(self.birthday):
	# 				raise ValidationError("Work experience date should not be less than date of birth.")
	# 			except_experience = self.work_experience_ids - experience
	# 			overlap_experience = except_experience.filtered(
	# 				lambda r: r.effective_from <= experience.effective_from <= r.effective_to or r.effective_from <= experience.effective_to <= r.effective_to)
	# 			if overlap_experience:
	# 				raise ValidationError(f"Overlapping experiences are not allowed.")
	#
	# @api.constrains('educational_ids')
	# def validate_edu_data(self):
	# 	if self.educational_ids and self.birthday:
	# 		for record in self.educational_ids:
	# 			if str(record.passing_year) < str(self.birthday):
	# 				raise ValidationError("Passing year should not be less than date of birth.")
	# 	if self.educational_ids and not self.birthday:
	# 		raise ValidationError("Please enter your date of birth.")
	#
	# @api.constrains('identification_ids')
	# def validate_issue_date(self):
	# 	if self.identification_ids and self.birthday:
	# 		for record in self.identification_ids:
	# 			if str(record.date_of_issue) < str(self.birthday):
	# 				raise ValidationError("Date of issue should not be less than date of birth.")
	# 	if self.identification_ids and not self.birthday:
	# 		raise ValidationError("Please enter your date of birth.")

	@api.onchange('domain_login_id')
	def check_domain_id(self):
		for record in self:
			if record.domain_login_id:
				emp_dom = self.env['hr.employee'].sudo().search(
					[('domain_login_id', '=', record.domain_login_id), '|', ('active', '=', True), ('active', '=', False)])
				enroll_dom = self.env['kwonboard_enrollment'].sudo().search(
					[('domain_login_id', '=', record.domain_login_id), '|', ('active', '=', True), ('active', '=', False)]) - self
				if enroll_dom or emp_dom:
					raise ValidationError("This Domain ID already exists.")

	"""# validate work email"""
	@api.onchange('csm_email_id')
	def check_work_email(self):
		for record in self:
			if record.csm_email_id:
				pass
			# emp_work_email = self.env['hr.employee'].sudo().search(
			#     [('work_email', '=', record.csm_email_id), '|', ('active', '=', True), ('active', '=', False)])
			# enroll_work_email = self.env['kwonboard_enrollment'].sudo().search(
			#     [('csm_email_id', '=', record.csm_email_id), '|', ('active', '=', True), ('active', '=', False)]) - self
			# if emp_work_email or enroll_work_email:
			#     raise ValidationError("This Outlook id already exists...")

	@api.onchange('sbu_type')
	def _onchange_sbu_type(self):
		self.sbu_master_id = False

	@api.constrains('email')
	def check_email(self):
		for record in self:
			pass

	# records = self.env['kwonboard_enrollment'].search([]) - self
	# for info in records:
	#     if info.email == self.email:
	#         raise ValidationError("This  Email ID is already exist.")

	@api.constrains('present_addr_zip')
	def check_present_pincode(self):
		for record in self:
			if record.present_addr_zip:
				if not re.match("^[0-9]*$", str(record.present_addr_zip)) != None:
					raise ValidationError("Present pincode is not valid")

	@api.constrains('permanent_addr_zip')
	def check_permanent_pincode(self):
		for record in self:
			if record.permanent_addr_zip:
				if not re.match("^[0-9]*$", str(record.permanent_addr_zip)) != None:
					raise ValidationError("Permanent pincode is not valid")

	@api.constrains('mobile')
	def check_mobile(self):
		for record in self:
			if record.mobile:
				# if record.location_id.country.name != 'India':
				if not len(record.mobile) == 10:
					raise ValidationError("Your number is invalid for: %s" % record.mobile)
				if not re.match("^[0-9]*$", str(record.mobile)) != None:
					raise ValidationError("Your number is invalid for: %s" % record.mobile)
		# records = self.env['kwonboard_enrollment'].search([]) - self
		# for info in records:
		#     if info.mobile == self.mobile:
		#         raise ValidationError("This mobile number already exists.")

	@api.constrains('image')
	def _check_filename(self):
		allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png']
		for rec in self:
			if rec.image:
				pass

	@api.constrains('medical_certificate')
	def _check_medical_certificate(self):
		allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
		for record in self:
			if record.medical_certificate:
				pass

	"""# method to override the create method and generate a random reference number"""
	@api.model
	def create(self, vals):
		tm = time.strftime('%Y')
		enroll_record_ids = self.search([], order='id desc', limit=1)
		last_id = enroll_record_ids.id
		reference_number = 'CSM' + tm[2:] + str(last_id + 1).zfill(4)
		# reference_msg = 'Hello ' + str(vals['name']) + ', your reference number is :' + str(reference_number) + '. Keep it for future reference. Please visit the link ' + self.env['ir.config_parameter'].sudo().get_param('web.base.url') + ' and fill up your details. '
		reference_msg = (f"Hello {str(vals['name'])}, your reference number is :{str(reference_number)}.",
		f"Keep it for future reference.",
		f"Please visit the link {self.env['ir.config_parameter'].sudo().get_param('web.base.url')} and fill up your details.")
		vals['reference_no'] = reference_number
		new_record = super(kwonboard_enrollment, self).create(vals)

		# Change state to profile submitted if create_full_profile is checked or employment type is indirect outsource

		# if new_record.create_uid.id == 1 and emp_id:
		#     emp = self.env['hr.employee'].sudo().browse(emp_id)
		#     email_to = emp.work_email
		# else:
		#     emp = self.env['res.users'].sudo().browse(new_record.create_uid.id)
		#     email_to = emp.email

		ir_config_params = request.env['ir.config_parameter'].sudo()
		demo_mode_config = ir_config_params.get_param('kw_onboarding_process.module_onboarding_mode_status') or False
		send_mail_config = vals.get('module_onboarding_mail_status') or False
		send_sms_config = vals.get('module_onboarding_sms_status') or False
		hrd_mail = ir_config_params.get_param('hrd_mail') or False
		email_fr = ir_config_params.get_param('kw_onboarding_process.responsible_person')
		emp_id = int(email_fr) if email_fr != 'False' else False
		# For sending SMS
		if not demo_mode_config:
			if send_sms_config:
				template = self.env.ref('kw_onboarding_process.employee_email_template')
				record_id = new_record.id
				force_send=not (self.env.context.get('import_file',False))
				template.send_mail(new_record.id)
		# Send email to candidate on creation if type of employment is other than Contractual Outsourced - Indirect

		if new_record:
			if vals.get('applicant_id'):
				self.env['hr.applicant'].search([('id', '=', vals.get('applicant_id'))]).write({'enrollment_id': new_record.id})

		return new_record

	def button_send_invitation(self):
		self.send_invitation()


	def send_invitation(self):
		ir_config_params = request.env['ir.config_parameter'].sudo()
		send_mail_config = ir_config_params.get_param('kw_onboarding_process.module_onboarding_mail_status') or False
		hrd_mail = ir_config_params.get_param('hrd_mail') or False
		email_fr = ir_config_params.get_param('kw_onboarding_process.responsible_person')
		emp_id = int(email_fr) if email_fr != 'False' else False
		for new_record in self:
			print(send_mail_config, new_record, new_record.tmp_direct_indirect, hrd_mail)
			if send_mail_config and new_record.tmp_direct_indirect != '2' and hrd_mail != False:
				template = self.env.ref('kw_onboarding_process.employee_email_template')
				mail_status = self.env['mail.template'].browse(template.id)\
					.with_context(email_from=hrd_mail, email_cc=self.get_designation_cc(rec_set=new_record),
					resp_mail=self.env['hr.employee'].sudo().browse(emp_id).work_email if emp_id != 'False' else '')\
					.send_mail(new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

	""" Overriding write method to be able to assign/un-assign card upon selection """

	def write(self, values):
		rec = self.env['kwonboard_enrollment'].sudo().search([('id', '=', self.id)])
		result = super(kwonboard_enrollment, self).write(values)
		return result

	""" Overriding unlink method to be able to delete only records which are not approved """

	def unlink(self):
		for rec in self:
			if rec.state == '5':
				raise ValidationError(f'Approved record "{rec.name}" cannot be deleted!')
			else:
				result = super(kwonboard_enrollment, rec).unlink()
		return result


	def home_action_scheduler(self):
		# user_action = self.env.ref('kw_hr_attendance.action_my_office_time')
		user_action =  int(self.env['ir.config_parameter'].sudo().get_param('kw_sync.home_action'))
		query = f"update res_users set action_id = {user_action} where action_id is null"
		self._cr.execute(query)
