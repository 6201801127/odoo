# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import json
from odoo.addons.portal.controllers.mail import PortalChatter
import base64
from odoo.addons.sh_rfq_portal.controllers.portal import PurchaseRFQPortal
from odoo.tools.translate import _
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from datetime import date, datetime


class TenderChatterController(PortalChatter):

    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        res = super(TenderChatterController, self).portal_chatter_post(
            res_model, res_id, message, **kw)
        if kw.get('doc_file'):
            file_read = kw.get('doc_file')
            result = base64.b64encode(file_read.read())
            attachment_list = []
            message_id = request.env['mail.message'].sudo().search(
                [('res_id', '=', res_id)], limit=1)
            attachment_list.append(request.env['ir.attachment'].sudo().create({
                'name': file_read.filename,
                'datas': result,
                'type': 'binary',
                'mimetype': file_read.mimetype,
                'datas_fname': file_read.filename,
                'store_fname': file_read.filename,
                'res_model': res_model,
                'res_id': res_id,
            }).id)
            message_id.sudo().write(
                {'attachment_ids': [(6, 0, attachment_list)]})
        return res


class TenderPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):

        values = super(TenderPortal, self)._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        tenders = tender_obj.sudo().search([('state', 'not in', ['draft', 'confirm', 'cancel']), ('is_published', '=', True),
                                            '|', (
            'partner_ids', 'in', [request.env.user.partner_id.id]), ('partner_ids', '=', False)])
        tender_count = tender_obj.sudo().search_count([('state', 'not in', ['draft', 'confirm', 'cancel']),
                                                       ('is_published', '=', True), '|', (
            'partner_ids', 'in', [request.env.user.partner_id.id]), ('partner_ids', '=', False)])
        values['tender_count'] = tender_count
        values['tenders'] = tenders
        return values

    @http.route(['/my/tender', '/my/tender/page/<int:page>'], type='http', auth="public", website=True)
    def portal_my_home_tender(self, page=1):
        values = self._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        domain = [
            ('state', 'not in', ['draft', 'confirm', 'cancel']), ('is_published', '=', True),
            '|',
            ('partner_ids', 'in', [request.env.user.partner_id.id]),
            ('partner_ids', '=', False)
        ]

        tender_count = tender_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/tender",
            total=tender_count,
            page=page,
        )

        tenders = tender_obj.sudo().search(
            domain, limit=self._items_per_page, offset=pager['offset'])

        attachment_ids = []
        for tender in tenders:
            for lines in tender.tender_documents_ids:
                attachment_ids.append(lines.sh_attachment_id.id)

        attachments = request.env['ir.attachment'].sudo().search([('id', 'in', attachment_ids)])

        values.update({
            'tenders': tenders,
            'attachments': attachments,
            'page_name': 'tender',
            'pager': pager,
            'default_url': '/my/tender',
            'tender_count': tender_count,
            'current_date': datetime.now()
        })
        return request.render("sh_po_tender_portal.portal_my_tenders", values)

    @http.route(['/my/tender/<int:tender_id>'], type='http', auth="public", website=True)
    def portal_my_tender_form(self, tender_id, report_type=None, access_token=None, message=False, download=False, **kw):
        tender_sudo = request.env['purchase.agreement'].sudo().search(
            [('id', '=', tender_id)], limit=1)
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=tender_sudo, report_type=report_type, report_ref='sh_po_tender_management.action_report_purchase_tender', download=download)
        values = {
            'token': access_token,
            'tender': tender_sudo,
            'message': message,
            'bootstrap_formatting': True,
            'partner_id': tender_sudo.partner_id.id,
            'report_type': 'html',
            'current_date': datetime.now()
        }
        return request.render('sh_po_tender_portal.portal_tender_form_template', values)

    @http.route(['/rfq/create'], type='http', auth='public', website=True, csrf=False)
    def portal_create_rfq(self, **kw):
        dic = {}
        purchase_tender = request.env['purchase.agreement'].sudo().search(
            [('id', '=', int(kw.get('tender_id')))], limit=1)

        purchase_order = request.env['purchase.order'].sudo().search(
            [('agreement_id', '=', purchase_tender.id), ('partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['draft'])])
        if purchase_order and len(purchase_order.ids) > 1:
            dic.update({
                'url': '/my/rfq'
            })
        elif purchase_order and len(purchase_order.ids) == 1:
            dic.update({
                'url': '/my/rfq/'+str(purchase_order.id)
            })
        else:
            order_dic = {}
            analytic_account = False
            if purchase_tender.project_id:
                analytic_account = purchase_tender.project_id.analytic_account_id.id
            order_dic.update({
                'partner_id': request.env.user.partner_id.id,
                'agreement_id': purchase_tender.id,
                'date_order': fields.Datetime.now(),
                'user_id': purchase_tender.sh_purchase_user_id.id,
                'state': 'draft',
                'analytic_account_id': analytic_account
            })
            if purchase_tender.sh_agreement_deadline:
                order_dic.update({
                    'date_planned': purchase_tender.sh_agreement_deadline,
                })
            else:
                order_dic.update({
                    'date_planned': fields.Datetime.now(),
                })
            purchase_order_id = request.env['purchase.order'].sudo().create(
                order_dic)
            line_ids = []
            for line in purchase_tender.sh_purchase_agreement_line_ids:
                line_vals = {
                    'order_id': purchase_order_id.id,
                    'product_id': line.sh_product_id.id,
                    'agreement_id': purchase_tender.id,
                    'status': 'draft',
                    'name': line.sh_product_id.name,
                    'product_qty': line.sh_qty,
                    'product_uom': line.sh_product_id.uom_id.id,
                    'price_unit': 0.0,
                    'account_analytic_id': analytic_account
                }
                if purchase_tender.sh_agreement_deadline:
                    line_vals.update({
                        'date_planned': purchase_tender.sh_agreement_deadline,
                    })
                else:
                    line_vals.update({
                        'date_planned': fields.Datetime.now(),
                    })
                line_ids.append((0, 0, line_vals))
            purchase_order_id.order_line = line_ids
            dic.update({
                'url': '/my/rfq/'+str(purchase_order_id.id)
            })
        return json.dumps(dic)

    @http.route(['/rfq/marks/<int:tender_id>'], type='http', auth="public", website=True)
    def portal_rfq_marks_form(self, tender_id, report_type=None, access_token=None, message=False, download=False,
                              **kw):
        rfq_sudo = request.env['purchase.order'].sudo().search([('agreement_id', '=', tender_id)])
        purchase_tender = request.env['purchase.agreement'].sudo().search([('id', '=', tender_id)],
                                                                          limit=1)
        values = {
            'rfqs': rfq_sudo,
            'tender': purchase_tender
        }
        return request.render("sh_po_tender_portal.open_rfq_marks", values)


class TenderRFQPOrtal(PurchaseRFQPortal):

    @http.route(['/rfq/update'], type='http', auth="public", methods=['POST', ], website=True, csrf=False)
    def custom_rfq_update(self, access_token=None, **kw):
        if kw.get('order_id'):
            purchase_order = request.env['purchase.order'].sudo().search(
                [('id', '=', kw.get('order_id'))], limit=1)
            if purchase_order and purchase_order.agreement_id.state != 'closed':
                if kw.get('technical_document'):
                    technical_attachment = base64.encodestring(kw['technical_document'].read())
                    purchase_order.write({
                        'sh_technical_attachment': technical_attachment,
                        'sh_technical_attachment_name': kw.get('technical_document').filename})

                if kw.get('financial_document'):
                    financial_attachment = base64.encodestring(kw['financial_document'].read())
                    purchase_order.write({
                            'sh_financial_attachment': financial_attachment,
                            'sh_financial_attachment_name': kw.get('financial_document').filename})

                if purchase_order.order_line:
                    for k, v in kw.items():
                        if k not in ['order_id', 'technical_document', 'financial_document']:
                            purchase_order_line = request.env['purchase.order.line'].sudo().search(
                                [('order_id', '=', purchase_order.id), ('id', '=', k)], limit=1)
                            if purchase_order_line:
                                price = v
                                if ',' in price:
                                    price = price.replace(",", ".")
                                if float(price) == 0.0:
                                    raise UserError(_('Unit Price should be greater than zero!'))
                                purchase_order_line.sudo().write({
                                    'price_unit':float(price),
                                    })

        url = '/my/rfq/update/'+str(kw.get('order_id'))
        return request.redirect(url)
