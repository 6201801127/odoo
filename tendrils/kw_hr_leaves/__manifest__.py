# -*- coding: utf-8 -*-
{
    'name': "Kwantify Leave Management",

    'summary': """
        Kwantify Leave Management""",

    'description': """
        Kwantify Leave Management
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Employee',
    'version': '0.1',

    'depends': ['base', 'hr_holidays', 'kw_account_fiscal_year', 'kw_employee'],

    'data': [
        'security/ir.model.access.csv',
        'security/kw_hr_leaves_security.xml',
        
        'views/hr_leave_type.xml',
        # 'views/kw_leave_type_master.xml',
        'views/kw_leave_cycle_master.xml',
        'views/kw_leave_entitlements.xml',
        'views/kw_credit_rule_config.xml',
        # 'views/kw_comp_off.xml',
        # 'wizard/kw_leave_take_action_wizard.xml',
        'views/hr_leave_views.xml',
        'views/kw_set_encashment_period.xml',
        'views/kw_compute_cf_encashment.xml',
        'views/kw_leave_type_config.xml',
        'views/kw_cancel_leave.xml',
        'views/hr_employee_in.xml',

        'data/kw_leave_allocation_cron.xml',
        'data/kw_hr_leave_approval_mail.xml',
        'data/kw_hr_leave_apply_mail.xml',
        'data/kw_hr_leave_reject_mail.xml',
        'data/kw_hr_leave_forward_mail.xml',
        'data/kw_hr_leave_hold_mail.xml',
        'data/kw_hr_leave_cancel_mail.xml',
        'data/kw_hr_leave_cancel_apply_mail.xml',
        'data/kw_hr_leave_cancel_approve_mail.xml',
        'data/kw_hr_leave_cancel_reject_mail.xml',
        'data/kw_hr_leave_cancel_forward_mail.xml',
        'data/kw_hr_leave_escallation_forward_mail.xml',
        # 'data/kw_comp_off_apply_mail.xml',
        # 'data/kw_comp_off_approval_mail.xml',
        # 'data/kw_comp_off_reject_mail.xml',

        'report/hr_leave_reports.xml',
        'report/hr_leave_summary_report.xml',
        'report/kw_hr_leave_report.xml',
        'report/kw_hr_leave_type_report.xml',
        'report/hr_leave_status_report.xml',
        'views/kw_leave_approval_log.xml',
        'wizard/kw_leave_approval_wizard.xml',
        'views/hr_leave_allocation.xml',
        'views/res_config_settings_view.xml',
        'views/kw_leave_menu.xml',
        'report/kw_carryforward_encashment_report.xml',
        'views/leave_assets.xml',
    ],
    
}