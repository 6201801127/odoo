# -*- coding: utf-8 -*-
{
    'name': 'Employee Directory - STPI',
    'version': '12.0.0.0.0',
    'summary': """Employee Directory - STPI""",
    'description': """Employee Customisation - STPI
                    Last Updated by Sangita changes in Employee Service Report
                    """,
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'version': '12.0.4',
    'depends': ['base','hr', 'hr_employee_stpi'],
    'data': [
        'wizard/employee_action_select.xml',
        'views/employee_b_view.xml',

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
