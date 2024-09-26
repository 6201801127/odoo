# -*- coding: utf-8 -*-
{

    'name': "Knowledge Transfer",
    'summary': """Knowledge Transfer""",
    'description': """ Knowledge Transfer Module
        
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Employee',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'project'],

    # always loaded
    'data': [
        'security/kw_kt_security.xml',
        'security/ir.model.access.csv',

        'data/kt_type_master.xml',
        'data/ir_sequence_data.xml',
        # 'data/kt_reminder_scheduler.xml',

        'views/email/kw_kt_plan_configure_mail_template.xml',
        'views/kw_kt_view.xml',
        'views/kw_kt_project_doc.xml',
        'views/kw_remark_view.xml',
        'views/kw_new_plan_request.xml',
        'views/res_config_setting_views.xml',

        # 'views/kw_project_document.xml',
        'views/kw_kt_type_master.xml',
        'views/kw_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
