# -*- coding: utf-8 -*-


import json
from datetime import datetime, timedelta

from odoo import http,fields
from odoo.http import request


class KwFaceReader(http.Controller):  
    
    @http.route('/kw_face_reader/get_employee_data', methods=['POST','GET'], csrf=False, type='http',auth='public', cors='*') ##
    def get_employee_data(self, **kw):
        employee_rec = http.request.env['hr.employee'].sudo().search([])
       
        employee_data =[]

        for employee in employee_rec:
            id = str(employee.id)+'/'+str(employee.emp_code)+'/'+str(employee.biometric_id)
            employee_data.append({'id':id,'emp_id':employee.id,'name':employee.name,'designation':employee.job_id.name,'department':employee.department_id.name})        
        
        return json.dumps(employee_data)

        #return Response(employee_data,[('Content-Type', 'application/json'),('Access-Control-Allow-Origin','*' )])



    @http.route('/kw_face_reader/save_face_training_data', methods=['POST'], website=True, csrf=False, type='http',auth='public', cors='*') ##
    def save_face_training_data(self, **kw):

        kw_face_training_data = http.request.env['kw_face_training_data'].sudo()
        
        # print(kw)

        face_training_data = []
        try:
            for emp_data in kw:
                if 'employee_id' in kw:
                    
                    if emp_data.startswith(('image_name')):

                        face_training_data.append({'employee_id':kw['employee_id'],'image_name':kw[emp_data]})
                
            # print(face_training_data)


            training_data = kw_face_training_data.create(face_training_data)
            
            if training_data:        
                return json.dumps([{'status':200,'message':'Data saved successfully'}])
        except Exception as e:
            #print(e)

            return json.dumps([{'status':500,'message':str(e)}])


    @http.route('/kw_face_reader/matchUserFacedata', methods=['POST'], website=True, csrf=False, type='http',auth='public', cors='*') ##
    def matchUserFacedata(self, **kw):

        kw_face_matched_log     = http.request.env['kw_face_matched_log'].sudo()
        kw_face_unmatched_log   = http.request.env['kw_face_unmatched_log'].sudo()
        kw_face_training_data   = http.request.env['kw_face_training_data'].sudo()

        hr_employee             = http.request.env['hr.employee'].sudo()
        # match_date_time  employee_id   image_name  

        # print(kw)

        #image_name , employee_id 

        face_training_data  = []
        face_unmatched_log  = []
        face_matched_log    = []

        #for face_data in kw:
        try:
            if int(kw['recognition_status']) == 1 :
                employee_code = 0
                if 'employee_code' in kw:
                    emp_rec         = hr_employee.search([('emp_code','=',kw['employee_code'])],limit=1)
                    employee_id     = emp_rec.id

                if employee_id and 'match_date_time' in kw:                   
                    face_matched_log.append({'employee_id':employee_id,'match_date_time':kw['match_date_time']})
                if employee_id and 'model_image_name' in kw:
                    face_training_data.append({'employee_id':employee_id,'image_name':kw['model_image_name']})

            elif int(kw['recognition_status']) == 0 :

                if 'model_image_name' in kw:
                    face_unmatched_log.append({'image_name':kw['model_image_name']})

            # print(face_training_data)
            # print(face_matched_log)
            # print(face_unmatched_log)

            if len(face_training_data):
                kw_face_training_data.create(face_training_data)

            if len(face_matched_log):
                kw_face_matched_log.create(face_matched_log)

            if len(face_unmatched_log):
                kw_face_unmatched_log.create(face_unmatched_log)
            
            
            return json.dumps([{'status':200,'message':'Data saved successfully'}])

        except Exception as e:
            #print(e)

            return json.dumps([{'status':500,'message':str(e)}])


    @http.route('/api/kw_face_reader/validate_token', methods=['POST'], csrf=False, type='http',auth='public', cors='*') ##
    def validate_token(self, **kw):

        kw_face_training_data     = http.request.env['kw_face_training_data']

        if 'token' in kw:
            try:
                decrypt_str = kw_face_training_data._encrypt_decrypt('decrypt',kw['token'])
              
                user_data   = decrypt_str.split('|')

                user_name   = user_data[0].split('#')[1]
                time_stamp  = user_data[1].split('#')[1]
                
                if datetime.now() > fields.Datetime.from_string(time_stamp):               
                    return json.dumps([{'status':401,'message':'token seems to have expired or invalid'}]) 
                else:
                
                    user_rec  = http.request.env["api.access_token"].sudo().search([("login", "=", user_name)])   
                    if user_rec:
                        json.dumps([{'status':200,'message':'Valid User'}])   
                    else:
                        json.dumps([{'status':401,'message':'Not a valid user !'}])   
               
            except Exception as e:
                return json.dumps([{'status':500,'error_log':str(e)}])

        else:
            return json.dumps([{'status':401,'message':'No access token was provided in request!'}])       


   