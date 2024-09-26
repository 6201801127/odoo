# -*- coding: utf-8 -*-
{
    'name': "EOS KT Integration",
    'summary': """KT Integartion with EOS""",
    'description': """ KT Integartion with Resignation & EOS
        
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Integration',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_kt','kw_eos'],

    # always loaded
    'data': [
        # 'views/menus.xml',
        'views/kw_kt_menu_view.xml',
        'views/kw_kt_remainder_mail.xml',
        'data/kw_kt_remainder_before_rl.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}