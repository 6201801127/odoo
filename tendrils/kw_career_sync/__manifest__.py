# -*- coding: utf-8 -*-
{
    'name': "kwantify career sync",

    'summary': """Sync with career site""",

    'description': """
        
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'kwantify/Recruitment',
    'version': '0.1',

    'depends': ['base','kw_recruitment'],

    'data': [
        'security/ir.model.access.csv',
        'data/kw_sync_with_career_data.xml',
        'data/kw_recruitment_career_sync_system_parameter.xml',
        'views/tree_view_asset.xml',
        "views/kw_recruitment_career_sync_log_view.xml",
        'views/kw_sync_with_career_view.xml',
        'data/kw_career_sync_applicant_scheduler.xml',
    ],

    'qweb': ['static/src/xml/tree_view_buttons.xml'],

    'installable': True,
    'application': False,
    'auto_install': False,
}
