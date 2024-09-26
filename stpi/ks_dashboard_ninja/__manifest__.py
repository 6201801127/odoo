# -*- coding: utf-8 -*-
{
    'name': "STPI Dashboard",

    'summary': """
    STPI Dashboard
    """,

    'description': """
        STPI Dashboard

    """,

    'depends': ['base', 'web', 'base_setup','hr',],

    'data': [
        'security/ks_security_groups.xml',
        'security/ir.model.access.csv',
        'data/ks_default_data.xml',
        'data/portlet_master.xml',
        'views/ks_dashboard_ninja_item_view.xml',
        'views/portlet_master.xml',
        'views/ks_dashboard_ninja_view.xml',
        'views/ks_dashboard_userwise_portlet.xml',
        'views/ks_dashboard_ninja_assets.xml',
        'views/ks_dashboard_action.xml',
    ],
    'qweb': [
        'static/src/xml/ks_dashboard_ninja_templates.xml',
        'static/src/xml/ks_dashboard_ninja_item_templates.xml',
        'static/src/xml/ks_dashboard_ninja_item_theme.xml',
        'static/src/xml/ks_widget_toggle.xml',
        'static/src/xml/ks_dashboard_pro.xml',
        'static/src/xml/stpi_dashboard.xml',
        'static/src/xml/ks_import_list_view_template.xml',
        'static/src/xml/ks_quick_edit_view.xml',
    ],

    'demo': [
        # 'demo/ks_dashboard_ninja_demo.xml',
    ],
    'installable': True,
    'application': True,
    'uninstall_hook': 'uninstall_hook',

}
