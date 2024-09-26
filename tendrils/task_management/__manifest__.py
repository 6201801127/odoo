# -*- coding: utf-8 -*-
{
    'name': "Task Management",

    'summary': """Kwantify Task Management""",

    'description': """
        Kwantify Task Management Module Management
    """,

    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','kw_employee','kw_project','kw_timesheets'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/assign_task_email.xml',
        'data/closed_task_email.xml',
        'data/complete_task_email.xml',
        'data/extend_effort_hour_email.xml',
        'data/sync_user_access.xml',
        'data/task_start_reminder_cron.xml',
        'data/reminder_email_template.xml',

        'views/task_management_menu.xml',
        'views/master.xml',
        'views/task_management.xml',
        'wizard/extend_effort_hour.xml',
        'wizard/action.xml',
        'reports/task_management_report.xml',
        'reports/task_productivity_report.xml',

    ],
    'qweb': ["static/src/xml/sync_user_access.xml",
    "static/src/xml/task_management_user_guide.xml"],
             

    'application': True,
    'installable': True,
    'auto_install': False,

}
