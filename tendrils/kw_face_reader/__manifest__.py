# -*- coding: utf-8 -*-
{
    'name': "Kwantify Face Reader",

    'summary': """
        Employee face reader """,

    'description': """
        Employee face reader
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/kw_face_matched_log_views.xml',        
        'views/kw_face_training_data_views.xml',
        'views/kw_face_unmatched_log_views.xml',
        'views/res_config_settings_views.xml',
        'views/kw_face_reader_menus.xml',

        'views/kw_manage_iot_device.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}