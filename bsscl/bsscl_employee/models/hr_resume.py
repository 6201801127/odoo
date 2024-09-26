# -*- coding: utf-8 -*-
# start : merged from hr_skills
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# start : skill section
class SkillLevel(models.Model):
    _name = 'hr.skill.level'
    _description = "Skill Level"

    skill_type_id = fields.Many2one('hr.skill.type')
    name = fields.Char(required=True,string="Name / नाम")
    level_progress = fields.Integer(string="Progress / प्रगति", help="Progress from zero knowledge (0%) to fully mastered (100%).")
    sequence = fields.Integer(default=100, string="Sequence / क्रम")


class SkillType(models.Model):
    _name = 'hr.skill.type'
    _description = "Skill Type"

    name = fields.Char(required=True, string="Name / नाम" )
    skill_ids = fields.One2many('hr.skill', 'skill_type_id', string="Skills", ondelete='cascade')
    skill_level_ids = fields.One2many('hr.skill.level', 'skill_type_id', string="Levels / स्तर", ondelete='cascade')


class Skill(models.Model):
    _name = 'hr.skill'
    _description = "Skill"

    name = fields.Char(required=True ,string="Name / नाम")
    skill_type_id = fields.Many2one('hr.skill.type', string="Skill Type / कौशल प्रकार")


class EmployeeSkill(models.Model):
    _name = 'hr.employee.skill'
    _description = "Skill level for an employee"

    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', string='Skill')
    skill_level_id = fields.Many2one('hr.skill.level', string='Skill Level')
    skill_type_id = fields.Many2one('hr.skill.type', string="Skill Type / कौशल प्रकार")
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (employee_id, skill_id)', _("Two levels for the same skill is not allowed")),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(_("The skill %s and skill type %s doesn't match") % (record.skill_id.name, record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %s is not valid for skill type: %s ") % (record.skill_level_id.name, record.skill_type_id.name))

# end : skill section

class ResumeLineType(models.Model):
    _name = 'hr.resume.line.type'
    _description = "Type of a resume line"

    name = fields.Char(required=True,string="Name / नाम")


class ResumeHrEducation(models.Model):
    _name = 'hr.education'
    _description = 'Hr education field'

    name = fields.Char(required = True,string="Name / नाम")
    
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
            
    @api.constrains('date_start', 'date_end')
    def onchange_date(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))
            
            
class Employee(models.Model):
    _inherit = 'hr.employee'

    resume_line_ids = fields.One2many('hr.resume.line', 'resume_employee_id', string="Resume lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")
   
# end : merged from hr_skills