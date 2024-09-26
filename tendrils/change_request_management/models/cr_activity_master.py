# -*- coding: utf-8 -*-
"""
Module Name: KwCrActivityMaster

Description: This module defines the CR Activity Master model in Kwantify.
"""

from odoo import models, fields, api


class KwCrActivityMaster(models.Model):
    """
    Model class for CR Activity Master in Kwantify.
    """
    _name = 'kw_cr_activity_master'
    _description = 'CR Activity Master '

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)
    cr_type = fields.Selection(string='Type', selection=[('CR', 'CR'), ('SR', 'SR')], default='CR', required=True)
    cr_sub_activity_ids = fields.One2many(comodel_name='kw_cr_sub_activity_master', inverse_name='cr_activity_id',
                                          string='Activity')
    estimate_time = fields.Float('Estimate Time')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code already exist.'),
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]

    @api.onchange('cr_type')
    def _type_onchange(self):
        if self.cr_type == 'CR':
            self.cr_sub_activity_ids = False


class KwCrSubActivityMaster(models.Model):
    """
    Model class for CR Sub Activity Master in Kwantify.
    """
    _name = 'kw_cr_sub_activity_master'
    _description = 'Sub Activity Master '

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence')
    cr_activity_id = fields.Many2one('kw_cr_activity_master')
    estimate_time_sr = fields.Float('Estimate Time (HH:MM)')


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwPlatformMaster(models.Model):
    """
    Model class for Platform Master in Kwantify.
    """
    _name = 'kw_cr_platform_master'
    _description = 'Platform Master '

    name = fields.Char(string='Platform', required=True)
    # code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwOwnerMaster(models.Model):
    """
    Model class for Owner Master in Kwantify.
    """
    _name = 'kw_cr_owner_master'
    _description = 'Owner Master '

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwOsTypeMaster(models.Model):
    """
    Model class for Operating System Type Master in Kwantify.
    """
    _name = 'kw_cr_os_type_master'
    _description = 'OS Type Master '

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwOsMaster(models.Model):
    """
    Model class for OS Master in Kwantify.
    """
    _name = 'kw_cr_os_master'
    _description = 'OS Master '

    name = fields.Char(string='Name', required=True)
    os_type_id = fields.Many2one("kw_cr_os_type_master", string="OS Type")
    server_sequence = fields.Integer(string="Count")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwDatabaseMaster(models.Model):
    """
    Model class for Database Master in Kwantify.
    """
    _name = 'kw_cr_database_master'
    _description = 'Database Master '

    name = fields.Char(string='Name', required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwPlatform1Master(models.Model):
    """
    Model class for Platform1 Master in Kwantify.
    """
    _name = 'kw_cr_platform1_master'
    _description = 'Platform1 Master '

    name = fields.Char(string='Name', required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwPlatform2Master(models.Model):
    """
    Model class for Platform2 Master in Kwantify.
    """
    _name = 'kw_cr_platform2_master'
    _description = 'Platform2 Master '

    name = fields.Char(string='Name', required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwPlatform2Master(models.Model):
    """
    Model representing the infrastructure details master for KwPlatform2.
    """
    _name = 'kw_infra_details_master'
    _description = 'Infra Details Master '

    name = fields.Char(string='Name', required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]


class KwdomainMaster(models.Model):
    """
    Model class for Domain Master in Kwantify.
    """
    _name = 'kw_domain_master'
    _description = 'Domain Master '

    name = fields.Char(string='Name', required=True)
    # domain_master_id =fields.Many2one('kw_cr_project_configuration')
    environment_id = fields.Many2one('kw_environment_master', string="Environment")

    _sql_constraints = [
        ('domain_name_uniq', 'unique(name)', 'Domain Name already exists.'),
    ]


class KwDomainDNSTypeMaster(models.Model):
    """
    Model class for Domain DNS Type Master in Kwantify.
    """
    _name = 'kw_domain_dns_type_master'
    _description = 'Domain DNS Type Master'
    _rec_name = 'sub_domain_name'

    sub_domain_name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('sub_domain_name_uniq', 'unique(sub_domain_name)', 'Name already exists.'),
    ]


class KwAccountHeadMaster(models.Model):
    """
    Model class for Account Head Master in Kwantify.
    """
    _name = 'kw_account_head_master'
    _description = 'Account Head Master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('account_head_name_uniq', 'unique(name)', 'Name already exists.'),
    ]


class KwDataCenterMaster(models.Model):
    """
    Model class for Data Center Master in Kwantify.
    """
    _name = 'kw_data_center_master'
    _description = 'Data center Master'

    name = fields.Char(string='Center Name', required=True)

    _sql_constraints = [
        ('data_center_name_uniq', 'unique(name)', 'Name already exists.'),
    ]
    
