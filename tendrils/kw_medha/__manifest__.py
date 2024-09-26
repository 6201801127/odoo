# -*- coding: utf-8 -*-
{
    'name': "kw_medha",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_setting_view.xml',
        'data/system_param_data.xml',   
        'views/assets.xml',

    ],
    'qweb': [ 'views/qweb/medha_menu_inherit.xml',],
    'installable': True,
    'application': True,
    'auto_install': False,
}