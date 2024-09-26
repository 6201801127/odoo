import pytz
import datetime
from datetime import date
import base64
import io
import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import math, random, string
#import secrets

import odoo.addons.calendar.controllers.main as main
from odoo.api import Environment
import odoo.http as http
from odoo.http import request, content_disposition
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.exceptions import ValidationError, AccessDenied


class RecruitmentOfferLetter(http.Controller):

	@http.route('/recruitment/applicant/approve', type='http', auth="none", website=True, method="get", csrf=False)
	def approve_offer_letter(self, db, token, action, view='calendar', id=''):
		# import pdb
		# pdb.set_trace()
		registry = registry_get(db)
		with registry.cursor() as cr:
			# Since we are in auth=none, create an env with SUPERUSER_ID
			env = Environment(cr, SUPERUSER_ID, {})
			mrftoken = env['kw_recruitment_requisition_approval'].sudo().search(
				[('access_token', '=', token), ('status', '=', True)])

			if not mrftoken:
				return Forbidden()
			else:
				generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
				# generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))
				if generate_otp:
					current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
					date_time = current_date_time + datetime.timedelta(0, 600)
					date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
					res = mrftoken.sudo().write(
						{'otp': generate_otp, 'expire_time': date_time}
					)
					# print(f"res >>> {res}")
					# return
					# applicant_id = mrftoken.sudo().applicant_id
					# template_obj = request.env.ref('kw_recruitment.offer_letter_verify_otp_mail_template')
					# mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
					# 	name=applicant_id.partner_name,
					# 	mailto=applicant_id.email_from,
					# 	otp=generate_otp,
					# ).send_mail(applicant_id.id,
					# 			notif_layout='kwantify_theme.csm_mail_notification_light',
					# 			force_send=True)
		return http.request.redirect(f'/accept-offer-letter?db={db}&token={token}', )

	@http.route('/accept-offer-letter', type='http', auth="public", method='get', website=True)
	def accept_offer_letter(self, db='', token='', action='', view='calendar', aid=''):
		registry = registry_get(db)
		with registry.cursor() as cr:
			# Since we are in auth=none, create an env with SUPERUSER_ID
			env = Environment(cr, SUPERUSER_ID, {})
			mrftoken = env['kw_recruitment_requisition_approval'].sudo().search(
				[('access_token', '=', token), ('status', '=', True)])
			# print(f"mrftoken >>> {mrftoken}")
			# return
			if not mrftoken:
				return Forbidden()
			else:
				# generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
				offer_release_id = request.env['hr.recruitment.stage'].sudo().search([('code', '=', 'OR')]).id
				applicant_id = mrftoken.sudo().applicant_id
				# print(f"applicant_id.stage_id.id >>> {applicant_id.stage_id.id} >> {offer_release_id}")
				# return

				if applicant_id.stage_id.id == offer_release_id:
					return http.request.render('kw_recruitment.kw_recruitment_offer_acceptance_button_redirect',
											   {'datas': applicant_id, 'token': token}, )
				else:
					return request.not_found()

	@http.route('/recruitment/verify_offer_letter', type="json", auth="public", method="POST", csrf=False, cors='*')
	def recruitment_otp_verified(self, name='', email='', token='', otp=''):
		if token:
			mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search([('access_token', '=', token)])
			# , ('status', '=', True)
			applicant = mrftoken.sudo().applicant_id
			if name == '':
				name = applicant.partner_name
			# print(f"mrftoken >> {mrftoken}")
			# print(f"applicant >> {applicant}   {name}")

			current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
			date_time = datetime.datetime.strptime(current_date_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

			if mrftoken:
				""" 1) fire mail to hr about offer acceptance
					2) Change the applicant state to offer accepted """
				recruitment_group = request.env.ref('kw_recruitment.group_hr_recruitment_offer_letter_notification')
				recruitment_emp = recruitment_group.sudo().users and recruitment_group.sudo().users.mapped('employee_ids') or False
				email_cc_users = recruitment_emp and recruitment_emp.sudo().mapped('work_email') or []
				# email_cc_users.append(applicant.create_uid.email)
				cc_emails = ','.join(set(email_cc_users))

				mail_to = applicant.offer_id.create_uid.email
				template_obj = request.env.ref('kw_recruitment.offer_accepted_template')
				mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
					name=name,
					mail_to=mail_to,
					cc_emails=cc_emails,
				).send_mail(applicant.id,
							notif_layout='kwantify_theme.csm_mail_notification_light',
							force_send=True)
				stage_id = request.env['hr.recruitment.stage'].sudo().search([('code', '=', 'OA')]).id
				applicant.sudo().write({'stage_id': stage_id, 'acceptance_date': date.today()})
				request.env.user.notify_success("Mail sent successfully.")
				return 'success'
		else:
			return 'status2'

	@http.route('/recruitment/decline_offer_letter', type="json", auth="public", website=False, methods=["POST"], csrf=False, cors='*')
	def recruitment_decline_offer_letter(self, name='', email='', token='', reason='', other_reason='', otp=''):
		if token:
			mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search([('access_token', '=', token)])
			# , ('status', '=', True)
			applicant = mrftoken.sudo().applicant_id
			if name == '':
				name = applicant.partner_name
			current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
			date_time = datetime.datetime.strptime(current_date_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

			if mrftoken:
				""" 1) fire mail to hr about offer Decline
					2) Change the applicant state to offer Declined """
				recruitment_group = request.env.ref(
					'kw_recruitment.group_hr_recruitment_offer_letter_notification')
				recruitment_emp = recruitment_group.sudo().users and recruitment_group.sudo().users.mapped('employee_ids') or False
				email_cc_users = recruitment_emp and recruitment_emp.sudo().mapped('work_email') or []
				# email_cc_users.append(applicant.create_uid.email)
				cc_emails = ','.join(set(email_cc_users))

				mail_to = applicant.offer_id.create_uid.email
				template_obj = request.env.ref('kw_recruitment.offer_declined_template')
				mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
					name=name,
					mail_to=mail_to,
					cc_emails=cc_emails,
				).send_mail(applicant.id,
							notif_layout='kwantify_theme.csm_mail_notification_light',
							force_send=True)
				request.env.user.notify_success("Mail sent successfully.")
				stage_id = request.env['hr.recruitment.stage'].sudo().search([('code', '=', 'OD')]).id
				applicant.sudo().write({'stage_id': stage_id, 'acceptance_date': date.today(),'reason_choose':reason,'special_reason':other_reason})
				return 'success'
		else:
			return 'status2'

	@http.route('/recruitment/offer/accepted/', type="http", auth="public", website=True, methods=["GET"], csrf=False, cors='*')
	def recruitment_offer_approved(self):
		return http.request.render('kw_recruitment.kw_recr_applicant_ofr_acceptance_success')

	@http.route('/recruitment/offer/declined/', type="http", auth="public", website=True, methods=["GET"], csrf=False, cors='*')
	def recruitment_offer_declined(self):
		return http.request.render('kw_recruitment.kw_recr_applicant_ofr_declined')

	@http.route('/recruitment/send_otp', type="json", auth="public", website=True, methods=["POST"], csrf=False, cors='*')
	def recruitment_send_otp(self, name, email, token):
		# print("opt sent--------------------")
		current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
		date_time = current_date_time + datetime.timedelta(0, 600)
		date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
		generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
		# generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))

		if generate_otp:
			mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search(
				[('access_token', '=', token), ('status', '=', True)])
			applicant = mrftoken.sudo().applicant_id

			# applicant = request.env['hr.applicant'].sudo().search([('partner_name', '=', name), ('email_from', '=', email)])
			# mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search(
			#     [('applicant_id', '=', applicant.id), ('status', '=', True)], order='id desc', limit=1)
			mrftoken.sudo().write({'applicant_id': applicant.id, 'otp': generate_otp, 'expire_time': date_time})

			template_obj = request.env.ref('kw_recruitment.offer_letter_verify_otp_mail_template')
			mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
				name=name,
				mailto=email,
				otp=generate_otp,
			).send_mail(applicant.id,
						notif_layout='kwantify_theme.csm_mail_notification_light',
						force_send=True)
			request.env.user.notify_success("Mail sent successfully.")
			return {'success': 'yes'}

	@http.route('/recruitment/offer/view_offer_letter_intern/', type="http", auth="public", website=True, methods=["GET"], csrf=False, cors='*')
	def view_offer_letter_intern(self, **args):
		# employee_app_data = request.env['hr.applicant.offer'].sudo().search([])
		offer_data_intern = {}
		application_data = http.request.env['hr.applicant.offer'].sudo().search([])
		for record in application_data:
			if record.offer_type == "Intern":
				offer_data_intern.update({
					'ref_code': record.ref_code,
					'name': record.name,
					'date': record.current_date,
					'salutation': record.salutation,
					'designation': record.designation,
					'department': record.department,
					'joining_date': record.joining_date,
					'city_id': record.city_id,
					'state_id': record.state_id,
					'currency_id': record.currency_id,
					'first_amount': record.first_amount,
					'amount_in_word': record.amount_in_word,
					'revised_amount': record.revised_amount,
					'amount_in_word_reviised': record.amount_in_word_reviised,
					'annual_amount': record.annual_amount,
					'amount_in_word_annual': record.amount_in_word_annual,
					'agreement_months': record.agreement_months,
					'contact_no': record.contact_no,
					'medical_leave': record.medical_leave,
				})

		return http.request.render('kw_recruitment.kw_recruitment_offer_letter_mail_redirect_intern',offer_data_intern)

	@http.route('/recruitment/offer/view_offer_letter_lateral/', type="http", auth="public", website=True, methods=["GET"], csrf=False, cors='*')
	def view_offer_letter_lateral(self, **args):
		# employee_app_data = request.env['hr.applicant.offer'].sudo().search([])
		offer_data_lat = {}
		application_data = http.request.env['hr.applicant.offer'].sudo().search([])
		for record in application_data:
			if record.offer_type == "Lateral":
				offer_data_lat.update({
					'ref_code': record.ref_code,
					'name': record.name,
					'date': record.current_date,
					'salutation': record.salutation,
					'designation': record.designation,
					'department': record.department,
					'joining_date': record.joining_date,
					'city_id': record.city_id,
					'state_id': record.state_id,
					'currency_id': record.currency_id,
					'annual_amount_lateral': record.annual_amount_lateral,
					'amount_in_word_annual_lat': record.amount_in_word_annual_lat,
					'pt_type': record.pt_type,
					'months': record.months,
					'annual_amount': record.annual_amount,
					'agreement_months': record.agreement_months,
					'contact_no': record.contact_no,
					'medical_leave': record.medical_leave,
					'casual_leave': record.casual_leave,
					'earned_leaves': record.earned_leaves,
				})

		return http.request.render('kw_recruitment.kw_recruitment_offer_letter_mail_redirect_lateral',offer_data_lat)

	@http.route('/recruitment/offer/view_offer_letter_ret/', type="http", auth="public", website=True, methods=["GET"], csrf=False, cors='*')
	def view_offer_letter_ret(self):
		# employee_app_data = request.env['hr.applicant.offer'].sudo().search([])
		offer_data_ret = {}
		application_data = http.request.env['hr.applicant.offer'].sudo().search([])
		for record in application_data:
			if record.offer_type == "RET":
				offer_data_ret.update({
					'ref_code': record.ref_code,
					'name': record.name,
					'date': record.current_date,
					'salutation': record.salutation,
					'designation': record.designation,
					'department': record.department,
					'joining_date': record.joining_date,
					'city_id': record.city_id,
					'state_id': record.state_id,
					'currency_id': record.currency_id,
					'annual_amount_ret': record.annual_amount_ret,
					'amount_in_word_annual_ret': record.amount_in_word_annual_ret,
					'contact_no': record.contact_no,
					'months': record.months,
					'annual_amount': record.annual_amount,
					'agreement_months': record.agreement_months,
					'medical_leave': record.medical_leave,
					'casual_leave': record.casual_leave,
					'earned_leaves': record.earned_leaves,
				})

		return http.request.render('kw_recruitment.kw_recruitment_offer_letter_mail_redirect_ret',offer_data_ret)

	@http.route('/download-applicant-offer-letter/<string:token>', methods=['GET'], csrf=False, type='http', auth="none", website=True)
	def download_applicant_offer_letter(self, token):
		mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search([('access_token', '=', token), ('status', '=', True)])

		if not mrftoken:
			return Forbidden()
		else:
			generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
			# generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))
			if generate_otp:
				current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
				date_time = current_date_time + datetime.timedelta(0, 600)
				date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
				res = mrftoken.sudo().write({'otp': generate_otp, 'expire_time': date_time})
				# print(f"res >>> {res}")
				# return
				applicant_id = mrftoken.sudo().applicant_id
				template_obj = request.env.ref('kw_recruitment.offer_letter_downloar_verify_otp_mail_template')
				# print(applicant_id, template_obj)
				mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
					name=applicant_id.partner_name,
					mailto=applicant_id.email_from,
					otp=generate_otp,
				).send_mail(applicant_id.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=True)
		return http.request.redirect(f'/download-offer-letter/{token}', )

	@http.route('/download-offer-letter/<string:token>', methods=['GET'], csrf=False, type='http', auth="public", website=True)
	def accept_download_offer_letter(self, token, download=False, **args):
		mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search([('access_token', '=', token), ('status', '=', True)])
		if not mrftoken:
			return Forbidden()
		else:
			applicant_id = mrftoken.sudo().applicant_id

			if not download:
				return http.request.render('kw_recruitment.kw_recruitment_offer_download_button_redirect',
											{'applicant': applicant_id, 'token': token}, )
			else:
				report_obj = request.env['hr.applicant.offer'].sudo().search([('applicant_id','=',applicant_id.id)])
				if report_obj.offer_type == 'Intern':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent').sudo().render_qweb_pdf(report_obj.id)
				elif report_obj.offer_type == 'Lateral':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_lateral').sudo().render_qweb_pdf(report_obj.id)
				elif report_obj.offer_type == 'RET':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_ret').sudo().render_qweb_pdf(report_obj.id)
				elif report_obj.offer_type == 'Offshore':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_offshore').sudo().render_qweb_pdf(report_obj.id)

				data_record = base64.b64encode(report_template_id[0])
				
				ir_values = {
					'name': "Offer Letter Report",
					'type': 'binary',
					'datas': data_record,
					'datas_fname': f"{report_obj.applicant_id.partner_name.replace(' ', '-')}-Offer-Letter.pdf",
					'mimetype': 'application/x-pdf',
				}
				pdf_http_headers = [('Content-Type', 'application/pdf'),
									('Content-Disposition', f"attachment; filename={report_obj.applicant_id.partner_name.replace(' ', '-')}-Offer-Letter.pdf"),
									('Content-Length', len(data_record))]
				return request.make_response(report_template_id[0], headers=pdf_http_headers)

	@http.route('/recruitment/verify_offer_letter_download', type="json", auth="public", method="POST", csrf=False, cors='*')
	def recruitment_otp_verified_download(self, token, otp):
		if token and otp:
			mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search(
				[('access_token', '=', token), ('status', '=', True)])
			applicant = mrftoken.sudo().applicant_id
			current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
			date_time = datetime.datetime.strptime(current_date_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

			if mrftoken:
				# print(f"mrftoken.expire_time >> {mrftoken.expire_time} >> {date_time} >> {mrftoken.otp} >> {otp}")
				if mrftoken.otp == otp:
					if mrftoken.expire_time < date_time:
						return 'expired'
					else:
						return 'success'
				else:
					return 'invalid'
		else:
			return 'required'

	# @http.route('/recruitment/offer/download/', type="http", auth="public", website=True, methods=["GET"], csrf=False,
	# 			cors='*')
	# def recruitment_offer_downloaded(self):
	# 	return http.request.render('kw_recruitment.kw_recr_applicant_ofr_download_success')
	@http.route('/recruitment/send_otp/offer_letter', type="json", auth="public", website=True, methods=["POST"], csrf=False,
				cors='*')
	def recruitment_send_otp_download(self, name, email, token):
		current_date_time = datetime.datetime.now(pytz.timezone('UTC'))
		date_time = current_date_time + datetime.timedelta(0, 600)
		date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
		generate_otp = ''.join(random.choice(string.digits) for _ in range(4))
		# generate_otp = ''.join(secrets.choice(string.digits) for _ in range(4))

		if generate_otp:
			mrftoken = request.env['kw_recruitment_requisition_approval'].sudo().search(
				[('access_token', '=', token), ('status', '=', True)])
			applicant = mrftoken.sudo().applicant_id
			mrftoken.sudo().write({'applicant_id': applicant.id, 'otp': generate_otp, 'expire_time': date_time})

			template_obj = request.env.ref('kw_recruitment.offer_letter_downloar_verify_otp_mail_template')
			mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
				name=name,
				mailto=email,
				otp=generate_otp,
			).send_mail(applicant.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=True)
			request.env.user.notify_success("Mail sent successfully.")
			return {'success': 'yes'}

	@http.route('/download-offer-letter', methods=['GET'], csrf=False, type='http', auth="public", website=True, cors='*')
	def download_offer_letter(self, **kw):
		# print('kw===========', kw)
		record_id = int(kw['id'])
		# print("record_id >> ", record_id)
		if record_id:
			# pdf = request.env['hr.application.offer'].sudo().get_pdf(record_id,
			#                                                          'kw_recruitment.report_letter_appointment_permanent',
			#                                                          data=None)
			# pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
			# return request.make_response(pdf, headers=pdfhttpheaders)
			report_obj = request.env['hr.applicant.offer'].sudo().browse(record_id)
			for rec in report_obj:
				if rec.offer_type == 'Intern':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent').render_qweb_pdf(record_id)
				if rec.offer_type == 'Lateral':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_lateral').render_qweb_pdf(record_id)
				if rec.offer_type == 'RET':
					report_template_id = request.env.ref('kw_recruitment.report_letter_appointment_permanent_ret').render_qweb_pdf(record_id)
				data_record = base64.b64encode(report_template_id[0])
				# print("report_template_id  .... ", report_template_id)
				# print("data_record >>>>>>> ", data_record)
				ir_values = {
					'name': "Offer Letter Report",
					'type': 'binary',
					'datas': data_record,
					'datas_fname': f"{rec.name.replace(' ', '-')}-Offer-Letter.pdf",
					'mimetype': 'application/x-pdf',
				}
				pdf_http_headers = [('Content-Type', 'application/pdf'),
									('Content-Disposition', f"{rec.name.replace(' ', '-')}-Offer-Letter.pdf"),
									('Content-Length', len(data_record))]
			return request.make_response(report_template_id[0], headers=pdf_http_headers)
