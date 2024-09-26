# -*- coding: utf-8 -*-
import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class Tag(models.Model):
    
    _name = 'kw_dms.tag'
    _description = "Document Tag"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name', 
        required=True, 
        translate=True)
    
    active = fields.Boolean(
        default=True, 
        help="The active field allows you to hide the tag without removing it.")
    
    category = fields.Many2one(
        comodel_name='kw_dms.category', 
        context="{'dms_category_show_path': True}",
        string='Category',
        ondelete='set null')
    
    color = fields.Integer(
        string='Color Index', 
        default=10)

    directories = fields.Many2many(
        comodel_name='kw_dms.directory',
        relation='kw_dms_directory_tag_rel', 
        column1='tid',
        column2='did',
        string='Directories',
        readonly=True)
    
    files = fields.Many2many(
        comodel_name='kw_dms.file',
        relation='kw_dms_file_tag_rel', 
        column1='tid',
        column2='fid',
        string='Files',
        readonly=True)
    
    count_directories = fields.Integer(
        compute='_compute_count_directories',
        string="Count Directories")
    
    count_files = fields.Integer(
        compute='_compute_count_files',
        string="Count Files")
    
    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------

    _sql_constraints = [
        ('name_uniq', 'unique (name, category)', "Tag name already exists!"),
    ]
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('directories')
    def _compute_count_directories(self):
        for record in self:
            record.count_directories = len(record.directories)
    
    @api.depends('files')
    def _compute_count_files(self):
        for record in self:
            record.count_files = len(record.files)