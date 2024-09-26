# -*- coding: utf-8 -*-

{
    'name': 'Project and Task Risk Management',
    "author": "Edge Technologies",
    'version': '14.0.1.0',
    "images": ["static/description/main_screenshot.png"],
    'live_test_url': 'https://youtu.be/JQ6-TIRy-08',
    'summary': 'App for Project Risk Management for project tasks risk management for tasks prioritization of risks '
               'management app project task risk management application Risk management activities for task Risk '
               'management activities for project',
    'description': """ Project Risk Management """,
    'depends': ['project', 'hr_timesheet', 'gts_change_request'],
    "license": "OPL-1",
    'data': [
        'security/risk_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/sequence_risk_category.xml',
        'data/sequence_risk_type.xml',
        'data/sequence_risk_response.xml',
        'data/activity_data.xml',
        'data/schedular_for_task_reminder.xml',
        'data/email_template.xml',
        'wizard/create_incident_wizard.xml',
        'views/main_menu.xml',
        'views/project_and_task.xml',
        'views/project_risk.xml',
        'views/risk_incident_menu.xml',
        'views/configuration_menu.xml',
    ],

    "auto_install": False,
    "installable": True,
    "price": 28,
    "currency": 'EUR',
    'category': 'Project',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
