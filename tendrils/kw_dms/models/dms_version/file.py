# -*- coding: utf-8 -*-
import os

import logging

from odoo import models, api, fields, tools,SUPERUSER_ID
from odoo.exceptions import ValidationError,AccessError

from odoo.addons.kw_dms.tools.security import NoSecurityUid

from odoo.addons.kw_dms_utils.tools import file

_logger = logging.getLogger(__name__)

class File(models.Model):
    
    _inherit = 'kw_dms.file'      
             
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    @api.model
    def _default_version(self):       
        return self.env.context.get('default_version') or 1.0


    version     = fields.Float(string="Version", 
        default=_default_version,
        required=True,
        digits=(12,1)
    )

    document_name = fields.Char(
        string=u'Document Name', 
        required=True
        
    )
    description = fields.Text(
        string=u'File description',
    )
    
        
    prev_version_id = fields.Many2one(
        string=u'Prev Version',
        comodel_name='kw_dms.file',
        ondelete='restrict',
    )

    next_version_id = fields.Many2one(
        string=u'Next Version',
        comodel_name='kw_dms.file',
        ondelete='restrict',
    )

    latest_version_id = fields.Many2one(
        string=u'Latest Version',
        comodel_name='kw_dms.file',
        ondelete='restrict',
    )
    
    initial_version_id = fields.Many2one(
        string=u'Initial Version',
        comodel_name='kw_dms.file',
        ondelete='restrict',
    )

    file_versions_ids = fields.Many2many(
        string      =u'Complete Versions',
        comodel_name='kw_dms.file',
        relation    ='kw_dms_file_version_rel',
        column1     ='file_id',
        column2     ='version_id',
        compute     ='_compute_versions',
        readonly    =True,
        # store=True,
        # automatic   =True,
    )


    ##related field
    version_enabled       = fields.Boolean(string="Activate Versioning",related='storage.activate_versioning')


    # @api.model
    def action_other_versions(self):
        # print(self)
       

        search_version_id = self.initial_version_id.id or self.id
        return {
            'name'      : 'File Versions',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_dms.file',
            'view_type' : 'form',
            'view_mode' : 'kanban,tree,graph,pivot,form',
            'domain'    : ['&',("is_hidden", "=",  False),'|',("initial_version_id", "=",search_version_id),("id", "=", search_version_id)]
           
        }   


    @api.onchange('document_name','name','version')
    def _compute_file_name(self):
       if self.document_name and self.name and self.version:            
            name, extension = os.path.splitext(self.name)

            self.name       = "%s_%s%s" % (file.slugify(self.document_name),str(round(self.version,1)),extension) 
    
    #----------------------------------------------------------
    # Read 
    #----------------------------------------------------------     

    @api.multi
    def name_get(self):
        result = []
        for record in self:            
            record_name = str(record.document_name)+ ' ' + str(round(record.version,1))
            result.append((record.id, record_name))
        return result

    @api.depends('latest_version_id')
    def _compute_versions(self):

        for record in self:
            if self.env.context.get('default_file_versions_ids') :
                record.file_versions_ids  =  self.env.context.get('default_file_versions_ids')
            else:
                # print('sdsd')
                if record.initial_version_id:
                    record.file_versions_ids  = self.search(['|',('initial_version_id', '=', record.initial_version_id.id),('id', '=', record.initial_version_id.id)]).mapped('id')
                elif record.id:
                   record.file_versions_ids  = self.search(['|',('initial_version_id', '=', record.id),('id', '=', record.id)]).mapped('id')     

   
                

    #----------------------------------------------------------
    # Read, View 
    #---------------------------------------------------------- 

    def action_create_new_version(self):


        view_id                      = self.env.ref('kw_dms.view_dms_file_form').id        
      
        default_version              = round(float(self.version)+float(0.1),1)      
       
        default_document_name        = self.document_name
        default_description          = self.description

        default_directory            = self.directory.id
        default_storage              = self.storage.id
        default_category             = self.category.id
        default_prev_version_id      = self.id
        # default_total_version_count  = self.total_version_count+1
        
        initial_version_id           = self.initial_version_id.id or self.id

        file_versioning_ids          = self.search(['|',('initial_version_id', '=', initial_version_id),('id', '=', initial_version_id)]).mapped('id')        
           
        return {
            'name'      : 'New Version',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_dms.file',
            'view_type' : 'form',
            'view_mode' : 'form',
            'views'     : [(view_id, 'form')],
            'context'   :{'default_document_name':default_document_name,'default_version': default_version,'default_description':default_description,'default_directory':default_directory,'default_storage':default_storage,'default_category':default_category,'default_prev_version_id':default_prev_version_id,'default_latest_version_id':False,'default_initial_version_id':initial_version_id,'default_file_versions_ids':file_versioning_ids},
          
        }

  
    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------
    
    @api.constrains('version')
    def _check_version(self):

        for record in self:

            if record.version <= 0:
                raise ValidationError("The version should be greater than 0")


            if self.env.context.get('default_prev_version_id'):
                prev_version = self.browse(self.env.context.get('default_prev_version_id')).version
            else:
                prev_version = record.prev_version_id.version
            # print(prev_version)
            if prev_version:

                # print(record.version)
                # print(prev_version)
                if record.version <= prev_version:
                    raise ValidationError("The version should be greater than previous version %s"%(prev_version))

            if record.next_version_id:
                if record.version >= record.next_version_id.version:
                    raise ValidationError("The version should be less than next version %s"%(record.next_version_id.version))
                
                


    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    

    @api.model
    def create(self, vals): 

        new_record           = super(File, self).create(vals)
        if new_record:            
            if new_record.initial_version_id:
                self.search(['|',('initial_version_id', '=', new_record.initial_version_id.id),('id', '=', new_record.initial_version_id.id)]).write({'latest_version_id':new_record.id})
            else:
                new_record.latest_version_id = new_record.id
            
            if self.env.context.get('default_prev_version_id'):                
                self.env['kw_dms.file'].browse(self.env.context.get('default_prev_version_id')).write({'next_version_id':new_record.id})

        return new_record



