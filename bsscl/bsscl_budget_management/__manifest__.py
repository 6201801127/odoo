# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget Management',
    'author': 'Deepak Yadav',
    'category': 'Accounting',
    'description': """Use budgets to compare actual with expected revenues and costs""",
    'summary': 'Odoo 14 Budget Management',
    'depends': ['account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/account_budget_security.xml',
        'data/ir_sequence_data.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/investment_views.xml',
        'views/budget_utilization_view.xml',
        'views/fund_utilization_views.xml',
        'views/menu.xml',
        'views/res_config_settings.xml',
    ],

    "images": ['static/description/banner.gif'],
    # 'demo': ['data/account_budget_demo.xml'],
}
