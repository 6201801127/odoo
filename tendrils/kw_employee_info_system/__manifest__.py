{
    'name': "Employee Information System",
    'summary': "Employee Information",
    'description': "Employee MIS",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    'depends': ['base', 'hr', 'kw_employee', 'payroll_inherit', 'kw_eos', 'kw_resource_management'],
    'data': [
        'security/kwemp_security.xml',
        'security/ir.model.access.csv',
        'views/total_resource_vs_ctc.xml',
        'views/vendor_wise_records.xml',
        'wizards/vendorwise_records_wizard.xml',
        'wizards/total_resource_vs_ctc_wizard.xml',
        'views/mis_menu.xml',

        'views/mis_manager.xml',
        'views/access_report_views.xml',
        'data/experience_update_cron.xml',
        # 'views/kw_fy_emp_report_view.xml',
        'views/kw_ir_cron_details.xml',
        'views/year_on_year_resource_report.xml',
        'views/asset.xml',
        'views/kw_employee_mis_report.xml',
        # 'views/kwemp_resource_budget.xml',
        # 'views/kw_resource_budget_settings.xml',
        # 'wizards/employment_close.xml',

        # 'views/contract_end_report.xml',
        'views/mis_for_academic_professional_qualification.xml',
        'views/mis_resource_report.xml',
        'views/mis_outsource_view.xml',
        'views/employee_personal_details_report.xml',
        'views/joining_attrition_report_view.xml',
        'views/departmentwise_report.xml',
        

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

