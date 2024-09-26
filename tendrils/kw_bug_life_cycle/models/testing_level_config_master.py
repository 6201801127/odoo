from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TestingLevelConfigMaster(models.Model):
    _name = 'testing_level_config_master'
    _description = 'testing_level_config_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('name')
    def validation_testing_level_config_master(self):
        severity_data = self.env['testing_level_config_master'].search([('name', '=', self.name)]) - self
        if severity_data:
            raise ValidationError('This Name already Exist.')
