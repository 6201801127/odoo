# -*- coding: utf-8 -*-
{
    'name': "Kwantify Disable Export Option",

    'summary': """
        Remove the \'Export\' option from the \'More\' menu...""",

    'description': """
        A useful module which allows removal of export option easily using the access rights and permissions from the user Settings
    """,

    'author' : "CSM Tech",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '12.0.1.0.0',
    'category': 'Kwantify Extra Tools',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'security/export_visible_security.xml',
        'views/kw_export_assests.xml',
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
}