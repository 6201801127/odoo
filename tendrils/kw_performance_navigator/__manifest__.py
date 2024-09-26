# -*- coding: utf-8 -*-
{
    'name': "Performance Navigator",

    'summary': """
        Performace Navigator""",

    'description': """
        Performance Navigator.
    """,

    'author': "CSM Tech",
    'website': "https://csm.tech",
 
    'category': 'Tendrils/Integration',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_appraisal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kw_performance_navigator_security.xml',
        'data/goal_milestone_reminder_scheduler.xml',
        'views/kw_performance_navigator_goal.xml',
        'views/kw_performance_navigator_kra.xml',
        'views/kw_cxo_configuration.xml',
        'views/goal_milestone_reminder_mail.xml',
        'views/kw_performance_navigator_competencies.xml',
        'views/kw_probation_completion_details.xml',
        'views/kw_performance_navigator_training.xml',
        'views/menu.xml',
    ],
   

    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
