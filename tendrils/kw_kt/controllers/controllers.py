# -*- coding: utf-8 -*-
from odoo import http

# class KwKt/(http.Controller):
#     @http.route('/kw_kt//kw_kt//', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_kt//kw_kt//objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_kt/.listing', {
#             'root': '/kw_kt//kw_kt/',
#             'objects': http.request.env['kw_kt/.kw_kt/'].search([]),
#         })

#     @http.route('/kw_kt//kw_kt//objects/<model("kw_kt/.kw_kt/"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_kt/.object', {
#             'object': obj
#         })