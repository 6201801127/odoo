# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget Guarantees Management',
    'author': 'Deepak Yadav',
    'category': 'Accounting',
    'description': """Bank Guarantees management record monitoring module""",
    'summary': 'Odoo 14 Bank Guarantees Management',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/update_bank_guarantee_views.xml',
        'views/contracts_views.xml',
        'views/bank_quarantee_views.xml',
        'views/menus.xml',

    ],

    "images": ['static/description/icon.png'],
    # 'demo': ['data/account_budget_demo.xml'],
}
