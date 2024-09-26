# -*- coding: utf-8 -*-
{
    'name': "Kwantify Performance Improvement Plan (PIP)",

    'summary': """Kwantify Performance Improvement Plan (PIP)""",

    'description': """
        Kwantify Performance Improvement Plan (PIP)
    """,

    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",

    'category': 'Employee',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','kw_meeting_schedule'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/sequence_data.xml',
        'views/menu.xml',
        'data/remainder_mail_counselling.xml',
        'data/sync_user_pip.xml',
        'views/performance_improvement_plan_apply.xml',
        'views/performance_improvement_plan_take_action.xml',
        'views/pip_reason_config_view.xml',
        'views/mail_to_approver_template.xml',
        'wizard/remarks_approve_view.xml',

        'views/pip_counselling_details.xml',
        'views/my_pip_view.xml',

        'views/pip_hr_screen_view.xml',
        'views/all_pip_report_view.xml',
        'views/kw_recommend_training.xml',
        

    ],
    'qweb': ["static/src/xml/sync_user_access_pip.xml"],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}