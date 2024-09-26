# -*- coding: utf-8 -*-
{
    'name': "Kwantify Accounting",

    'summary': """Kwantify Accounting""",

    'description': """
        Kwantify Accounting
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','web','portal','kw_account_accountant', 'sale', 'sale_management', 'account','payment',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/data.xml',
        'data/account_financial_report_data.xml',
        'data/group_head_data.xml',
        'data/group_type_master.xml',
        'data/serial_sequence.xml',
        'wizard/renew_date_assign_wizard.xml',
        'data/fd_expire_reminder_scheduler.xml',
        'data/fd_expire_reminder_mail.xml',
        'data/v5_accounting_system_parameter.xml',
        'views/views.xml',
        'views/kw_group_type_view.xml',
        'views/kw_group_head_view.xml',
        'views/kw_group_name_view.xml',
        'views/kw_account_head_view.xml',
        'views/kw_account_subhead_view.xml',
        'views/chart_of_accounts.xml',
        'views/kw_workorder_master.xml',
        'views/kw_vendor_master.xml',

        'views/print_report/move_voucher.xml',
        'views/fd_tracker.xml',
        'views/calc_fd_interest_wizard.xml',
        'views/fd_report_wizard.xml',
        'views/bg_tracker_view.xml',
        'views/fd_bg_report.xml',
        'views/account_invoice.xml',
        # 'views/account_payment.xml',
        'views/account_move.xml',
        'views/res_partner.xml',
        # 'views/account_payment_method.xml',
        'views/draft_voucher.xml',
        'views/state_gstin.xml',
        'views/server_action_menus.xml',
        'views/agreement.xml',
        'views/creditor_ageing.xml',


        'views/menus.xml',
        'views/hr_loan.xml',

        'reports/account_report_view.xml',
        'reports/company_view.xml',
        'reports/report_financial.xml',
        'reports/search_template_view.xml',
        'reports/report_followup.xml',
        'reports/partner_view.xml',
        'reports/followup_view.xml',
        'reports/account_journal_dashboard_view.xml',
        'reports/res_config_settings_views.xml',

        #bank reconciliation
        'wizard/bank_reconciliation_wizard.xml',
        'views/bank_reconciliation.xml',
        'wizard/bank_reconciliation_wizard_report.xml',
        'wizard/account_company_login.xml',
        'wizard/fd_bg_report.xml',

        #gst&tds report
        'accounting_reports/views/domestic_sales_register_report.xml',
        'accounting_reports/views/export_sales_register_report.xml',
        'accounting_reports/views/creditnote_domestic_sales_register_report.xml',
        'accounting_reports/views/creditnote_export_sales_register_report.xml',
        
        'accounting_reports/views/domestic_purchase_register_report.xml',
        'accounting_reports/views/export_purchase_register_report.xml',
        'accounting_reports/views/creditnote_domestic_purchase_register_report.xml',
        'accounting_reports/views/creditnote_export_purchase_register_report.xml',

        'accounting_reports/views/sales_register_report.xml',
        'accounting_reports/views/sales_credit_note_register_report.xml',
        'accounting_reports/views/purchase_register_report.xml',
        'accounting_reports/views/purchase_debit_note_register_report.xml',
        'accounting_reports/views/tds_payable_register_report.xml',
        'accounting_reports/views/tds_receivable_register_report.xml',

        # 'views/ir_actions_report.xml',
        'accounting_reports/views/menu.xml',
        
        # 'views/print_report/tax_invoice_report.xml',
        # 'views/print_report/vendor_bill_report.xml',
        # 'views/print_report/payment_receipt_voucher.xml',
        # 'views/print_report/report.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
}
