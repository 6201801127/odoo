# -*- coding: utf-8 -*-
{
    'name': "Kwantify Integrations",

    'summary': """
        Integration with Kwantify to sync resources""",

    'description': """
        Integration with Kwantify to sync resources
    """,

    'author': "CSM Technologies",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Extra Tools/Sync Scheduler',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee', 'mail', 'kw_usability'],  # , 'kw_synchronization'

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kw_integration_log_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_config_home_ation_view.xml',
        'data/data_cron.xml',

        'views/kw_sync_email_template.xml',

        'views/kw_integration_menus.xml',
        'views/kw_employee_sync_wizard.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
