{
    'name': "Kwantify Inventory",

    'summary': """
        Kwantify inventory, purchase, stock and logistics activities
    """,

    'description': """
        Kwantify inventory, purchase, stock and logistics activities
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale_management', 'product', 'uom', 'l10n_in', 'payment',
                'purchase_stock', 'delivery'],

    # always loaded
    'data': [
        'security/kw_inventory_security.xml',
        'security/ir.model.access.csv',
        'views/purchase/kw_quotation_action.xml',
        'data/kw_sequence_data.xml',
        'data/kw_pr_sequence.xml',
        'data/kw_inventory_email.xml',
        'data/product_category_Data.xml',

        'views/inventory/product_views.xml',
        'views/inventory/kw_indent_sequence.xml',
        'views/inventory/kw_remark.xml',
        'views/inventory/kw_remark_reject.xml',
        'views/inventory/inventory_adjustment_view.xml',
        'views/inventory/indent_consolidation.xml',
        'views/inventory/kw_inventory_res_partner_view.xml',
        'views/inventory/kw_rfq.xml',
        'views/inventory/chart_of_account.xml',
        'views/inventory/kw_inventory_wizard.xml',
        'views/inventory/kw_inventory_view_asset.xml',
        'views/inventory/kw_remark_onhold.xml',
        'views/inventory/kw_inventory_report_views.xml',
        'views/inventory/res_config_setting_view.xml',
        'views/inventory/res_config_setting_view_signature_autority.xml',
        'views/inventory/res_partner_view.xml',
        'views/inventory/kw_inventory_transporter_master_view.xml',

        'views/inventory/kw_sequence_master_view.xml',

        'views/inventory/kw_asset.xml',
        'views/inventory/asset_tracker.xml',
        'views/inventory/kw_daily_receipt_register.xml',
        'views/inventory/kw_stock_picking_view.xml',
        'views/inventory/stock_picking_inherit.xml',
        'views/inventory/kw_product_template_views.xml',
        'views/purchase/kw_inventory_quotation_wizard.xml',
        'views/inventory/res_partner_vendor_inherited.xml',
        'views/inventory/vendor_approval_mail_template.xml',

       
        'views/purchase/kw_inventory_quotation_consolidation_wizard.xml',
        'views/purchase/kw_quotation_consolidation_sequence.xml',
        'views/purchase/kw_mode_of_negotiation_master.xml',
        'views/purchase/kw_quotation_sequence.xml',
        'views/purchase/stock_warehouse_orderpoint.xml',
        'views/purchase/kw_quotation_consolidation.xml',
        'views/purchase/add_product_consolidation.xml',
        'views/purchase/approved_requisition_items.xml',
        'views/purchase/add_product.xml',
        'views/purchase/negotiation_consolidation_report.xml',
        'views/purchase/negotiation.xml',
        'views/purchase/purchase_requisition_view.xml',
        'views/purchase/kw_quotation.xml',
        'views/purchase/kw_quotation_items.xml',
        'views/purchase/kw_quotation_consolidation_items.xml',
        'views/purchase/kw_approved_negotiations.xml',
        'views/purchase/kw_quotation_consolidation_decision_stage.xml',
        'views/purchase/consolidation_template.xml',
        'views/purchase/kw_negotiation.xml',
        'views/purchase/kw_ready_for_po.xml',
        'views/purchase/kw_quotation_consolidation_items_wizard.xml',
        'views/purchase/stock_move_line_view.xml',
        'views/purchase/kw_purchase_report.xml',
        'views/purchase/kw_po_register_view.xml',
        'views/purchase/purchase_type_views.xml',
        'views/purchase/stock_move_inherit.xml',

        'wizards/kw_material_management_remark.xml',
        'wizards/product_receive_remark.xml',
        'wizards/kw_requisition_remark.xml',
        'views/material_management/requisition_report_assets.xml',

        'wizards/kw_material_request_quotation_wizard.xml',
        'wizards/kw_issue_repair_damage_wiz.xml',
        'wizards/kw_gatepass_assign_wiz.xml',
        'wizards/asset_tracker_wizard.xml',
        'views/material_management/add_product_items.xml',
        'views/material_management/material_request.xml',
        'views/material_management/material_request_take_action.xml',
        'views/material_management/material_request_store_manager_action.xml',
        'views/material_management/kw_product_assign_release_log.xml',
        # 'views/material_management/stock_quant_inherited.xml',
        'views/material_management/material_request_report.xml',
        'views/material_management/product_inherit_buttons.xml',
        
        'views/material_management/service_register.xml',

        'reports/grn_action.xml',
        'reports/gatepass.xml',
        'reports/kw_srv_report.xml',
        'reports/inventory_report.xml',
        'reports/kw_grn_report_view.xml',
        'reports/kw_inspection_report.xml',

        'views/inventory/inventory_menu.xml',
        'views/material_management/kw_material_store.xml',
        'views/material_management/fa_register.xml',
        'views/inventory/stock_operations.xml',
        'views/inventory/stock_picking_type_view.xml',
        'views/material_management/templates.xml',
        'data/material_management_email_template.xml',
        'views/material_management/codification_master.xml',
        'views/material_management/kw_product_category_master.xml',
        'views/material_management/stock_dept_config.xml',
        'views/material_management/material_management_log.xml',

        
    ],
    'qweb': ['static/src/xml/kw_inventory_report_view.xml',
             'static/src/xml/form_view_button.xml',
             ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# -*- coding: utf-8 -*-
