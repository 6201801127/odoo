from unicodedata import category
from odoo import models, fields, api

class kw_grievance_category_master(models.Model):
    _name        = 'kw.grievance.category'
    _description = 'A model to manage grievance categories'
    _rec_name    = 'sub_category'
    
    sub_category = fields.Char(string="Sub Category", required=True)
    main_category=fields.Many2one('kw.grievance.type',string="Category")
