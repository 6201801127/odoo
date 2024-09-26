# -*- coding: utf-8 -*-
{
    'name': "Kwantify Skill Assessment",

    'summary': """
        Online skill assessment of employees""",

    'description': """
        Kwantify Skill Assessment Module
    """,

    'author': "CSM technology pvt.ltd.",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Employee',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_web_notify', 'hr', 'mail', 'kw_account_fiscal_year','kw_resource_management'],

    # always loaded
    'data': [

        'security/kw_skill_assessment_security.xml',
        'security/ir.model.access.csv',

        'data/calculate_mark.xml',
        # 'data/kw_skill_assessment_dynamic_workflow.xml',
        'report/kw_employee_test_report.xml',
        'report/skill_sheet_report.xml',
        'views/kw_skill_score_master.xml',
        'views/kw_skill_type_master.xml',
        'views/kw_skill_master.xml',
        'views/kw_skill_group_master.xml',
        'views/kw_question_bank.xml',
        'views/kw_question_bank_master.xml',
        'views/kw_available_test.xml',
        'views/kw_skill_result_web.xml',
        'views/kw_question_set_config.xml',
        'views/kw_skill_confirmation.xml',
        'views/kw_skill_assessment_instruction.xml',
        'views/kw_my_skill.xml',
        'views/kw_skill_assessment_test_web.xml',
        'views/kw_question_weightage.xml',
        'views/kw_skill_report_action_url.xml',
        # 'views/kw_demo_answer_master.xml',
        'views/kw_demo_answer_child.xml',
        'views/kw_user_test_report.xml',
        'views/kw_skill_index_report.xml',
        'views/view_test_details.xml',
        'views/kw_skill_experience_view.xml',
        'views/skill_sheet.xml',
        'views/skill_assessment_reminder_mail.xml',
        'views/kw_skill_date_configuration.xml',
        'views/kw_skill_assessment_menu.xml',
        'views/kw_skill_mail_template.xml',
        'views/res_config_settings_views.xml',
        'views/skill_config_mail_template.xml',
        'views/kw_skill_no_of_questions.xml',
        'views/kw_skill_assesment_index.xml',

    ],

    'qweb': [
        "static/src/xml/*.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
