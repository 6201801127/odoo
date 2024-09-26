# -*- coding: utf-8 -*-
from odoo import http

# class DynamicDashboardsAndReports(http.Controller):
#     @http.route('/dynamic_dashboards_and_reports/dynamic_dashboards_and_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dynamic_dashboards_and_reports/dynamic_dashboards_and_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dynamic_dashboards_and_reports.listing', {
#             'root': '/dynamic_dashboards_and_reports/dynamic_dashboards_and_reports',
#             'objects': http.request.env['dynamic_dashboards_and_reports.dynamic_dashboards_and_reports'].search([]),
#         })

#     @http.route('/dynamic_dashboards_and_reports/dynamic_dashboards_and_reports/objects/<model("dynamic_dashboards_and_reports.dynamic_dashboards_and_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dynamic_dashboards_and_reports.object', {
#             'object': obj
#         })