# -*- coding: utf-8 -*-
{
    'name': "Kwantify Accounting Integration",

    'summary': """
        Kwantify Accounting Integration""",

    'description': """
        Kwantify Accounting Integration
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_accounting', 'kw_tour', 'kw_advance_claim', 'kw_web_notify', 'hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        # 'data/accounting_configuration_data.xml',
        # 'data/tour_workflows.xml',
        'data/advance_claim_workflows.xml',
        'data/accounting_system_parameter.xml',
        'data/invoice_creation_cron.xml',
        # 'views/tour_views.xml',
        'views/advance_claim_views.xml',
        'views/payroll_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
