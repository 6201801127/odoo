# -*- coding: utf-8 -*-
{
    'name': "Kwantify Onboarding Integration",
    'summary': "Integration of Onboarding with Attendance and Workstation",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_onboarding', 'kw_hr_attendance', 'kw_workstation', 'kw_resource_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kwonboard_integration.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
