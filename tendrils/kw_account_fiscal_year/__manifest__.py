# -*- encoding: utf-8 -*-
{
    'name': 'Kwantify Account Fiscal Year',
    'version': '12.0.0.1',
    'category': 'Kwantify/Tools',
    'summary': 'Fiscal year and account period creation',
    'description': """
        This module provide feature to define fiscal year and period for company 
        and link with journal entry and journal items
    """,
    'author': 'CSM Technologies Pvt Ltd',
    'website': 'https://www.geotechnosoft.com',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_fiscal_year_view.xml',
        'views/account_move_view.xml',
    ],
    # 'price': 19.00,
    # 'currency': 'EUR',
    # 'license': 'OPL-1',
    'installable': True,
    'application': True,
}
