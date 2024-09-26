import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceModeMaster(models.Model):
    _name = 'kw_attendance_mode_master'
    _description = 'Attendance Mode Master'

    name = fields.Char(string="Name", required=True)
    alias = fields.Char(string="Alias", required=True)

    color = fields.Integer(
        string='Color', default=4
    )

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Attendance Mode name already exists.'),
        ('alias_unique', 'unique (alias)', "The alias already exists.")
    ]

    @api.constrains('name', 'alias')
    def attendance_mode_validation(self):
        for record in self:
            if not (re.match('^[ a-zA-Z0-9]+$', record.name)):
                raise ValidationError("Name input accepts only alphanumeric values.")
            if not (re.match('^[a-zA-Z0-9_]+$', record.alias)):
                raise ValidationError("Alias input does not accept special characters.")
