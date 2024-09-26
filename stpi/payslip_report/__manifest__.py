{
    "name": "PaySlip Report",
    "version": "12.0.0.6",
    "category": "PaySlip",
    'summary': 'PaySlip Report',
    'description': """
                
                    """,
    "author": "Sangita",
    "contributors": [
                    "Dexciss Technology (Sangita)",
                    ],
    "depends": [
                'hr','hr_payroll','hr_holidays','mail','hr_employee_stpi','leaves_stpi','hr_branch_company','l10n_in_hr_payroll'
                ],
    
    "data": [
            "security/security_payslip_batch_view.xml",
            "security/security.xml",
            "report/payslip_report_view.xml",
            "report/payslip_report.xml",
            "view/payslip_report_template_view.xml",
            "view/payroll_register_report.xml",
            "view/hr_salary_rule_view.xml",
            "view/hr_payslip_run_view.xml",
            "view/payroll_register_view.xml",
            "view/hr_payslip_view.xml",
            ],
            
    "installable": True
}
