from datetime import date
import base64
import io
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import math, random, string
from ast import literal_eval

import odoo.addons.calendar.controllers.main as main
from odoo.api import Environment
import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.exceptions import ValidationError, AccessDenied
from ast import literal_eval



class DownloadDocument(http.Controller):

    @http.route(['/download/document/<string:attachment_id>/<string:document_id>'], type='http', auth='public',
                methods=["GET"], csrf=False, cors='*', website=True)
    def download_attachment(self, attachment_id, document_id):
        # download document if endpoint hit with required parameters
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])
        document = request.env['health_insurance_policy_master'].sudo().search([('id', '=', int(document_id))])
        if attachment["datas"]:
            data = io.BytesIO(base64.b64decode(attachment["datas"]))
            return http.send_file(data, filename=document['file_name'] if document['file_name'] else 'Document',
                                  as_attachment=True)
        else:
            return request.not_found()
