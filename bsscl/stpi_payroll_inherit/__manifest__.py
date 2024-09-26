# -*- coding: utf-8 -*-
{
    'name': 'Payroll Biharsharif Nagar Nigam  and Paylevel',
    'version': '14.0.0',
    'summary': """Payroll.""",
    'description': """Paylevel Master""",
    'category': 'Module for Biharsharif Nagar Nigam',
    'author': 'CSM technologies pvt ltd @deepak yadav',
    'company': 'CSM technologies pvt ltd ',
    'maintainer': 'CSM technologies pvt ltd ',
    'website': "https://www.csm.com",
    'version': '14.0.0',
    'depends': ['base','hr','hr_contract','bsscl_hr_payroll'],
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
        'views/pay_level.xml',
        'views/group_master.xml',
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