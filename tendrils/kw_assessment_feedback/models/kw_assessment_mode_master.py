from odoo import fields,models,api

class AssessmentModeMaster(models.Model):
    _name = 'kw_assessment_mode_master'
    _description = 'Assessment Feedback Mode Master'

    name = fields.Char(string="Name",required=True)

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Assessment Mode name already exists.'),
    ]