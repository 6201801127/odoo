from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class KwLeaveTypeCycle(models.Model):
    _name           = 'kw_leave_type_master'
    _description    = "Leave type master sheet"

    name            = fields.Char(string="Name", required=True, size=100)
    leave_code      = fields.Char(string='Leave Code',  required=True)
    description     = fields.Text(string="Description")

    for_probationary        = fields.Boolean(string='Applicable to Probation Employee')   
    employement_type_ids    = fields.Many2many('kwemp_employment_type', string="Applicable For")

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'The name must be unique!'),
    ]

    @api.constrains('leave_code')
    def check_code(self):
        for record in self:
            if not re.match("^[0-9a-zA-Z_]+$", str(record.leave_code)) != None:
                raise ValidationError(
                    "Please remove special character from Leave code")

