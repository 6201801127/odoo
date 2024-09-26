

from odoo import models, fields, api

class AccessGroups(models.Model):
    
    _name           = 'kw_dms_security.access_groups'
    _description    = "Record Access Groups"
    _inherit        = 'kw_dms_utils.mixins.groups'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    perm_read = fields.Boolean(
        string='Read Access')
    
    perm_create = fields.Boolean(
        string='Create Access')
    
    perm_write = fields.Boolean(
        string='Write Access')
    
    perm_unlink = fields.Boolean(
        string='Unlink Access')
 