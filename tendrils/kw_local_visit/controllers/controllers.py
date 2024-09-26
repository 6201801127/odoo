# -*- coding: utf-8 -*-
from odoo import http

# class KwLocalVisit(http.Controller):
#     @http.route('/kw_local_visit/kw_local_visit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_local_visit/kw_local_visit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_local_visit.listing', {
#             'root': '/kw_local_visit/kw_local_visit',
#             'objects': http.request.env['kw_local_visit.kw_local_visit'].search([]),
#         })

#     @http.route('/kw_local_visit/kw_local_visit/objects/<model("kw_local_visit.kw_local_visit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_local_visit.object', {
#             'object': obj
#         })