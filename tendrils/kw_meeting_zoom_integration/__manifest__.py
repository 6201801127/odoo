{
    'name': "Kwantify Meeting Zoom Integration",

    'summary': """
        Schedule your meetings with zoom""",
    'description': """
        Scheduling of daily day to day meetings with Zoom 
    """,
    'author': "Kwantify/Integration",
    'website': "https://www.csm.tech",
    'category': 'Kwantify',
    'version': '1.0',
    # 'external_dependencies': {
    #     'python': [
    #         'pyjwt',
    #     ],
    # },
    'depends': ['base', 'web', 'hr', 'kw_meeting_schedule'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_get_zoom_user_deatails.xml',
        'data/mail_meeting_invitation_data.xml',
        'data/mail_meeting_invitation_external.xml',
        'data/mail_meeting_invitation_admin_it_team.xml',
        'data/zoom_meeting_parameter.xml',
        'wizard/zoom_account_tag_view.xml',
        'wizard/mom_mail_wizard.xml',
        'views/kw_meeting_zoom_attendace_action.xml',
        'views/templates.xml',
        # 'views/res_company.xml',
        'views/meeting_event.xml',
        'views/res_config_setting_views.xml',
        'views/res_user.xml',
        'views/zoom_event_log.xml',
        'views/kw_zoom_meeting.xml',
        'views/zoom_users_views.xml',
        'views/zoom_meetings_report.xml',
        'views/kw_meeting_zoom_integration_menus.xml',

    ],
    'demo': [
    ],
    'qweb': [
     "static/src/xml/base.xml",
     "static/src/xml/zoom_attendance_template.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# -*- coding: utf-8 -*-
