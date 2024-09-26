# -*- coding: utf-8 -*-
{
    'name': 'GTS Project Rename',
    'version': '14.0.0.1',
    'category': 'Sale, Purchase, Account',
    'description': """
    This Module will rename the Analytic Account and Analytic tags to project name and project tags form sale, 
    purchase, Account
    """,
    'depends': ['account', 'analytic', 'sale', 'purchase'],
    'data': [
        'views/analytic_account.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
