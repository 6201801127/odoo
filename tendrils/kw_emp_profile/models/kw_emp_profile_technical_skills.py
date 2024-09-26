# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from odoo import tools, _
import re
from lxml import etree
from datetime import date, datetime
from dateutil import relativedelta


# class for technical skills
class kw_emp_profile_technical_skills(models.Model):
    _name = 'kw_emp_profile_technical_skills'
    _description = "A model to store the technical skills of employees."
    _rec_name = "skill_id"

    category_id = fields.Many2one('kwemp_technical_category', string="Category", required=True)
    skill_id = fields.Many2one('kwemp_technical_skill', string="Skill", required=True)
    proficiency = fields.Selection(string="Proficiency",
                                   selection=[('1', 'Excellent'), ('2', 'Good'), ('3', 'Average')], required=True)
    emp_id = fields.Many2one('kw_emp_profile', string="Employee ID")
    emp_technical_id = fields.Many2one('kwemp_technical_skills', string='Technical Id')

    @api.onchange('category_id')
    def change_stream(self):
        self.skill_id = False
        return {'domain': {'skill_id': ([('category_id', '=', self.category_id.id)]), }}

    @api.constrains('proficiency')
    def validate_proficiency(self):
        for record in self:
            if not (record.proficiency):
                raise ValidationError("Please choose your technical proficiency.")

    _sql_constraints = [('technical_skill_uniq', 'unique (emp_id,category_id,skill_id)',
                         'Duplicate technical categories not allowed.!')]
