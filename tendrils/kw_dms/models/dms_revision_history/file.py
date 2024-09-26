# -*- coding: utf-8 -*-
from odoo import models, api, fields, tools

class File(models.Model):
    
    _inherit = 'kw_dms.file' 

    revision_ids = fields.One2many(
        string='Revision Ids',
        comodel_name='kw_dms.file_revision_history',
        inverse_name='file_id',
        
    )

    revision_enabled       = fields.Boolean(string="Activate Versioning",related='storage.activate_revision')


    @api.multi
    def write(self,vals):
        
        revision_history  = self.env['kw_dms.file_revision_history']
        for obj in self:
            # print('------------')
            # print(obj.name)
            # print(vals.get('name'))

            old_content = obj.content
            old_name    = obj.name

            if 'content'in vals and self.revision_enabled:
                revision_history.create({

                    'file_id'       :int(obj.id),
                    'name'          :old_name, #self.name
                    'directory'     :obj.directory.id,
                    'storage'       :obj.storage.id,
                    'path_names'    :obj.path_names,
                    'content'       :old_content, #self.content
                    'extension'     :obj.extension,
                    'size'          :obj.size, 
                    'checksum'      :obj.checksum,
                    'version'       :obj.version,
                    'mimetype'      :obj.mimetype,
                })
                # print(old_name)
               
                # print('------------')
                     

        return super(File,self).write(vals)

