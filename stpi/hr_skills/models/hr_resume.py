# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    resume_line_ids = fields.One2many('hr.resume.line', 'resume_employee_id', string="Resume lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")




    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(Employee, self).create(vals_list)
    #     resume_lines_values = []
    #     for employee in res:
    #         line_type = self.env.ref('hr_skills.resume_type_experience', raise_if_not_found=False)
    #         resume_lines_values.append({
    #             'employee_id': employee.id,
    #             'name': employee.company_id.name,
    #             'date_start': employee.create_date.date(),
    #             'description': employee.job_title,
    #             'line_type_id': line_type and line_type.id,
    #         })
    #     self.env['hr.resume.line'].create(resume_lines_values)
    #     return res


class ResumeLine(models.Model):
    _name = 'hr.resume.line'
    _description = "Resume line of an employee"

    resume_employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    name = fields.Char(string='Title')
    date_start = fields.Date(string='Date Start')
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


class ResumeLineType(models.Model):
    _name = 'hr.resume.line.type'
    _description = "Type of a resume line"

    name = fields.Char(required=True)


class ResumeHrEducation(models.Model):
    _name = 'hr.education'
    _description = 'Hr education field'

    name = fields.Char(required = True)