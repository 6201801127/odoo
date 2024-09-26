# -*- coding: utf-8 -*-
{
    'name': "Kwantify Meeting Schedule",

    'summary': """
        Schedule your meetings""",

    'description': """
        Scheduling of daily day to day meetings 
    """,

    'author': "Kwantify",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Employee',
    'version': '1.0',

    # any module necessary for this one to work correctly   ,'board','web_timeline'
    'depends': ['base', 'calendar', 'mail', 'hr', 'kw_utility_tools', 'crm', 'contacts', 'kw_sendsms'],

    # always loaded
    'data': [
        'security/kwmeeting_schedule_security.xml',
        'security/ir.model.access.csv',

        'data/data_meeting_type_master.xml',
        'data/data_meeting_room_master.xml',
        'data/mail_meeting_invitation_data.xml',
        'data/mail_meeting_invitation_external.xml',
        'data/mail_meeting_invitation_admin_it_team.xml',
        'data/remainder_data.xml',
        'data/meeting_cron_data.xml',
        'data/seq_meeting_data.xml',
        'data/data_kw_whatsapp_template.xml',

        'views/assests.xml',
        'views/partner.xml',
        'views/calendar_event_type.xml',
        'views/kw_meeting_amenity_master.xml',
        'views/kw_meeting_room_master.xml',
        # 'views/kw_meeting_zoom_attendee_form.xml',
        # 'views/kw_meeting_project_master.xml',
        # 'views/kw_meeting_time_master.xml',

        'views/kw_meeting_agenda_proposals.xml',
        'views/kw_meeting_all_participants.xml',
        'views/kw_meeting_agenda_activities.xml',
        'views/kw_meeting_calendar.xml',
        # 'views/kw_meeting_schedule.xml',
        'views/kw_meeting_agenda.xml',
        'views/calendar_attendee_view.xml',
        'views/calendar_mom_report.xml',
        # 'views/calendar_view.xml',

        'views/kw_my_meetings_view.xml',
        # 'views/kw_meeting_participant_events_view.xml',
        # 'views/dashboard.xml',

        'views/calendar_event_report.xml',
        'report/kw_meeting_tagwise_hour_expense_report_view.xml',
        'report/kw_meeting_statistics_report_view.xml',
        'report/kw_meeting_monthwise_attendee_report.xml',
        'report/kw_meeting_employee_attendance_report.xml',
        'views/kw_meeting_groups.xml',

        'views/kw_meeting_menu.xml',
        'views/kw_meeting_external_participants.xml',
        'views/contacts_view.xml',
        'views/kw_meeting_schedule_templates.xml',
        'views/kw_recruitment_hr_employee_view.xml',
        'views/kw_meeting_schedule_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/kw_meeting_dashboard.xml',
        'static/src/xml/kw_meeting_room_availability.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
