# -*- coding: utf-8 -*-

from odoo import models, api, fields


class File(models.Model):
    
    _inherit = 'kw_dms.file'      
             

    ##for file downloading count
    # file_download_log_ids = fields.One2many(
    #     string=u'Download Logs',
    #     comodel_name='kw_dms.file_download_log',
    #     inverse_name='file_id',
    # )

    # download_count = fields.Integer(string="Download Count", 
    #     default=0,
    #     compute='_get_download_count'
        
    # ) 

    ##action to display the downloaded file 
    def action_show_download_log(self):

        return {
            'name'      : 'File Download Logs',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_dms.file_download_log',
            'view_type' : 'form',
            'target'    : 'new',
            'view_mode' : 'tree,form',
            'domain'    : [("file_id", "=",self.id)],
            'flags'     : {'action_buttons': False,"toolbar":False},
           
        }     

    ##method to compute the download count
    def _get_download_count(self):
        for record in self:
            record.download_count = len(record.file_download_log_ids)               


    ##method action to download a file 
    def action_download_file(self):
        return {
            'type'  : 'ir.actions.act_url',
            'url'   :  '/web/content?id=%s&field=content&model=kw_dms.file&filename_field=name&download=true' % ( self.id ),
            'target': 'self',
        }

   