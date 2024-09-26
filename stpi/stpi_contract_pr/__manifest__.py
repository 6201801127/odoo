# -*- coding: utf-8 -*-
{
    'name': 'Contract and Paylevel',
    'version': '12.0.1.0.1',
    'summary': """Paylevel Master.""",
    'description': """Paylevel Master""",
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'version': '12.0.4',
    'depends': ['base','hr','hr_contract','hr_payroll','base_address_city','l10n_in_hr_payroll'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/update_basic_da_cron.xml',
        'views/res_city_inherit.xml',
        'views/hr_payroll.xml',
        'views/hr_employee_contracts.xml',
        'views/contract_basic_da_change_log_views.xml',
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