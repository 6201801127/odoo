# -*- coding: utf-8 -*-
{
    'name': 'Payroll STPI and Paylevel',
    'version': '12.0.1.0.1',
    'summary': """Payroll.""",
    'description': """Paylevel Master""",
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'version': '12.0.4',
    'depends': ['base','hr','hr_contract','hr_payroll','l10n_in_hr_payroll'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/hr_salary_rule.xml',
        # 'data/hr_payslip_prof_tax.xml',
        'wizard/hr_payment_advices_by_employees_views.xml',
        'wizard/generate_arrear.xml',
        'views/payment_advices.xml',
        'views/hr_payslip_prof_tax.xml',
        'views/leave_deduction_report.xml',
        'views/misc_allowence_deduction.xml',
        'views/arrear.xml',
        'views/arrear_batch.xml',

        'views/res_config_settings.xml',
    ],

    # 'demo': [
    #     'data/previous_occupation_organisation_type_demo.xml',
    #
    # ],


    'installable': True,
    'application': True,
    'auto_install': False,
    'demo': True

}