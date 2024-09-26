# -*- coding: utf-8 -*-

from odoo import models, api, fields


class Directory_download(models.Model):

    _inherit = 'kw_dms.directory'


    ##for file downloading count
    # directory_download_log_ids = fields.One2many(
    #     string=u'Download Logs',
    #     comodel_name='kw_dms.directory_download_log',
    #     inverse_name='directory_id',
    # )

    # download_count = fields.Integer(string="Download Count", 
    #     default=0,
    #     compute='_get_download_count'
        
    # ) 


    def action_show_download_log(self):

        return {
            'name'      : 'Directory Download Logs',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_dms.directory_download_log',
            'view_type' : 'form',
            'target'    : 'new',
            'view_mode' : 'tree,form',
            'domain'    : [("directory_id", "=",self.id)],
            'flags'     : {'action_buttons': False,"toolbar":False},
           
        }     


    def _get_download_count(self):
        for record in self:
            record.download_count = len(record.directory_download_log_ids)  


    @api.multi
    def action_download_directory(self):

        return {
            'type'  : 'ir.actions.act_url',
            'url'   :  '/download/kw_dms_directory/%s'%(self.id),
            'target': 'self',
        }


      