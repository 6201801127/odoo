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

    'depends': ['base', 'kw_employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kw_report_security.xml',
        # 'views/asset.xml',
        'data/project_monitoring_sequences.xml',
        'data/data.xml',
        'views/kw_new_projects.xml',
        'views/kw_life_cycle_master.xml',
        'views/kw_project_type_master.xml',
        'views/kw_project_manage_use_case_views.xml',
        'views/kw_project_effort_estimation.xml',
        'views/kw_project_milestone.xml',
        'views/manage_resource.xml',
        'views/project_rido_view.xml',
        'views/project_environment_info.xml',
        'wizard/project_milestone_wizard_view.xml',
        'views/menu.xml',

    ],

    'application': True,
    'installable': True,
    'auto_install': False,

}
