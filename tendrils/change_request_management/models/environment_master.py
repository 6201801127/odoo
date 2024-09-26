# -*- coding: utf-8 -*-
"""
Model Name: KwEnvironmentMaster

Description: This module contains a model for managing environment master data in Kwantify.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwEnvironmentMaster(models.Model):
    """
    Model class for Environment Master in Kwantify.
    """
    _name = 'kw_environment_master'
    _description = 'Environment Master '

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence')
    is_approval_required = fields.Boolean('PM Approval Required')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code already exist.'),
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class CrOfficerAccess(models.Model):
    """
    Model class for Officer Access in Change Requests.
    """
    _name = 'cr_officer_access'
    _description = 'Officer Access'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    # employee_ids = fields.Many2many(
    #     string='Employee Name',
    #     comodel_name='hr.employee',
    #     relation='officer_emp_rel',
    #     column1='emp_cr_id',
    #     column2='officer_id',
    # )

    @api.constrains('employee_ids')
    def check_single_record(self):
        officer_access_records = self.env['cr_officer_access'].search([])
        if len(officer_access_records) > 1:
            raise ValidationError("Only one record is allowed to give officer access.")

    @api.multi
    def give_officer_group_access(self):
        project_env_data = self.env['kw_project_environment_management'].sudo().search([]).mapped('project_manager_id')
        user_groups = self.env.ref('change_request_management.group_cr_user')
        for user in project_env_data:
            user = user.user_id
            user.write({'groups_id': [(4, user_groups.id)]})

        officer_group = self.env.ref('change_request_management.group_cr_officer')

        officer_access_records = self.env['cr_officer_access'].sudo().search([])
        officer_users = officer_access_records.mapped('employee_id.user_id')
        # print("officer_users >>> ", officer_users, officer_group.users)

        users_to_add = officer_users - officer_group.users
        for user in users_to_add:
            officer_group.sudo().write({'users': [(4, user.id)]})

        users_to_remove = officer_group.users - officer_users
        for user in users_to_remove:
            officer_group.sudo().write({'users': [(3, user.id)]})


class CrconfigurationManager(models.Model):
    """
    Model class for Configuration Manager Access in Change Requests.
    """
    _name = 'cr_configuration_access'
    _description = 'Configuration Manager Access'

    empl_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    def give_config_manager_group_access(self):
        """
        Method to grant access to the configuration manager group.
        """
        configuration_group = self.env.ref('change_request_management.group_cr_configuration_manager')

        configuration_access_records = self.env['cr_configuration_access'].sudo().search([])
        officer_users = configuration_access_records.mapped('empl_id.user_id')

        users_to_add = officer_users - configuration_group.users
        for user in users_to_add:
            configuration_group.sudo().write({'users': [(4, user.id)]})

        users_to_remove = configuration_group.users - officer_users
        for user in users_to_remove:
            configuration_group.sudo().write({'users': [(3, user.id)]})
