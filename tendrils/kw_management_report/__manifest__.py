# -*- coding: utf-8 -*-
{
    'name': "kwantify Management Report",
    'summary': "Kwantify Employee Reports For management.",

    'description': "Kwantify Management Report",

    'author': "CSM Tech",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing

    'category': 'Kwantify',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['base', 'kw_employee', 'payroll_inherit','kw_resource_management','kw_employee_info_system'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kw_report_security.xml',
        'views/asset.xml',
        'views/employee_role_category_wise_report.xml',
        'views/kw_emp_head_count_report.xml',
        'views/resource_serving_notice_period_report.xml',
        'views/kw_head_count_dashboard.xml',
        'views/kw_emp_month_wise_report.xml',
        'views/kw_employee_parent_details.xml',
        'views/menu.xml',

    ],

    'application': True,
    'installable': True,
    'auto_install': False,

}
