# -*- coding: utf-8 -*-
import requests, base64 ,json
from io import BytesIO

from cryptography.fernet import Fernet

from datetime import datetime, timedelta


from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError

FERNET_KEY      = b'E2AyACw-KvR9MafdTChpXiQB3taHVWZexJeEZrOvqyM='

class kw_face_training_data(models.Model):
    _name       = 'kw_face_training_data'
    _description = 'Facereader Training Data'  
    _rec_name   = 'image_name'
    
    image_name  = fields.Char(
        string='Image Name',
    ) 
       
    image_binary = fields.Binary(
        string='Image', compute='_compute_face_model_image', default=False,store=False,attachment=False,
        prefetch=False,
        readonly=True 
        
    )  

    employee_code  = fields.Char(
        string='Employee Code',inverse="_inverse_emp_code"
    )   
   
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )


    @api.multi
    def _inverse_emp_code(self):
        for record in self:
            if not record.employee_id and record.employee_code:
                emp_rec             = self.env['hr.employee'].search([('emp_code','=',record.employee_code)],limit=1)
                record.employee_id  = emp_rec.id

    @api.depends('image_name')
    def _compute_face_model_image(self):
       
        params                      = self.env['ir.config_parameter'].sudo()
        employee_image_url          = params.get_param('kw_face_reader.employee_image_path',False)

        for rec in self:
            if rec.image_name:
                image_url               = employee_image_url+'/'+str(rec.employee_code)+'/'+rec.image_name
                try:
                    #print(requests.get(image_url).content)
                    
                    get_response = requests.get(image_url)
                    #print(get_response)
                    if get_response.status_code == 200:                   
                        buffered            = BytesIO(get_response.content)
                        rec.image_binary    =  base64.b64encode(buffered.getvalue())

                    
                except Exception as e:
                    rec.image_binary    = False
           

    def goto_external_training_url(self):

        params                      = self.env['ir.config_parameter'].sudo()
        employee_image_url          = params.get_param('kw_face_reader.training_url',False)

        ##validity 12 hours : 43200
        expires                     = datetime.now() + timedelta(
            seconds=43200
        )

        #vals = [{"user_id": self.env.user.login,"expires": expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}]

        #print(vals) 
        raw             = f"username#{self.env.user.login}|timestamp#{expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}"
        #print(raw) 

      
        encrypt_token = self._encrypt_decrypt('encrypt',raw)        
        employee_image_url +='?token='+encrypt_token

        return {
            'name'  : 'Start Training',
            'type'  : 'ir.actions.act_url',
            'url'   : employee_image_url,
            'target': 'new'
        }

    
    ####Sync training data , from external traing app
    def sync_training_data(self):

        params                      = self.env['ir.config_parameter'].sudo()
        kw_face_reader_api_url      = params.get_param('kw_face_reader.api_url',False)

        url                         = str(kw_face_reader_api_url)+'/_get_employee_facedata'
        json_data                   = {}
    
        header                      = {'Content-type': 'application/json',} 
        data                        = json.dumps(json_data)
        #########################################################################################

        resp                = ''
        try:
            
            response_result     = requests.post(url, data = data,headers=header,timeout=30)           
            resp                = json.loads(response_result.text)
            #print(resp)
        except Exception as e:
            #print(e)

            raise ValidationError('Some error occured while accessing Face Reader APP. '+str(e))

        if resp:

            emp_training_data           = []

            for jsn_record in resp:

                #training_data           = {'image_name':jsn_record['imagename'],'employee_id':int(jsn_record['employee_id'])} 
                training_data           = {'image_name':jsn_record['imagename'],'employee_code':jsn_record['employee_code']} 
                if training_data not in emp_training_data:
                    emp_training_data.append(training_data)

            #print(emp_training_data)

            if len(emp_training_data)>0:
                self.env['kw_face_training_data'].sudo().create(emp_training_data)


            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    def goto_face_reader_url(self):
        params                      = self.env['ir.config_parameter'].sudo()
        kw_face_reader_url          = params.get_param('kw_face_reader.reader_url',False)

        ##validity 12 hours : 43200
        expires                     = datetime.now() + timedelta(
            seconds=43200
        )
        raw                         = f"username#{self.env.user.login}|timestamp#{expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}"
        #print(raw) 

        encrypt_token               = self._encrypt_decrypt('encrypt',raw)        
        kw_face_reader_url +='?token='+encrypt_token


        return {
            'name': 'Face Reader',
            'type': 'ir.actions.act_url',
            'url': kw_face_reader_url,
            'target': 'new'
        }


    
    @api.multi
    def unlink(self):
        """
            Delete all record(s) from recordset
            return True on success, False otherwise
    
            @return: True on success, False otherwise
    
            #TODO: process before delete resource
        """
        # print("Inside unlink ---")
        # print(self)

        params                      = self.env['ir.config_parameter'].sudo()
        kw_face_reader_api_url      = params.get_param('kw_face_reader.api_url',False)

        url          = str(kw_face_reader_api_url)+'/_photo_delete'
        json_data    = {
            "photo_name":self.image_name,
            "employee_id":str(self.employee_id.id),
        }
    
        header                  = {'Content-type': 'application/json',} 
        data                    = json.dumps(json_data)
        #########################################################################################

        resp                = ''
        try:
            
            response_result     = requests.post(url, data = data,headers=header,timeout=30)           
            resp                = json.loads(response_result.text)
           
        except Exception as e:
            #print(e)

            raise ValidationError('Some error occured while accessing Face Reader APP. '+str(e))

        if resp:
            if resp['status'] == 200:
                result = super(kw_face_training_data, self).unlink()
            else:
                raise ValidationError('Some error occured while deleting from Face Reader APP . '+resp['message'])

            
        return result
    


    def _encrypt_decrypt(self,type,raw):
      
        f               = Fernet(FERNET_KEY)

        if type =='encrypt':
            encrypt_token   = f.encrypt(raw.encode())
            return encrypt_token.decode()

        elif type =='decrypt':
            decrypted = f.decrypt(raw.encode())

            return decrypted.decode()


   