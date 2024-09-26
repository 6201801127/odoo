# -*- coding: utf-8 -*-
{
    'name': "Kwantify Assessment Feedback",
    'version': '0.1',
    'summary': """Roll out monthly assessment feedback and get the best of your workforce""",
    'description': """Roll out monthly assessment feedback and get the best of your workforce""",
    'category': 'Kwantify/Human Resources',
    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'survey', 'kwantify', 'kw_meeting_schedule'],

    # always loaded
    'data': [
        'security/kw_assessment_feedback_security.xml',
        'security/ir.model.access.csv',
        # data files
        'data/request_code.xml',
        'data/kw_assessment_mode_master_data.xml',
        'data/kw_feedback_assessment_master_data.xml',
        'data/kw_feedback_weightage_master_data.xml',
        'data/kw_feedback_survey_data.xml',
        'data/kw_feedback_cron.xml',
        'data/performance_mail.xml',
        'views/templates.xml',

        'views/kw_feedback_assessment_period.xml',
        'views/hr_employee.xml',
        'views/kw_feedback_map_resources.xml',
        'views/kw_feedback_weightage_master.xml',
        'views/kw_feedback_goal_and_milestone.xml',
        'views/kw_feedback_milestone.xml',

        'views/kw_feedback_add_feedback.xml',
        'views/kw_feedback_view_feedback.xml',
        'wizard/kw_feedback_publish_wizard.xml',
        'wizard/kw_feedback_approval.xml',
        'wizard/kw_update_period_date.xml',
        'wizard/send_mail.xml',
        'views/kw_feedback_publish_feedback.xml',
        'views/kw_assessment_feedback_assets.xml',
        'views/kw_feedback_assessment.xml',
        'views/kw_feedback_period_schedule.xml',
        'views/kw_assessment_mode_master.xml',
        'views/survey.xml',
        'views/performance_improvement_apply.xml',
        'views/performance_approve_wizard.xml',
        'views/performance_close_wizard.xml',
        'views/performance_submit_wizard.xml',
        'views/performance_update_wizard.xml',
        'views/assessment_pip_report.xml',

        ## Report
        'report/assessment_progress_report.xml',
        'report/assessor_wise_report.xml',
        'report/assessee_wise_report.xml',
        'report/goal_milestone.xml',
        'report/probationary_assessment_report.xml',
        'report/assessment_pip_emp_report.xml',

        ## Menu
        'views/kw_feedback_menus.xml',

        
        # Templates
        'views/templates/kw_feedback_form.xml',
        'views/templates/kw_feedback_templates.xml',
        'views/templates/kw_feedback_view_form.xml',
        'views/templates/kw_assessor_feedback.xml',
        'views/templates/kw_weightage_master_view.xml',
        'views/templates/kw_feedback_goal_template.xml',
        'views/templates/kw_probation_completion_pdf.xml',


        # Wizards
        'wizard/kw_feedback_period_schedule.xml',
        'wizard/kw_update_publish_date.xml',

        # Email Templates
        'views/email/kw_schedule_periodic_feedback.xml',
        'views/email/kw_schedule_probationary_feedback.xml',
        'views/email/kw_publish_feedback.xml',
        'views/email/kw_assessment_periodic_reminder_mail.xml',
        'views/email/kw_assessment_probationary_reminder_mail.xml',
        'views/email/kw_assessment_goal.xml',
        'views/email/kw_assessment_update_progress.xml',
        'views/email/kw_goal_milestone.xml',
        'views/email/kw_probation_period_extension.xml',
        'views/email/kw_probation_completion_letter.xml',
        'views/email/kw_assessment_Final_Internship_extension_F2F_mail.xml',
        'views/email/kw_assessment_practical_test_extension_mail.xml',
        'views/email/kw_assessment_final _internship_completion_mail.xml',
        'views/res_config_settings.xml',
        'views/update_probation_completion.xml',
        
    ],
}
