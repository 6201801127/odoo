# -*- coding: utf-8 -*-
{
    'name': "Issue Tracker",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'sequence': 1,
    'description': """
        Long description of module's purpose
    """,
    'author': "Ajay Kumar Ravidas",
    'website': "https://www.ask.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/manage_issue.xml',
        'views/resolve_issue.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'price': 9.99,
    'currency': 'USD',
    'images': ['static/description/issue_tracker.png'],
}
