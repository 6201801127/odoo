from odoo import http
from odoo.http import request
import logging, requests
from odoo import models, fields, api, _
from odoo.service import security
from datetime import datetime
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessDenied
from odoo.addons.web.controllers.main import Home
from odoo import http
from odoo.http import request
from odoo.service import security

class OdooPhpSynch(http.Controller):


	@http.route(['/createpropertytax'], type='json', auth='public', csrf=False, methods=['POST'])
	def create_property_tax(self, **kwargs):
		resp_dic={}
		resp_res={}
		property_dic = {}
		property_line_dic = {}
		response=request.jsonrequest
		partner_id = ''
		property_id = ''
		partner_obj = request.env['res.partner'].sudo()
		property_obj = request.env['property.details'].sudo()
		property_line_obj = request.env['property.floor.details'].sudo()
		_logger.info("Property tax json ------------------ %s", response)

		if response.get('owner'):
			for part in response.get('owner'):
				if part.get('name'):
					resp_dic.update({
						'name': part.get('name') or '',
						'street': part.get('adress'),
						'father_name': part.get('father_name'),
						'mobile': response.get('mobile'),
						'email': response.get('email'),
						'property_id': True
					})

			if resp_dic and resp_dic.get('mobile'):
				partner_id = partner_obj.search([('mobile', '=', resp_dic.get('mobile'))], limit=1)
			elif resp_dic and resp_dic.get('email') and not partner_id:
				partner_id = partner_obj.search([('mobile', '=', resp_dic.get('email'))], limit=1)

			if not partner_id:
				partner_id = partner_obj.create(resp_dic)

			if partner_id:
				property_dic.update({'partner_id': partner_id.id, 'active': True, 'data_type': 'property'})
				if response.get('old_holding_no'):
					property_dic.update({'old_holding_no': response.get('old_holding_no')})

				if response.get('new_holding_no'):
					property_dic.update({'new_holding_no': response.get('new_holding_no')})

				if response.get('builtup_area'):
					property_dic.update({'builtup_area': response.get('builtup_area')})
				if response.get('old_pid'):
					property_dic.update({'old_pid': response.get('old_pid')})
				if response.get('new_pid'):
					property_dic.update({'new_pid': response.get('new_pid')})
				if response.get('ward'):
					property_dic.update({'ward': response.get('ward')})
				if response.get('area'):
					property_dic.update({'area': response.get('area')})

				if response.get('road_type'):
					property_dic.update({'road_type': response.get('road_type')})

				if response.get('user_id'):
					property_dic.update({'userid': response.get('user_id')})

				if response.get('remark'):
					property_dic.update({'remark': response.get('remark')})

				if property_dic and property_dic.get('new_holding_no'):
					property_id = property_obj.search([('new_holding_no', '=', property_dic.get('new_holding_no')),
						('partner_id', '=', partner_id.id), ('data_type', '=', 'property')], limit=1)
					if not property_id:
						property_id = property_obj.create(property_dic)

					if property_id and response.get('floor_detail'):
						for floor in response.get('floor_detail'):
							property_line_dic.update({
								'floor_no': floor.get('floor_no') or '',
								'acquisition_year': floor.get('acquisition_year') or '',
								'type_of_use': floor.get('type_of_use') or '',
								'construction_type': floor.get('construction_type') or '',
								'rateble_area': floor.get('rateble_area') or '',
								'use_factor': floor.get('use_factor') or '',
								'occupancy_factor': floor.get('occupancy_factor') or '',
								'property_id': property_id.id
							})
						if  property_id and property_line_dic.get('floor_no'):
							line_id = property_line_obj.search([('property_id', '=', property_id.id),('floor_no', '=', property_line_dic.get('floor_no'))], limit=1)
							if not line_id:
								property_line_obj.create(property_line_dic)
							else:
								line_id.write(property_line_dic)
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
			return resp_res
		if property_id:
			resp_res.update({'status_code':200,'status':"Property tax record created successfully",'property_id':property_id.id})
			return resp_res

	@http.route(['/UpdatePropertyTax'],type='json',auth='public',csrf=False,methods=['POST'])
	def update_property_tax (self, **kwargs):
		resp_dic={}
		resp_res={}
		property_id = ''
		property_dic={}
		property_line_dic={}
		response=request.jsonrequest
		partner_id=''
		partner_obj=request.env['res.partner'].sudo()
		property_obj=request.env['property.details'].sudo()
		property_line_obj=request.env['property.floor.details'].sudo()
		if response.get('owner'):
			for part in response.get('owner'):
				if part.get('name'):
					resp_dic.update({'name':part.get('name') or '','street':part.get('adress'),
						'father_name':      part.get('father_name'),'mobile':response.get('mobile'),
						'email':            response.get('email'),'property_id':True})



		if response.get('old_holding_no'):
			property_dic.update({'old_holding_no':response.get('old_holding_no')})

		if response.get('new_holding_no'):
			property_dic.update({'new_holding_no':response.get('new_holding_no')})

		if response.get('builtup_area'):
			property_dic.update({'builtup_area':response.get('builtup_area')})
		if response.get('old_pid'):
			property_dic.update({'old_pid':response.get('old_pid')})
		if response.get('new_pid'):
			property_dic.update({'new_pid':response.get('new_pid')})
		if response.get('ward'):
			property_dic.update({'ward':response.get('ward')})
		if response.get('area'):
			property_dic.update({'area':response.get('area')})

		if response.get('road_type'):
			property_dic.update({'road_type':response.get('road_type')})

		if response.get('user_id'):
			property_dic.update({'userid':response.get('user_id')})

		if response.get('remark'):
			property_dic.update({'remark':response.get('remark')})

		if property_dic and property_dic.get('new_holding_no'):
			property_id=property_obj.search(
				[('new_holding_no','=',property_dic.get('new_holding_no')),('partner_id','=',partner_id.id)],
				limit=1)
			if property_id:
				property_id= property_obj.create(property_dic)
			else:
				property_id.write(property_dic)


			if property_id and response.get('floor_detail'):
				for floor in response.get('floor_detail'):
					property_line_dic.update({'floor_no':floor.get('floor_no') or '',
						'acquisition_year':              floor.get('acquisition_year') or '',
						'type_of_use':                   floor.get('type_of_use') or '',
						'construction_type':             floor.get('construction_type') or '',
						'rateble_area':                  floor.get('rateble_area') or '',
						'use_factor':                    floor.get('use_factor') or '',
						'occupancy_factor':              floor.get('occupancy_factor') or '',
						'property_id':                   property_id.id})
				if property_id and property_line_dic.get('floor_no'):
					line_id=property_line_obj.search(
						[('property_id','=',property_id.id),('floor_no','=',property_line_dic.get('floor_no'))],
						limit=1)
					if line_id:
						property_line_obj.create(property_line_dic)
					else:
						line_id.write(property_line_dic)



		if property_id:
			resp_res.update(
				{'status_code':200,'status':"Property tax record updated successfully",'property_id':property_id.id})
			return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
		return resp_res

	@http.route(['/createpayment'],type='json',auth='public',csrf=False,methods=['POST'])
	def payment_details (self,**kwargs):
		resp_dic={}
		resp_res={}
		payment_id = ''
		payment_line_dic={}
		response=request.jsonrequest
		payment_id=''
		partner_obj=request.env['res.partner'].sudo()
		payment_obj=request.env['payment.details'].sudo()
		payment_line_obj=request.env['payment.details.line'].sudo()
		if response:
			resp_dic.update({'data_type': 'property'})
			if response.get('pid'):
				resp_dic.update({
					'pid': response.get('pid') or ''
				})
			if response.get('fin_year'):
				resp_dic.update({
					'fin_year': response.get('fin_year') or ''
				})
			if response.get('tax_amount'):
				resp_dic.update({
					'tax_amount': response.get('tax_amount') or ''
				})

			if response.get('arrear'):
				resp_dic.update({
					'arrear': response.get('arrear') or ''
				})
			if response.get('payment_mode'):
				resp_dic.update({
					'payment_mode': response.get('payment_mode') or ''
				})
			if response.get('paid_on'):
				resp_dic.update({
					'paid_on': response.get('paid_on') or ''
				})

			if response.get('transaction_ref_no'):
				resp_dic.update({
					'transaction_ref_no': response.get('transaction_ref_no') or ''
				})

			if response.get('challan_no'):
				resp_dic.update({
					'challan_no': response.get('challan_no') or ''
				})

			if response.get('receipt_no'):
				resp_dic.update({
					'receipt_no': response.get('receipt_no') or ''
				})
			if response.get('received_by'):
				resp_dic.update({
					'received_by': response.get('received_by') or ''
				})
			if response.get('ptax_ref_no'):
				resp_dic.update({
					'ptax_ref_no': response.get('ptax_ref_no') or ''
				})

			if response.get('remark'):
				resp_dic.update({
					'remark': response.get('remark') or ''
				})
			if response.get('status'):
				resp_dic.update({
					'status': response.get('status') or ''
				})
			if resp_dic and response.get('challan_no'):
				payment_id = payment_obj.search([('challan_no', '=', response.get('challan_no')),('data_type', '=', 'property')], limit=1)
				if not payment_id:
					payment_id = payment_obj.create(resp_dic)
				else:
					payment_id.write(resp_dic)
			if response.get('payment_detail'):
				for line in response.get('payment_detail'):
					payment_line_dic.update({
						'transaction_date': line.get('transaction_date') or '',
						'transaction_id': line.get('transaction_id') or '',
						'transaction_amount': line.get('transaction_amount') or '',
						'transaction_mode': line.get('transaction_mode') or '',
						'payment_id': payment_id.id

					})
				if payment_line_dic and line.get('transaction_id'):
					line_id = payment_line_obj.search([('transaction_id', '=', line.get('transaction_id'))], limit=1)
					if line_id:
						line_id.write(payment_line_dic)
					else:
						payment_line_obj.create(payment_line_dic)


		if payment_id:
			resp_res.update({'status_code':200,'status':"Payment created successfully",
				'payment_id':payment_id.id})
			return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
		return resp_res

	@http.route(['/advertisementHoarding'],type='json',auth='public',csrf=False,methods=['POST'])
	def create_advertismenthoarding(self,**kwargs):
		resp_dic={}
		resp_res={}
		property_dic={}
		property_line_dic={}
		response=request.jsonrequest
		partner_id=''
		adv_id=''
		partner_obj=request.env['res.partner'].sudo()
		property_obj=request.env['property.details'].sudo()
		property_line_obj=request.env['property.floor.details'].sudo()
		_logger.info("hoarding tax json ------------------ %s",response)

		if response.get('owner'):
			for part in response.get('owner'):
				if part.get('comp_name'):
					resp_dic.update({'name':part.get('comp_name') or '','street':part.get('adress'),
						'father_name':      part.get('father_name'),'mobile':response.get('mobile'),
						'email':            response.get('email'),'property_id':True})

			if resp_dic and resp_dic.get('mobile'):
				partner_id=partner_obj.search([('mobile','=',resp_dic.get('mobile'))],limit=1)
			elif resp_dic and resp_dic.get('email') and not partner_id:
				partner_id=partner_obj.search([('mobile','=',resp_dic.get('email'))],limit=1)

			if not partner_id:
				partner_id=partner_obj.create(resp_dic)

			if partner_id:
				property_dic.update({'partner_id':partner_id.id,'active':True,'data_type':'other'})
				if response.get('old_holding_no'):
					property_dic.update({'old_holding_no':response.get('old_holding_no')})

				if response.get('new_holding_no'):
					property_dic.update({'new_holding_no':response.get('new_holding_no')})

				if response.get('builtup_area'):
					property_dic.update({'builtup_area':response.get('builtup_area')})
				if response.get('old_pid'):
					property_dic.update({'old_pid':response.get('old_pid')})
				if response.get('new_pid'):
					property_dic.update({'new_pid':response.get('new_pid')})
				if response.get('ward'):
					property_dic.update({'ward':response.get('ward')})
				if response.get('area'):
					property_dic.update({'area':response.get('area')})

				if response.get('road_type'):
					property_dic.update({'road_type':response.get('road_type')})

				if response.get('user_id'):
					property_dic.update({'userid':response.get('user_id')})

				if response.get('remark'):
					property_dic.update({'remark':response.get('remark')})

				if property_dic and property_dic.get('new_pid'):
					adv_id=property_obj.search(
						[('new_pid','=',property_dic.get('new_pid')),('partner_id','=',partner_id.id),('data_type', '=', 'other')],
						limit=1)
					if not adv_id:
						adv_id=property_obj.create(property_dic)

		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
			return resp_res
		if adv_id:
			resp_res.update(
				{'status_code':200,'status':"Advertisement Hoarding created successfully",'adv_id':adv_id.id})
			return resp_res

	@http.route(['/createpaymentadvertisement'],type='json',auth='public',csrf=False,methods=['POST'])
	def payment_details_advertisement(self,**kwargs):
		resp_dic={}
		resp_res={}
		payment_id=''
		payment_line_dic={}
		response=request.jsonrequest
		payment_id=''
		partner_obj=request.env['res.partner'].sudo()
		payment_obj=request.env['payment.details'].sudo()
		payment_line_obj=request.env['payment.details.line'].sudo()
		if response:
			resp_dic.update({'data_type':'other'})
			if response.get('application_id'):
				resp_dic.update({'pid':response.get('application_id') or ''})

			if response.get('payment_type'):
				resp_dic.update({'payment_mode':response.get('payment_type') or ''})
			if response.get('payment_ref_no'):
				resp_dic.update({'transaction_ref_no':response.get('payment_ref_no') or ''})


			if response.get('remark'):
				resp_dic.update({'remark':response.get('remark') or ''})
			if response.get('status'):
				resp_dic.update({'status':response.get('status') or ''})
			if resp_dic and response.get('application_id'):
				payment_id=payment_obj.search(
					[('pid','=',response.get('application_id')),('data_type','=','other'), ('payment_type','=','direct')],limit=1)
				if not payment_id:
					payment_id=payment_obj.create(resp_dic)
				else:
					payment_id.write(resp_dic)
			if response.get('payment_detail'):
				for line in response.get('payment_detail'):
					payment_line_dic.update({'transaction_date':line.get('transaction_date') or '',
						'transaction_id':                       line.get('transaction_id') or '',
						'transaction_amount':                   line.get('transaction_amount') or '',
						'transaction_mode':                     line.get('transaction_mode') or '',
						'payment_id':                           payment_id.id

					})
				if payment_line_dic and line.get('transaction_id'):
					line_id=payment_line_obj.search([('transaction_id','=',line.get('transaction_id'))],limit=1)
					if line_id:
						line_id.write(payment_line_dic)
					else:
						payment_line_obj.create(payment_line_dic)

		if payment_id:
			resp_res.update({'status_code':200,'status':"Payment created successfully",'payment_id':payment_id.id})
			return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
		return resp_res

	@http.route(['/updatepaymentadvertisement'],type='json',auth='public',csrf=False,methods=['POST'])
	def update_details_advertisement (self,**kwargs):
		resp_dic={}
		resp_res={}
		payment_id=''
		payment_line_dic={}
		response=request.jsonrequest
		payment_id=''
		partner_obj=request.env['res.partner'].sudo()
		payment_obj=request.env['payment.details'].sudo()
		payment_line_obj=request.env['payment.details.line'].sudo()
		if response:
			resp_dic.update({'data_type':'other', 'payment_type': 'revised'})
			if response.get('application_id'):
				resp_dic.update({'pid':response.get('application_id') or ''})

			if response.get('payment_type'):
				resp_dic.update({'payment_mode':response.get('payment_type') or ''})
			if response.get('payment_ref_no'):
				resp_dic.update({'transaction_ref_no':response.get('payment_ref_no') or ''})

			if response.get('remark'):
				resp_dic.update({'remark':response.get('remark') or ''})
			if response.get('status'):
				resp_dic.update({'status':response.get('status') or ''})
			if response.get('revised_amount'):
				resp_dic.update({'tax_amount':response.get('revised_amount') or ''})

			if resp_dic and response.get('application_id'):
				payment_id=payment_obj.search([('pid','=',response.get('application_id')),
					('data_type','=','other'), ('payment_type','=','revised')],
					limit=1)
				if not payment_id:
					payment_id=payment_obj.create(resp_dic)
				else:
					payment_id.write(resp_dic)
			if response.get('cancelled_detail'):
				for line in response.get('cancelled_detail'):
					payment_line_dic.update({'transaction_date':line.get('transaction_date') or '',
						'transaction_id':                       line.get('transaction_id') or '',
						'transaction_amount':                   line.get('transaction_amount') or '',
						'transaction_mode':                     line.get('transaction_mode') or '',
						'payment_id':                           payment_id.id

					})
				if payment_line_dic and line.get('transaction_id'):
					line_id=payment_line_obj.search([('transaction_id','=',line.get('transaction_id'))],limit=1)
					if line_id:
						line_id.write(payment_line_dic)
					else:
						payment_line_obj.create(payment_line_dic)

		if payment_id:
			resp_res.update({'status_code':200,'status':"Payment created successfully",'payment_id':payment_id.id})
			return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
		return resp_res

	@http.route(['/createemployee'],type='json',auth='public',csrf=False,methods=['POST'])
	def create_employee (self,**kwargs):
		resp_res={}
		emp_res={}
		add_res={}
		response=request.jsonrequest
		employee_id=''
		user_obj = request.env['res.users'].sudo()
		hr_employee = request.env['hr.employee'].sudo()
		_logger.info("Employee sso json ------------------ %s",response)
		if response:
			if response.get('email'):
				email = response.get('email').strip()
				user_id = hr_employee.search([('identify_id', '=', response.get('username'))], limit=1)
				if user_id:
					resp_res.update({'status_code':400,'status':"Invalid Json, User Exist with same User Name",})
					return resp_res
				else:
					emp_res.update({'personal_email': email, 'identify_id':response.get('username')})
				if response.get('name'):
					emp_res.update({'first_name':response.get('name')})
				if response.get('mobile'):
					emp_res.update({'mobile_phone':response.get('mobile')})

				if response.get('gender'):
					if response.get('gender') == '1':
						emp_res.update({'gende': 'male'})
					elif response.get('gender') == '2':
						emp_res.update({'gende': 'female'})
					else:
						emp_res.update({'gende':'transgender'})
				if response.get('dob'):
					datetime_object=datetime.strptime(response.get('dob'),'%Y-%m-%d')
					emp_res.update({'birthday':datetime_object.date()})
				if response.get('aadhar'):
					emp_res.update({'aadhar_no': response.get('aadhar')})

				employee_id = hr_employee.create(emp_res)
				if employee_id:
					user_id = user_obj.search([('login','=',email)],limit=1)
					if user_id:
						resp_res.update({'status_code':400,'status':"Invalid Json, User Exist with same email in user",})
						return resp_res
					else:
						user_id = user_obj.create({'login': email, 'name': response.get('name')})
						if user_id:
							if response.get('confirm_password'):
								user_id.password = response.get('confirm_password')
							employee_id.user_id = user_id.id
			else:
				resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json with Email"})
				return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
			return resp_res
		if employee_id:
			resp_res.update(
				{'status_code':200,'status':"Employee created successfully",'employee_id':employee_id.id})
			return resp_res

	@http.route(['/updateemployee'],type='json',auth='public',csrf=False,methods=['POST'])
	def update_employee (self,**kwargs):
		resp_res={}
		emp_res={}
		add_res={}
		response=request.jsonrequest
		employee_id=''
		user_obj=request.env['res.users'].sudo()
		hr_employee=request.env['hr.employee'].sudo()
		_logger.info("Employee sso json ------------------ %s",response)
		if response:
			if response.get('username'):
				email=response.get('email').strip()
				employee_id=hr_employee.search([('identify_id','=',response.get('username'))],limit=1)
				if not employee_id:
					resp_res.update({'status_code':400,'status':"Invalid Json, User does not exist with User Name",})
					return resp_res
				else:
					emp_res.update({'personal_email':email, 'identify_id': response.get('username')})
				if response.get('name'):
					emp_res.update({'first_name':response.get('name')})
				if response.get('mobile'):
					emp_res.update({'mobile_phone':response.get('mobile')})

				if response.get('gender'):
					if response.get('gender')=='1':
						emp_res.update({'gende':'male'})
					elif response.get('gender')=='2':
						emp_res.update({'gende':'female'})
					else:
						emp_res.update({'gende':'transgender'})
				if response.get('dob'):
					datetime_object=datetime.strptime(response.get('dob'),'%Y-%m-%d')
					emp_res.update({'birthday':datetime_object.date()})
				if response.get('aadhar'):
					emp_res.update({'aadhar_no':response.get('aadhar')})

				if employee_id:
					employee_id.write(emp_res)
					user_id= user_obj.search([('login','=',email)],limit=1)

					if user_id:
						user_obj.write({'name':response.get('name')})
						if response.get('confirm_password'):
							user_id.password=response.get('confirm_password')
			else:
				resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json with Email"})
				return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
			return resp_res
		if employee_id:
			resp_res.update({'status_code':200,'status':"Employee updated successfully",'employee_id':employee_id.id})
			return resp_res

	@http.route(['/getemployee'],type='json',auth='public',csrf=False,methods=['GET'])
	def get_employee_details(self,**kwargs):
		resp_res={}
		emp_res={}
		add_res={}
		response=request.jsonrequest
		employee_id=''
		user_obj=request.env['res.users'].sudo()
		hr_employee=request.env['hr.employee'].sudo()
		_logger.info("Employee sso json ------------------ %s",response)
		if response:
			if response.get('username'):
				employee_id=hr_employee.search([('identify_id','=',response.get('username'))],limit=1)
				if not employee_id:
					resp_res.update({'status_code':400,'status':"Invalid Json, User does not exist with User Name",})
					return resp_res
			else:
				resp_res.update({'status_code':400,'status':"Invalid Json, Please check Json",})
				return resp_res


			if employee_id:
				emp_res.update({
					'userType':'1',
					'aadhar': employee_id.aadhar_no,
					'name': employee_id.first_name,
					'dob': employee_id.birthday,
					'mobile': employee_id.mobile_phone,
					'email': employee_id.personal_email,
					'username':employee_id.user_id.partner_id.name,
				})
				if employee_id.gende == 'male':
					emp_res.update({'gender': '1'})
				if employee_id.gende == 'female':
					emp_res.update({'gender':'2'})
				else:
					emp_res.update({'gender':'3'})
				resp_res.update({'status_code':200,'status':"Data Fetched successfully", 'Data': emp_res})
				return resp_res
		else:
			resp_res.update({'status_code':400,'status':"Invalid Json",})
			return

	@http.route(['/CreateUserInHRMS'],type='json',auth='public',cors="*",csrf=False,methods=['POST'])
	def create_users_in_details (self,**kwargs):
		response=request.jsonrequest
		res_dic =[]
		login = response.get('login')
		login=login.lower().strip()
		request.env.cr.execute("SELECT id, active FROM res_users WHERE lower(login)=%s",(login,))
		res=request.env.cr.fetchone()
		if res:
			if res[1]:
				res_dic.append({'status_code':200,'status':"User Already exist with given details",'user_id_odoo':res[0]})
				return res_dic
		else:
			_logger.debug("Creating new Odoo user \"%s\" from LDAP"%login)
			SudoUser=request.env['res.users'].sudo().with_context(no_reset_password=True)
			values ={
				'active': True,
				'login': login,
				'name': response.get('Name'),
				'php_user_id': response.get('php_user_id')
			}
			user_id =  SudoUser.create(values)
			if user_id:
				res_dic.append({
					'status_code': 200,
					'status': "User Create sucessfully",
					'user_id_odoo': user_id.id
				})
			else:
				res_dic.append({'status_code':400,'status':"User not Created",'user_id_odoo':False})
			return res_dic

		raise AccessDenied(_("No local user found for Php login and not configured to create one"))






class ImpersonateHome(Home):
	@http.route("/php/login", type="http", auth="none", sitemap=False)
	def impersonate_user(self, **kw):
		if kw.get('data'):
			php_url = request.env['php.url'].sudo().search([], limit=1)
			user_detailes = self.get_user_attribute(kw.get('data'),php_url )
			if user_detailes.status_code == 200 :
				res = user_detailes.json()
				if  res['active'] and res['username'] :
					data = self.get_user_detailes(res['username'], php_url)
					if data.status_code == 200:
						final_d = data.json()
						user_id = request.env['res.users'].search([('php_user_id', '=', final_d['userId'])])
						if user_id:

							uid=request.session.uid=user_id.id
							# invalidate session token cache as we've changed the uid
							request.env["res.users"].clear_caches()
							request.session.session_token=security.compute_session_token(request.session,request.env)

							return http.redirect_with_hash(self._login_redirect(uid))
						else:
							return http.redirect_with_hash(php_url.url5)
				else:
					return http.redirect_with_hash(php_url.url5)
			else:
				return http.redirect_with_hash(php_url.url5)

	def get_user_attribute(self, token,php_url):
		import requests
		import json
		url=php_url.url
		dic_d = {"access_token":token}
		payload=json.dumps(dic_d)
		headers={'Content-Type':'application/json'}
		response=requests.request("POST",url,headers=headers,data=payload)
		return response


	def get_user_detailes(self, user_name, php_url):
		import requests
		import json

		url=php_url.url2

		payload=json.dumps({"username":user_name})
		headers={'Content-Type':'application/json'}

		response=requests.request("POST",url,headers=headers,data=payload)

		return response

# def _login_redirect (self,uid,redirect=None):
# 	partner_sudo=request.env['res.users'].sudo().browse(uid)
# 	print("redirect=========",redirect)
# 	try:
# 		# if partner_sudo.access_type_ids and partner_sudo.partner_type in  ('portfolio','hq','coe', 'center', 'directorate', 'hrms'):
# 		if partner_sudo.access_type_ids:
# 			connection_rec=request.env['server.connection'].search([],limit=1)
# 			url=str(connection_rec.url).strip()
# 			encoded_jwt=jwt.encode({'token':partner_sudo.token},key)
# 			password=str(encoded_jwt.decode("utf-8"))
# 			login=partner_sudo.login
# 			# login ='ragini@asdffd'
#
# 			if len(partner_sudo.access_type_ids)==1:
# 				for access in partner_sudo.access_type_ids:
# 					if access.name=='HRMS':
# 						if connection_rec.instance_type=='coe':
# 							data=url + '/web/switch' + '?' + 'login' + '=' + login + '&' + 'password' + '=' + password
# 							return data
# 						elif connection_rec.instance_type=='hrms':
# 							return '/web'
# 						else:
# 							return redirect if redirect else '/web'
# 			else:
# 				return redirect if redirect else '/web'
# 		else:
# 			return '/'
# 	except Exception as e:
# 		return '/'