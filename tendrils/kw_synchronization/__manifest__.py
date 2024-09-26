# -*- coding: utf-8 -*-
{
    'name': "Kwantify Synchronization",
    'summary': "Used to maintain the DB sync log files",
    'description': "It is used to map db entities and store log files.",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'kw_employee', 'mail'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kw_synchronization.xml',
        'views/kw_emp_sync_log.xml',
        'data/ir_cron_data.xml',
        'data/kwsync_system_parameter.xml',
        'data/kw_employee_sync.xml',
        'views/tree_view_asset.xml',
        'views/email/kw_failed_api_mail.xml',
        'views/master_view_inherit.xml',
        'wizard/kw_synchronization_education_data.xml',
        'wizard/kw_synchronization_cv_data.xml',
        'wizard/kw_identification_data_synchronization.xml',
    ],

    'qweb': ['static/src/xml/tree_view_buttons.xml'],

    'application': True,
    'installable': True,
    'auto_install': False,

}
