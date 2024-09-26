# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Ticket',
    'category': 'Website',
    'summary': 'Website Form',
    'depends': [
        'gts_ticket_management',
        'website_form',
    ],
    'description': """Enables the functionality of online submission of tickets.
    """,
    'data': [
        'data/website_support.xml',
        'views/support_team_views.xml',
        'views/support_ticket_templates.xml'
    ],
    'post_init_hook': 'post_install_hook_ensure_team_forms',
}
