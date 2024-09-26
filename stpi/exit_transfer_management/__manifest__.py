# -*- coding: utf-8 -*-
{
    'name': "Exit / Transfer Management",
    'summary': """ Manage employee exit transfer data""",
    'description': "Group Category 'Exit or Transfer'",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Hrms',
    'version': '12.0.1',
    'depends': ['base',"mail",'hr','leaves_stpi','reimbursement_stpi','ohrms_loan','pf_withdrawl','tds'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/exit_transfer_views.xml',
        'views/print_template.xml',
        'views/exit_transfer_mail_template.xml',
        'views/compute_status.xml',
        'views/reminder_scheduler.xml',
        'views/reminder_mail_template.xml',
        'data/config_param.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}