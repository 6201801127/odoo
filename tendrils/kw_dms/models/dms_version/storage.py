# -*- coding: utf-8 -*-

import logging
from odoo import models, api, fields, tools, _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class Storage(models.Model):
    _inherit = 'kw_dms.storage'


    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    activate_versioning = fields.Boolean(
        string="Activate Versioning", 
        default=False,
        help="Indicates if file versioning is enabled or not, default disabled.")
    
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    