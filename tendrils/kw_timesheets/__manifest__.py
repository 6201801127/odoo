{
    'name': "Kwantify Timesheet",
    'summary': """
        Manage Employee Timesheet
        """,
    'description': """
    
This module implements a timesheet system.
==========================================

Each employee can encode and track their time spent on the different projects.

Lots of reporting on time and employee tracking are provided.

It is completely integrated with the cost accounting module. It allows you to set
up a management by affair.
    """,

    'author': "CSM",
    'website': "https://csm.tech",


    # for the full list
    'category': 'Human Resources',
    'sequence': 4,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'analytic', 'project', 'uom', 'hr_timesheet', 'web_grid', 'timesheet_grid','kw_resource_management'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_cron.xml',
        'data/reminder_email_template.xml',
        'data/auto_validate_email_template.xml',
        'data/project_system_parameters.xml',
        'data/task_not_assigned_email_template.xml',

        'views/timesheet_menu.xml',
        'views/kw_project_category_master_view.xml',
        'views/kw_activity_master_view.xml',
        'views/kw_inherit_project_view.xml',
        'views/kw_timesheet_client_action.xml',
        'views/kw_timesheet_report_view.xml',
        'views/kw_timesheet_grid_view.xml',
        'views/kw_account_analytic_line_view.xml',
        'views/project_timesheet.xml',

        'report/kw_timesheet_attendance_report_view.xml',
        'report/kw_timesheet_report_view.xml',
        'report/kw_timesheet_calendar_report.xml',
        'report/kw_daily_timesheets_report_view.xml',
        'report/kw_weekly_timesheet_report.xml',
        'report/kw_timesheet_payroll_report_view.xml',
        'report/project_wise_resource_count.xml',
        'report/kw_project_task_assign_report_view.xml',
        'report/kw_project_task_not_assigned_view.xml',

        'views/res_config_setting_views.xml',
        'views/kw_validate_timesheet.xml',
        'views/qweb/kw_timesheet_summary_report_view_login.xml',
        'views/hr_employee_timesheet.xml',
        'views/kw_timesheet_employee.xml',
        'views/kw_project_sub_task_master.xml',
        'views/timesheets_to_validate.xml',

        'report/kw_timesheet_leave_deduct_view.xml',
        'report/kw_timesheet_summary_report_view.xml',
        'wizard/kw_timesheet_el_deduction.xml',
        'wizard/kw_share_timesheet_el_deduct_wizard.xml',
        'wizard/kw_project_tagging_filter_wizard.xml',
        'wizard/kw_timesheet_project_report.xml',
        'wizard/kw_project_task_not_assign_send_mail_wizrad_view.xml',
        'views/allow_backdate.xml',
        'data/timesheet_el_deduction_email_template.xml',
        'wizard/kw_tagged_dept_actvity_type_wizard_view.xml',
        # 'report/kw_timesheet_project_tag_report_view.xml',
        'wizard/kw_timesheets_validate_wizard_view.xml',
        'wizard/kw_project_task_assigned_wizard_view.xml',
        'report/kw_sbu_tagging_report_view.xml',
        'report/kw_project_wise_resources_report_view.xml',
        'report/kw_timesheet_project_report_view.xml',
        'report/timesheet_el_deduct_report.xml',
        'report/resourse_cost_report_view.xml',
        'report/unit_bench.xml',
        'report/kw_timesheet_sub_task_report.xml',
        'report/sbu_resource_cost.xml',
        'report/sbu_tour_expense_report.xml',
        'report/timesheet_per_hour_ctc_report.xml',
        'report/talent_pool_report.xml',
        'report/kw_validated_timesheet_report.xml',
        'report/kw_non_validated_timesheet_report.xml',
        'report/kw_subordinates_timesheet_report.xml',
    ],
    'qweb': ['static/xml/*.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
# -*- coding: utf-8 -*-
