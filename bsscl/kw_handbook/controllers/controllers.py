# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import base64
import werkzeug
from werkzeug.utils import redirect
from odoo.api import Environment
from odoo.exceptions import AccessError


class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self,model,field,id,filename,**kw):
        # return 'hello nikunja'
        filecontent = base64.b64decode(filename)
        if not filecontent:
            return request.not_found()
        else:
            # return filename
            # return filecontent
            # return 'file not found'
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
                return request.make_response(filecontent,
                                [('Content-Type', 'application/octet-stream'),
                                ('Content-Disposition', content_disposition(filename))])                        


class Ternary(http.Controller):
    @http.route('/web/binary/download_document/files', type='http', auth="public")
    def download_document_files(self,**kw):
        record = request.env['kw_onboarding_handbook'].sudo().search([],order='id desc', limit=1)  
        pdf_file = record.title
        print(pdf_file)
        return request.render("kw_handbook.pdf_record",
                              {
                                  'pdf_file': record,
                              })


class EmployeePolicy(http.Controller):
    @http.route('/employee-handbook', auth='public', type='http', website=True,csrf=False)
    def handbook_policy_details(self, **kw):
        # emp_handbook_data  = request.env['kw_onboarding_handbook'].sudo().search([])
        return http.request.render('kw_handbook.employee_handbook_policy')

    @http.route('/redirect-employee-handbook', type='http', auth='user', website=True, csrf=False)
    def go_to_employee_handbook(self,**kw):
        try:
            action_id = request.env.ref("kw_handbook.kw_handbook_login_actions_window").id
            view_id = request.env.ref("kw_handbook.kw_office_view_kanban").id
            profile_url = '/web#view_type=kanban&action=%s&model=kw_onboarding_handbook&view_id=%s' %(action_id,view_id)
            request.session['skip_handbook'] = True
            return http.request.redirect(profile_url)
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
