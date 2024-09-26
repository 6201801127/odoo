# -*- coding: utf-8 -*-
{
    'name': "KW Email_marketing",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
       Design, send and track emails
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",


    # for the full list
    'category': 'E-mail Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mass_mailing',
        'contacts',
        'mail',
        'utm',
        'link_tracker',
        'web_editor',
        'web_kanban_gauge',
        'social_media',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kw_mass_mailing_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}