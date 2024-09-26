# -*- coding: utf-8 -*-
{
    'name': "Partner Profiling",

    'summary': "Partner Profiling",

    'description': """
        Partner Profiling Dashboard
    """,

    'author': "CSM Tech",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    
    'category': 'Tendrils',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/partner_report.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'qweb': ["static/src/xml/partner_dashboard.xml"],

}