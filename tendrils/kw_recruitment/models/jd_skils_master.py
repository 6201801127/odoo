from odoo import models, fields, api
from odoo.exceptions import ValidationError


class JDSkillsMaster(models.Model):
    _name = 'jd_skills_master'
    _description = 'JD Skills'
    _rec_name = 'skill'

    skill = fields.Char(string="Skill Name")
    skill_code = fields.Char(string="Skill Code")


    @api.model
    def create(self, vals):
        vals['skill_code'] = self.env['ir.sequence'].next_by_code('JDSkillsMaster.sequence') or '/'
        return super(JDSkillsMaster, self).create(vals)
    

    @api.constrains('skill')
    def check_unique_skill(self):
        for record in self:
            normalized_skill = record.skill.strip().lower()
            existing_skills = self.search([('id', '!=', record.id)])
            normalized_existing_skills = list(map(lambda s: s.skill.strip().lower(), existing_skills))
            if normalized_skill in normalized_existing_skills:
                raise ValidationError(f'The skill name "{record.skill}" already exists. Please enter a unique skill.')