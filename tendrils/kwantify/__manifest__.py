# -*- coding: utf-8 -*-
{
    'name': "Kwantify",
    'sequence': 1,
    'summary': "ERP solution out of the box",
    'description': "Kwantify ERP application",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",

    'category': 'Kwantify',
    'version': '0.1',

    'depends': ['base', 'mail', 'auth_signup', 'hr', 'portal', 'website', 'hr_holidays', 'hr_recruitment', 'survey',
                'kw_sendsms', 'kw_debranding', 'kw_employee', 'kw_web_notify',
                'kw_account_fiscal_year', 'kw_fiscal_year_sequence_extensible',
                'kw_branch_master', 'kw_remove_export_option', 'kw_utility_tools', 'restful'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/res_lang_data.xml',

        'views/menu.xml',
        # 'views/res_users.xml',
        'views/templates.xml',
        'views/hr_employee_template.xml',
        'views/portal_data.xml',
        'views/pwa_template.xml',
        'views/website_menu.xml',
        # 'views/empcode_of_users.xml',
        'views/kw_survey_survey_views.xml',
        'data/system_param_data.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
