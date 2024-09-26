
import os
import logging

from odoo import models, api, fields, tools,_
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'kw_dms.storage'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    save_type = fields.Selection(
        selection_add=[('file', "Filestore")])
    
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    @api.multi
    def action_storage_migrate(self):
        if not self.env.user.has_group('kw_dms.group_dms_manager'):
            raise AccessError(_('Only managers can execute this action.'))

        records = self.filtered(lambda rec: rec.save_type == 'file')
        files   = self.env['kw_dms.file'].with_context(active_test=False).sudo()
        for record in records:
            domain = ['&', ('content_file', '=', False), ('storage', '=', record.id)]
            files |= files.search(domain)
        files.action_migrate()
        super(Storage, self - records).action_storage_migrate()