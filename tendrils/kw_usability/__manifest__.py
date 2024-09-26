# -*- coding: utf-8 -*-

{
    'name': "Kwantify Usability",
    'summary': """User usability""",
    'description': "Log to store user login and usability of kwantify.",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify / Tools',
    'version': '1.0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/kw_user_login_view.xml',
        'views/kw_usability_tree_view_asset.xml',
        'views/kw_discuss_usability_view.xml',
        'views/kw_usability_menus.xml',
        'report/kw_discuss_usability_report.xml',
        ],
    'qweb': [
        'static/src/xml/usability_tree_view_buttons.xml'
    ],
    'application':True,
    'installable': True,
    'auto_install': False,
}
