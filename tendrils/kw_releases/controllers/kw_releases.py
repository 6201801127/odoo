# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Releases(http.Controller):
    @http.route(['/release-note'], auth="public", website=True)
    def getReleasenotes(self, **kwargs):
        data = dict()
        data['release_notes'] = request.env['kw_release_notes'].search([])
        return request.render("kw_releases.kw_release_note", data)
