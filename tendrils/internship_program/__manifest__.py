# -*- coding: utf-8 -*-
{
    'name': "Kwantify Internship Program",

    'summary': """
    Kwantify Internship Program
        """,

    'description': """
        Kwantify Internship Program
    """,

    'author': "CSM Technology",
    'website': "https://www.csm.tech",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee', 'kw_recruitment'],

    # always loaded
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/mail_notify_group_emp.xml',
        'views/kw_l_k_batch_details.xml',
        'views/l_k_intership_details.xml',
        'views/pyroll_revise_views.xml',
        'views/wizards.xml',
        'views/join_type_scheduler.xml',

        'reports/internship_report.xml',
    ],
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
