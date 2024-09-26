# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class EmployeeLanguage(models.Model):
	_inherit = "employee.language"

	enrole_id=fields.Many2one('kwonboard_enrollment',ondelete='cascade',string="Enrollment ID")
