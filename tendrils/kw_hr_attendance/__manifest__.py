# -*- coding: utf-8 -*-
{
    'name'      : "Kwantify Employee Attendance ",

    'summary'   : """
        Track employee attendance""",

    'description': """
        Track employee attendance details
    """,

    'author'    : "CSM Technologies",
    'website'   : "https://www.yourcompany.com",

    'category'  : 'Kwantify/HR+',
    'version'   : '0.1',

    # any module necessary for this one to work correctly
    'depends'   : ['base','hr_attendance','hr_calendar_rest_time','kw_branch_master','kw_utility_tools',
                   'kw_hr_holidays_public','oca_web_widget_x2many_2d_matrix', 'kw_employee'],

    # always loaded
    'data': [
        'security/kw_hr_attendance_security.xml',
        'security/ir.model.access.csv',

        'views/res_config_settings_view.xml',

        # 'data/attendance_mode_data.xml',
        'views/kw_holiday_client_action.xml',
        'views/resource_calendar_views.xml',
        'views/hr_employee_view.xml',
        'views/kw_attendance_asset_back_end.xml',
        'views/kw_roaster_group_config.xml',
        'wizard/views/kw_shift_assignment.xml',
        'wizard/views/kw_attendance_mode.xml',
        'wizard/views/kw_roaster_manage.xml',
        'views/kw_employee_roaster_shift.xml',
        'views/kw_attendance_mode_master.xml',
        'views/kw_flexi_timing_manage.xml',
        'views/qweb/kw_late_entry.xml',
        'views/qweb/kw_hr_attendance_approval_redirect.xml',
        'views/kw_res_branch.xml',
        # 'wizard/kw_fixed_holiday_assignment.xml',
        'views/kw_late_entry_approval_log.xml',
        'wizard/views/kw_late_entry_approval_wizard.xml',
        'views/late_entry_view.xml',
        'views/kw_daily_employee_attendance.xml',
        'views/resource_calendar_leaves.xml',

        # 'views/kw_employee_manual_attendance_request.xml',

        'wizard/views/kw_manual_attendance_hr_wizard.xml',
        
        # 'data/attendance_mode_data.xml',
        # 'wizard/views/kw_holiday_year_view.xml',
        
        'views/kw_lunch_client_action.xml',

        'wizard/views/kw_employee_attendance_approval_wizard.xml',
        'views/kw_employee_apply_attendance.xml',
        'wizard/views/kw_shift_holidays_assignment_wizard.xml',
        'views/kw_attendance_shift_views.xml',
        'wizard/views/kw_shift_weekoff_assign.xml',
        'wizard/views/kw_attendance_copy_shift_fixed_holidays_views.xml',
        'views/resource_calendar_leaves_view.xml',

        # 'report/kw_attendance_log.xml',
        'report/late_entry_reason_wizard.xml',
        'report/kw_employee_shift_assignment.xml',
        'report/kw_attendance_summary_report.xml',
        'report/kw_employee_attendance_summary_report.xml',
        'report/kw_dept_attendnace_summary_report.xml',
        'report/kw_late_attendance_summary_report.xml',
        'report/kw_productive_summary_report.xml',
        'report/kw_effort_estimation_report.xml',
        'report/kw_attendance_shift_log.xml',
        'report/kw_daily_matching_report.xml',
        'report/kw_attendance_request_report.xml',
        'report/kw_attendance_absent_report_view.xml',
        'report/kw_attendance_paycut_report_view.xml',
        'report/kw_attendance_bio_report_views.xml',
        'views/kw_bio_attendance_log.xml',
        'views/kw_bio_attendance_request_response_log.xml',
        'views/kw_device_master.xml',
        'views/kw_attendance_grace_time_log.xml',
        'views/kw_employee_monthly_payroll_info.xml',
        'report/kw_attendance_employee_wise_paycut_report_view.xml',
        # 'report/kw_daily_attendance_tracker_view.xml',
        'report/kw_daily_attendance_tracker_pivot_report_view.xml',
        'views/hr_attendance_view.xml',
        'views/kw_attendance_quotes_view.xml',
        # 'views/kw_hr_comp_off_allocation.xml',
        # 'views/kw_off_day_entry_views.xml',
        'views/kw_hr_attendance_menu.xml',

        'data/attendance_scheduler_data.xml',

        'views/email/kw_late_entry_applied_request.xml',
        'views/email/kw_late_entry_approved.xml',
        'views/email/kw_pending_late_entry_approval.xml',
        'views/email/kw_late_entry_forwarded.xml',
        'views/email/kw_absentee_statement.xml',
        'views/email/kw_apply_attendance_request.xml',
        'views/email/kw_attendance_request_approved_rejected.xml',
        'views/email/kw_roster_assign_template.xml',
        'views/email/kw_pending_attendance_request_approval.xml',
        'views/email/kw_flexi_shift_apply_mail.xml',
        'wizard/views/kw_payroll_process_wizard.xml',
        'wizard/views/kw_attendance_update_wfh_wizard_views.xml',
        'wizard/views/kw_attendance_paycut_take_action_wizard.xml',
        'wizard/views/kw_attendance_employee_wise_paycut_take_action_views.xml',
        'wizard/views/kw_daily_attendance_create_views.xml',

        # 'report/employee_monthly_attendance_report.xml',

    ],
    'qweb': ['static/src/xml/*.xml', ],
    'installable': True,
    'application': False,
}
