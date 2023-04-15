# -*- coding: utf-8 -*-
# from odoo import http


# class IssueTracker(http.Controller):
#     @http.route('/issue_tracker/issue_tracker/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/issue_tracker/issue_tracker/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('issue_tracker.listing', {
#             'root': '/issue_tracker/issue_tracker',
#             'objects': http.request.env['issue_tracker.issue_tracker'].search([]),
#         })

#     @http.route('/issue_tracker/issue_tracker/objects/<model("issue_tracker.issue_tracker"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('issue_tracker.object', {
#             'object': obj
#         })
