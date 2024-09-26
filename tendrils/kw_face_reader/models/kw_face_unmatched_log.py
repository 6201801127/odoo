# -*- coding: utf-8 -*-
import requests, base64 ,json
from io import BytesIO

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class kw_face_unmatched_log(models.Model):
    _name       = 'kw_face_unmatched_log'  
    _description = 'Facereader Unmatched Log'  
    _rec_name   = 'image_name'
    
       
    image_name  = fields.Char(
        string='Image Name',
    )  

    image_binary = fields.Binary(
        string='Image', compute='_compute_face_model_image',default=False,store=False,attachment=False,
        prefetch=False,
        readonly=True 
        
    )   

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
   

    @api.depends('image_name')
    def _compute_face_model_image(self):

        params                      = self.env['ir.config_parameter'].sudo()
        unmatched_image_url         = params.get_param('kw_face_reader.unmatched_image_path',False)

        #url = 'http://192.168.103.139:3000/static/employee_image'
        for rec in self:
            if rec.image_name:
                image_url       = unmatched_image_url+'/'+rec.image_name
                try:
                    get_response = requests.get(image_url)
                    if get_response.status_code == 200:    

                        buffered            = BytesIO(requests.get(image_url).content)
                        rec.image_binary    =  base64.b64encode(buffered.getvalue())   

                except Exception as e:
                    
                    rec.image_binary    = False


    
    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
    
        result = super(kw_face_unmatched_log, self).write(values)

        if 'employee_id' in values:

            params                      = self.env['ir.config_parameter'].sudo()
            kw_face_reader_api_url      = params.get_param('kw_face_reader.api_url',False)

            url          = str(kw_face_reader_api_url)+'/_photo_tag'

            json_data   = {
                "photo_name":self.image_name,
                "employee_id":str(self.employee_id.id),
                "employee_name":self.employee_id.name
            }
        
            header                  = {'Content-type': 'application/json',} 
            data                    = json.dumps(json_data)

            #########################################################################################

            resp                = ''
            try:
               
                response_result     = requests.post(url, data = data,headers=header,timeout=30)  
               
                resp                = json.loads(response_result.text)
               
            except Exception as e:

                raise ValidationError('Some error occured while accessing Face Reader APP. '+str(e))
         
            if resp:
                if resp['status'] == 200:
                    self.env['kw_face_training_data'].sudo().create({'employee_id':self.employee_id.id,'image_name':self.image_name})
                else:
                    raise ValidationError('Some error occured while connecting to Face Reader APP . '+resp['message'])

    
        return result
    
              

      
           

   