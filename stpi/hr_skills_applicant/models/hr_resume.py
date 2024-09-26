# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.applicant'

    resume_line_applicant_ids = fields.One2many('hr.resume.line.applicant', 'resume_applicant_id', string="Resume lines")
    applicant_skill_ids = fields.One2many('hr.applicant.skill', 'applicant_id', string="Skills")


class ResumeLine(models.Model):
    _name = 'hr.resume.line.applicant'
    _description = "Resume line of an applicant"

    resume_applicant_id = fields.Many2one('hr.applicant', ondelete='cascade')
    name = fields.Char(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    description = fields.Text(string="Description")
    upload_qualification_proof = fields.Binary(string="Upload")
    line_type_id = fields.Many2one('hr.resume.line.type', string="Type")
    type_name=fields.Char(related = 'line_type_id.name')
    title = fields.Many2one('hr.education', string = 'Qualification')
    specialization = fields.Char(string = 'Specialization')
    sequence = fields.Integer(default=100)
    acquired = fields.Selection([('at_appointment_time', 'At Appointment time'),
                                   ('subsequently_acquired', 'Subsequently Acquired'),
                                   ], default='at_appointment_time', string="Acquired")

    _sql_constraints = [
        ('date_check', "CHECK ((date_start <= date_end OR date_end = NULL))", "The start date must be anterior to the end date."),
    ]

    @api.onchange('title','specialization')
    def set_data(self):
        if not self.name and self.title:
            self.name = self.title.name
        if self.title and self.specialization:
            self.name = self.title.name + ' - ' + self.specialization
