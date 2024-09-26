# -*- coding: utf-8 -*-


from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError
from odoo.addons.kw_dms_utils.tools import file

class DmsIntegration(models.AbstractModel):
    
    _name           = 'kw_dms.mixins.integration'
    _description    = 'DMS File Integration Mixin'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    

    content_file     = fields.Binary(
        compute='_compute_content',
        inverse='_inverse_content',
        string='Content',
        attachment=False,
        readonly=False,
        prefetch=False, 
        store=False)

    file_name       = fields.Char(
        string="Filename", 
        compute='_compute_content',
        store=False)

    dms_file_id     = fields.Many2one(
        string='DMS File ID',
        comodel_name='kw_dms.file',
        ondelete='restrict',
    )


    def _compute_content(self):
        for record in self:        
            #dms_rec                 = self.env['kw_dms.file'].search([('res_model','=',self._name),('res_id','=',record.id)], limit=1) 
         
            if record.dms_file_id:   
                record.content_file     = record.dms_file_id.content or False
                record.file_name        = record.dms_file_id.name or False

    @api.multi
    def _inverse_content(self):       
        for record in self: 

            existing_rec = record.dms_file_id
           
            if existing_rec:
                existing_rec.write({'content':record.content_file})
            
   

    @api.model
    def create(self, vals_list):

        # print(vals_list)
        new_rec = super(DmsIntegration, self).create(vals_list)
       
        if 'content_file' in vals_list:
            new_rec.create_dms_file(vals_list['content_file'],vals_list['file_name'])

        return new_rec

    @api.multi
    def write(self, vals_list):

        # print(vals_list)
        update_rec = super(DmsIntegration, self).write(vals_list)

        if 'content_file' in vals_list:
            self.create_dms_file(vals_list['content_file'],vals_list['file_name'])

        return update_rec



    def get_config_folder(self,model_name):
        
        params = self.env['ir.config_parameter'].sudo()

        switcher={
                'kw_onboarding_handbook':params.get_param('kw_dms.policy_doc_folder', default=False),
                'kw_training_material': params.get_param('kw_dms.training_material_folder', default=False),
             }

        return switcher.get(model_name,False)

    def create_dms_file(self,content_file,file_name):
        
        ##create file record
        model_rec            = self.env['ir.model'].sudo().search([('model','=',self._name)])
     
        if model_rec and content_file and not self.dms_file_id:
            directory_id        =  self.get_config_folder(model_rec.model)
            
            if directory_id:
                name            = self.name_get()[0][1]               
                extension       = file.guess_extension(file_name)

                directory_rec   = self.env['kw_dms.directory'].browse([int(directory_id)])
                
                if directory_rec.root_storage.activate_versioning:
                    file_name   = "%s_%s.%s" % (file.slugify(name),str(1.0),extension) 
                else:
                    file_name   = "%s.%s" % (file.slugify(name),extension)  

                ##
                dms_rec          = self.env['kw_dms.file'].create({'name':file_name,'document_name':name,'version':1.0,'content':content_file,'directory':directory_id,'res_id':self.id,'res_name':name,'res_model':model_rec.model,'res_model_name':model_rec.name})

                self.dms_file_id = dms_rec.id
               

            else:
                raise ValidationError("There is no configuration defined for the selected model at DMS.  ")

        
