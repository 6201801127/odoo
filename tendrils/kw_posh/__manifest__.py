# -*- coding: utf-8 -*-
{
    'name': "kw_posh",

    'summary': """POSH""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.csmpl.com",

    'category': 'Uncategorized',
    'version': '0.1',



    # any module necessary for this one to work correctly
    'depends': ['base'],



    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kw_posh_view.xml',
    ],



    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}