{
    "name": "PaySlip Report",
    "category": "Kwantify/Human Resources",
    'summary': "Kwantify Payroll Reports",
    'description': """
                
                    """,
    "author": "kwantify@csm.tech",
    "contributors": ["CSM Technologies", ],
    "depends": [
        'hr', 'hr_payroll', 'hr_holidays', 'mail', 'l10n_in_hr_payroll'
    ],
    "version": "12.0.0.6",
    "data": [
        "security/security_payslip_batch_view.xml",
        "security/security.xml",
        "report/payslip_report_view.xml",
        "report/payslip_report.xml",
        # 'view/report_action.xml',
        "view/payslip_report_template_view.xml",
        # "view/hr_salary_rule_view.xml",
        # "view/hr_payslip_run_view.xml",
        "view/payroll_register_view.xml",
        "view/hr_payslip_view.xml"
    ],
    "installable": True
}




