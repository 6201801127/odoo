# -*- coding: utf-8 -*-
{
    'name': "Kwantify Employee Handbook",
    'summary': "Employee Handbook",
    'description': "Employee Handbook",
    'author': "CSM Technologies",
    'website': "http://www.csm.tech",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly   , 'kw_employee', 'hr'
    'depends': ['base','hr','kw_web_notify'],

    # always loaded
    'data': [
        'security/kw_handbook_security_manager.xml',
        'security/ir.model.access.csv',
        'data/kw_handbook_types.xml',
        'data/handbook_parameter.xml',
        'data/handbook_mail_send_cron.xml',

        'views/kw_emp_policy_template.xml',
        'views/assets.xml',
        'views/kw_attachment_view.xml',
        'views/kw_handbook_views.xml',
        'views/kw_onboarding_handbook.xml',
        'views/kw_onboarding_handbook_category.xml',
        'views/kw_onboarding_handbook_form.xml',
        'views/kw_onboarding_handbook_category_form.xml',
        'views/kw_handbook_menu_items.xml',
        'views/department_structure.xml',
        'views/business_rules.xml',
        'views/finance_process.xml',
        'views/software_development_process.xml',
        'views/kw_handbook_type.xml',
        'views/kw_handbook_log.xml',
        'views/it_policies_processes.xml',
        'views/admin_processes.xml',
        'views/kw_handbook_templates.xml',
        'views/kw_policy_document_log.xml',
        'views/kw_onboarding_handbook_mail_template.xml',
        'views/kw_handbook_parsing_log_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'data/handbook_data.xml',
        # 'data/handbook_file.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
