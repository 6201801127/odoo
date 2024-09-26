from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SeverityMaster(models.Model):
    _name = 'severity_master'
    _description = 'severity_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('name')
    def validation_for_duplicate_severity(self):
        severity_data = self.env['severity_master'].search([('name', '=', self.name)]) - self
        if severity_data:
            raise ValidationError('This Severity name already Exist.')


class PriorityMaster(models.Model):
    _name = 'priority_master'
    _description = 'priority_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('name')
    def validation_for_duplicate_priority(self):
        severity_data = self.env['priority_master'].search([('name', '=', self.name)]) - self
        if severity_data:
            raise ValidationError('This Priority name alredy Exist.')
