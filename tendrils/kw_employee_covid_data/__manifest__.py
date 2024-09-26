# -*- coding: utf-8 -*-
{
    'name': "Employee Covid Data",
    'summary': "Advance features of employee",
    'description': "Employee Covid Data",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/WebTemplate/kw_employee_covid_data_controller.xml',
        'views/assets.xml',
        'views/kw_employee_covid_data.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
