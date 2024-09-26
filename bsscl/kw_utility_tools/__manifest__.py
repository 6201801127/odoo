# -*- coding: utf-8 -*-
{
    'name': "BSAP Utility Tools",

    'summary': """
        BSAP utility resources""",

    'description': """
        BSAP Whatsapp models, validations,Execute query etc
    """,

    'author': "CSM Technologies",
    'website': "http://www.csm.co.in",

    # for the full list
    'category': 'BSAP/Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/utility_tools_security.xml',
        'security/ir.model.access.csv',
        'views/kw_whatsapp_message_log.xml',
        'views/kw_whatsapp_template_views.xml',
        'views/ms_query_view.xml',
        'data/data_cron.xml',
        'views/kw_utility_menus.xml'

    ],
    # only loaded in demonstration mode
    'demo': [

    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
