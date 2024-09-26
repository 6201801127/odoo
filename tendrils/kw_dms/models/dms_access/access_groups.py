# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccessGroups(models.Model):
    
    _inherit = 'kw_dms_security.access_groups'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    directories = fields.Many2many(
        comodel_name='kw_dms.directory',        
        relation='kw_dms_directory_groups_rel',
        string="Directories",
        column1='gid',
        column2='aid',
        readonly=True)
    
    count_directories = fields.Integer(
        compute='_compute_count_directories',
        string="Count Directories")

    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------

    @api.depends('directories')
    def _compute_count_directories(self):
        for record in self:
            record.count_directories = len(record.directories)