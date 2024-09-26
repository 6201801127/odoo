# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class WebsiteSupport(http.Controller):

    def get_support_team_data(self, team, search=None):
        return {'team': team}

    def _get_partner_data(self):
        partner = request.env.user.partner_id
        partner_values = {}
        if partner != request.website.user_id.sudo().partner_id:
            partner_values['name'] = partner.name
            partner_values['email'] = partner.email
        return partner_values

    @http.route(['/support/', '/support/<model("support.team"):team>'], type='http',
                auth="public", website=True, sitemap=True)
    def website_support_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        teams = request.env['support.team'].search([('use_website_support_form', '=', True)], order="id asc")
        if not request.env.user.has_group('gts_ticket_management.group_support_ticket_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("gts_ticket_management.not_published_any_team")
        result = self.get_support_team_data(team or teams[0], search=search)
        result['teams'] = teams
        result['default_partner_values'] = self._get_partner_data()
        return request.render("gts_ticket_management.team", result)
