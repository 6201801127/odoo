# -*- coding: utf-8 -*-
{
    'name': 'Document Master - STPI',
    'version': '12.0.1.0.0',
    'summary': """Employee Customisation - STPI""",
    'description': """Employee Customisation - STPI""",
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'version': '12.0.4',
    'depends': ['base','hr','oh_employee_documents_expiry'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/relative_type_demo.xml',
        'views/hr_employee_main.xml',
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