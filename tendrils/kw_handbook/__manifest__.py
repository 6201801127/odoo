# -*- coding: utf-8 -*-
{
    'name': "Kwantify Employee Handbook",
    'summary': "Employee Handbook",
    'description': "Employee Handbook",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly   , 'kw_employee', 'hr'
    'depends': ['base', 'kw_web_notify'],

    # always loaded
    'data': [
        'data/sync_officer_group_access.xml',
        'security/kw_handbook_security_manager.xml',
        'security/ir.model.access.csv',

        # 'data/kw_handbook_types.xml',
        'data/handbook_parameter.xml',
        'data/handbook_mail_send_cron.xml',
        'views/kw_handbook_views.xml',
        'views/kw_attachment_view.xml',
        'views/kw_onboarding_handbook.xml',
        'views/kw_onboarding_handbook_category.xml',
        'views/kw_onboarding_handbook_form.xml',
        'views/kw_onboarding_handbook_category_form.xml',

        'views/kw_handbook_menu_items.xml',

        'views/kw_handbook_type.xml',
        'views/kw_emp_policy_template.xml',
        'views/kw_handbook_log.xml',
        'views/kw_handbook_templates.xml',
        'views/kw_policy_document_log.xml',
        'views/kw_onboarding_handbook_mail_template.xml',
        'views/kw_handbook_parsing_log_views.xml',

        'views/assets.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'data/handbook_data.xml',
        # 'data/handbook_file.xml',
    ],
    'qweb': ["static/src/xml/sync_officer_group_access.xml"],
    

    'installable': True,
    'application': True,
    'auto_install': False,
}
