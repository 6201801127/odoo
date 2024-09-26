# -*- coding: utf-8 -*-
{
    "name": "Kwantify Payroll Integration",
    "summary": """Kwantify Payroll Integration.""",
    "description": """Kwantify Payroll Integration with Attendance and Advance.""",
    "category": "Kwantify/Human Resources",
    "author": "kwantify@csm.tech",
    "company": "CSM Technologies",
    "maintainer": "CSM Technologies",
    "website": "https://www.csm.tech",
    "version": "1.0.1",
    "depends": ["payroll_inherit", "kw_hr_attendance", "kw_hr_leaves", 'kw_emp_profile', 'tds'],
    "data": [
        "security/ir.model.access.csv",
        "data/payroll_salary_rule_data.xml",
        "views/kw_hr_attendance_payroll_report.xml",
        "views/employee_profile_inherit.xml",
        "views/kw_employee_bonus_report.xml",
        "views/health_insurance_policy_master.xml"
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
