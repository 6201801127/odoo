# -*- coding: utf-8 -*-
{
    'name': "Kwantify Advance Claim Integration",

    'summary': """Kwantify Advance Claim Integration""",

    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['kw_advance_claim'],
    # always loaded
    'data': [
        'data/system_params_data.xml',
        'views/advance_salary_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
