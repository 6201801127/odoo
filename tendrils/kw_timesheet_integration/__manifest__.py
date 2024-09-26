# -*- coding: utf-8 -*-
{
    'name': "kw_timesheet_integration",

    'summary': """
      """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','payroll_inherit','kw_timesheets'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
        'views/kw_timesheet_payroll_inherit_view.xml',
        'views/kw_timesheet_payroll_integration.xml',
        # 'views/kw_payroll_el_deduction.xml',
        'wizard/views/kw_share_timesheet_wizard.xml',
        # 'views/kw_timesheet_inherit_search_view.xml',
        'views/sbu_plan_report.xml',
      
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}