# -*- encoding: utf-8 -*-
{
    'name': 'Fiscal Year',
    'version': '14.0.0.1',
    'category': 'Fiscal Year',
    'summary': 'Fiscal year and account period creation',
    'description': """
        This module provide feature to define fiscal year and period for company 
        and link with journal entry and journal items 
    """,
    'author': 'Ajay Kumar Ravidas',
    'website': 'https://www.ask.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_year_view.xml',
    ],
    'installable': True,
    'application': True,
    'price': 49.99,
    'currency': 'USD',
    'images': ['static/description/test_fiscal_year.jpeg'],
}
