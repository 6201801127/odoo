# -*- coding: utf-8 -*-
{
    'name': "kwantify Grievance",
    'summary': "kwantify Grievance",
    'description': " kwantify Grievance",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'kwantify/Human Resources',
    'version': '0.1',
    'depends': ['base','hr',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'wizards/employee_so_remark.xml',
        'data/kw_grievance_type.xml',
        'data/kw_applicant.xml',
        # 'reports/report_grievance.xml',
        # 'reports/report_action.xml',
        'views/kw_grievance_type.xml',
        'views/kw_grievance.xml',
        'data/kw_grievance_mail_template.xml',
        # 'views/kw_gievance_category_view.xml',
        # 'views/kw_report_grievance.xml',
        'views/level_config.xml',
        'data/kw_ir_sequence.xml',
        # 'data/email_template.xml',
        'views/kw_grievnance_spoc_msater_view.xml',
        'views/kw_grievance_action_log_view.xml',
        'views/grievance_menu.xml',
        'views/kw_grievance_report.xml',

    ],
    # 'demo': [
        
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
