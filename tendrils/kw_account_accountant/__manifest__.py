# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kwantify Accounting',
    'version': '0.1',
    'category': 'Kwantify/Accounting',
    'description': 'Account Management',
    'summary': 'Kwantify Accounting Reports,Kwantify Asset Management and Account Budget ',
    'sequence': '8',
    'author': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': 'https://www.csm.tech',
    'depends': ['kw_accounting_pdf_reports', 'kw_account_asset', 'kw_account_budget'],
    'demo': [],
    'data': [
        'views/account.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
