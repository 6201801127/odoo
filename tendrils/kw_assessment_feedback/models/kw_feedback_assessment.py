# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class kw_feedback_assessment(models.Model):
    _name = "kw_feedback_assessment"
    _description = "Assessment feedback"

    name = fields.Char(string='Assessment Type', required=True, autocomplete="off")
    code = fields.Char(string='Code', autocomplete="off")
    frequency = fields.Selection(string='Frequency',
                                 selection=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('bi_monthly', 'Bi Monthly'),
                                            ('quarterly', 'Quarterly'), ('half_yearly', 'Half yearly'),
                                            ('yearly', 'Yearly'), ('daily', 'Daily'), ('custom', 'Custom')],
                                 required=True)
    is_goal = fields.Boolean(string="Goal Settings", )
    portal = fields.Boolean(string="Portal", )
    face_to_face = fields.Boolean(string="Face to Face", )
    practical_test = fields.Boolean(string="Practical Test", )
    presentation = fields.Boolean(string="Presentation", )
    benchmark = fields.Float(string="Benchmark (in %)", required=True, default="1.00")
    assessment_type = fields.Selection(string='Type', selection=[('probationary', 'Final'), ('periodic', 'Periodic')])

    description = fields.Text(string='Description')
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Assessment type already exists.'),
    ]

    @api.constrains('benchmark')
    def benchmark_validation(self):
        for record in self:
            if record.benchmark < 0 or record.benchmark > 100:
                raise ValidationError("Benchmark percentage should be between 0 to 100.")

    @api.constrains('name')
    def check_name(self):
        record = self.env['kw_feedback_assessment'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError('Exists! Already a same assessment name exist.')

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
