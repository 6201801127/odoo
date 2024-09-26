# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

from . import controller
from . import models


def post_install_hook_ensure_team_forms(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    teams = env['support.team'].search([('use_website_support_form', '=', True)])
    teams._ensure_submit_form_view()
