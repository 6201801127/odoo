# -*- coding: utf-8 -*-
from odoo import http

# class KwSynchronization(http.Controller):
#     @http.route('/kw_synchronization/kw_synchronization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_synchronization/kw_synchronization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_synchronization.listing', {
#             'root': '/kw_synchronization/kw_synchronization',
#             'objects': http.request.env['kw_synchronization.kw_synchronization'].search([]),
#         })

#     @http.route('/kw_synchronization/kw_synchronization/objects/<model("kw_synchronization.kw_synchronization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_synchronization.object', {
#             'object': obj
#         })