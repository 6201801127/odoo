# -*- coding: utf-8 -*-
{
    'name': "Kwantify Accounting",

    'summary': """Kwantify Accounting""",

    'description': """
        Kwantify Accounting
    """,

    'author': "CSM Technologies",
    'website': "http://www.csm.tech",
    'category': 'Kwantify/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'account','payment','bsscl_budget_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/account_financial_report_data.xml',
        'data/group_head_data.xml',
        'data/group_type_master.xml',
        'views/views.xml',
        'views/kw_group_type_view.xml',
        'views/kw_group_head_view.xml',
        'views/kw_group_name_view.xml',
        'views/kw_account_head_view.xml',
        'views/kw_account_subhead_view.xml',
        'views/chart_of_accounts.xml',

        #'views/account_invoice.xml',
        #'views/account_payment.xml',
        #'views/res_partner.xml',
        #'views/account_payment_method.xml',
        'views/menus.xml',
        'reports/account_report_view.xml',
        # 'reports/company_view.xml',
        'reports/report_financial.xml',
        'reports/search_template_view.xml',
        #'reports/report_followup.xml',
        # 'reports/partner_view.xml',
        'reports/followup_view.xml',
        'reports/account_journal_dashboard_view.xml',
        # 'reports/res_config_settings_views.xml',

        #bank reconciliation
        #'wizard/bank_reconciliation_wizard.xml',
        #'views/bank_reconciliation.xml',
        
        # 'views/print_report/tax_invoice_report.xml',
        # 'views/print_report/vendor_bill_report.xml',
        # 'views/print_report/payment_receipt_voucher.xml',
        # 'views/print_report/accounting_voucher.xml',
        # 'views/print_report/report.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
    ],
    'installable': True,
    'application': True,
}
