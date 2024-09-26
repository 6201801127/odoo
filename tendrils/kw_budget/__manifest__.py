# -*- coding: utf-8 -*-
{
    'name': "Kwantify Budget",

    'summary': """
          This project would be an in-house application that should capable to manage budget management 
        for all CSM projects. After LIVE the maintenance cost has to be minimum
       """,

    'description': """
      
    """,

    'author': "CSM Technology",
    'website': "http://www.csm.co.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','account','kw_accounting'],

    # always loaded
    'data': [
        'security/groups_security.xml',
        'security/ir.model.access.csv',
        'wizard/budget_revert_wizard_views.xml',
        'wizard/kw_xlsx_report.xml',
        'wizard/budget_status_views.xml',
        'views/kw_capital_budget_view.xml',
        'views/kw_revenue_budget_view.xml',
        'views/budget_dept_mapping.xml',
        'views/sbu_project_mapping_view.xml',
        'views/sbu_project_category_master_view.xml',
        'views/sbu_project_budget_view.xml',
        'views/kw_budget_group_mapping_view.xml',
        # 'views/budget_report_group_mapping_view.xml',
        'reports/revenue_budget_report.xml',
        'reports/capital_budget_report.xml',
        'reports/capital_budget_expense_report.xml',
        'reports/revenue_budget_expense_report.xml',
        'reports/project_expense_report_view.xml',
        'reports/kw_consolidated_revenue_budget_report_view.xml',
        'reports/kw_consolidated_capital_budget_report_view.xml',
        'reports/kw_consolidated_sbu_project_budget_view.xml',
        'reports/kw_project_budget_report_view.xml',
        'reports/kw_cash_flow_report.xml',
        'reports/kw_annual_approved_budget_report_view.xml',
        'reports/annual_treasury_report_budget_actual_view.xml',
        'reports/annual_treasury_draft_budget_actual_view.xml',
        'reports/annual_capital_budget_vs_actual_view.xml',
        'reports/annual_project_budget_vs_actual_view.xml',
        'reports/annual_capital_draft_budget_vs_actual_view.xml',
        'reports/annual_project_draft_budget_vs_actual_view.xml',
        'reports/annual_revenue_draft_budget_vs_actual_view.xml',
        'reports/revenue_budget_vs_actual_view.xml',
        'reports/annual_revenue_budget_vs_actual_view.xml',
        'reports/department_wise_treasury_report_view.xml',
        'reports/department_wise_capital_budget_view.xml',
        'reports/project_wise_budget_vs_actual_view.xml',
        'reports/kw_treasury_approved_budget_view.xml',
        'reports/kw_capital_approved_budget_report_view.xml',
        'reports/kw_project_approved_budget_report_view.xml',
        'reports/kw_cash_flow_budget_vs_actual_view.xml',
        'views/api_system_parameters.xml',
        'views/project_budget_sync_data.xml',
        'views/account_views.xml',
        'views/kw_cash_flow.xml',
        'reports/kw_consolidated_revenue_budget_next_fy_view.xml',
        'views/kw_resource_budget.xml',
        # 'views/budget_allocation.xml',
        'views/fy_wise_plan.xml',
        'views/sub_head_wise_role_tagging.xml',
        'views/transfer_monthly_amount_wizard.xml',
        'views/budget_transfer_approval_wizard.xml',
        'views/kw_project_budget_transfer.xml',
        'views/report_groups_access_views.xml',
        'views/menus.xml',

    ],
    #  'qweb': [
    #     'static/src/xml/*.xml',
    #  ],
    # only loaded in demonstration mode

    'demo': [

    ],
}