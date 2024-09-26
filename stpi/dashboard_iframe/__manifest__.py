# -*- coding: utf-8 -*-
{
    'name': "dashboard_iframes",

    'summary': """
        Extending the Odoo Dashboard with the option of adding external iFrames.
        """,

    'description': """
        This module lets your users add iFrames to their personal dashboards. This can be used  to add content 
        from sources like external reporting servers.
    """,

    'author': "info@greenivy.eu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'support': 'david.scholz@greenivy.eu',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_iframe.xml',
        'security/dashboard_iframe_access_rules.xml'
    ],
    'images': ['static/description/main_screenshot.png'],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
