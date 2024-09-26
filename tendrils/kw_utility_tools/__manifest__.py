# -*- coding: utf-8 -*-
{
    'name': "Kwantify Utility Tools",

    'summary': """
        Kwantify utility resources""",

    'description': """
        Whatsapp models, validations,Execute query etc
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','kw_usability'],

    # always loaded
    'data': [
        'security/utility_tools_security.xml',
        'security/ir.model.access.csv',
        'views/kw_whatsapp_message_log.xml',
        'views/kw_whatsapp_template_views.xml',
        # 'views/ms_query_view.xml',
        'data/data_cron.xml',
        'views/kw_utility_menus.xml',
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}