import logging

from odoo import _, models, api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'kw_dms.storage'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    thumbnails = fields.Selection(
        selection=[
            ('immediate', "On Creation/Update"),
            ('cron', "On Cron Job")
        ],
        string="Thumbnails",
        default='cron',
        help="""Thumbnails can be created either directly when
            changing the file or once an hour via cron job.""")
