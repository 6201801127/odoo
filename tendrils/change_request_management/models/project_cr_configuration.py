# -*- coding: utf-8 -*-
"""

Description: This module contains a model for storing project change request configurations.

"""
from odoo import models, fields, api


class KwProjectCrConfiguration(models.Model):
    """
    Model class for storing project change request configurations.
    """
    _name = 'kw_project_cr_configuration'
    _description = 'Project CR Configuration'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string='Project Name')
    employee_ids = fields.Many2many(string='Employee Name', comodel_name='hr.employee', relation='project_emp_rel',
                                    column1='project_cr_id', column2='emp_id', )

    _sql_constraints = [
        ('project_id_uniq', 'unique(project_id)', 'Project already exists.')
    ]
