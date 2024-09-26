# -*- coding: utf-8 -*-
from odoo import http

# class KwTimesheetIntegration(http.Controller):
#     @http.route('/kw_timesheet_integration/kw_timesheet_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_timesheet_integration/kw_timesheet_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_timesheet_integration.listing', {
#             'root': '/kw_timesheet_integration/kw_timesheet_integration',
#             'objects': http.request.env['kw_timesheet_integration.kw_timesheet_integration'].search([]),
#         })

#     @http.route('/kw_timesheet_integration/kw_timesheet_integration/objects/<model("kw_timesheet_integration.kw_timesheet_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_timesheet_integration.object', {
#             'object': obj
#         })