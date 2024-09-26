# -*- coding: utf-8 -*-
{
    'name': "LTC - STPI",
    'summary': """ LTC - STPI""",
    'description': """
    """,
    'author': "Dexciss Technology Pvt Ldt (RGupta)",
    'website': "http://www.dexciss.com",
    'description': """

    """,
    'category': 'hrms',
    'version': '12.0.1',
    'depends': ['base','hr','hr_holidays','hr_applicant'],
    'data': [
        'security/ir.model.access.csv',
        'security/ltc_security.xml',
        'wizard/select_child_block.xml',
        'data/ltc_mode_demo_data.xml',
        'views/employee_ltc.xml',
        'views/ltc_configuration.xml',
        'report/ltc_report.xml',
        'wizard/same_address_wizard_views.xml',

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