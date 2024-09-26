# -*- coding: utf-8 -*-
"""
Module: KW Learning and Knowledge HTTP Controllers

HTTP controllers for managing learning and knowledge-related functionality.
"""
from odoo import http

# class KwLearningAndKnowledge(http.Controller):
#     @http.route('/internship_program/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internship_program/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internship_program.listing', {
#             'root': '/internship_program',
#             'objects': http.request.env['internship_program.model'].search([]),
#         })

#     @http.route('/internship_program/objects/<model("internship_program.model"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internship_program.object', {
#             'object': obj
#         })