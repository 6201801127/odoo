from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations


class CvSkillMaster(models.Model):
    _name = 'cv_skill_master'
    _description = 'Skill MAster For Curriculum Vitae'

    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Skill")
    
class CvQualificationMaster(models.Model):
    _name = 'cv_qualification_master'
    _description = 'Qualification Master for CV'

    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Qualification")