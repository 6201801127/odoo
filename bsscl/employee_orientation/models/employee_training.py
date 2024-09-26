# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	certificates = fields.Boolean(string="Certificates /प्रमाण पत्र", default=False)
	attended = fields.Boolean("Attended?")
	comment = fields.Char("Comment/Feedback")
	training_id = fields.Many2one('employee.training')

	@api.onchange('attended')
	def _onchange_attended(self):
		if self.attended:
			self.certificates = True
		else:
			self.certificates=False



class EmployeeTraining(models.Model):
	_name = 'employee.training'
	_rec_name = 'program_name'
	_description = "Employee Training"
	_inherit = 'mail.thread'

	program_name = fields.Char(string='Training Program /प्रशिक्षण कार्यक्रम', required=True,size=50)
	program_department = fields.Many2one('hr.department', string='Department /विभाग', required=True)
	program_convener = fields.Many2one('res.users', string='Responsible User /जिम्मेदार उपयोगकर्ता', size=32, required=True,
	default=lambda self: self.env.user.id)
	training_id = fields.One2many('hr.employee', 'training_id', string='Employee Details /कर्मचारी विवरण')
	training_ids = fields.One2many('hr.employee.line', 'training_id', string='Employee Details /कर्मचारी विवरण')
	note_id = fields.Text('Description /विवरण')
	date_from = fields.Datetime(string="Date From /तारीख से")
	date_to = fields.Datetime(string="Date To /की तारीख")
	user_id = fields.Many2one('res.users', string='users /उपयोगकर्ताओं', default=lambda self: self.env.user)
	company_id = fields.Many2one('res.company', string='Company /कंपनी', required=True,
		default=lambda self: self.env.user.company_id)

	state = fields.Selection([
		('new', 'New /नया'),
		('confirm', 'Confirmed /की पुष्टि'),
		('cancel', 'Canceled /रद्द'),
		('complete', 'Completed /पुरा होना'),
		('print', 'Print /छाप'),
	], string='Status /दर्जा', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

	@api.constrains('program_department')
	# @api.onchange('program_department')
	def _onchange_department(self):
		model_id = self.env['employee.training'].sudo().search([('program_department','=',self.program_department.id)]) - self
		if model_id:
			for record in model_id:
				if (self.date_from.date() >= record.date_from.date() and self.date_from.date() <= record.date_to.date()) or (self.date_to.date() <= record.date_to.date() and self.date_to.date() >= record.date_from.date()):
					raise ValidationError("The Date period of existing training is %s to %s for %s department,Hence you can not specify from date and to date in between existing training." % (record.date_from.date(),record.date_to.date(), self.program_department.name))
				

	@api.constrains('date_from', 'date_to')
	def onchange_date_from(self):
		current_Date = datetime.now().date()
		if self.date_from:

			if self.date_from.date() < current_Date:
				raise UserError(_("Training Date can not be less then current date"))
		if self.date_to and self.date_to.date() < current_Date:
			raise UserError(_("Training end Date can not be less then current date"))
		if self.date_to and self.date_from and self.date_from.date() > self.date_to.date():
			raise UserError(_("Training start should be less then end date"))
		emp_list=[]



	@api.constrains('program_name')
	@api.onchange('program_name')	
	def _onchange_program_name(self):
		if self.program_name and not re.match(r'^[A-Za-z\s]*$',str(self.program_name)):
			raise ValidationError("Training Program should be an alphabet")
		

	@api.onchange('program_department')
	def employee_details(self):
		emp_list=[]
		if self.program_department:
			datas = self.env['hr.employee'].search([('department_id', '=', self.program_department.id)])

			for dd in datas:
				emp_list.append((0,0, {
					'employee_id': dd.id,
					'job_id': dd.job_id.id,
					'parent_id': dd.parent_id.id,
					'training_id': self.id
				}))
		self.training_ids = [(6, 0, [])]
		self.training_ids = emp_list

	def print_event(self):
		self.ensure_one()
		started_date = datetime.strftime(self.create_date, "%Y-%m-%d ")
		duration = (self.write_date - self.create_date).days
		pause = relativedelta(hours=0)
		difference = relativedelta(self.write_date, self.create_date) - pause
		hours = difference.hours
		minutes = difference.minutes
		data = {
			'dept_id': self.program_department.id,
			'program_name': self.program_name,
			'company_name': self.company_id.name,
			'date_to': started_date,
			'duration': duration,
			'hours': hours,
			'minutes': minutes,
			'program_convener': self.program_convener.name,
			'id': self.id

		}
		return self.env.ref('employee_orientation.print_pack_certificates').report_action(self, data=data)

	def complete_event(self):
		self.write({'state': 'complete'})

	def confirm_event(self):
		self.write({'state': 'confirm'})

	def cancel_event(self):
		self.write({'state': 'cancel'})

	def confirm_send_mail(self):
		employee_ids = []
		if self.training_ids:
			for emp in self.training_ids:
				if emp.employee_id.user_id:
					employee_ids.append(emp.employee_id.user_id.partner_id.id)
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('employee_orientation', 'orientation_training_mailer')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = dict(self.env.context or {})
		ctx.update({
			'default_model': 'employee.training',
			'default_res_id': self.ids[0],
			'default_partner_ids': [(6,0, employee_ids)],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
		})

		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}


class HREMployeeLine(models.Model):
	_name = 'hr.employee.line'

	training_id = fields.Many2one('employee.training')
	employee_id = fields.Many2one('hr.employee', "Employee Name")
	job_id = fields.Many2one('hr.department', "Department")
	parent_id = fields.Many2one('hr.employee', "Manager")
	attendent = fields.Boolean("Attendent")
	certificates = fields.Boolean("Certificates")
	feedback = fields.Char("Feed Back")