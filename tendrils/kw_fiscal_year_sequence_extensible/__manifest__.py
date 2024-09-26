# -*- coding: utf-8 -*-
{
    'name': "Fiscal Year Sequence Extensible",

    'summary': """
        Fiscal Year Sequence Extensible""",

    'description': """
        Fiscal year sequence extensible module is to add prefix and suffix from date range of sequence. 
        We can use %(prefix)s and %('suffix')s as prefix and suffix code.
    """,

    "author": "Kwantify",
    "website": "https://csm.tech",
    "complexity": "easy",
    'license': 'LGPL-3',
    'support': 'kwantify@csm.tech',
    # for the full list
    'category': 'Kwantify/Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_sequence_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
