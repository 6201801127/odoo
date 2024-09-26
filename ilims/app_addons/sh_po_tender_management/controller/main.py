import base64
from werkzeug.utils import redirect
import io
import werkzeug.urls
from odoo import http
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.http import request
from datetime import date, datetime


class WebsiteOpenTendersPage(http.Controller):

    @http.route(['/tenders'], type='http', auth="public", website=True)
    def all_showcase_detail(self, **post):
        tenders = request.env['purchase.agreement'].sudo().search([('is_published', '=', True),
                                                                   ('state', 'not in', ['draft', 'confirm', 'cancel'])])
        values = {
            'tenders': tenders,
            'current_date': datetime.now()
        }
        return request.render("sh_po_tender_management.open_tenders_list", values)
    
    @http.route(['/attachment/downloads',], type='http', auth='public')
    def download_attachment(self, attachment_id, document_id):

        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])
        document = request.env['tender.document'].sudo().search([('id', '=', int(document_id))])
        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/tenders')

        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.b64decode(attachment["datas"]))
            return http.send_file(data, filename=document['sh_attachment_name'] if document['sh_attachment_name'] else 'Document', as_attachment=True)
        else:
            return request.not_found()
