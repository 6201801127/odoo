# -*- coding: utf-8 -*-
from odoo import http

# class birthday(http.Controller):

#     def birthday(self, **kw):
#         return http.request.render('kw_office_coordinates.listing', {
#             'root': '/kw_office_coordinates/kw_office_coordinates',
#             'objects': http.request.env['kw_office_coordinates.kw_office_coordinates'].search([]),
#         })

#     @http.route('/kw_office_coordinates/kw_office_coordinates/objects/<model("kw_office_coordinates.kw_office_coordinates"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_office_coordinates.object', {
#             'object': obj
#         })