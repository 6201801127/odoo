# -*- coding: utf-8 -*-
import logging

from odoo import _,models, api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class Category(models.Model):
    
    _name           = 'kw_dms.category'
    _description    = "Document Category"
    
    _inherit        = [
        'kw_dms_utils.mixins.hierarchy',
    ]
    
    _order          = "name asc"
    
    _parent_store   = True
    _parent_name    = "parent_category"
    
    _parent_path_sudo = False
    _parent_path_store = True
    
    _name_path_context = "dms_category_show_path"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name', 
        required=True, 
        translate=True)
    
    active = fields.Boolean(
        default=True, 
        help="The active field allows you to hide the category without removing it.")
    
    parent_category = fields.Many2one(
        comodel_name='kw_dms.category', 
        context="{'dms_category_show_path': True}",
        string='Parent Category',
        ondelete='cascade',
        index=True)
    
    child_categories = fields.One2many(
        comodel_name='kw_dms.category', 
        inverse_name='parent_category',
        string='Child Categories')
    
    parent_path = fields.Char(
        string="Parent Path", 
        index=True)
    
    tags = fields.One2many(
        comodel_name='kw_dms.tag', 
        inverse_name='category',
        string='Tags')
    
    directories = fields.One2many(
        comodel_name='kw_dms.directory', 
        inverse_name='category',
        string='Directories',
        readonly=True)
    
    files = fields.One2many(
        comodel_name='kw_dms.file', 
        inverse_name='category',
        string='Files',
        readonly=True)
    
    count_categories = fields.Integer(
        compute='_compute_count_categories',
        string="Count Subcategories")
    
    count_tags = fields.Integer(
        compute='_compute_count_tags',
        string="Count Tags")
    
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
        ('name_uniq', 'unique (name)', "Category name already exists!"),
    ]
       
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('child_categories')
    def _compute_count_categories(self):
        for record in self:
            record.count_categories = len(record.child_categories)
    
    @api.depends('tags')
    def _compute_count_tags(self):
        for record in self:
            record.count_tags = len(record.tags)
    
    @api.depends('directories')
    def _compute_count_directories(self):
        for record in self:
            record.count_directories = len(record.directories)
    
    @api.depends('files')
    def _compute_count_files(self):
        for record in self:
            record.count_files = len(record.files)
    
    #----------------------------------------------------------
    # Create
    #----------------------------------------------------------
    
    @api.constrains('parent_category')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive categories.'))
        return True
    