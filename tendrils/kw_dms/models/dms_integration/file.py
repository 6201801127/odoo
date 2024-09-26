# -*- coding: utf-8 -*-
import os
import logging

from odoo import models, api, fields, tools
from odoo.exceptions import ValidationError

from odoo.addons.kw_dms_utils.tools import file

_logger = logging.getLogger(__name__)

class File(models.Model):
    
    _inherit = 'kw_dms.file'      
             
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
  
    res_id              =  fields.Integer(string="Resource ID", )
    res_name            = fields.Char(string=u'Resource Name')
        
    res_model           = fields.Char(string=u'Resource Model ',)
    res_model_name      = fields.Char(string=u'Resource Model Name')

  

    def action_related_rec(self):
         
           
        return {
            'name'      : self.res_name,
            'type'      : 'ir.actions.act_window',
            'res_id'    : self.res_id,   
            'res_model' : self.res_model,            
            'view_type' : 'form',
            'view_mode' : 'form',
            'target'    : 'same',
            'flags'     : {'mode': 'readonly'},
          
        }



