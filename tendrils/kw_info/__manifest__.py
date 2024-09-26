# -*- coding: utf-8 -*-
{
    'name': "kwantify info",

    'summary': "Kwantify Informations And Release Notes.",

    'description': "Kwantify Info Module",

    'author': "CSM Tech",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing

    'category': 'Kwantify/Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/kw_info_security.xml',
        # 'security/ir.model.access.csv',
        'views/kw_info_views.xml',
        'views/kw_info_templates.xml',
    ],
    'qweb': ['static/src/xml/kw_info_aboutus.xml'],
    'application': True,
    'installable': True,
    'auto_install': False,

}
