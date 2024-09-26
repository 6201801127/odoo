
# -*- coding: utf-8 -*-
import os
import json
import base64

import shutil

from zipfile import ZipFile
from io import BytesIO


from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import content_disposition


class DirectoryDownload(http.Controller):
    

    @http.route(['/download/kw_dms_directory/<int:id>'], type='http', auth="user")
    def download_zip(self,id=None,**kw):

        # print(self.get_file_paths('onboarding_docs'))

        source_dir = request.env['kw_dms.directory'].browse([id])
      

        byte         = BytesIO()
        zf           = ZipFile(byte, "w")
        # zipped_files = []
        zip_filename = source_dir.name+'.zip'

        # os.makedirs('subdirectory')

        self.addDirectories(source_dir,source_dir.name,zf)

        shutil.rmtree(source_dir.name)

        zf.close()  

        ##START : create file logs 
        # uid         = request.env.user.id    
        # emp_id      = request.env['hr.employee'].sudo().search([('user_id','=',uid)], limit=1).id or False

        # file_ids        = request.env['kw_dms.file'].search(['&',('directory', 'child_of',id),('next_version_id', '=',False)]).ids
        # file_log_data   = []
        # for file_id in file_ids:
        #     file_log_data.append({'user_id':uid,'employee_id':emp_id,'file_id':file_id})

        # request.env['kw_dms.file_download_log'].create(file_log_data)

        ##END : create file logs 


        ##START : create directory logs 
        # directory_ids        = request.env['kw_dms.directory'].search([('id', 'child_of',id)]).ids        
        # dir_log_data        = []
        # for directory_id in directory_ids:
        #     dir_log_data.append({'user_id':uid,'employee_id':emp_id,'directory_id':directory_id})

        # request.env['kw_dms.directory_download_log'].create(dir_log_data)

        ##END : create directory logs


        return request.make_response(byte.getvalue(),[('Content-Type', 'application/x-zip-compressed'),('Content-Disposition', content_disposition(zip_filename))])


    def addDirectories(self,source_dir,parent_path,zf):
      
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)

        file_paths  = [] 
       
        if source_dir.child_directories:

            for sub_dir in source_dir.child_directories:
                new_parent_path = parent_path+"/"+sub_dir.name
                self.addDirectories(sub_dir,new_parent_path,zf)               

        if source_dir.files:

            for record in source_dir.files:
                if not record.next_version_id:
                    c_data          = base64.b64decode(record.content)                
                    current_file    = record.name
                    
                    open(parent_path+'/'+current_file, 'wb').write(c_data)
                    zf.write(parent_path+'/'+current_file)
                    os.unlink(parent_path+'/'+current_file)

        # print(file_paths)

        return file_paths

