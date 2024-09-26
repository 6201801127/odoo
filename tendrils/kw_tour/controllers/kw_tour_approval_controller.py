import werkzeug
import odoo.http as http
from odoo.http import request
from werkzeug.exceptions import Forbidden #BadRequest
import requests, os, zipfile, base64, shutil
from mimetypes import guess_extension
from odoo.tools.mimetypes import guess_mimetype
from zipfile import ZipFile
from io import BytesIO
from odoo.addons.web.controllers.main import content_disposition


# from datetime import date,datetime
# from odoo.api import Environment
# from odoo import SUPERUSER_ID, _
# from odoo import registry as registry_get
# import odoo.addons.calendar.controllers.main as main


class TourApproval(http.Controller):

    @http.route('/tour/view', type='http', auth="user", website=True)
    def view(self,id):
        # registry = registry_get(db)
        # with registry.cursor() as cr:
        #     env = Environment(cr, SUPERUSER_ID, {})
        tour = request.env['kw_tour'].browse(int(id))
        if not tour:
            return request.not_found()

        if not tour.can_take_action():
            return Forbidden()

        action = request.env.ref('kw_tour.action_kw_tour_take_action_act_window').id
        return werkzeug.utils.redirect(f'/web?#id={id}&view_type=form&model=kw_tour&action={action}')

    @http.route('/tour/reject', type='http', auth="user", website=True)
    def reject(self,token):
        # registry = registry_get(db)
        # with registry.cursor() as cr:
        #     env = Environment(cr, SUPERUSER_ID, {})
        user = request.env.user
        tour = request.env['kw_tour'].search([('access_token', '=', token), ('state', 'in', ['Applied', 'Approved','Forwarded','Traveldesk Approved'])])
        if not tour:
            return request.not_found()
        else:
            if not tour.can_take_action():
                return Forbidden()

            tour.action_reject_tour(by_email = True,remark=f'Rejected Through Email')
        return http.request.render('kw_tour.kw_tour_approval_redirect', {'tour': tour})

    @http.route('/tour/approve', type='http', auth="user", website=True)
    def approve(self,token):
        # registry = registry_get(db)
        # with registry.cursor() as cr:
        #     env = Environment(cr, SUPERUSER_ID, {})
        user = request.env.user
        tour = request.env['kw_tour'].search([('access_token', '=', token),('state','in',['Applied','Forwarded'])])
        if not tour:
            return request.not_found()
        else:
            if not tour.can_take_action():
                return Forbidden()

            tour.action_approve_tour(by_email=True,remark=f'Approved Through Email')

        return http.request.render('kw_tour.kw_tour_approval_redirect', {'tour': tour} )
    
    
    @http.route('/download_update_doc/<int:id>', type='http', auth="user")
    def get_download_zip(self, id=None, **kwargs):
        empObj = request.env['hr.employee'].sudo().browse(id)
        if not empObj.identification_ids:
            return request.not_found()

        empDir = str(empObj.id)
        byte = BytesIO()
        zf = ZipFile(byte, "w")
        emp_name = empObj.name.replace(" ", "_")
        zip_filename = emp_name + '_' + str(empObj.emp_code) + '.zip'
        mainDirectory = 'EmployeeDocs'
        
        flagdict = {'identification_flag': False}
        if not os.path.exists(mainDirectory):
            os.makedirs(mainDirectory)
            
        identification_path = os.path.join(mainDirectory, empDir, 'identification')
            
        if empObj.identification_ids:
            if not os.path.exists(identification_path):
                os.makedirs(identification_path)
            for rec in empObj.identification_ids:
                if rec.uploaded_doc:
                    flagdict['identification_flag'] = True
                    identification_type = dict(request.env['kwemp_identity_docs']._fields['name'].selection).get(rec.name)
                    if identification_type == "Passport" or identification_type == "Yellow Fever":
                        uploaded_doc_b64_string = base64.b64decode(rec.uploaded_doc)
                        extension = guess_extension(guess_mimetype(uploaded_doc_b64_string))
                        identification_file = f'{mainDirectory}/{identification_type}{extension}'
                        with open(identification_file, 'wb') as fp:
                            fp.write(uploaded_doc_b64_string)
                        zf.write(identification_file)   
                     
        zf.close()
        shutil.rmtree(os.path.join(mainDirectory, empDir))
        if any(flagdict):
            return request.make_response(byte.getvalue(), [('Content-Type', 'employee/x-zip-compressed'),
                                                           ('Content-Disposition', content_disposition(zip_filename))])
        else:
            return request.not_found()             

    
    
    
    
    
    # def get_download_zip(self, id=None, **kwargs):
    #     source_dir = request.env['kwemp_identity_docs'].browse([id])
    #     print("source=======1=====",source_dir)
    #     print("source========2====",source_dir.name)
        
    #     byte         = BytesIO()
    #     zf           = ZipFile(byte, "w")
    #     # zipped_files = []
    #     zip_filename = source_dir.name+'.zip'
    #     print("file=============",zip_filename)

        # os.makedirs('subdirectory')

        # self.addDirectories(source_dir,source_dir.name,zf)

        # shutil.rmtree(source_dir.name)

        # zf.close() 
        # empObj = request.env['kwemp_identity_docs'].sudo().browse(id)
        # empDir = str(empObj.id)
        # byte = BytesIO()
        # zf = ZipFile(byte, "w")
        # emp_name = empObj.name.replace(" ", "_")
        # zip_filename = emp_name + '_' +  str(empObj.id) + '.zip'
        # mainDirectory = 'UpdateDocs'
        
        
        
        # if not os.path.exists(mainDirectory):
        #     os.makedirs(mainDirectory)

       
       
        # passport_path = os.path.join(mainDirectory, empDir, 'passport')
        # yellow_fever_path = os.path.join(mainDirectory, empDir, 'fever')
       

    # @http.route('/tour/traveldesk_approve', type='http', auth="user", website=True)
    # def traveldesk_approve(self, token):
    #     # registry = registry_get(db)
    #     # with registry.cursor() as cr:
    #     #     env = Environment(cr, SUPERUSER_ID, {})
    #     user = request.env.user
    #     tour = request.env['kw_tour'].search(
    #         [('access_token', '=', token), ('state', '=', 'Approved')])
    #     if not tour:
    #         return request.not_found()
    #     else:
    #         if not tour.can_take_action():
    #             return Forbidden()

    #         tour.action_traveldesk_approve_tour(
    #             by_email=True, remark=f'Granted Through Email')

    #     return http.request.render('kw_tour.kw_tour_approval_redirect', {'tour': tour})

    # @http.route('/tour/finance_approve', type='http', auth="user", website=True)
    # def finance_approve(self, token):
    #     # registry = registry_get(db)
    #     # with registry.cursor() as cr:
    #     #     env = Environment(cr, SUPERUSER_ID, {})
    #     user = request.env.user
    #     tour = request.env['kw_tour'].search(
    #         [('access_token', '=', token), ('state', '=', 'Traveldesk Approved')])
    #     if not tour:
    #         return request.not_found()
    #     else:
    #         if not tour.can_take_action():
    #             return Forbidden()

    #         tour.action_finace_approve_tour(
    #             by_email=True, remark=f'Granted Through Email')

    #     return http.request.render('kw_tour.kw_tour_approval_redirect', {'tour': tour})
    
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
