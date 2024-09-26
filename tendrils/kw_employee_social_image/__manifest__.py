# -*- coding: utf-8 -*-
{
    'name': "Kwantify Employee Candid Image",
    'summary': "Candid Image of employee",
    'description': "Employee details module",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/system_params_data.xml',
        'data/kw_employee_social_notify_data.xml',
        'data/email/notification_mail_template.xml',

        'views/kw_employee_social_image.xml',
        'views/kw_employee_social_sync.xml',
        'views/kw_sync_log.xml',
        'views/kw_image.xml',
        # 'views/menu.xml',
        
        'views/kw_employee_social_notify.xml',
        'views/image_upload_web_page.xml',
        'views/employee_certification.xml',
        'views/employee_certification_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': [
       
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
