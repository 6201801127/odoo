import os
# import sys
# import json
# import base64

# import shutil

# from zipfile import ZipFile
# from io import BytesIO


from odoo import http
from odoo.http import request

# from odoo.addons.web.controllers.main import content_disposition


class DirectoryDownload(http.Controller):

    # @http.route(['/download/form16/<int:id>'], type='http', auth="user", website=True)
    # def download_pdf(self, id=None, **kw):
    #     # scriptPath = sys.path[0]
    #     downloadPath = os.path.join('C:\\Users\\girish.mohanta\\Documents\\')
    #     file = f"{downloadPath}vs_2.pdf"
    #     pdf = open(file, mode="rb")
    #     contents = pdf.read()
    #     pdf.close()
    #     file_size = os.path.getsize(file)
    #     # print("downloadPath >>>>>>>>>>>>>>> ", file, file_size)
    #     # return 0

    #     pdf_http_headers = [('Content-Type', 'application/pdf'),
    #                         ('Content-Disposition',
    #                          f"attachment; filename=vs_2.pdf"),
    #                         ('Content-Length', file_size)]

    #     return request.make_response(contents, headers=pdf_http_headers)
    
    
    
    
    @http.route('/get_task_response',type='json', auth='public',cors='*', method=["POST"], csrf=False)
    def get_task_response(self, **post):
        try:
            task_response_data = request.jsonrequest.get('param',{}).get('data',{})
            print('Response', task_response_data)
            if task_response_data:
                curr_ai_slab = request.env['ai_slab_log'].search([('task_id','=',task_response_data.get('id'))])
                curr_ai_slab.write({
                    'response': str(task_response_data.get('amount',0))
                })
                slab_details = request.env['declaration.slab'].browse(curr_ai_slab.slab_rec_id)
                slab_details.sudo().write({
                    'ai_amt' : task_response_data.get('amount',0)
                })
                
                return {'status':'success','message':'Response recieved successfully'}
            else:
                curr_ai_slab = request.env['ai_slab_log'].search([('task_id','=',task_response_data.get('id'))])
                curr_ai_slab.write({
                    'response': str(task_response_data.get('amount',0))
                })
                return {'status':'error', 'message':'Invalid data format'}
        except Exception as e:
            curr_ai_slab = request.env['ai_slab_log'].search([('task_id','=',task_response_data.get('id'))])
            curr_ai_slab.write({
                    'response': str(e)
                })
            return {'status':'error', 'message':str(e)}