# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main
import requests, os, zipfile, base64, shutil, json
from mimetypes import guess_extension
from odoo.tools.mimetypes import guess_mimetype
from zipfile import ZipFile
from io import BytesIO
from odoo.addons.web.controllers.main import content_disposition
from odoo.addons.restful.common import valid_response,invalid_response

class EmployeeDocDownload(http.Controller):
    """ 
        1)  Update Employee's Workexperience,Education details,Identification details document 
            if they are imported in kw_emp_update_workexperience,kw_emp_update_educational_details,
            kw_emp_update_identification_details 
    """
    @http.route('/update_experience_document', type='http', auth="public")
    def get_exp_doc(self):
        work_exp_ids = request.env['kw_emp_update_workexperience'].search([('status','=',False)],limit=10)
        if work_exp_ids:
            for val in work_exp_ids:
                val.call_update_doc(val)
            return valid_response("Success",)
        else:
            return invalid_response(
                    "Message", "Failed", 401
                )

    @http.route('/update_education_document', type='http', auth="public")
    def get_edu_doc(self):
        educational_ids = request.env['kw_emp_update_educational_details'].sudo().search([('status','=',False)],limit=10)
        if educational_ids:
            for val in educational_ids:
                request.env['kw_emp_update_workexperience'].call_update_doc(val)
            return valid_response("Success",)
        else:
            return invalid_response(
                    "Message", "Failed", 401
                )

    @http.route('/update_identification_document', type='http', auth="public")
    def get_identification_doc(self):
        identification_ids = request.env['kw_emp_update_identification_details'].sudo().search([('status','=',False)],limit=10)
        if identification_ids:
            for val in identification_ids:
                request.env['kw_emp_update_workexperience'].call_update_doc(val)
            return valid_response("Success",)
        else:
            return invalid_response("Message", "Failed", 401)