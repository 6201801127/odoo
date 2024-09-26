# -*- coding: utf-8 -*-
{
    'name': "kw_bug_life_cycle",

    'summary': """
    
        """,

    'description': """
        This project would be an in-house application that should capable to manage the life cycle of a defect
         for all CSM projects. After LIVE the maintenance cost has to be minimum
    """,

    'author': "CSM Technology",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_project'],

    # always loaded
    'data': [
        'security/groups_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_for_developer.xml',
        'data/bug_life_cycle_data.xml',
        'reports/bug_life_report.xml',
        'reports/daily_activity_report.xml',
        'wizards/forword_bug_wizard.xml',
        'wizards/remark_assign_wizards.xml',
        'wizards/developer_assign_wizard.xml',
        'wizards/complete_execution_wizard.xml',
        'views/kw_raise_defect.xml',
        'wizards/bug_life_cycle_read_policy_open_menu.xml',
        'views/kw_bug_life_cycle_configuration.xml',
        'views/severity_master.xml',
        'views/testing_level_config_master.xml',
        'views/sla_configuration.xml',
        'views/kw_module_access_permission.xml',
        'views/kw_test_scenario_view.xml',
        'views/test_scenario_take_action_view.xml',
        'views/kw_view_test_scenario.xml',
        # 'views/test_scenario_approval_view.xml',
        'views/kw_test_case.xml',
        'views/test_case_execution.xml',
        'views/kw_use_case_mapping.xml',
        'views/test_case_review.xml',
        'views/automation_config.xml',
        'views/menus.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}