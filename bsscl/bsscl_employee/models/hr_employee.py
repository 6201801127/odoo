# -*- coding: utf-8 -*-
import base64,re
from datetime import datetime,date,timedelta
from odoo import models,fields,api,_
from odoo import tools
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.addons.kw_utility_tools import kw_validations, kw_whatsapp_integration



class EmployeeAddress(models.Model):
	_name='employee.address'
	_description='Address'

	def default_country (self):
		return self.env['res.country'].search([('code','=','IN')],limit=1)

	address_type=fields.Selection(
		[('permanent_add','Permanent Add'),('present_add','Present Add'),('office_add','Office Add'),
			('hometown_add','HomeTown Add'),('communication_add','Communication Add')],string='Address Type',
		required=True)

	resource_calendar_id=fields.Many2one('resource.calendar','Working Hours',store=True,readonly=False)
	employee_id=fields.Many2one('hr.employee','Employee Id')
	street=fields.Char('Address Line 1')
	street2=fields.Char('Address Line 2')
	zip=fields.Char('PIN',change_default=True)
	is_correspondence_address=fields.Boolean('Is Correspondence Address')
	city_id=fields.Many2one('res.city','City/District')
	city=fields.Char('City')
	state_id=fields.Many2one("res.country.state",string='State')
	country_id=fields.Many2one('res.country',string='Country',default=default_country)
	count=fields.Integer('Count')
	image=fields.Binary("Photo",attachment=True,
		help="This field holds the image used as photo for the employee, limited to 1024x1024px.")

	image_medium=fields.Binary("Medium-sized photo",attachment=True,
		help="Medium-sized photo of the employee. It is automatically "
			 "resized as a 128x128px image, with aspect ratio preserved. "
			 "Use this field in form views or some kanban views.")
	image_small=fields.Binary("Small-sized photo",attachment=True,
		help="Small-sized photo of the employee. It is automatically "
			 "resized as a 64x64px image, with aspect ratio preserved. "
			 "Use this field anywhere a small image is required.")


class EmployeeInherit(models.Model):
	_inherit='hr.employee'

	def action_promotion (self):
		pass

	def default_country (self):
		return self.env['res.country'].search([('code','=','IN')],limit=1)

	branch_id=fields.Many2one('res.branch',string='Center',store=True,track_visibility='onchange')
	country_id=fields.Many2one('res.country',string='Country',default=default_country)
	department_id=fields.Many2one('hr.department',track_visibility='onchange')
	job_id=fields.Many2one('hr.job',track_visibility='onchange',string="Post")
	parent_id=fields.Many2one('hr.employee',track_visibility='onchange')
	manager=fields.Boolean(track_visibility='onchange')

	date_join_month=fields.Integer(compute='compute_date_join_month',store=True)
	file_no=fields.Char('File No',track_visibility='always')
	file_open_date=fields.Date('File Open Date',track_visibility='always')
	file_close_date=fields.Date('File close Date',track_visibility='always')
	file_remark=fields.Text('Remark',track_visibility='always')
	name=fields.Char(string="Employee Name",store=True,readonly=False,tracking=True)
	user_id=fields.Many2one('res.users','User',store=True,readonly=False)
	active=fields.Boolean('Active',default=True,store=True,readonly=False)

	# employee_type = fields.Many2one('employee.type', string='Employment type / रोजगार के प्रकार',
	#                                  track_visibility='always', store=True)
	employee_type=fields.Selection(
		[('regular','Regular Employee'),('contractual_with_agency','Contractual with Agency'),
			('contractual_with_bsscl','Contractual with BSSCL')],string='Employment Type',tracking=True,store=True)
	first_name=fields.Char(string="First Name / प्रथम नाम")
	middle_name=fields.Char(string="Middle Name / मध्य नाम")

	last_name=fields.Char(string="Last Name / उपनाम")
	administrative_task_ids=fields.One2many(comodel_name="administrative.task.details",inverse_name="employee_id")
	recruitment_type=fields.Selection([('d_recruitment','Direct Recruitment(DR)'),('transfer','Transfer(Absorption)'),
		('i_absorption','Immediate Absorption'),('deputation','Deputation'),
		('c_appointment','Compassionate Appointment'),('promotion','Promotion'),],'Recruitment Type',
		track_visibility='always',store=True)

	salutation=fields.Many2one('res.partner.title',track_visibility='always')

	fax_number=fields.Char('FAX number',track_visibility='always')

	citizen_number=fields.Char('Citizen Number',track_visibility='always')
	citizen_eligibility_date=fields.Date(string='Date of Eligibility',track_visibility='always')
	citizen_file_data=fields.Binary('Upload',track_visibility='always',attachment=True)
	date_of_eligibility=fields.Date(track_visibility='always')
	citizen_file_name=fields.Char('File Name',track_visibility='always')
	show_citizen_field=fields.Boolean('Show Field',default=False,copy=False,track_visibility='always')

	# religion
	category=fields.Many2one('employee.category',string='Category',track_visibility='always')
	religion=fields.Many2one('employee.religion',string='Religion',track_visibility='always')
	minority=fields.Boolean('Minority',default=False,track_visibility='always')
	validate_details=fields.Boolean("Validate Employee Details",compute='_compute_validate_emp_details',default=True)

	current_office_id=fields.Many2one('res.branch',string="Current Office / वर्तमान कार्यालय")
	emp_stages=[('test_period','Probation'),('contract','Contract'),('deputation','Deputation'),
		('employment','Regular'),]
	state=fields.Selection(emp_stages,string='Stage / स्थिति')
	mid_year_factor=fields.Boolean(string="Mid Year Factor")
	work_shifts=fields.Many2one('resource.calendar',string="Working Shifts / काम की शिफ्ट")
	minority_bool=fields.Boolean(string="Minority visible")
	last_working_date = fields.Date('Last Working Day')
	handbook_info_details_ids = fields.One2many('kw_handbook','employee_id', string = 'Policy Tracking Details / पॉलिसी ट्रैकिंग विवरण')
	show_handbook = fields.Boolean('Show Handbook', compute='check_show_handbook')

	def check_show_handbook(self):
		for record in self:
			record.show_handbook = False
			if record.user_id.id == self.env.user.id:
				record.show_handbook = True


	@api.onchange('category')
	def onchange_category (self):
		for rec in self:
			rec.minority_bool = False
			if rec.category.name == 'General':
				rec.minority_bool = True
			else:
				rec.minority_bool = False
				rec.minority = True

				# def isValid(s):

				#     # 1) Begins with 0 or 91
				#     # 2) Then contains 6,7 or 8 or 9.
				#     # 3) Then contains 9 digits
				#     Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
				#     return Pattern.match(s)

				#   s = "347873923408"
				#   if (isValid(s)):
				#       print ("Valid Number")
				#   else :
				#       print ("Invalid Number")

	def apply_legal_issue (self):
		tree_view=self.env.ref('bsscl_employee.view_legal_issue_tree')

		return {'type': 'ir.actions.act_window','name':_('Legal Issue'),'view_mode':'form',
			'res_model':'change.request','res_id':self.id,'views':[[tree_view.id,'form']],}

	
	def apply_change_request (self):
		tree_view=self.env.ref('bsscl_employee.view_change_request_tree')
		form_view=self.env.ref('bsscl_employee.view_change_request_form')
		model_id = self.env['change.request'].search([])
		# print("model_id==================",model_id)
		hr_data ={
			'employee_id':    self.id,
			'department_id':self.department_id.id if self.department_id.id else '',
			'job_id':self.job_id.id if self.job_id.id else '',
			'country_id':  self.country_id.id if self.country_id.id else '',
			'work_email':self.work_email if self.work_email else '',
			'work_location':self.work_location if self.work_location else '',
			'mobile_phone':self.mobile_phone if self.mobile_phone else '',
			'employee_type':self.employee_type if self.employee_type else '',
			'aadhar_no': self.aadhar_no if self.aadhar_no else '',
			'aadhar_upload': self.aadhar_upload if self.aadhar_upload else '',
		}
		# print("===============================hr_data========================",hr_data)
		# print("===============================get========================",hr_data.get('work_email'))

		self_id = self.env['change.request']
		# print("self_id==================",self_id)
		apl_id = []
		for rec in model_id:
			if rec.employee_id.user_id == self.env.user:
				apl_id.append(rec)
		# print("apl_id==================",apl_id)
		if apl_id:
			# print("+++++++++++if condition called++++++++++++++++++++++++++")
			# print("=======================total change re idapplied id==================",len(apl_id))
			applied_id =[]
			for rec in apl_id:
				if rec.status == 'applied' or rec.status == 'approved':
					applied_id.append(rec)
			# print("=======================total applied id==================",len(applied_id))
			if not applied_id:
				return {'type': 'ir.actions.act_window',
					'name':_('Change Request'),'view_mode':'tree',
					'res_model':'change.request',
					'res_id':self_id.id,
					'tag': 'reload',
					'views':[[form_view.id,'form']],
					'context':{
						'employee_id': hr_data.get('employee_id'),
						'department_id':hr_data.get('department_id'),
						'job_id':hr_data.get('job_id'),
						'country_id':hr_data.get('country_id'),
						'default_work_email':hr_data.get('work_email'),
						'default_work_location':hr_data.get('work_location'),
						'default_mobile_phone':hr_data.get('mobile_phone'),
						'default_employee_type':hr_data.get('employee_type'),
						'default_aadhar_no': hr_data.get('aadhar_no'),
						'default_aadhar_upload': hr_data.get('aadhar_upload'),
				}
				}
			else: 
				raise ValidationError("Some Change request already on applied or validate state once all change request confirmed than you can apply change request. ")
			
		else:
			return {'type': 'ir.actions.act_window',
				'name':_('Change Request'),'view_mode':'tree',
				'res_model':'change.request',
				'res_id':self_id.id,
				'tag': 'reload',
				'views':[[form_view.id,'form']],
				'context':{
					'employee_id': hr_data.get('employee_id'),
					'department_id':hr_data.get('department_id'),
					'job_id':hr_data.get('job_id'),
					'country_id':hr_data.get('country_id'),
					'default_work_email':hr_data.get('work_email'),
					'default_work_location':hr_data.get('work_location'),
					'default_mobile_phone':hr_data.get('mobile_phone'),
					'default_employee_type':hr_data.get('employee_type'),
					'default_aadhar_no': hr_data.get('aadhar_no'),
					'default_aadhar_upload': hr_data.get('aadhar_upload'),
				}
			}

	def action_update_administrative_services (self):
		location=self.work_location
		action={'name': 'Update Administrative Services / अद्यतन प्रशासनिक सेवाएं','view_mode':'form',
			'res_model':'administrative.task','type':'ir.actions.act_window','target':'new',
			'view_id':  self.env.ref('bsscl_employee.employee_administrative_task_view_form_id').id,
			'context':  {'default_current_work_location':location, 'default_employee_id': self.id},}
		return action

	def _compute_validate_emp_details (self):
		for record in self:
			if 'hide_personal' not in self._context and (
				self.env.user.has_group('hr.group_hr_manager') or record.user_id==self.env.user):
				record.validate_details=True
			else:
				record.validate_details=False

	gende=fields.Selection([('male','Male'),('female','Female'),('transgender','Others')],string="Gender",
		track_visibility='always')

	date_of_join=fields.Date('Date of Joining',track_visibility='always')

	#contact
	personal_email=fields.Char('Personal Email',track_visibility='always')
	my_home_phone=fields.Char('Phone (Home)',track_visibility='always')

	#work_infroamtion
	ex_serviceman=fields.Selection([('no','No'),('yes','Yes')],string='Whether Ex Service Man',
		track_visibility='always')

	#physical
	height=fields.Float('Height (in CMs)',track_visibility='always')
	weight=fields.Float('Weight (in KGs)',track_visibility='always')
	blood_group=fields.Selection(
		[('a+','A+'),('a1+','A1+'),('a-','A-'),('b+','B+'),('b-','B-'),('o+','O+'),('o-','O-'),('ab+','AB+'),
			('ab-','AB-')],string='Blood Group',track_visibility='always')

	# def find_age(self):
	#     age = (date.today() - self.birthday) // timedelta(days=365.2425)
	#     return age

	@api.constrains('birthday')
	@api.onchange('birthday')
	def _check_birthday_app (self):
		for employee in self:
			today=datetime.now().date()
			print("today today", today, employee.birthday)
			if employee.birthday:
				if employee.birthday > today:
					raise ValidationError(_('Your DOB can not be a future date. Please enter correct Date of Birth.'))
				if today.year - employee.birthday.year - (
					(today.month,today.day)<(employee.birthday.month,employee.birthday.day))<18:
					raise ValidationError(_('Age Should not be less than 18. Please enter correct Date of Birth.'))
				if today.year - employee.birthday.year - (
					(today.month,today.day)<(employee.birthday.month,employee.birthday.day))>60:
					raise ValidationError(_('Age Should not be greater than 60. Please enter correct Date of Birth.'))


	_sql_constraints=[('pan_uniq','unique (pan_no)','Pan No must be unique!'),
		('aadhar_uniq','unique (aadhar_no)','Aadhar no must be unique!'),
		('passport_uniq','unique (passport_id)','Passport no must be unique!'),
		('uan_uniq','unique (uan_no)','UAN no must be unique!'),

	]

	@api.constrains('first_name', 'middle_name', 'last_name')
	@api.onchange('first_name', 'middle_name', 'last_name')
	def _check_first_name (self):
		for rec in self:
			if rec.first_name:
				if self.first_name.isalpha() == False:
					raise ValidationError(_("Please enter only alphabets in first name of employee..."))
			if rec.middle_name:
				if self.middle_name.isalpha() == False:
					raise ValidationError(_("Please enter only alphabets in middle name of employee..."))
			if rec.last_name:
				if self.last_name.isalpha() == False:
					raise ValidationError(_("Please enter only alphabets in last name name of employee..."))

	@api.constrains('identify_id')
	@api.onchange('identify_id')
	def _check_identify_id (self):
		for rec in self:
			if rec.identify_id:
				if rec.identify_id.isalnum() == False:
					raise ValidationError(_("Please enter only alphabets/numeric data in Identification number of employee..."))

	@api.constrains('work_location')
	@api.onchange('work_location')
	def _check_work_location (self):
		for rec in self:
			if rec.work_location:
				if rec.work_location.isalpha() == False:
					raise ValidationError(_("Please enter only alphabets in work location of employee..."))


	@api.constrains('place_of_birth')
	@api.onchange('place_of_birth')
	def _check_place_of_birth(self):
		if self.place_of_birth:
			if self.place_of_birth.isalpha() == False:
				raise ValidationError(_("Please enter only alphabets in Place of birth contract location of employee..."))

	@api.constrains('emergency_phone')
	@api.onchange('emergency_phone')
	def _check_emergency_phone (self):
		Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
		for rec in self:
			if rec.emergency_phone:
				if not Pattern.match(rec.emergency_phone):
					raise ValidationError(_("Please enter correct Emegency Phone, it must be start from 6 to 9.../ ..."))
				for e in rec.emergency_phone:
					if not e.isdigit():
						raise ValidationError(_("Please enter correct Emegency Phone, it must be numeric.../ ..."))
				if len(rec.emergency_phone)!=10:
					raise ValidationError(_("Please enter correct Emegency Phone, it must be of 10 digits.../..."))

	@api.constrains('my_home_phone')
	@api.onchange('my_home_phone')
	def _check_my_home_phone (self):
		Pattern = re.compile("(0|91)?[0-9]{9}")
		for rec in self:
			if rec.my_home_phone:
				if not Pattern.match(rec.my_home_phone):
					raise ValidationError(_("Please enter correct Phone(Home), it must be start from 6 to 9.../ ..."))
				for e in rec.my_home_phone:
					if not e.isdigit():
						raise ValidationError(_("Please enter Phone(Home), it must be numeric.../ ..."))
				if len(rec.my_home_phone)!=10:
					raise ValidationError(_("Please enter Phone(Home), it must be of 10 digits.../..."))

	@api.constrains('mobile_phone')
	@api.onchange('mobile_phone')
	def _check_mobile_phone (self):
		Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
		for rec in self:
			if rec.mobile_phone:
				if not Pattern.match(rec.mobile_phone):
					raise ValidationError(_("Please enter correct Phone Number, it must be start from 6 to 9.../ ..."))
				for e in rec.mobile_phone:
					if not e.isdigit():
						raise ValidationError(_("Please enter Phone Number, it must be numeric.../ ..."))
				if len(rec.mobile_phone)!=10:
					raise ValidationError(_("Please enter Phone number, it must be of 10 digits.../..."))

	@api.constrains('pan_no')
	@api.onchange('pan_no')
	def _check_pan_number (self):
		for rec in self:
			if rec.pan_no and not re.match(r'^[A-Za-z]{5}[0-9]{4}[A-Za-z]$',str(rec.pan_no)):
				raise ValidationError(_("Please enter correct PAN number.../ कृपया सही पैन नंबर दर्ज करें...."))


	@api.constrains('aadhar_no')
	@api.onchange('aadhar_no')
	def _check_aadhar_number (self):
		for rec in self:
			if rec.aadhar_no:
				for e in rec.aadhar_no:
					if not e.isdigit():
						raise ValidationError(
							_("Please enter correct Aadhar number, it must be numeric.../ कृपया सही आधार संख्या दर्ज करें, यह संख्यात्मक होना चाहिए..."))
				if len(rec.aadhar_no)!=12:
					raise ValidationError(
						_("Please enter correct Aadhar number, it must be of 12 digits.../ कृपया सही आधार संख्या दर्ज करें, यह संख्यात्मक होना चाहिए..."))

	@api.constrains('aadhar_upload')
	def _check_uploaded_aadhar(self):
		allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
		if self.aadhar_upload:
			kw_validations.validate_file_mimetype(self.aadhar_upload, allowed_file_list)
			kw_validations.validate_file_size(self.aadhar_upload, 25)

	@api.constrains('pan_upload')
	def _check_pan_upload(self):
		allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
		if self.pan_upload:
			kw_validations.validate_file_mimetype(self.pan_upload, allowed_file_list)
			kw_validations.validate_file_size(self.pan_upload, 25)

	@api.constrains('passport_upload')
	def _check_passport_upload(self):
		allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
		if self.passport_upload:
			kw_validations.validate_file_mimetype(self.passport_upload, allowed_file_list)
			kw_validations.validate_file_size(self.passport_upload, 25)


	@api.constrains('uan_no')
	@api.onchange('uan_no')
	def _check_uan_number (self):
		for rec in self:
			if rec.uan_no:
				for e in rec.uan_no:
					if not e.isdigit():
						raise ValidationError(
							_("Please enter correct UAN number, it must be numeric.../ कृपया सही यूएएन नंबर दर्ज करें, यह संख्यात्मक होना चाहिए..."))
					if len(rec.uan_no)!=12:
						raise ValidationError(
							_("Please enter correct UAN number, it must be of 12 digits..."))


	@api.constrains('personal_email')
	@api.onchange('personal_email')
	def _check_personal_email (self):
		for rec in self:
			if rec.personal_email and not re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$",str(rec.personal_email)):
				raise ValidationError(_("Please enter correct Email.../ कृपया सही ईमेल दर्ज करें..."))

	@api.constrains('work_email')
	@api.onchange('work_email')
	def _check_work_email (self):
		for rec in self:
			if rec.work_email and not re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$",str(rec.work_email)):
				raise ValidationError(_("Please enter correct Work Email.../ कृपया सही कार्य ईमेल दर्ज करें..."))

	@api.constrains('height')
	def _check_height(self):
		if not self.height > 0:
			raise ValidationError(_("Height should be greater than 0."))

	@api.constrains('weight')
	def _check_height(self):
		if not self.weight > 0:
			raise ValidationError(_("weight should be greater than 0."))


	#Identification
	identify_id=fields.Char(string='Identification No.',copy=False,store=True,track_visibility='always')
	pan_no=fields.Char('PAN Card No.',track_visibility='always')
	uan_no=fields.Char('UAN No.',track_visibility='always')
	pan_upload=fields.Binary('Upload(PAN)',track_visibility='always',attachment=True)
	pan_upload_filename=fields.Char('Upload(PAN) Filename / ')
	aadhar_no=fields.Char('Aadhaar Card No.',track_visibility='always')
	aadhar_upload=fields.Binary('Upload(Aadhaar)',track_visibility='always',attachment=True)
	aadhar_upload_filename=fields.Char('Upload(Aadhaar) Filename')
	passport_upload=fields.Binary('Upload(Passport)',track_visibility='always',attachment=True)
	passport_upload_filename=fields.Char('Upload(Passport) Filename')
	bank_name=fields.Char(string='Bank Name')
	bank_account_number=fields.Char(string='Bank Account number')
	ifsc_code=fields.Char(string='IFSC Code')
	image_name=fields.Char(string=u'Image Name',)

	address_ids=fields.One2many('employee.address','employee_id',string='Address',track_visibility='always')

	partner_id=fields.Many2one('res.partner','Partner',related='user_id.partner_id')
	bank_account_id=fields.Many2one('res.partner.bank','Bank Account Number',)
	is_blind=fields.Boolean('Blind',default=False)
	is_deaf=fields.Boolean('Deaf',default=False)
	is_dumb=fields.Boolean('Dumb',default=False)
	is_ortho_handicapp=fields.Boolean('Orthopedically Handicapped',default=False)
	transfer_date=fields.Date('Joining Date',required=True)
	salary=fields.Float('Salary',track_visibility='always')
	ctc=fields.Float('CTC',track_visibility='always')
	document_count=fields.Integer(compute='_document_count',string='# Documents / दस्तावेज़')
	# Recruitment field by Khusboo
	relative_ids=fields.One2many('employee.relative','employee_id','Relative Ref.')

	no_of_relative=fields.Integer('No of Relative',compute='_compute_no_of_relative',readonly=True)
	vrs_retirement=fields.Integer('VRS Retirement',compute='_compute_no_of_vrs',readonly=True)
	vrs_ids=fields.One2many('bsscl.vrs','employee_id','VRS Ref.')

	change_request=fields.Integer('Change Request',compute='_compute_change_request',readonly=True)

	legal_request=fields.Integer('Change Request',compute='_compute_legal_request',readonly=True)

	change_request_ids=fields.One2many('change.request','employee_id','Change Req.')

	@api.depends('relative_ids')
	def _compute_no_of_relative (self):
		for rec in self:
			rec.no_of_relative=len(rec.relative_ids.ids)

	@api.depends('vrs_ids')
	def _compute_no_of_vrs (self):
		for rec in self:
			rec.vrs_retirement=len(rec.vrs_ids.ids)

	def _compute_legal_request (self):
		for rec in self:
			rec.legal_request=len(self.env['legal.issue'].sudo().search([('employee_id', '=', self.id)]))

	@api.depends('change_request_ids')
	def _compute_change_request (self):
		for rec in self:
			rec.change_request=len(rec.change_request_ids.ids)

	# language field by Khusboo

	lang_ids=fields.One2many('employee.language','employee_id','Language Ref.')
	no_of_lang=fields.Integer('No of Language',compute='_compute_no_of_lang',readonly=True)

	@api.depends('lang_ids')
	def _compute_no_of_lang (self):
		for rec in self:
			rec.no_of_lang=len(rec.lang_ids.ids)

	# educations field by Khusboo

	education_ids=fields.One2many('employee.education','employee_id','Education Ref.')
	no_of_education=fields.Integer('No of Education',compute='_compute_no_of_education',readonly=True)

	@api.depends('education_ids')
	def _compute_no_of_education (self):
		for rec in self:
			rec.no_of_education=len(rec.education_ids.ids)

	# @api.multi
	def _document_count (self):
		for each in self:
			document_ids=self.env['hr.employee.document'].sudo().search([('employee_ref','=',each.id)])
			each.document_count=len(document_ids)

	# @api.multi
	def document_view (self):
		self.ensure_one()
		domain=[('employee_ref','=',self.id)]
		return {'name':_('Documents / दस्तावेज़'),'domain':domain,'res_model':'hr.employee.document',
			'type':    'ir.actions.act_window','view_id':False,'view_mode':'tree,form','view_type':'form','help':_('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),'limit':80,}

	@api.depends('date_of_join')
	def compute_date_join_month (self):
		for rec in self:
			if rec.date_of_join:
				rec.date_join_month=int(rec.date_of_join.strftime('%m'))

	@api.model
	def create (self,vals):
		vals[
			'name']=f"{vals.get('first_name') if vals.get('first_name') else ''} {vals.get('middle_name') if vals.get('middle_name') else ''} {vals.get('last_name') if vals.get('last_name') else ''}"
		result=super(EmployeeInherit,self).create(vals)
		# if not result.identify_id:
		#     if result.employee_type == 'regular':
		#         seq = self.env['ir.sequence'].next_by_code('hr.employee')
		#         result.identify_id = '' + str(seq)
		#     else:
		#         seq = self.env['ir.sequence'].next_by_code('employee.contractual.agency.bsscl')
		#         result.identify_id = f"BSSCL{'T' if result.employee_type == 'contractual_with_agency' else 'C'}{str(seq)}"
		return result

	def write (self,vals):
		first_name=vals.get('first_name') if vals.get('first_name') else ""
		middleName=vals.get('middle_name') if vals.get('middle_name') else ""
		lastName=vals.get('last_name') if vals.get('last_name') else ""
		for rec in self:
			if not first_name and vals.get('first_name')!=False:
				vals['first_name']=rec.first_name
			if not middleName and vals.get('middle_name')!=False:
				vals['middle_name']=rec.middle_name
			if not lastName and vals.get('last_name')!=False:
				vals['last_name']=rec.last_name
		vals[
			'name']=f"{vals.get('first_name') if vals.get('first_name') else ''} {vals.get('middle_name') if vals.get('middle_name') else ''} {vals.get('last_name') if vals.get('last_name') else ''}"

		res=super(EmployeeInherit,self).write(vals)
		return res

	# award page added by khusboo
	suspension_details_ids=fields.One2many('hr.employee.rewards_details','employee_id')
	rewards_details_ids=fields.One2many('hr.employee.rewards_details','employee_id')

	pension_ids=fields.One2many(comodel_name="employee.pension",inverse_name="employee_id",string="Pension / पेंशन")
	punishment_ids=fields.One2many(comodel_name="employee.punishment",inverse_name="employee_id",
		string="Punishment / सजा")


class EmployeePension(models.Model):
	_name='employee.pension'
	_description='Pension'

	employee_id=fields.Many2one('hr.employee','Employee Id')
	start_date=fields.Date(string='Start Date / आरंभ करने की तिथि')
	end_date=fields.Date(string='End Date / अंतिम तिथि')
	amount=fields.Float(string='Amount / राशि')
	approved_by=fields.Many2one(comodel_name="hr.employee",string='Approved by / के द्वारा अनुमोदित')
