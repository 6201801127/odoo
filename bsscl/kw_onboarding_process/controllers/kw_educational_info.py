# -*- coding: utf-8 -*-
import base64, re

from odoo import http
from odoo.exceptions import ValidationError


class EducationalInfo:
	# #get specilization master data
	def getSpecializationMaster(self):
		specialization_rec = http.request.env['kwmaster_specializations'].sudo().search([])
		specialization_data = {}

		for record in specialization_rec:
			# print(record.stream_id.course_id.id)
			if record.stream_id.course_id.id not in specialization_data:
				# course_index = course_index+str(record.stream_id.course_id.id)
				specialization_data[record.stream_id.course_id.id] = []

			specialization_data[record.stream_id.course_id.id].append(
				dict(id=record.id,
					stream_id=record.stream_id.id,
					name=record.name,
					course_id=record.stream_id.course_id.id
				)
			)
		return specialization_data

	# #read educational information data from DB
	def getEducationalInfofromDB(self, enroll_data):
		education_data = enroll_data.educational_ids  #
		# print(education_data)
		edudict = {}
		# edudict['edu']  = []
		edudict['professionalcourse'] = []
		edudict['trainingcourse'] = []
		finaltrainingcourse = []
		finalprofessionalcourse = []
		# specialization_data             = {}

		for record in education_data:
			for data in record:

				if record.course_type == '2':
					temp = {'ddlprofStream': data.course_id, 'ddlprofBoard': "dd",
						'ddlprofYear': data.passing_year, 'txtprofGrade': data.division,
						'txtprofPercent': data.marks_obtained, 'proffilename': data.filename}
					finalprofessionalcourse.append(temp)

		edudict['professionalcourse'] = finalprofessionalcourse
		edudict['specialization_master'] = ''
		return edudict

	def saveEducationalinfo(self, enrollment_data, **kw):
		# print(kw)
		try:
			# courses = http.request.env['kwmaster_course_name'].sudo().search([])
			specialization_data = ''

			professional_course_id = training_course_id = 0
			educational_form_data = {}

			kw['trainingcourse'] = kw['professionalcourse'] = []
			employee_data = {'educational_ids': []}

			# fetch existing data from education table
			education_data = enrollment_data.educational_ids  # http.request.env['kwonboard_edu_qualification'].sudo().search([('enrole_id', '=', enrolment_id)])

			edited_education_data = []
			posted_education_info = []
			# saving basic education details
			for course in kw:
				# temp_data = dict()
				#
				# uploaddoc = base64.encodestring(kw['ddlFile'].read()) if kw['ddlFile'] else ''
				stream_id = kw['ddlStream'] or ''
				university_name = kw['ddlBoard'] or ''
				passing_year = kw['ddlPYear'] or ''
				division = kw['txtGrade'].strip() or ''
				marks_obtained = kw['txtPercent'].strip() or ''
				# file_name = kw['hidDllFile'] or ''

				temp_data = {'course_type': '2',
					'course_id': "",
					'stream_id': stream_id,
					'university_name': university_name,
					'passing_year': passing_year,
					'division': division,
					'marks_obtained': marks_obtained,
					'uploaded_doc': '',
					'filename': 'file_name',
					'passing_details': []}

				#
			posted_education_info.append(temp_data)


			if len(posted_education_info) > 0:
				for post_info in posted_education_info:

					if post_info['uploaded_doc'] == b'':
						del post_info['uploaded_doc']
						del post_info['filename']

					if post_info['course_type'] == '1':
						filtered_edit_data = education_data.filtered(lambda r: r.course_id.id == int(post_info['course_id']) and r.course_type == post_info['course_type'])

						if len(post_info['passing_details']):
							post_info['passing_details'] = [[6, 'false', post_info['passing_details']]]

					else:
						filtered_edit_data = education_data.filtered(lambda r: r.course_id == post_info['course_id'])

					if filtered_edit_data:
						employee_data['educational_ids'].append([1, filtered_edit_data.id, post_info])
						edited_education_data.append(filtered_edit_data.id)
					else:
						post_info.pop('course_id')
						post_info.pop('stream_id')
						post_info.pop('passing_details')
						post_info.pop('university_name')
						employee_data['educational_ids'].append([0, 0, post_info])

			# #for the records to be deleted
			if edited_education_data:
				filtered_del_data = education_data.filtered(lambda r: r.id not in edited_education_data)

				if filtered_del_data:
					for del_data in filtered_del_data:
						employee_data['educational_ids'].append([2, del_data.id, False])

			# print(employee_data)

			# #update the onboarding record
			enrollment_data.sudo().write(employee_data)

			# #after saving into db, return data frm db
			resdata = self.getEducationalInfofromDB(enrollment_data)
			resdata['success_msg'] = 'Educational details saved successfully'

			if 'draft' in kw:
				resdata['draft'] = kw['draft']
			return resdata

		except Exception as e:
			http.request._cr.rollback()
			kw['err_msg'] = str(e)

			return kw
