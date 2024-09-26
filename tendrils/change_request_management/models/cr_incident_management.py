"""
Module Name: KwProjectIncidentManagement

Description: This module contains a model for managing incident environments in Kwantify.
"""
from odoo import models, fields, api


class KwProjectIncidentManagement(models.Model):
    """
    Model class for Incident Environment Management in Kwantify.
    """
    _name = 'kw_incident_environment_management'
    _description = 'Incident Environment Management'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string='Project Name', )
    date_time_incident = fields.Datetime(string="Date time of Incident")
    date_time_resolution = fields.Datetime(string="Date time of Resolution")
    incident_type = fields.Selection(string="Incident Type", selection=[('Natural', 'Natural'),
                                                                        ('Manual', 'Manual'),
                                                                        ('Accidental', 'Accidental'),
                                                                        ('Planned', 'Planned')])
    person_envolved = fields.Char(string="Person Envolved")
    any_evidence = fields.Boolean(string="Evidence")
    any_mitigation = fields.Boolean(string="Mitigation")
    description_incident = fields.Text(string="Incident Description")
