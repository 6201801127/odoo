# -*- coding: utf-8 -*-
from odoo import http

# class Kwantify-odoo/kwEmailMarketing(http.Controller):
#     @http.route('/kwantify-odoo/kw_email_marketing/kwantify-odoo/kw_email_marketing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kwantify-odoo/kw_email_marketing/kwantify-odoo/kw_email_marketing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kwantify-odoo/kw_email_marketing.listing', {
#             'root': '/kwantify-odoo/kw_email_marketing/kwantify-odoo/kw_email_marketing',
#             'objects': http.request.env['kwantify-odoo/kw_email_marketing.kwantify-odoo/kw_email_marketing'].search([]),
#         })

#     @http.route('/kwantify-odoo/kw_email_marketing/kwantify-odoo/kw_email_marketing/objects/<model("kwantify-odoo/kw_email_marketing.kwantify-odoo/kw_email_marketing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kwantify-odoo/kw_email_marketing.object', {
#             'object': obj
#         })