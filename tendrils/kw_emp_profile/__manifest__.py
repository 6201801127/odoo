# -*- coding: utf-8 -*-
{
    "name": "Kwantify Employee Profile",
    "summary": "Kwantify Employee Profile",
    "description": "Kwantify Employee Profile",
    "author": "CSM Technologies",
    "website": "https://www.csm.tech",

    "category": "Kwantify",
    "version": "0.1",

    "depends": ["base", "kw_employee", "kw_employee_info_system", 'kw_appraisal', 'performance_improvement_plan'],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        'data/kw_cdp_category_data.xml',
        'data/hr_job_cdp_data.xml',
        "data/get_employee.xml",
        "data/employees_to_ra_scheduler.xml",

        "views/email/kw_emp_profile_change_request.xml",
        "views/email/kw_emp_profile_approve_changes.xml",
        "views/email/kw_emp_profile_reject_changes.xml",
        "views/email/kw_emp_profile_passport_dl_expiry.xml",
        'views/res_config_setting.xml',
        "views/menu.xml",
        "views/template.xml",
        "views/kw_emp_profile.xml",
        "views/kw_emp_profile_new_data_view.xml",
        "views/all_approvals.xml",
        "views/profile_summary_report.xml",
        "views/educational_update_emp_profile.xml",
        "views/emp_pan_update_log.xml",
        "views/emp_pan_update_login_template.xml",
        "reports/kw_employee_profile_skill.xml",
        'views/hr_job_cdp.xml',
        'views/kw_cdp_category.xml',
        'views/organisation_commitee.xml',
        'views/cv_info_template.xml',
        'views/kw_emp_cv_new_info_view.xml',

    ],
    "qweb": [
        "static/src/xml/appmenu.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
