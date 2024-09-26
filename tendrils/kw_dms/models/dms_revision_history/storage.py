# -*- coding: utf-8 -*-

import logging

from odoo import models, api, fields, tools,_

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'kw_dms.storage'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    activate_revision = fields.Boolean(
        string="Store Revision History", 
        default=False,
        help="Indicates if file revision history is enabled or not, default disabled.")
    
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    