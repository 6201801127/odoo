# -*- coding: utf-8 -*-
{
    'name': "Kwantify Greetings",

    'summary': """
        Greetings Module""",

    'description': """
        Greetings Module for wish.
    """,

    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail'],

    # always loaded
    'data': [
        'security/security_greetings_manager_group.xml',
        'security/ir.model.access.csv',

        'views/kw_greetings_template_category.xml',
        'views/kw_greeting_template_view.xml',
        'views/kw_greeting_send_wishes_view.xml',
        'views/menu.xml',

        'views/kw_greetings_employee_view.xml',
        'views/res_config_settings_views.xml',
        'views/email/kw_greetings_email_template.xml',
        'views/tree_view_asset.xml',

        'data/kwgreetings_category_data.xml',
        'data/kwgreetings_template_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/tree_view_buttons.xml'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
