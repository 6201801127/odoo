# -*- coding: utf-8 -*-
{
    'name': "Kwantify Survey",

    'summary': """
        Employee Fill the Kwantify Survey Form""",

    'description': """
        Kwantify Survey Template
    """,

    'author': "CSM technology pvt.ltd.",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['survey', 'kw_employee', 'kwantify', 'kw_appraisal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/kwantify_survey.xml',
        # 'data/kw_survey_mode_master_data.xml',
        'data/kw_survey_email_template.xml',
        'data/kw_survey_type_data.xml',
        'views/kw_surveys.xml',
        'views/survey.xml',
        'report/kw_survey_report.xml',
        'views/res_config_settings_view.xml',
        # 'views/kw_survey_config.xml',
        # 'views/kw_survey_mode_master.xml',
        'views/kw_survey_details_view.xml',
        'views/kw_survey_edit_view.xml',
        'views/kw_start_survey_view.xml',
        'views/qweb/survey_form.xml',
        'views/qweb/survey_form_view.xml',
        'views/kw_surveys_menu.xml',

        'wizard/kwantify_survey_publish_wizard.xml',
        'report/kw_survey_result_report.xml',
        'views/kw_surveys_result_view.xml',
        'wizard/kwantify_survey_send_mail.xml',
        'views/kw_survey_question_inherit_view.xml',
        # 'views/survey_inherit.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
