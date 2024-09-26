# -*- coding: utf-8 -*-
{
    'name': "Lost & Found",

    'summary': """
        Lost & Found""",

    'description': """
        Lost & Found
    """,

    'depends': ['base','mail'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/lost_found.xml',
        'views/informed.xml',
        'views/hand_over.xml',
        'views/lost_and_found_email_template.xml',
        'reports/report_action.xml',
        'wizard/lost_found_report_wizard.xml',
        'views/spoc_master.xml',
        
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
}