# -*- coding: utf-8 -*-
{
    'name': "Employee BGV Integration",

    'summary': """
       
       """,

    'description': """
        This project would be an in-house application that should capable to manage the background verification of 
        all experience candidate. After LIVE the maintenance cost has to be minimum

    """,

    'author': "CSM Technology",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_onboarding'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kw_bgv_log.xml',
        'views/enrollment_bgv.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}