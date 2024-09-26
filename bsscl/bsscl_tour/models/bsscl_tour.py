# *******************************************************************************************************************
#  File Name             :   bsscl_tour.py
#  Description           :   This is a Tour model which is used to fill all tour details 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields, api, _
import datetime
from datetime import date
from odoo.exceptions import ValidationError
import re

class BssclTour(models.Model):
	_name = "bsscl.tour"
	_description = "Tour model"
	_inherit = ['mail.thread.cc', 'mail.activity.mixin']
	_rec_name='originating_place_id'

	def _get_default_employee_records(self):
		if self.apply_for == '1':
			datas=self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
			return datas

	apply_for = fields.Selection([('1','Self'),('2','Others')], default="1", string="Apply For/के लिए आवेदन देना")
	date_of_travel = fields.Date(string="Date Of Travel / यात्रा की तिथि")
	originating_place_id = fields.Many2one(comodel_name="res.country.state", string="Originating Place / उद्गम स्थल")
	return_date = fields.Date(string="Return Date / वापसी दिनांक")
	employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name / कर्मचारी का नाम", default=_get_default_employee_records)
	travel_arrangement = fields.Selection(string="Travel Arrangement / यात्रा व्यवस्था",
		selection=[('Self', 'Self / खुद'), ('Company', 'Company / कंपनी')], required=True,
		default="Company")
	purpose_of_travel = fields.Text(string="Purpose Of Travel / यात्रा का उद्देश्य")
	word_limit = fields.Integer(string="Limit", default=500)
	# state = fields.Selection(string='Status / दर्जा',
	# 	selection=[
	# 		('Draft', 'Draft / प्रारूप'),
	# 		('Applied', 'Applied / लागू'),
	# 		('approved_by_manager', 'Approved By Manager / प्रबंधक द्वारा स्वीकृत'),
	# 		('approved_by_deputy', 'Approved By Deputy-Commissioner / उपायुक्त द्वारा स्वीकृत'),
	# 		('completed','Completed / पुरा होना।'),
	# 		('cancelled','Rejected / अस्वीकृत')
	# 	],tracking=True)
	state = fields.Selection(string='Status / दर्जा',
		selection=[
			('Draft', 'Draft / प्रारूप'),
			('Applied', 'Applied / लागू'),
			('completed','Completed / पुरा होना।'),
			('cancelled','Rejected / अस्वीकृत')
		],tracking=True)

	travel_expense_details_ids = fields.One2many(comodel_name="bsscl.tour.travel.expense.details",inverse_name="tour_id", string="Travel Expense / यात्रा खर्च")
	medical_exp_ids = fields.One2many(comodel_name="bsscl.medical.expense", inverse_name="tour_id", string="Medical Expense / चिकित्सा खर्च")
	telephone_bill_exp_ids = fields.One2many(comodel_name="bsscl.telephone.expense", inverse_name="tour_id")
	tour_details_ids = fields.One2many(comodel_name="bsscl.tour.details", inverse_name="tour_id", string="Tour Details / भ्रमण विवरण")
	boolean_checked_by_manager = fields.Boolean('Checked By Manager',compute="_compute_boolean_checked")
	boolean_checked_by_deputy_comm = fields.Boolean('Checked By Deputy Commissioner',compute="_compute_boolean_checked")
	boolean_checked_by_commissioner = fields.Boolean('Checked By Commissioner',compute="_compute_boolean_checked")
	manager_rejection_reason = fields.Text("Manager Rejection Remarks")
	deputy_rejection_reason = fields.Text("Dpt-Commissioner Rejection Remarks")
	commissioner_rejection_reason = fields.Text("Commissioner Rejection Remarks")
	advance_id = fields.Many2one(comodel_name="tour.advance", string="Tour Advance")
	currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')
	advance_amount = fields.Float('Advance Amount')
	tour_settlement_ids = fields.One2many(comodel_name="tour.settlement" , inverse_name="tour_id", string="Tour Settlement")
	travel_booking_ids = fields.One2many(comodel_name="travel.booking" , inverse_name="tour_id", string="Travel Booking")
	amount_total = fields.Float(string="Total Travel cost")
	medical_amount_total = fields.Float(string="Total Medical cost")
	telephone_amount_total = fields.Float(string="Total Telephone bill cost")
	advance_amount_total = fields.Float(string="Advance Claim Amount")
	travel_expense_ammount = fields.Float(string="Travel Expense Amount")
	claim_ammount = fields.Float(string="Tour Claim Amount")

	#***********************************************All Onchange method here *******************************************
	@api.onchange('tour_details_ids')
	def _onchange_tour_details_ids(self):
		if self.tour_details_ids.tour_type == 'Domestic':
			exp_type = self.env['bsscl.tour.allowance'].sudo().search([])
			for rec in exp_type:
				if rec.name == 'X Class':
					self.travel_expense_details_ids = [[0, 0,{
						'expense_type_id': expense.expense_type_id,
						'currency_id': expense.currency_id,
						'amount': expense.amount * float(self.tour_details_ids.number_of_days) if self.tour_details_ids.number_of_days else False,
					}] for expense in rec.expense_ids]
		elif self.tour_details_ids.tour_type == 'International':
			exp_type = self.env['bsscl.tour.allowance'].sudo().search([])
			for rec in exp_type:
				if rec.name == 'I Class':
					self.travel_expense_details_ids = [[0, 0,{
						'expense_type_id': expense.expense_type_id,
						'currency_id': expense.currency_id,
						'amount': expense.amount * float(self.tour_details_ids.number_of_days) if self.tour_details_ids.number_of_days else False,
					}] for expense in rec.expense_ids]
		else:
			pass

	@api.onchange('date_of_travel')
	def _onchange_date_of_travel(self):
		for rec in self:
			if rec.date_of_travel:
				today_date = date.today()
				if rec.date_of_travel <= today_date:
					raise ValidationError('Date of travel should be future date')

	@api.constrains('return_date')
	def _onchange_return_date(self):
		for rec in self:
			if rec.return_date <= rec.date_of_travel:
				raise ValidationError('Date of return should be greater than date of travel')


	@api.onchange('return_date')
	def _onchange_data_return_date(self):
		for rec in self:
			if rec.return_date and (rec.return_date<=rec.date_of_travel):
				raise ValidationError('Date of return should be greater than date of travel')
			
	@api.constrains('purpose_of_travel')
	@api.onchange('purpose_of_travel')
	def _onchnage_purpose_of_travel(self):
		if self.purpose_of_travel:
			self.word_limit = 500 - len(self.purpose_of_travel)
		if self.purpose_of_travel and re.match(r'^[\s]*$', str(self.purpose_of_travel)):
			raise ValidationError("Purpose of travel not allow  only white sapces / यात्रा के उद्देश्य के लिए केवल सफ़ेद सपकेस की अनुमति नहीं है")
		if self.purpose_of_travel and not re.match(r'^[A-Za-z ]*$',str(self.purpose_of_travel)):
			raise ValidationError("Purpose of travel allow only alphabets and space / यात्रा का उद्देश्य केवल अक्षर और स्थान की अनुमति देता है")
	#******************************************* End *****************************************************************

	#******************************** Create Method ******************************************************************
	@api.model
	def create(self,vals):
		res =super(BssclTour, self).create(vals)
		print('=====vals========@@@@@@@@@@@@@@',vals)
		res.state = 'Draft'
		return res
	# *********************************************** End *************************************************************

	@api.depends('state')
	def _compute_boolean_checked(self):
		for rec in self:
			if self.env.user.has_group('bsscl_tour.bsscl_tour_manager_group_id') and rec.state == 'approved_by_manager':
				rec.boolean_checked_by_manager = True
			else:
				rec.boolean_checked_by_manager = False
			if self.env.user.has_group('bsscl_employee.deputy_com_id') and rec.state == 'approved_by_deputy':
				rec.boolean_checked_by_deputy_comm = True
			else:
				rec.boolean_checked_by_deputy_comm = False
			if self.env.user.has_group('bsscl_employee.commissioner_id') and rec.state == 'completed':
				rec.boolean_checked_by_commissioner = True
			else:
				rec.boolean_checked_by_commissioner = False

	
					
	#*****************************  Call these all methods by button click ********************************************
	def action_apply_tour(self):
		for rec in self:
			rec.state = 'Applied'
			tour_purpose = rec.purpose_of_travel
			# print('login_user-------------------------',login_user)
			email = rec.employee_id.work_email
			name = rec.employee_id.user_id.name
			print('name===================',name)
			user = self.env['res.users'].sudo().search([])
			manager = user.filtered(lambda user: user.has_group('bsscl_tour.bsscl_tour_manager_group_id') == True)
			for reccord in manager:
				mngr_name = reccord.name
				mngr_email = reccord.work_email
				print('Manager email===================',mngr_email)
				print('Manager===================',mngr_name)
			commissioner = user.filtered(lambda user: user.has_group('bsscl_employee.commissioner_id') == True)
			for reccord in commissioner:
				com = reccord.work_email

			# print('commissioner==================',commissioner.name)
			deputy_commissioner = user.filtered(lambda user: user.has_group('bsscl_employee.deputy_com_id') == True)
			for reccord in deputy_commissioner:
				deputy = reccord.work_email
			# print("Deputy commissioner========================",deputy_commissioner.name)
			template = self.env.ref('bsscl_tour.create_tour_email_template_id')
			template.with_context(email_to=email,subject=tour_purpose).send_mail(rec.id)

	def action_reject_tour(self):
			if self.state == 'Applied' and not self.manager_rejection_reason:
				raise ValidationError("Please give your rejection remarks")
			if self.state == 'approved_by_manager' and not self.deputy_rejection_reason:
				raise ValidationError("Please give your rejection remarks")
			if self.state == 'approved_by_deputy' and not self.commissioner_rejection_reason:
				raise ValidationError("Please give your rejection remarks")
			for rec in self:
				rec.state = 'cancelled'
	
	def action_approve_tour_by_manager(self):
		for rec in self:
			model_id = self.env['tour.advance'].sudo().search([('state','=','2')])
			print("===============Model Id==============================",model_id)
			if model_id:
				for record in model_id:
					if record.tour_id.id == rec.id:
						raise ValidationError("Tour advace applied by user.Please approve advance and after that approve tour")
			rec.state = 'completed'

	# def action_approve_tour_by_deputy_comm(self):
	# 	for rec in self:
	# 		rec.state = 'approved_by_deputy'

	# def action_approve_tour_by_commissioner(self):
	# 	for rec in self:
	# 		rec.state = 'completed'
			
# ************************************************ End ***********************************************************