# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.
{
    'name': 'Ticket Management',
    'version': '1.1.0',
    'category': 'Services/Support',
    'sequence': 110,
    'summary': 'Track, prioritize, and solve customer tickets',
    'website': 'https://www.geotechnosoft.com/',
    'depends': ['base', 'base_setup', 'contacts', 'mail', 'utm', 'rating', 'web_tour', 'resource', 'portal', 'digest',
                'website', 'project', 'gts_project_cost_analysis'],
    'description': """Ticket Management""",
    'data': [

        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_data.xml',
        'data/email_templates.xml',
        'data/activity_data.xml',
        'views/support_ticket_views.xml',
        'views/support_team_views.xml',
        'views/assets.xml',
        'views/portal_templates.xml',
        'data/website_data.xml',
        'views/support_templates.xml',
        'views/res_partner_views.xml',
        'views/mail_activity_views.xml',
        'views/project_view.xml',
        'report/sla_report_analysis_views.xml',
    ],
    'qweb': [
        "static/src/xml/support_team_templates.xml",
    ],
    'application': True,
}

