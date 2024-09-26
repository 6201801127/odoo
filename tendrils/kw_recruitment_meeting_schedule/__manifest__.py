# -*- coding: utf-8 -*-
{
    'name': "Kwantify Recruitment Meeting Schedule",

    'summary': """
        Schedule your meetings""",

    'description': """
        Recruitment Meeting Schedule for scheduling meeting for an interview.
    """,

    'author': "CSM Tech",
    'website': "https://csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Integration',
    'version': '1.0',

    # any module necessary for this one to work correctly   ,'board','web_timeline'
    'depends': ['base', 'kw_meeting_schedule', 'kw_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_corn.xml',
        'data/survey_template.xml',
        'data/kw_recruitment_mail_templates.xml',
        'data/kw_hr_applicant_meeting_template.xml',
        'data/survey_candidate_feedback.xml',
        'data/kw_recruitment_candidate_survey_mail.xml',
        'views/res_config_settings_view.xml',
        'views/kw_meeting_calendar.xml',
        'views/kw_meeting_schedule_attendee_view.xml',
        'views/my_interviews_views.xml',
        'views/kw_meeting_feedback.xml',
        # 'views/kw_recruitment_appicant_feedback_report.xml',
        'views/kw_interview_summary_report.xml',
        'wizards/kw_applicant_feedback_view.xml',
        'wizards/kw_recruitment_summary_report.xml',
        'wizards/recruitment_summary_report.xml',
        # 'views/survey_templates/candidate_feedback_survey.xml',
        'views/survey_result.xml',
        'views/kw_hr_applicant_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
