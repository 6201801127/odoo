# -*- coding: utf-8 -*-
from odoo import http

# class PerformanceImprovementPlan(http.Controller):
#     @http.route('/performance_improvement_plan/performance_improvement_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/performance_improvement_plan/performance_improvement_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('performance_improvement_plan.listing', {
#             'root': '/performance_improvement_plan/performance_improvement_plan',
#             'objects': http.request.env['performance_improvement_plan.performance_improvement_plan'].search([]),
#         })

#     @http.route('/performance_improvement_plan/performance_improvement_plan/objects/<model("performance_improvement_plan.performance_improvement_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('performance_improvement_plan.object', {
#             'object': obj
#         })