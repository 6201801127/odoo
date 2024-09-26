# -*- coding: utf-8 -*-
from odoo import http

# class KwSales(http.Controller):
#     @http.route('/kw_sales/kw_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_sales/kw_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_sales.listing', {
#             'root': '/kw_sales/kw_sales',
#             'objects': http.request.env['kw_sales.kw_sales'].search([]),
#         })

#     @http.route('/kw_sales/kw_sales/objects/<model("kw_sales.kw_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_sales.object', {
#             'object': obj
#         })