# -*- coding: utf-8 -*-
from odoo import http

# class KwRecruitmentBgvIntegration(http.Controller):
#     @http.route('/kw_recruitment_bgv_integration/kw_recruitment_bgv_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_recruitment_bgv_integration/kw_recruitment_bgv_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_recruitment_bgv_integration.listing', {
#             'root': '/kw_recruitment_bgv_integration/kw_recruitment_bgv_integration',
#             'objects': http.request.env['kw_recruitment_bgv_integration.kw_recruitment_bgv_integration'].search([]),
#         })

#     @http.route('/kw_recruitment_bgv_integration/kw_recruitment_bgv_integration/objects/<model("kw_recruitment_bgv_integration.kw_recruitment_bgv_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_recruitment_bgv_integration.object', {
#             'object': obj
#         })