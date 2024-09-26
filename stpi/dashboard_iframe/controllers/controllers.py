# -*- coding: utf-8 -*-
from odoo import http

# class DashboardExternalIframe(http.Controller):
#     @http.route('/dashboard_external_iframe/dashboard_external_iframe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dashboard_external_iframe/dashboard_external_iframe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dashboard_external_iframe.listing', {
#             'root': '/dashboard_external_iframe/dashboard_external_iframe',
#             'objects': http.request.env['dashboard_external_iframe.dashboard_external_iframe'].search([]),
#         })

#     @http.route('/dashboard_external_iframe/dashboard_external_iframe/objects/<model("dashboard_external_iframe.dashboard_external_iframe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dashboard_external_iframe.object', {
#             'object': obj
#         })