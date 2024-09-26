# -*- coding: utf-8 -*-
{
    'name': "kw_onboarding_induction_feedback",

    'summary': """Kwantify Onboarding Induction Feedback""",

    'description': """
        Kwantify Onboarding Induction Feedback
    """,

    'author': "CSM Technology",
    'website': "https://www.csm.tech",

    'category': 'Kwantify',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee', 'kw_skill_assessment','kw_onboarding'],

    # always loaded
    'data': [
        'security/kw_onboard_induction_security.xml',
        'security/ir.model.access.csv',

        'data/onboarding_induction_survey_type.xml',

        'views/confirm_wizard_view.xml',
        'views/kw_onboarding_induction_feedback_config.xml',
        'views/mail_notify_to_employee_templates.xml',
        'views/induction_assessment_type.xml',
        'views/views.xml',
        'views/kw_onboard_feedback_emp_report.xml',
        'views/kw_question_bank_master_induction.xml',
        # 'views/kw_induction_assessment_score.xml',
        'views/kw_emp_induction_assessment.xml',
        'views/kw_emp_data_views.xml',

        'wizards/induction_reschedule_wizard.xml',
        'views/kw_induction_plan.xml',
        'views/kw_employee_posh_induction_details.xml',
        'views/kw_psychometric_views.xml',
        'report/posh_paper_format.xml',
        'report/posh_certificate.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}