# -*- coding: utf-8 -*-
import requests, base64 ,json

from odoo import models, api
from odoo.exceptions import ValidationError

class kw_manage_iot_device(models.TransientModel):
    _name        = 'kw_manage_iot_device'
    _description = 'Facereader Manage IOT Devices'  


    # @api.multi
    # def action_sync_training_data(self):

    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }

    # @api.multi
    # def action_sync_attendance_data(self):

    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }


    ####Sync training data , from external traing app
    @api.multi
    def action_sync_odoo_training_data(self):

        params                      = self.env['ir.config_parameter'].sudo()
        kw_face_reader_api_url      = params.get_param('kw_face_reader.api_url',False)

        url                         = str(kw_face_reader_api_url)+'/_get_employee_facedata_odoo'
        json_data                   = {}
    
        header                      = {'Content-type': 'application/json',} 
        data                        = json.dumps(json_data)
        #########################################################################################

        resp                        = ''
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
                if 'employee_code' in jsn_record:
                    training_data           = {'image_name':jsn_record['imagename'],'employee_code':jsn_record['employee_code']} 
                if training_data not in emp_training_data:
                    emp_training_data.append(training_data)

            #print(emp_training_data)

            if len(emp_training_data)>0:
                self.env['kw_face_training_data'].sudo().create(emp_training_data)


        return True   
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    ####Sync training data , from external traing app
    @api.multi
    def action_sync_odoo_attendance_data(self):

        params                      = self.env['ir.config_parameter'].sudo()
        kw_face_reader_api_url      = params.get_param('kw_face_reader.api_url',False)

        url                         = str(kw_face_reader_api_url)+'/_get_employee_logdata_odoo'
        json_data                   = {}
    
        header                      = {'Content-type': 'application/json',} 
        data                        = json.dumps(json_data)
        #########################################################################################

        resp                        = ''
        try:
            
            response_result     = requests.post(url, data = data,headers=header,timeout=30)           
            resp                = json.loads(response_result.text)
            #print(resp)
        except Exception as e:
            #print(e)

            raise ValidationError('Some error occured while accessing Face Reader APP. '+str(e))

        if resp:

            #print(resp)

            emp_attendance_data     = []

            for jsn_record in resp:

                attendance_data           = {'match_date_time':jsn_record['match_date_time'],'employee_code':jsn_record['employee_code']} 

                if attendance_data not in emp_attendance_data:
                    emp_attendance_data.append(attendance_data)

            # print(attendance_data)

            if len(attendance_data)>0:
                self.env['kw_face_matched_log'].create(attendance_data)

            
        return True

   