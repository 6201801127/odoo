# -*- coding: utf-8 -*-
{
    'name': "Internship",

    'summary': """
       Tendrils Intership Module Management""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/chro_approval_email.xml',
        'data/dept_head_internship_reject_mail.xml',
        'data/applied_internship_mail.xml',
        'data/dept_head_internship_approve_mail.xml',
        'data/chro_reject_internship_mail.xml',
        'data/chro_auto_grant_mail.xml',
        'views/menu.xml',
        'views/tendrils_internship.xml',
        'wizard/action.xml',
        'views/l&k_training.xml',
        'views/tendrils_internship_schedule.xml',
        'reports/batch_wise_internship_complete.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}