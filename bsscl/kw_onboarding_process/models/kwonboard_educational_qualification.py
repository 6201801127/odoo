# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from datetime import date, datetime

import os, base64

# from odoo.tools.mimetypes import guess_mimetype



# a model for Education details : opening
class kwonboard_edu_qualification(models.Model):
	_name = 'kwonboard_edu_qualification'
	_description = "A  model to store different educational qualifications of on-boarding."

	course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
		('3', 'Training And Certification')], required=True)
	enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID")
	passing_year = fields.Selection(string="Passing Year", selection='_get_year_list', required=True)
	division = fields.Char(string="Division / Grade", required=True, size=6)
	marks_obtained = fields.Float(string="% of marks obtained", required=True)
	uploaded_doc = fields.Binary(string="Document Upload", attachment=True, required=True)  # ,inverse="_inverse_field"
	filename = fields.Char('filename')
	emp_id = fields.Many2one('hr.employee')
	course_id=fields.Char(string="Course Name",required=True)

	@api.model
	def _get_year_list (self):
		current_year=date.today().year
		return [(str(i),i) for i in range(current_year,1953,-1)]

	@api.model
	def get_year_options (self):
		return self._get_year_list()

