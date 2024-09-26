# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kwantify Budget Management',
    'author': 'CSM Technologies',
    'version': '0.1',
    'website': 'https://www.csm.tech',
    'category': 'Kwantify/Accounting',
    'description': """Compares the actual with the expected revenues and costs using Budget""",
    'summary': 'Kwantify Budget Management',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/res_config_settings_views.xml',
    ],
    "images": ['static/description/banner.gif'],
    'demo': ['data/account_budget_demo.xml'],
}
