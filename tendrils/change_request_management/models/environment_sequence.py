"""
Model: KwEnvironmentSequence

Description: This module contains a model for managing environment sequences in Kwantify.
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwEnvironmentSequence(models.Model):
    """
    Model class for Environment Sequence in Kwantify.
    """
    _name = 'kw_environment_sequence'
    _rec_name = 'environment_id'
    _description = 'Environment Sequence'

    project_id = fields.Many2one('project.project', string='Project')
    environment_id = fields.Many2one('kw_environment_master', string='Environment')
    cr_sequence = fields.Integer('CR Sequence')
    service_sequence = fields.Integer('Service Sequence')
    environment_management_id = fields.Many2one('kw_project_environment_management')
    cr_type = fields.Selection(string='Type', selection=[('CR', 'CR'), ('Service', 'Service')])

    @api.constrains('project_id', 'environment_id')
    def _check_project_env_uniq(self):
        for rec in self:
            exists_data = self.env['kw_environment_sequence'].search(
                [('project_id', '=', rec.project_id.id), ('environment_id', '=', rec.environment_id.id),
                 ('id', '!=', rec.id)])
            if exists_data:
                raise ValidationError('Project with this environment already exists.')
