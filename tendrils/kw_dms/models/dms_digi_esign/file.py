# -*- coding: utf-8 -*-

from odoo import models, api, fields


class File(models.Model):
    
    _inherit = 'kw_dms.file'     

   
    e_sign_status = fields.Boolean(
        string='E-sign Status', 
        default=False
        ,track_visibility=True
        
    ) 

    
    digitally_signed = fields.Char(
        string='Digitally Signed',
        default='No',
        compute='_compute_sign_status',
        readonly=True,
        store=False
    )


    @api.depends('e_sign_status')
    def _compute_sign_status(self):
        for record in self:
            record.digitally_signed = 'Yes' if record.e_sign_status else 'No'
             

    ##action to display the downloaded file 
    def action_digi_sign(self):

        return {
            'name'      : 'Digital Sign',
            'type'      : 'ir.actions.client',
            # 'res_model' : 'kw_dms.file',
            'tag'       : 'digisign',
            'target'    : 'new',
            'context'   : {'file_content': self.content,'file_id':self.id },
            'flags'     : {'action_buttons': False,"toolbar":False},
           
        }   


    @api.multi
    def save_signed_file(self,**kwargs):

        if 'content' in kwargs:
            self.write({'content': kwargs['content'],'e_sign_status':True})

        return True 

    @api.multi
    def write(self,vals):              
            
        if 'content' in vals and 'e_sign_status' not in vals:
            vals['e_sign_status'] = False
              
                     

        return super(File,self).write(vals)

  