# -*- coding: utf-8 -*-
from odoo import http

# class KwEosIntegrations(http.Controller):
#     @http.route('/kw_eos_integrations/kw_eos_integrations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kw_eos_integrations/kw_eos_integrations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kw_eos_integrations.listing', {
#             'root': '/kw_eos_integrations/kw_eos_integrations',
#             'objects': http.request.env['kw_eos_integrations.kw_eos_integrations'].search([]),
#         })

#     @http.route('/kw_eos_integrations/kw_eos_integrations/objects/<model("kw_eos_integrations.kw_eos_integrations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kw_eos_integrations.object', {
#             'object': obj
#         })