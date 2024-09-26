# -*- coding: utf-8 -*-
{
    'name': "Kwantify Review & Feedback",

    'summary': """
    You can Review and give Feed back of the the modules of the Kwantify""",
    
    'description': """
       Kwantify Review & Feedback
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_dynamic_workflow','mail'],

    # always loaded
    'data': [
        'security/kw_feedback_security.xml',
        'security/ir.model.access.csv',
        
        # 'data/kw_feedback_dynamic_workflow.xml',

        'views/kw_feedback_admin.xml',
        'views/kw_feedback_user_view.xml',
        'views/kw_feedback_reply.xml',
        'views/kw_reply_reply.xml',
        'views/kw_reply_of_reply_wizard.xml',
        'views/temp_kanban_view.xml',
        'views/kw_choose_module_kanban_view.xml',
        'views/kw_admin_module_rating_view.xml',
        'views/kw_module_rating_view.xml',
        'views/kw_choose_module.xml',
        'views/kw_feedback_report.xml',
        'views/email/kw_review_feedback_mail.xml',
        'views/kw_menu.xml',
       
    ],
    # only loaded in demonstration mode
    'application': True,
    'installable': True,
    'auto_install': False,
}